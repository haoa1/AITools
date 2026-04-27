"""
Sandbox tool - single tool with sub_cmd routing.

Sub-commands:
  start  - Create isolated Garuda sandbox environment
  send   - Send message to Garuda REPL, wait for response
  exec   - Run bash command in workspace window
  capture - Capture pane output
  list   - List active sandboxes
  stop   - Stop and clean up a sandbox

Architecture:
  - garuda REPL: subprocess.Popen with PIPE stdin/stdout (pipe method)
  - Bash workspace: tmux session with single window
  - Async notifications: Garuda event system (optional)
  - Isolated workspace: /tmp/garuda-sandbox-{name}/
"""

import os
import sys
import time
import json
import uuid
import select
import signal
import shutil
import threading
import subprocess
from typing import Optional, Dict, Any

# =============================================================================
# Garuda event system integration (optional - for async notifications)
# =============================================================================
try:
    from garuda.async_core.event_system import publish_event, EVENT_TASK_COMPLETED, EVENT_TASK_FAILED
    HAS_GARUDA_EVENTS = True
except ImportError:
    HAS_GARUDA_EVENTS = False

# =============================================================================
# Global state: active sandboxes registry (thread-safe)
# =============================================================================
_sandboxes: Dict[str, "SandboxInstance"] = {}
_sandboxes_lock = threading.Lock()

SANDMARK = "###SANDMARK_END###"

# =============================================================================
# SandboxInstance class - manages one sandbox lifecycle
# =============================================================================

