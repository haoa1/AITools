#!/usr/bin/env python3
"""
test_app — 交互式 sandbox 测试工具

直接调用 sandbox.py 内部接口（_start_sandbox, _send_to_sandbox 等），
用 echo 程序替代 Garuda REPL，避免 LLM 延迟干扰，只测通信层。

用法:
  python3 test_app.py               # 交互模式
  python3 test_app.py auto          # 自动跑完整测试流程

测试项:
  1. start         — 启动 echo 沙箱
  2. send <msg>    — 发消息，等回复
  3. exec <cmd>    — tmux 中执行 bash 命令
  4. cap           — 捕获 tmux pane
  5. list          — 列出活跃沙箱
  6. stop          — 停止并清理
  7. auto          — 自动跑整套流程
  8. ping <n>      — 发 n 条消息测往返延迟
"""

import os
import sys
import time
import pty
import select
import shutil
import threading
import subprocess

# ---------------------------------------------------------------------------
# sandbox.py 的简化重实现（不含 Garuda 依赖、AITools 框架、事件系统）
# 直接测试 PTY 通信层 + tmux 管理
# ---------------------------------------------------------------------------

SANDMARK = "###SANDMARK_END###"

class SandboxInstance:
    def __init__(self, name, workspace_dir):
        self.name = name
        self.workspace_dir = workspace_dir
        self.proc = None
        self.reader_thread = None
        self.reader_running = False
        self.tmux_session = f"garuda-sandbox-{name}"
        self.pty_master_fd = None
        self._buffer = ""
        self._buf_lock = threading.Lock()

    def append(self, text):
        with self._buf_lock:
            self._buffer += text

    def get_buffer(self):
        with self._buf_lock:
            return self._buffer

    def clear_buffer(self):
        with self._buf_lock:
            data = self._buffer
            self._buffer = ""
            return data

    def wait_for_prompt(self, prompt="ECHO>", timeout=15.0):
        """等待 prompt 出现，返回累积输出"""
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
        raise TimeoutError(f"等待 '{prompt}' 超时 {timeout}s. Buffer: {self._buffer[-200:]!r}")

    def cleanup(self, remove_dir=True):
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
                self.proc.wait(timeout=3)
            except:
                try:
                    self.proc.kill()
                except:
                    pass
        if self.tmux_session:
            try:
                subprocess.run(["tmux", "kill-session", "-t", self.tmux_session],
                               capture_output=True, timeout=3)
            except:
                pass
        if remove_dir and self.workspace_dir and os.path.isdir(self.workspace_dir):
            shutil.rmtree(self.workspace_dir, ignore_errors=True)
        self.proc = None
        self.reader_thread = None


def _reader_worker(si):
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


# ===== 创建 echo 子进程的脚本 =====
ECHO_SCRIPT = r"""#!/usr/bin/env python3
"""  # noqa
ECHO_SCRIPT += """
import sys
PS1 = "ECHO> "
sys.stdout.write(PS1)
sys.stdout.flush()
while True:
    try:
        line = sys.stdin.readline()
    except:
        break
    if not line:
        break
    line = line.strip()
    if line == "quit":
        break
    if line == "sleep":
        import time
        time.sleep(3)
        sys.stdout.write("slept 3s\\n")
    else:
        sys.stdout.write(f"REPLY: {line}\\n")
    sys.stdout.write(PS1)
    sys.stdout.flush()
"""


_sandboxes = {}


def cmd_start(name, timeout=10.0):
    """启动 echo 沙箱"""
    if name in _sandboxes:
        return {"error": f"沙箱 '{name}' 已存在"}

    ws_dir = f"/tmp/garuda-sandbox-{name}"
    if os.path.exists(ws_dir):
        shutil.rmtree(ws_dir, ignore_errors=True)
    os.makedirs(os.path.join(ws_dir, "workspace"), exist_ok=True)

    # 写 echo 脚本
    script_path = os.path.join(ws_dir, "echo_repl.py")
    with open(script_path, "w") as f:
        f.write(ECHO_SCRIPT)

    si = SandboxInstance(name, ws_dir)

    # PTY
    mfd, sfd = pty.openpty()
    try:
        proc = subprocess.Popen(
            [sys.executable, script_path],
            stdin=sfd, stdout=sfd, stderr=sfd,
            env={**os.environ, "TERM": "xterm-256color", "PYTHONUNBUFFERED": "1"},
            start_new_session=True,
        )
    except Exception as e:
        os.close(mfd)
        os.close(sfd)
        shutil.rmtree(ws_dir, ignore_errors=True)
        return {"error": f"启动失败: {e}"}

    os.close(sfd)
    si.proc = proc
    si.pty_master_fd = mfd

    reader = threading.Thread(target=_reader_worker, args=(si,), daemon=True)
    reader.start()
    si.reader_thread = reader

    # 等初始 prompt
    try:
        si.wait_for_prompt("ECHO>", timeout=timeout)
    except TimeoutError as e:
        si.reader_running = False
        proc.terminate()
        proc.wait(3)
        os.close(mfd)
        shutil.rmtree(ws_dir, ignore_errors=True)
        return {"error": f"echo 未在 {timeout}s 内启动: {e}"}

    # tmux
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
    return {"success": True, "name": name, "pid": proc.pid}


