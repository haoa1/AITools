"""
sandbox.py — 通用交互式应用沙箱

架构:
  sandbox = 隔离环境（tmux workspace + PTY 子进程）
  send()  → 跟内部 PTY 进程交互（任何应用）
  exec()  → tmux bash 命令
  start() → 异步部署，异步通知就绪

异步流程（像 agent_tool）：
  1. start(cmd="/tmp/some_app") → 立即返回 task_id
  2. 后台启动进程，准备好后 publish 通知
  3. send() → 写入 PTY，等 prompt，返回结果
  4. send(async=True) → 立即返回 task_id，后台等 prompt，完成后通知
"""

import os
import sys
import pty
import time
import json
import uuid
import select
import shutil
import threading
import subprocess
from typing import Optional, Dict, Any

# Tool definition framework
from base import function_ai, parameters_func, property_param

# ---------------------------------------------------------------------------
# 事件系统集成（可选）
# ---------------------------------------------------------------------------
try:
    from garuda.async_core.event_system import publish_event, \
        EVENT_TASK_COMPLETED, EVENT_TASK_FAILED
    HAS_EVENTS = True
except ImportError:
    HAS_EVENTS = False

# ---------------------------------------------------------------------------
# 全局状态
# ---------------------------------------------------------------------------
_sandboxes: Dict[str, "SandboxInstance"] = {}
_sandboxes_lock = threading.Lock()

SANDMARK = "###SANDMARK_END###"


# =============================================================================
# SandboxInstance — 一个沙箱管理一个隔离环境
# =============================================================================
class SandboxInstance:
    def __init__(self, name: str, workspace_dir: str):
        self.name = name
        self.workspace_dir = workspace_dir

        # PTY 子进程
        self.proc: Optional[subprocess.Popen] = None
        self.pty_master_fd: Optional[int] = None

        # Reader 线程
        self.reader_thread: Optional[threading.Thread] = None
        self.reader_running = False

        # Tmux workspace
        self.tmux_session = f"garuda-sandbox-{name}"

        # 输出 buffer
        self._buffer = ""
        self._buf_lock = threading.Lock()

        # 异步任务跟踪
        self._async_tasks: Dict[str, Dict] = {}
        self._async_lock = threading.Lock()

        # 就绪状态
        self._ready = threading.Event()
        self._start_result = None

    # ---- buffer 操作 ----
    def append(self, text: str):
        with self._buf_lock:
            self._buffer += text

    def get_buffer(self) -> str:
        with self._buf_lock:
            return self._buffer

    def clear_buffer(self) -> str:
        with self._buf_lock:
            data = self._buffer
            self._buffer = ""
            return data

    # ---- prompt 检测 ----
    def wait_for_prompt(self, prompt: str = None, timeout: float = 120.0) -> str:
        """等待 prompt 出现，返回累积输出"""
        if prompt is None:
            prompt = self._detect_prompt()
        deadline = time.time() + timeout
        last_len = -1
        while time.time() < deadline:
            with self._buf_lock:
                current_len = len(self._buffer)
            if current_len > last_len:
                last_len = current_len
                with self._buf_lock:
                    buf = self._buffer
                if prompt in buf:
                    parts = buf.split(prompt)
                    response = parts[-2].strip() if len(parts) >= 2 else buf.strip()
                    with self._buf_lock:
                        self._buffer = ""
                    return response
            time.sleep(0.05)
        raise TimeoutError(
            f"等待 '{prompt}' 超时 {timeout}s. "
            f"Buffer: {self._buffer[-300:]!r}"
        )

    def _detect_prompt(self) -> str:
        """从 buffer 开头尝试猜测 prompt 标记"""
        buf = self.get_buffer()
        lines = buf.split("\n")
        for line in lines[:10]:
            line = line.strip()
            if line and any(c in line for c in ">$%#]❯"):
                return line
        return "$ "

    # ---- 异步任务管理 ----
    def store_async_result(self, task_id: str, result: Dict):
        with self._async_lock:
            self._async_tasks[task_id] = result

    def get_async_result(self, task_id: str) -> Optional[Dict]:
        with self._async_lock:
            return self._async_tasks.get(task_id)

    # ---- 清理 ----
    def cleanup(self, remove_dir: bool = True):
        self.reader_running = False
        if self.pty_master_fd is not None:
            try:
                os.close(self.pty_master_fd)
            except:
                pass
            self.pty_master_fd = None
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except:
                try:
                    self.proc.kill()
                except:
                    pass
        if self.tmux_session:
            try:
                subprocess.run(["tmux", "kill-session", "-t", self.tmux_session],
                               capture_output=True, timeout=5)
            except:
                pass
        if remove_dir and self.workspace_dir and os.path.isdir(self.workspace_dir):
            shutil.rmtree(self.workspace_dir, ignore_errors=True)
        self.proc = None
        self.reader_thread = None