class SandboxInstance:
    """Represents a single sandbox with garuda process, workspace, and tmux session."""

    def __init__(self, name: str, workspace_dir: str):
        self.name = name
        self.workspace_dir = workspace_dir
        self.garuda_process: Optional[subprocess.Popen] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.reader_running = False
        self.tmux_session = f"garuda-sandbox-{name}"

        # Output buffer thread safety
        self._buffer = ""
        self._buffer_lock = threading.Lock()
        self._response_event: Optional[threading.Event] = None
        self._last_response = ""
        self._started = False

        # Async response tracking
        self._async_tasks: Dict[str, Dict] = {}
        self._async_lock = threading.Lock()

    # --- Buffer management ---

    def append_to_buffer(self, text: str):
        with self._buffer_lock:
            self._buffer += text

    def get_and_clear_buffer(self) -> str:
        with self._buffer_lock:
            data = self._buffer
            self._buffer = ""
            return data

    def peek_buffer(self) -> str:
        with self._buffer_lock:
            return self._buffer

    def wait_for_prompt_in_buffer(self, prompt: str = "Garuda >", timeout: float = 120.0) -> str:
        """Block until the prompt appears in buffer, then return accumulated output."""
        deadline = time.time() + timeout
        last_len = 0
        while time.time() < deadline:
            with self._buffer_lock:
                current_len = len(self._buffer)
            if current_len > last_len:
                last_len = current_len
                # Check if prompt appears in buffer
                with self._buffer_lock:
                    buf = self._buffer
                if prompt in buf:
                    # Split on prompt, keep content between prompts
                    parts = buf.split(prompt)
                    # If we have at least 2 parts, the response is the second-to-last segment
                    if len(parts) >= 2:
                        response = parts[-2].strip()
                    else:
                        response = buf.strip()
                    # Clear the consumed portion up to and including the prompt
                    with self._buffer_lock:
                        self._buffer = ""
                    return response
            time.sleep(0.1)
        raise TimeoutError(f"Timed out after {timeout}s waiting for Garuda prompt. Buffer so far: {self._buffer[-200:]!r}")

    def has_event(self) -> bool:
        return self._response_event is not None

    def signal_response(self):
        if self._response_event:
            self._response_event.set()

    # --- Cleanup ---

    def cleanup(self, remove_dir: bool = True):
        """Clean up all resources."""
        self.reader_running = False

        # Kill garuda process
        if self.garuda_process and self.garuda_process.poll() is None:
            try:
                self.garuda_process.terminate()
                self.garuda_process.wait(timeout=5)
            except Exception:
                try:
                    self.garuda_process.kill()
                except Exception:
                    pass

        # Kill tmux session
        if self.tmux_session:
            try:
                subprocess.run(
                    ["tmux", "kill-session", "-t", self.tmux_session],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass

        # Remove directory
        if remove_dir and self.workspace_dir and os.path.isdir(self.workspace_dir):
            try:
                shutil.rmtree(self.workspace_dir, ignore_errors=True)
            except Exception:
                pass

        self.garuda_process = None
        self.reader_thread = None


# =============================================================================
# Reader thread - continuously reads garuda stdout
# =============================================================================

def _reader_worker(si: SandboxInstance):
    """Background thread: continuously reads from garuda process stdout into buffer."""
    si.reader_running = True
    proc = si.garuda_process
    if not proc or not proc.stdout:
        si.reader_running = False
        return

    try:
        while si.reader_running and proc.poll() is None:
            ready, _, _ = select.select([proc.stdout], [], [], 0.5)
            if ready:
                chunk = os.read(proc.stdout.fileno(), 4096)
                if not chunk:
                    break
                text = chunk.decode("utf-8", errors="replace")
                si.append_to_buffer(text)
        # Read remaining after process ends
        while True:
            ready, _, _ = select.select([proc.stdout], [], [], 0.5)
            if ready:
                chunk = os.read(proc.stdout.fileno(), 4096)
                if not chunk:
                    break
                text = chunk.decode("utf-8", errors="replace")
                si.append_to_buffer(text)
            else:
                break
    except Exception:
        pass
    finally:
        si.reader_running = False


# =============================================================================
# Core operations
# =============================================================================

def _start_sandbox(name: str, garuda_path: str = "garuda", timeout: float = 15.0) -> Dict:
    """Start a sandbox: create workspace, start garuda pipe process, create tmux."""
    with _sandboxes_lock:
        if name in _sandboxes:
            return {"error": f"Sandbox '{name}' already exists"}

        workspace_dir = f"/tmp/garuda-sandbox-{name}"
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir, ignore_errors=True)

        # Create directory structure
        ws_workspace = os.path.join(workspace_dir, "workspace")
        os.makedirs(ws_workspace, exist_ok=True)
        logs_dir = os.path.join(workspace_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Create minimal config for sandbox
        config_path = os.path.join(workspace_dir, "config.toml")
        config_content = f"""# Sandbox config for '{name}'
[system]
name = "garuda-sandbox-{name}"

[ai]
provider = "openrouter"
model = "deepseek/deepseek-v4-flash"

[workspace]
path = "{ws_workspace}"
"""
        with open(config_path, "w") as f:
            f.write(config_content)

        si = SandboxInstance(name, workspace_dir)

        # Start garuda as subprocess with PIPE
        # Set GARUDA_SANDBOX_CHILD to prevent recursive sandbox tool loading
        sandbox_env = {
            **os.environ,
            "GARUDA_CONFIG": config_path,
            "GARUDA_SANDBOX_CHILD": "1"
        }
        try:
            proc = subprocess.Popen(
                [garuda_path, "-i"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=ws_workspace,
                bufsize=0,
                env=sandbox_env
            )
        except FileNotFoundError:
            shutil.rmtree(workspace_dir, ignore_errors=True)
            return {"error": f"garuda not found at '{garuda_path}'. Make sure it's installed and in PATH."}
        except Exception as e:
            shutil.rmtree(workspace_dir, ignore_errors=True)
            return {"error": f"Failed to start garuda: {e}"}

        si.garuda_process = proc

        # Start reader thread
        reader = threading.Thread(target=_reader_worker, args=(si,), daemon=True)
        reader.start()
        si.reader_thread = reader

        # Wait for initial "Garuda >" prompt
        try:
            si.wait_for_prompt_in_buffer(timeout=timeout)
        except TimeoutError as e:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
            reader_thread_running = si.reader_running
            si.reader_running = False
            shutil.rmtree(workspace_dir, ignore_errors=True)
            return {"error": f"Garuda did not start within {timeout}s: {e}"}

        # Create tmux session with bash window
        tmux_session = si.tmux_session
        try:
            # Create detached session
            subprocess.run(
                ["tmux", "new-session", "-d", "-s", tmux_session, "-n", "workspace"],
                capture_output=True, timeout=5, check=True
            )
            # Name the session
            subprocess.run(
                ["tmux", "send-keys", "-t", f"{tmux_session}:0", f"cd {ws_workspace} && clear", "Enter"],
                capture_output=True, timeout=5
            )
            # Also start a bash login shell
            subprocess.run(
                ["tmux", "send-keys", "-t", f"{tmux_session}:0", "PS1='\\w \\$ '", "Enter"],
                capture_output=True, timeout=5
            )
        except subprocess.CalledProcessError as e:
            # tmux not available - workspace mode only via pipe exec
            pass
        except FileNotFoundError:
            pass

        _sandboxes[name] = si
        si._started = True

        return {
            "success": True,
            "name": name,
            "workspace": workspace_dir,
            "tmux_session": tmux_session,
            "garuda_pid": proc.pid,
            "config": config_path
        }


def _send_to_sandbox(name: str, text: str, async_mode: bool = False, timeout: float = 120.0) -> Dict:
    """Send text to garuda REPL via pipe. Supports sync and async."""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"Sandbox '{name}' not found. Use 'sandbox start {name}' first."}
    if si.garuda_process is None or si.garuda_process.poll() is not None:
        return {"error": f"Garuda process in sandbox '{name}' is not running. Start it first."}

    proc = si.garuda_process

    if async_mode:
        # Async: write, fire-and-forget with event notification
        task_id = str(uuid.uuid4())[:8]
        try:
            proc.stdin.write((text + "\n").encode("utf-8"))
            proc.stdin.flush()
        except BrokenPipeError:
            return {"error": "Garuda process pipe is broken. The process may have exited."}

        # Start background watcher
        def _async_watcher():
            """Wait for response completion, then publish event."""
            try:
                response = si.wait_for_prompt_in_buffer(timeout=timeout)
                if HAS_GARUDA_EVENTS:
                    publish_event(EVENT_TASK_COMPLETED, {
                        "task_id": task_id,
                        "description": f"sandbox send: {text[:50]}",
                        "tool_name": "sandbox",
                        "completed_at": time.strftime("%H:%M:%S"),
                        "result_summary": response[:200] if response else "[empty response]",
                        "result": response
                    })
                else:
                    # Fallback: store response for polling
                    with si._async_lock:
                        si._async_tasks[task_id] = {
                            "status": "completed",
                            "response": response,
                            "completed_at": time.time()
                        }
            except TimeoutError as e:
                if HAS_GARUDA_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox send: {text[:50]}",
                        "tool_name": "sandbox",
                        "failed_at": time.strftime("%H:%M:%S"),
                        "error_message": str(e)
                    })
                else:
                    with si._async_lock:
                        si._async_tasks[task_id] = {
                            "status": "failed",
                            "error": str(e),
                            "completed_at": time.time()
                        }
            except Exception as e:
                if HAS_GARUDA_EVENTS:
                    publish_event(EVENT_TASK_FAILED, {
                        "task_id": task_id,
                        "description": f"sandbox send: {text[:50]}",
                        "tool_name": "sandbox",
                        "failed_at": time.strftime("%H:%M:%S"),
                        "error_message": f"Unexpected error: {e}"
                    })
                else:
                    with si._async_lock:
                        si._async_tasks[task_id] = {
                            "status": "failed",
                            "error": f"Unexpected error: {e}",
                            "completed_at": time.time()
                        }

        watcher = threading.Thread(target=_async_watcher, daemon=True)
        watcher.start()

        return {
            "success": True,
            "async": True,
            "task_id": task_id,
            "message": f"Message sent to Garuda sandbox '{name}' in async mode. Task {task_id} will notify when complete."
        }

    else:
        # Sync: write and wait for response
        try:
            proc.stdin.write((text + "\n").encode("utf-8"))
            proc.stdin.flush()
        except BrokenPipeError:
            return {"error": "Garuda process pipe is broken. The process may have exited."}

        try:
            response = si.wait_for_prompt_in_buffer(timeout=timeout)
        except TimeoutError as e:
            return {"error": f"Timeout waiting for response: {e}"}

        return {
            "success": True,
            "response": response,
            "name": name
        }


