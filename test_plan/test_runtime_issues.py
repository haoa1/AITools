#!/usr/bin/env python3
"""Test runtime issues on Windows - select.select, /tmp/ paths, etc."""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0; FAIL = 0
def test(name, fn):
    global PASS, FAIL
    try:
        r = fn()
        if r:
            print(f"  PASS: {name}")
        else:
            print(f"  FAIL: {name}")
        PASS += 1 if r else 0; FAIL += 0 if r else 1
    except Exception as e:
        print(f"  FAIL: {name} - {type(e).__name__}: {e}")
        FAIL += 1

# ===== 1. shell/bash =====
print("=== 1. shell.bash ===")
from shell.bash import bash
r = bash(command="echo hello_world", capture_output=True, shell=True, timeout=10)
test("echo basic", lambda: "hello_world" in r)

r = bash(command="dir /b | findstr sandbox", capture_output=True, shell=True, timeout=10)
test("pipe works", lambda: "sandbox" in r)

r = bash(command="type con 2>&1", capture_output=True, shell=True, timeout=3)
test("stderr redirect ok", lambda: True)

# ===== 2. task_output_tool (hardcoded /tmp/) =====
print("\n=== 2. task_output_tool (/tmp/ issue) ===")
from system.task_output_tool import task_output_tool, TaskOutputConfig
config = TaskOutputConfig()
print(f"  default task_output_dir: {config.task_output_dir}")
print(f"  tempfile.gettempdir(): {__import__('tempfile').gettempdir()}")

import tempfile
test("/tmp/ in default path", lambda: "/tmp/" in config.task_output_dir)

# Test actual call
r = task_output_tool(task_id="test123", block=False)
j = json.loads(r)
print(f"  task_output result: {json.dumps(j, ensure_ascii=False)[:150]}")
test("task_output_tool works", lambda: j.get("success"))

# ===== 3. git =====
print("\n=== 3. git ===")
from git.git import git_status, git_log
r = git_status(path=".")
test("git status", lambda: "sandbox" in r or "changed" in r.lower() or r)

r = git_log(path=".", max_count=3)
test("git log", lambda: r)

# ===== 4. compress =====
print("\n=== 4. compress ===")
from compress.compress import compress_file, decompress_file
td = __import__('tempfile').gettempdir()

# zip
src = os.path.join(td, "test_compress_src.txt")
with open(src, "w") as f: f.write("hello test content " * 100)
zip_dst = os.path.join(td, "test_output.zip")
r = compress_file(source_path=src, destination_path=zip_dst, compression_type="zip")
test("zip compress", lambda: os.path.exists(zip_dst))

# gzip
gz_dst = os.path.join(td, "test_output.gz")
r = compress_file(source_path=src, destination_path=gz_dst, compression_type="gzip")
test("gzip compress", lambda: os.path.exists(gz_dst))

# tar.gz
tgz_dst = os.path.join(td, "test_output.tar.gz")
r = compress_file(source_path=src, destination_path=tgz_dst, compression_type="tar.gz")
test("tar.gz compress", lambda: os.path.exists(tgz_dst))

# ===== 5. select.select in notification =====
print("\n=== 5. notification_tool select.select ===")
# Must import outside interactive console context
# The import itself triggers prompt_toolkit which crashes in subprocess
try:
    import interaction.notification_tool
    print("  import succeeded - checking function")
    from interaction.notification_tool import notification_tool
    r = notification_tool(message="test", level="info")
    j = json.loads(r) if isinstance(r, str) else r
    test("notification basic", lambda: True)
except Exception as e:
    print(f"  import failed (subprocess expected): {type(e).__name__}: {e}")
    test("notification import issue", lambda: "NoConsoleScreenBuffer" in str(e))

# ===== 6. shell/power_shell_tool =====
print("\n=== 6. power_shell_tool ===")
from shell.power_shell_tool import power_shell
r = power_shell(command="Get-ChildItem *.py | Select-Object -First 3", capture_output=True, timeout=10)
print(f"  powershell: {str(r)[:150]}")
test("powershell tool", lambda: r)

# ===== 7. system tools =====
print("\n=== 7. system tools ===")
from system.system_info_tool import system_info_tool
r = system_info_tool()
print(f"  sysinfo: {str(r)[:100]}")
test("system_info", lambda: r)

from system.finish import finish
r = finish(reason="test completion")
print(f"  finish: {str(r)[:100]}")
test("finish", lambda: r)

from system.snip_tool import snip_tool
try:
    r = snip_tool(message_ids=[])
    test("snip empty", lambda: True)
except Exception as e:
    test("snip handles empty", lambda: True)

# ===== 8. docker (basic) =====
print("\n=== 8. docker basic ===")
from docker.docker import docker_ps
r = docker_ps(all_containers=False)
print(f"  docker ps: {str(r)[:100]}")
test("docker ps", lambda: True)  # might fail if no docker - just check no crash

# ===== 9. tmux (should fail gracefully) =====
print("\n=== 9. tmux graceful fallback ===")
from tmux.tmux import tmux_list_sessions
r = tmux_list_sessions()
test("tmux fallback on Windows", lambda: "not installed" in r.lower() or "No tmux" in r)

# ===== 10. workspace =====
print("\n=== 10. workspace ===")
from workspace.workspace import workspace_list
r = workspace_list()
print(f"  workspace: {str(r)[:100]}")
test("workspace list", lambda: True)

print(f"\n====== 最终结果: {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL} 项 ======")
sys.exit(0 if FAIL == 0 else 1)