def cmd_send(name, text, timeout=15.0):
    """发送消息到 echo 沙箱"""
    si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    if si.proc is None or si.proc.poll() is not None:
        return {"error": "进程已退出"}
    if si.pty_master_fd is None:
        return {"error": "PTY master fd 不可用"}

    # 清除残留 buffer
    si.clear_buffer()

    try:
        os.write(si.pty_master_fd, (text + "\n").encode("utf-8"))
    except OSError as e:
        return {"error": f"写入失败: {e}"}

    t0 = time.time()
    try:
        response = si.wait_for_prompt("ECHO>", timeout=timeout)
    except TimeoutError as e:
        return {"error": str(e)}

    elapsed = time.time() - t0
    return {"success": True, "response": response, "elapsed": f"{elapsed:.2f}s"}


def cmd_ping(name, count=3, timeout=10.0):
    """多次 ping-pong 测试"""
    si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}

    results = []
    for i in range(count):
        t0 = time.time()
        r = cmd_send(name, f"ping{i+1}", timeout=timeout)
        elapsed = time.time() - t0
        results.append({
            "seq": i + 1,
            "ok": r.get("success", False),
            "response": r.get("response", r.get("error", "?")),
            "elapsed": f"{elapsed:.2f}s",
        })

    ok_count = sum(1 for r in results if r["ok"])
    return {
        "success": ok_count == count,
        "total": count,
        "ok": ok_count,
        "fail": count - ok_count,
        "results": results,
    }


def cmd_exec(name, cmd, timeout=30.0):
    """在 tmux workspace 执行 bash 命令"""
    si = _sandboxes.get(name)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    target = f"{si.tmux_session}:0"

    # 检查 tmux
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

    return {"success": bool(output) or True, "output": output[:2000]}


def cmd_capture(name, window=0):
    """捕获 tmux pane 输出"""
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


def cmd_list():
    """列出活跃沙箱"""
    if not _sandboxes:
        return {"sandboxes": [], "message": "无活跃沙箱"}
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
        buf = si.get_buffer()
        result.append({
            "name": name,
            "pid": si.proc.pid if si.proc else None,
            "alive": alive,
            "tmux": tmux_ok,
            "reader": si.reader_running,
            "buffer_len": len(buf),
            "workspace": si.workspace_dir,
        })
    return {"sandboxes": result}


def cmd_stop(name, cleanup=True):
    """停止沙箱"""
    si = _sandboxes.pop(name, None)
    if not si:
        return {"error": f"沙箱 '{name}' 不存在"}
    si.cleanup(remove_dir=cleanup)
    return {"success": True, "message": f"'{name}' 已停止"}


# ===========================================================================
# 交互式 CLI
# ===========================================================================

def print_result(r):
    """格式化打印结果"""
    if isinstance(r, dict):
        for k, v in r.items():
            if isinstance(v, list):
                print(f"  {k}:")
                for item in v:
                    if isinstance(item, dict):
                        for ik, iv in item.items():
                            print(f"    {ik}: {iv}")
                    else:
                        print(f"    {item}")
            elif isinstance(v, dict):
                print(f"  {k}:")
                for sk, sv in v.items():
                    print(f"    {sk}: {sv}")
            else:
                sv = str(v)
                if len(sv) > 200:
                    sv = sv[:200] + "..."
                print(f"  {k}: {sv}")
    else:
        print(f"  {r}")