def _exec_in_workspace(name: str, cmd: str, timeout: float = 30.0) -> Dict:
    """Execute a bash command in the tmux workspace window."""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"Sandbox '{name}' not found. Use 'sandbox start {name}' first."}

    tmux_session = si.tmux_session
    target = f"{tmux_session}:0"

    # Check if tmux session exists
    result = subprocess.run(
        ["tmux", "has-session", "-t", tmux_session],
        capture_output=True, timeout=5
    )
    if result.returncode != 0:
        return {"error": f"Tmux session '{tmux_session}' not found. The sandbox may need to be restarted."}

    try:
        # Capture baseline
        baseline = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p"],
            capture_output=True, timeout=5
        ).stdout.decode("utf-8", errors="replace")

        # Send command with marker
        subprocess.run(
            ["tmux", "send-keys", "-t", target, f"echo '{SANDMARK}' && {cmd} && echo '{SANDMARK}'", "Enter"],
            capture_output=True, timeout=5
        )

        # Wait for marker to appear in output
        deadline = time.time() + timeout
        output = ""
        new_content = ""
        captured = ""
        while time.time() < deadline:
            captured = subprocess.run(
                ["tmux", "capture-pane", "-t", target, "-p"],
                capture_output=True, timeout=5
            ).stdout.decode("utf-8", errors="replace")

            # Extract new content
            new_content = captured[len(baseline):] if len(captured) > len(baseline) else captured

            # Check for marker
            if SANDMARK in new_content:
                lines = new_content.split("\n")
                in_output = False
                cmd_output_lines = []
                for line in lines:
                    if SANDMARK in line and not in_output:
                        in_output = True
                        continue
                    elif SANDMARK in line and in_output:
                        break
                    if in_output:
                        cmd_output_lines.append(line)
                output = "\n".join(cmd_output_lines).strip()
                break

            time.sleep(0.3)

        if not output:
            # Fallback: return last N lines of new content
            output = (new_content or captured)[-2000:]

    except Exception as e:
        return {"error": f"Failed to execute command in tmux: {e}"}

    return {
        "success": True,
        "output": output,
        "name": name
    }