# =============================================================================
# Reader 线程
# =============================================================================
def _reader_worker(si: SandboxInstance):
    si.reader_running = True
    mfd = si.pty_master_fd
    if mfd is None:
        si.reader_running = False
        return
    try:
        while si.reader_running:
            ready, _, _ = select.select([mfd], [], [], 0.3)
            if not ready:
                continue
            try:
                chunk = os.read(mfd, 4096)
                if not chunk:
                    break
                si.append(chunk.decode("utf-8", errors="replace"))
            except OSError:
                break
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        si.reader_running = False


# =============================================================================
# Core API
# =============================================================================

def _start_sandbox(
    name: str,
    cmd: str = None,
    timeout: float = 30.0,
    prompt: str = None,
    async_mode: bool = False,
) -> Dict:
    """
    启动一个交互式应用沙箱。

    Args:
        name: 沙箱名称
        cmd: 要启动的交互式应用（如 "python3 test_app.py"）
        timeout: 等待应用就绪的超时
        prompt: 应用使用的 prompt 标记（用于等待就绪和提取响应）
        async_mode: 是否异步启动（立即返回 task_id）
    """
    with _sandboxes_lock:
        if name in _sandboxes:
            return {"error": f"沙箱 '{name}' 已存在"}

    # 创建工作空间
    ws_dir = f"/tmp/garuda-sandbox-{name}"
    if os.path.exists(ws_dir):
        shutil.rmtree(ws_dir, ignore_errors=True)
    os.makedirs(os.path.join(ws_dir, "workspace"), exist_ok=True)

    si = SandboxInstance(name, ws_dir)

    # 默认启动 garuda
    if cmd is None:
        cmd = "garuda -i --no-sandbox"

    # 解析命令
    cmd_parts = cmd.split()
    cmd_prog = cmd_parts[0]
    cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []

    # 默认 prompt - 根据命令猜测
    if prompt is None:
        if "garuda" in cmd:
            prompt = "Garuda >"
        elif "test_app" in cmd:
            prompt = "❯"
        elif "python" in cmd and "-i" in cmd:
            prompt = ">>>"
        else:
            prompt = "$"

    # 打开 PTY
    mfd, sfd = pty.openpty()

    # 环境
    env = {
        **os.environ,
        "TERM": "xterm-256color",
        "PYTHONUNBUFFERED": "1",
        "GARUDA_SANDBOX_CHILD": "1",
    }

    try:
        proc = subprocess.Popen(
            [cmd_prog] + cmd_args,
            stdin=sfd, stdout=sfd, stderr=sfd,
            cwd=os.path.join(ws_dir, "workspace"),
            env=env,
            start_new_session=True,
        )
    except FileNotFoundError:
        os.close(mfd)
        os.close(sfd)
        shutil.rmtree(ws_dir, ignore_errors=True)
        return {"error": f"命令未找到: '{cmd_prog}'"}
    except Exception as e:
        os.close(mfd)
        os.close(sfd)
        shutil.rmtree(ws_dir, ignore_errors=True)
        return {"error": f"启动失败: {e}"}

    os.close(sfd)
    si.proc = proc
    si.pty_master_fd = mfd

    # 启动 reader
    reader = threading.Thread(target=_reader_worker, args=(si,), daemon=True)
    reader.start()
    si.reader_thread = reader

    # 创建 tmux workspace
    try:
        subprocess.run(
            ["tmux", "new-session", "-d", "-s", si.tmux_session, "-n", "workspace"],
            capture_output=True, timeout=5, check=True
        )
        subprocess.run(
            ["tmux", "send-keys", "-t", f"{si.tmux_session}:0",
             f"cd {os.path.join(ws_dir, 'workspace')} && clear", "Enter"],
            capture_output=True, timeout=3
        )
    except:
        pass

    _sandboxes[name] = si

    if async_mode:
        # 异步启动
        task_id = f"sandbox_start_{uuid.uuid4().hex[:6]}"
        def _start_watcher():
            try:
                si.wait_for_prompt(prompt=prompt, timeout=timeout)
                si._ready.set()
                result = {
                    "status": "completed",
                    "name": name,
                    "pid": proc.pid,
                    "workspace": ws_dir,
                    "ready_at": time.strftime("%H:%M:%S"),
                }
                si._start_result = result
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_COMPLETED, {
                        "task_id": task_id,
                        "description": f"sandbox start: {name}",
                        "tool_name": "sandbox",
                        "result_summary": f"沙箱 '{name}' 已就绪 (PID={proc.pid})",
                        "result": result,
                    })
            except TimeoutError as e:
                result = {"status": "failed", "error": str(e)}
                si._start_result = result
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox start: {name}",
                        "tool_name": "sandbox",
                        "error_message": str(e),
                    })
            except Exception as e:
                result = {"status": "failed", "error": str(e)}
                si._start_result = result
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox start: {name}",
                        "tool_name": "sandbox",
                        "error_message": str(e),
                    })
        w = threading.Thread(target=_start_watcher, daemon=True)
        w.start()
        return {
            "success": True,
            "async": True,
            "task_id": task_id,
            "name": name,
            "message": f"沙箱 '{name}' 正在启动（{cmd}），就绪后将通知",
        }

    # 同步启动：等 prompt
    try:
        si.wait_for_prompt(prompt=prompt, timeout=timeout)
    except TimeoutError as e:
        proc.terminate()
        proc.wait(3)
        os.close(mfd)
        si.pty_master_fd = None
        si.reader_running = False
        shutil.rmtree(ws_dir, ignore_errors=True)
        _sandboxes.pop(name, None)
        return {"error": f"应用未在 {timeout}s 内启动: {e}"}

    si._ready.set()
    return {
        "success": True,
        "name": name,
        "workspace": ws_dir,
        "pid": proc.pid,
        "cmd": cmd,
    }