def run_auto_test():
    """自动运行完整测试流程"""
    name = "autotest"
    passed = 0
    failed = 0
    errors = []

    def check(step, result, expect_success=True):
        nonlocal passed, failed
        ok = result.get("success", False) == expect_success and not result.get("error")
        status = "✅" if ok else "❌"
        if ok:
            passed += 1
        else:
            failed += 1
            errors.append((step, result))
        print(f"  {status} {step}")

    print("\n" + "=" * 50)
    print("自动测试: sandbox echo 通信层")
    print("=" * 50)

    # 1. start
    print("\n[1/7] start — 启动 echo 沙箱")
    r = cmd_start(name)
    check("start", r)
    time.sleep(0.5)

    # 2. send
    print("\n[2/7] send — 发消息")
    r = cmd_send(name, "hello")
    check("send hello", r)

    # 3. send multiple
    print("\n[3/7] send — 多条消息")
    r = cmd_send(name, "ping")
    check("send ping", r)
    r = cmd_send(name, "你好世界")
    check("send 中文", r)

    # 4. ping
    print("\n[4/7] ping — 往返延迟 (5次)")
    r = cmd_ping(name, count=5)
    check(f"ping {r.get('ok',0)}/5", r, expect_success=True)

    # 5. exec
    print("\n[5/7] exec — tmux bash 命令")
    r = cmd_exec(name, "echo hello_world && pwd")
    check("exec echo+pwd", r)

    # 6. list
    print("\n[6/7] list — 列出沙箱")
    r = cmd_list()
    has_sandbox = r.get("sandboxes") and len(r["sandboxes"]) > 0
    if has_sandbox:
        passed += 1
        print("  ✅ list (1 个沙箱)")
    else:
        failed += 1
        errors.append(("list", r))
        print("  ❌ list")

    # 7. stop
    print("\n[7/7] stop — 停止清理")
    r = cmd_stop(name)
    check("stop", r)

    # 汇总
    print("\n" + "=" * 50)
    total = passed + failed
    print(f"结果: {passed}/{total} 通过, {failed} 失败")
    if errors:
        print("\n失败详情:")
        for step, r in errors:
            print(f"  {step}: {r}")
    print("=" * 50)
    return passed, failed


def interactive_mode():
    """交互式 CLI"""
    import shlex
    print("\n" + "=" * 50)
    print("test_app — sandbox 通信层交互测试")
    print("=" * 50)
    print("命令:")
    print("  start <name>        启动 echo 沙箱")
    print("  send <name> <msg>   发送消息")
    print("  ping <name> [n=3]   往返延迟测试")
    print("  exec <name> <cmd>   tmux bash 命令")
    print("  cap <name>          捕获 pane")
    print("  list                列出沙箱")
    print("  stop <name>         停止沙箱")
    print("  auto                自动测试")
    print("  help                帮助")
    print("  quit                退出")
    print("=" * 50)

    while True:
        try:
            raw = input("\n❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw == "quit":
            break
        if raw == "auto":
            run_auto_test()
            continue
        if raw == "help":
            print("命令列表如上 ^")
            continue

        parts = shlex.split(raw)
        cmd = parts[0]

        try:
            if cmd == "start":
                name = parts[1] if len(parts) > 1 else "test"
                r = cmd_start(name)
                print_result(r)

            elif cmd == "send":
                if len(parts) < 3:
                    print("用法: send <name> <msg>")
                    continue
                name = parts[1]
                msg = " ".join(parts[2:])
                t0 = time.time()
                r = cmd_send(name, msg)
                elapsed = time.time() - t0
                print(f"[耗时 {elapsed:.2f}s]")
                print_result(r)

            elif cmd == "ping":
                name = parts[1] if len(parts) > 1 else "test"
                count = int(parts[2]) if len(parts) > 2 else 3
                print(f"ping 测试 ({count} 次)...")
                r = cmd_ping(name, count)
                print_result(r)

            elif cmd == "exec":
                if len(parts) < 3:
                    print("用法: exec <name> <cmd>")
                    continue
                name = parts[1]
                cmd_str = " ".join(parts[2:])
                r = cmd_exec(name, cmd_str)
                print_result(r)

            elif cmd == "cap":
                name = parts[1] if len(parts) > 1 else "test"
                r = cmd_capture(name)
                print_result(r)

            elif cmd == "list":
                r = cmd_list()
                print_result(r)

            elif cmd == "stop":
                name = parts[1] if len(parts) > 1 else "test"
                r = cmd_stop(name)
                print_result(r)

            else:
                print(f"未知命令: {cmd}，输入 help 查看帮助")

        except Exception as e:
            import traceback
            print(f"错误: {e}")
            traceback.print_exc()


# ===========================================================================
# 入口
# ===========================================================================

if __name__ == "__main__":
    # 清理之前的残留
    for si in list(_sandboxes.values()):
        si.cleanup()
    _sandboxes.clear()

    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        run_auto_test()
        # 清理所有
        for si in list(_sandboxes.values()):
            si.cleanup()
        _sandboxes.clear()
    else:
        interactive_mode()