def _capture_pane(name: str, window: int = 0) -> Dict:
    """Capture tmux pane output."""
    with _sandboxes_lock:
        si = _sandboxes.get(name)
    if not si:
        return {"error": f"Sandbox '{name}' not found."}

    tmux_session = si.tmux_session
    target = f"{tmux_session}:{window}"

    try:
        captured = subprocess.run(
            ["tmux", "capture-pane", "-t", target, "-p"],
            capture_output=True, timeout=5
        )
        if captured.returncode != 0:
            return {"error": f"Failed to capture pane: {captured.stderr.decode()}"}
        output = captured.stdout.decode("utf-8", errors="replace")
    except FileNotFoundError:
        return {"error": "tmux not found on this system"}
    except Exception as e:
        return {"error": f"Failed to capture pane: {e}"}

    return {
        "success": True,
        "output": output[-5000:],  # Limit output size
        "name": name,
        "window": window
    }


def _list_sandboxes() -> Dict:
    """List all active sandboxes."""
    with _sandboxes_lock:
        if not _sandboxes:
            return {"sandboxes": [], "message": "No active sandboxes."}

        result = []
        for name, si in _sandboxes.items():
            garuda_alive = si.garuda_process is not None and si.garuda_process.poll() is None
            tmux_alive = False
            try:
                r = subprocess.run(
                    ["tmux", "has-session", "-t", si.tmux_session],
                    capture_output=True, timeout=3
                )
                tmux_alive = (r.returncode == 0)
            except Exception:
                pass

            result.append({
                "name": name,
                "workspace": si.workspace_dir,
                "garuda_pid": si.garuda_process.pid if si.garuda_process else None,
                "garuda_running": garuda_alive,
                "tmux_session": si.tmux_session,
                "tmux_alive": tmux_alive,
                "reader_running": si.reader_running
            })

        return {"sandboxes": result}


def _stop_sandbox(name: str, cleanup: bool = True) -> Dict:
    """Stop a sandbox and clean up resources."""
    with _sandboxes_lock:
        si = _sandboxes.pop(name, None)
    if not si:
        return {"error": f"Sandbox '{name}' not found."}

    si.cleanup(remove_dir=cleanup)

    return {
        "success": True,
        "name": name,
        "message": f"Sandbox '{name}' stopped and {'cleaned up' if cleanup else 'left for inspection'}.",
        "workspace": si.workspace_dir if not cleanup else None
    }


# =============================================================================
# Tool definition
# =============================================================================