def _send_to_sandbox(
    name: str,
    text: str,
    timeout: float = 120.0,
    prompt: str = None,
    async_mode: bool = False,
) -> Dict:
    """
    向沙箱内部应用发送消息并等待响应。

    sync 模式：阻塞等 prompt 返回
    async 模式：立即返回 task_id，完成后通知
    """
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    if si.proc is None or si.proc.poll() is not None:
        return {"error": f"沙箱进程已退出 (PID={si.proc.pid if si.proc else 'N/A'})"}
    if si.pty_master_fd is None:
        return {"error": "PTY 不可用"}

    mfd = si.pty_master_fd

    # 清除残留
    si.clear_buffer()

    # 写入
    try:
        os.write(mfd, (text + "\n").encode("utf-8"))
    except OSError as e:
        return {"error": f"PTY 写入失败: {e}"}

    if async_mode:
        task_id = f"sandbox_send_{uuid.uuid4().hex[:6]}"
        def _send_watcher():
            try:
                response = si.wait_for_prompt(prompt=prompt, timeout=timeout)
                result = {
                    "status": "completed",
                    "response": response,
                    "task_id": task_id,
                    "completed_at": time.strftime("%H:%M:%S"),
                }
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_COMPLETED, {
                        "task_id": task_id,
                        "description": f"sandbox send to '{name}': {text[:50]}",
                        "tool_name": "sandbox",
                        "result_summary": response[:200] if response else "[empty]",
                        "result": result,
                    })
            except TimeoutError as e:
                result = {"status": "failed", "error": str(e)}
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox send to '{name}'",
                        "tool_name": "sandbox",
                        "error_message": str(e),
                    })
            except Exception as e:
                result = {"status": "failed", "error": str(e)}
                si.store_async_result(task_id, result)
                if HAS_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox send to '{name}'",
                        "tool_name": "sandbox",
                        "error_message": str(e),
                    })
        w = threading.Thread(target=_send_watcher, daemon=True)
        w.start()
        return {
            "success": True,
            "async": True,
            "task_id": task_id,
            "name": name,
            "message": f"消息已发送到 '{name}'，完成后将通知（task: {task_id}）",
        }

    # sync
    try:
        response = si.wait_for_prompt(prompt=prompt, timeout=timeout)
    except TimeoutError as e:
        return {"error": str(e)}

    return {
        "success": True,
        "response": response,
        "name": name,
    }


def _exec_in_workspace(name: str, cmd: str, timeout: float = 30.0) -> Dict:
    """在 tmux workspace 执行 bash 命令（不变）"""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    target = f"{si.tmux_session}:0"

    r = subprocess.run(["tmux", "has-session", "-t", si.tmux_session],
                       capture_output=True, timeout=3)
    if r.returncode != 0:
        return {"error": "tmux session 不存在"}

    try:
        baseline = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p"],
            capture_output=True, timeout=5
        ).stdout.decode("utf-8", errors="replace")
    except:
        baseline = ""

    subprocess.run(
        ["tmux", "send-keys", "-t", target,
         f"echo '{SANDMARK}' && {cmd} && echo '{SANDMARK}'", "Enter"],
        capture_output=True, timeout=5
    )

    deadline = time.time() + timeout
    output = ""
    while time.time() < deadline:
        try:
            captured = subprocess.run(
                ["tmux", "capture-pane", "-t", target, "-p"],
                capture_output=True, timeout=5
            ).stdout.decode("utf-8", errors="replace")
        except:
            break
        new_content = captured[len(baseline):] if len(captured) > len(baseline) else captured
        if SANDMARK in new_content:
            lines = new_content.split("\n")
            in_output = False
            out_lines = []
            for line in lines:
                if not in_output and SANDMARK in line:
                    in_output = True
                    continue
                elif in_output and SANDMARK in line:
                    break
                if in_output:
                    out_lines.append(line)
            output = "\n".join(out_lines).strip()
            break
        time.sleep(0.3)

    if not output:
        output = (new_content or captured)[-2000:]

    return {"success": True, "output": output[:2000], "name": name}


def _capture_pane(name: str, window: int = 0) -> Dict:
    """捕获 tmux pane 输出（不变）"""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    try:
        r = subprocess.run(
            ["tmux", "capture-pane", "-t", f"{si.tmux_session}:{window}", "-p"],
            capture_output=True, timeout=5
        )
        return {"success": True, "output": r.stdout.decode("utf-8", errors="replace")[-3000:]}
    except Exception as e:
        return {"error": str(e)}


def _list_sandboxes() -> Dict:
    """列出所有活跃沙箱"""
    with _sandboxes_lock:
        if not _sandboxes:
            return {"success": True, "sandboxes": [], "message": "无活跃沙箱"}
        result = []
        for name, si in _sandboxes.items():
            alive = si.proc is not None and si.proc.poll() is None
            tmux_ok = False
            try:
                r = subprocess.run(["tmux", "has-session", "-t", si.tmux_session],
                                   capture_output=True, timeout=2)
                tmux_ok = r.returncode == 0
            except:
                pass
            result.append({
                "name": name,
                "pid": si.proc.pid if si.proc else None,
                "alive": alive,
                "cmd": si.proc.args if si.proc else None,
                "tmux": tmux_ok,
                "reader": si.reader_running,
                "workspace": si.workspace_dir,
                "ready": si._ready.is_set(),
                "async_tasks": list(si._async_tasks.keys()),
            })
        return {"success": True, "sandboxes": result}


def _check_task(name: str, task_id: str) -> Dict:
    """查询异步任务状态"""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    result = si.get_async_result(task_id)
    if result is None:
        # 如果在 _async_tasks 中还没完成，说明还在进行中
        with si._async_lock:
            if task_id in si._async_tasks:
                result = {"status": "completed", **si._async_tasks[task_id]}
            else:
                result = {"status": "pending", "message": "任务正在进行中"}
    return {"success": True, "task_id": task_id, "result": result}


def _stop_sandbox(name: str, cleanup: bool = True) -> Dict:
    """停止沙箱（不变）"""
    with _sandboxes_lock:
        si = _sandboxes.pop(name, None)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    si.cleanup(remove_dir=cleanup)
    return {"success": True, "message": f"沙箱 '{name}' 已停止"}


# =============================================================================
# sandbox_handler — 工具入口
# =============================================================================
def sandbox_handler(sub_cmd: str, name: str = "", **kwargs) -> str:
    """
    Sandbox tool — 通用交互式应用沙箱

    Sub-commands:
      start - 启动交互式应用
        name: 沙箱名称
        cmd: 启动命令（默认 "garuda -i"）
        timeout: 等待就绪超时
        prompt: 应用的 prompt 标记
        async: 异步启动（默认 false）
        
      send - 与沙箱内部应用交互
        name: 沙箱名称
        input: 输入文本
        timeout: 等待响应超时
        prompt: 应用的 prompt 标记
        async: 异步模式（默认 false）
        
      exec - tmux workspace bash
      capture - 捕获 tmux pane
      list - 列出沙箱
      check - 查询异步任务
      stop - 停止
    """
    try:
        sub_cmd = sub_cmd.strip().lower()

        if sub_cmd == "start":
            cmd = kwargs.get("cmd", None)
            timeout = float(kwargs.get("timeout", 30.0))
            prompt = kwargs.get("prompt", None)
            async_mode = kwargs.get("async", False)
            result = _start_sandbox(name, cmd, timeout, prompt, async_mode)

        elif sub_cmd == "send":
            text = kwargs.get("input", "")
            if not text:
                return json.dumps({"error": "缺少 'input' 参数"})
            timeout = float(kwargs.get("timeout", 120.0))
            prompt = kwargs.get("prompt", None)
            async_mode = kwargs.get("async", False)
            result = _send_to_sandbox(name, text, timeout, prompt, async_mode)

        elif sub_cmd == "exec":
            cmd = kwargs.get("cmd", "")
            if not cmd:
                return json.dumps({"error": "缺少 'cmd' 参数"})
            timeout = float(kwargs.get("timeout", 30.0))
            result = _exec_in_workspace(name, cmd, timeout)

        elif sub_cmd == "capture":
            window = int(kwargs.get("window", 0))
            result = _capture_pane(name, window)

        elif sub_cmd == "list":
            result = _list_sandboxes()

        elif sub_cmd == "check":
            task_id = kwargs.get("task_id", "")
            if not task_id:
                return json.dumps({"error": "缺少 'task_id' 参数"})
            result = _check_task(name, task_id)

        elif sub_cmd == "stop":
            cleanup = kwargs.get("cleanup", True)
            result = _stop_sandbox(name, cleanup)

        else:
            result = {
                "error": f"未知命令 '{sub_cmd}'. "
                f"支持: start, send, exec, capture, list, check, stop"
            }

        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        import traceback
        return json.dumps({
            "error": f"sandbox handler: {type(e).__name__}: {e}",
            "sub_cmd": sub_cmd,
            "name": name,
            "traceback": traceback.format_exc(),
        }, ensure_ascii=False)