def sandbox_handler(sub_cmd: str, name: str = "", **kwargs) -> str:
    """
    Sandbox tool - manage isolated Garuda testing environments.
    
    Args:
        sub_cmd: Sub-command to execute.
            'start'  - Create sandbox with garuda REPL (pipe) + tmux workspace
            'send'   - Send message to garuda through pipe, wait for response
            'exec'   - Run bash command in workspace tmux window
            'capture' - Capture tmux pane output
            'list'   - List all active sandboxes
            'stop'   - Stop sandbox and clean up
        name: Sandbox name (required for start/send/exec/capture/stop)
        **kwargs: Additional arguments depending on sub_cmd:
            For 'start':
                garuda_path (str): Path to garuda binary (default: "garuda")
                timeout (float): Timeout for waiting initial prompt (default: 15.0)
            For 'send':
                input (str): Message text to send to garuda
                async (bool): If True, return immediately and notify on completion
                timeout (float): Max wait time for response (default: 120.0)
            For 'exec':
                cmd (str): Bash command to execute in workspace
                timeout (float): Max wait time (default: 30.0)
            For 'capture':
                window (int): Window index to capture (default: 0)
            For 'stop':
                cleanup (bool): Remove workspace directory (default: True)
    
    Returns:
        JSON string with result data.
    """
    try:
        sub_cmd = sub_cmd.strip().lower()
        
        if sub_cmd == "start":
            garuda_path = kwargs.get("garuda_path", "garuda")
            timeout = float(kwargs.get("timeout", 15.0))
            result = _start_sandbox(name, garuda_path, timeout)

        elif sub_cmd == "send":
            text = kwargs.get("input", "")
            if not text:
                return json.dumps({"error": "Missing 'input' for send sub-command"})
            async_mode = kwargs.get("async", False)
            timeout = float(kwargs.get("timeout", 120.0))
            result = _send_to_sandbox(name, text, async_mode, timeout)

        elif sub_cmd == "exec":
            cmd = kwargs.get("cmd", "")
            if not cmd:
                return json.dumps({"error": "Missing 'cmd' for exec sub-command"})
            timeout = float(kwargs.get("timeout", 30.0))
            result = _exec_in_workspace(name, cmd, timeout)

        elif sub_cmd == "capture":
            window = int(kwargs.get("window", 0))
            result = _capture_pane(name, window)

        elif sub_cmd == "list":
            result = _list_sandboxes()

        elif sub_cmd == "stop":
            cleanup = kwargs.get("cleanup", True)
            result = _stop_sandbox(name, cleanup)

        else:
            result = {
                "error": f"Unknown sub_cmd: '{sub_cmd}'. Valid: start, send, exec, capture, list, stop"
            }

        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({
            "error": f"sandbox handler error: {type(e).__name__}: {e}",
            "sub_cmd": sub_cmd,
            "name": name
        }, ensure_ascii=False)


# =============================================================================
# Tool registration exports (for AITools framework)
# =============================================================================

# Property definitions for the sandbox tool parameters
from base import function_ai, parameters_func, property_param

_prop_sub_cmd = property_param(
    name="sub_cmd",
    description="Sub-command: 'start' (create sandbox), 'send' (send to garuda), 'exec' (bash in workspace), 'capture' (capture pane), 'list' (list all), 'stop' (destroy)",
    t="string",
    required=True
)

_prop_name = property_param(
    name="name",
    description="Sandbox name (required for start/send/exec/capture/stop). Use unique names to manage multiple sandboxes.",
    t="string",
    required=False
)

_prop_input = property_param(
    name="input",
    description="Text message to send to Garuda REPL when sub_cmd='send'",
    t="string",
    required=False
)

_prop_cmd = property_param(
    name="cmd",
    description="Bash command to execute in workspace window when sub_cmd='exec'",
    t="string",
    required=False
)

_prop_async = property_param(
    name="async",
    description="If true, send returns immediately with task_id; notifies via system when response is ready",
    t="boolean",
    required=False
)

_prop_timeout = property_param(
    name="timeout",
    description="Max wait time in seconds for response (default: 120 for send, 30 for exec, 15 for start)",
    t="number",
    required=False
)

_prop_window = property_param(
    name="window",
    description="Tmux window index to capture when sub_cmd='capture' (default: 0)",
    t="integer",
    required=False
)

_prop_garuda_path = property_param(
    name="garuda_path",
    description="Path to garuda binary when sub_cmd='start' (default: 'garuda')",
    t="string",
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
    description="""Sandbox tool for testing Garuda in isolated environments. 
    
    Sub-commands:
    - 'start': Create sandbox with garuda REPL (pipe-based) + tmux workspace.
    - 'send': Send message to garuda REPL, wait for AI response.
    - 'exec': Run bash command in workspace tmux window (no AI involved).
    - 'capture': Capture output from a tmux pane.
    - 'list': List all active sandboxes.
    - 'stop': Stop and optionally clean up a sandbox.
    
    Pipe-based architecture provides precise response detection. 
    Dual-mode: send (AI interaction via pipe) + exec (direct bash via tmux).
    Async mode for long-running responses with system notification.""",
    parameters=parameters_func([
        _prop_sub_cmd,
        _prop_name,
        _prop_input,
        _prop_cmd,
        _prop_async,
        _prop_timeout,
        _prop_window,
        _prop_garuda_path,
        _prop_cleanup
    ])
)

__tools__ = [_sandbox_function]
__tool_call_map__ = {"sandbox": sandbox_handler}