# =============================================================================
# Tool definition for AI framework
# =============================================================================

_prop_sub_cmd = property_param(
    name="sub_cmd",
    description="Sub-command: 'start' (create sandbox with app), 'send' (send to app via PTY), 'exec' (bash in workspace), 'capture' (capture pane), 'list' (list all), 'check' (check async task), 'stop' (destroy)",
    t="string",
    required=True
)

_prop_name = property_param(
    name="name",
    description="Sandbox name. Required for all sub-commands except 'list'. Use unique names.",
    t="string",
    required=False
)

_prop_input = property_param(
    name="input",
    description="Text to send to the sandboxed app when sub_cmd='send'",
    t="string",
    required=False
)

_prop_cmd = property_param(
    name="cmd",
    description="Startup command when sub_cmd='start' (default: 'garuda -i --no-sandbox'), or bash command when sub_cmd='exec'",
    t="string",
    required=False
)

_prop_async = property_param(
    name="async",
    description="Async mode: returns immediately with task_id, notifies via event system when response is ready",
    t="boolean",
    required=False
)

_prop_timeout = property_param(
    name="timeout",
    description="Max wait time in seconds (default: 120 for send, 30 for exec, 30 for start)",
    t="number",
    required=False
)

_prop_prompt = property_param(
    name="prompt",
    description="Application prompt marker for response detection (e.g. 'ECHO>', 'Garuda >', '$')",
    t="string",
    required=False
)

_prop_task_id = property_param(
    name="task_id",
    description="Task ID to check status when sub_cmd='check'",
    t="string",
    required=False
)

_prop_window = property_param(
    name="window",
    description="Tmux window index to capture when sub_cmd='capture' (default: 0)",
    t="integer",
    required=False
)

_prop_cleanup = property_param(
    name="cleanup",
    description="Remove workspace directory when sub_cmd='stop' (default: true)",
    t="boolean",
    required=False
)

_sandbox_function = function_ai(
    name="sandbox",
    description="""Sandbox tool for running and interacting with isolated applications.

    Architecture:
      - start <cmd>  → Launches ANY interactive app in a PTY (not just Garuda)
      - send <input>  → Writes to the app's PTY, waits for prompt response
      - exec <cmd>    → Runs bash in tmux workspace (independent channel)
      
    Dual-mode: send (PTY interaction with app) + exec (bash via tmux).
    Async mode: send(async=True) returns immediately with task_id, notifies on completion.
    Check mode: check(task_id) queries async task status.
    
    Sub-commands:
    - 'start': Create sandbox with given cmd (default: garuda). Set prompt for custom apps.
    - 'send': Send message to sandboxed app via PTY, wait for response.
    - 'exec': Run bash command in workspace tmux window.
    - 'capture': Capture output from a tmux pane.
    - 'list': List all active sandboxes.
    - 'check': Check status of an async task (from send/start async mode).
    - 'stop': Stop and optionally clean up a sandbox.""",
    parameters=parameters_func([
        _prop_sub_cmd,
        _prop_name,
        _prop_input,
        _prop_cmd,
        _prop_async,
        _prop_timeout,
        _prop_prompt,
        _prop_task_id,
        _prop_window,
        _prop_cleanup
    ])
)

__tools__ = [_sandbox_function]
__tool_call_map__ = {"sandbox": sandbox_handler}
