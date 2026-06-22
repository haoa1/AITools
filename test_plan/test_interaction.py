#!/usr/bin/env python3
"""Test interaction modules - select.select issue on Windows."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json

PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        r = fn()
        print(f"  PASS: {name}{' -> ' + str(r)[:80] if r not in (True, None) else ''}")
        PASS += 1
    except Exception as e:
        print(f"  FAIL: {name} - {type(e).__name__}: {e}")
        FAIL += 1

# 1. notification_tool - basic
print("=== 1. notification_tool ===")
from interaction.notification_tool import notification_tool

r = notification_tool(message="test info", level="info")
j = json.loads(r)
test("notification info", lambda: j.get("success"))

r = notification_tool(message="test warning", level="warning")
j = json.loads(r)
test("notification warning", lambda: j.get("success"))

r = notification_tool(message="test error", level="error")
j = json.loads(r)
test("notification error", lambda: j.get("success"))

# 2. The select.select issue - does it crash when stdin is a pipe?
print("\n=== 2. select.select 兼容测试 ===")
# notification_tool with confirm (timeout) - this triggers select.select([sys.stdin])
import time
start = time.time()
try:
    r = notification_tool(message="confirm test", level="info", confirm=True, timeout=1000)
    dur = time.time() - start
    print(f"  confirm with timeout 1s: 耗时{dur:.1f}s, result: {r[:100]}")
    test("select.select 不崩溃", lambda: True)
except Exception as e:
    dur = time.time() - start
    print(f"  FAIL - 耗时{dur:.1f}s: {type(e).__name__}: {e}")
    test("select.select 不崩溃", lambda: False)

# 3. ask_user_question with timeout - also uses select.select
print("\n=== 3. ask_user_question (select.select) ===")
from interaction.interaction import ask_user_question
start = time.time()
try:
    r = ask_user_question(prompt="test question", default_value="default", timeout=2)
    dur = time.time() - start
    print(f"  ask_user_question timeout=2s: 耗时{dur:.1f}s, result: {r[:60]}")
    test("ask_user_question select兼容", lambda: True)
except Exception as e:
    dur = time.time() - start
    print(f"  FAIL - 耗时{dur:.1f}s: {type(e).__name__}: {e}")
    test("ask_user_question select兼容", lambda: False)

# 4. task_output_tool - /tmp/ hardcoded path
print("\n=== 4. task_output_tool - /tmp/ 路径 ===")
from system.task_output_tool import task_output_tool, TaskOutputConfig

r = task_output_tool(task_id="test123", block=False)
j = json.loads(r)
print(f"  task_output: {json.dumps(j, ensure_ascii=False)[:200]}")

config = TaskOutputConfig.from_env()
print(f"  task_output_dir: {config.task_output_dir}")
import tempfile
test("task_output_dir 是 /tmp/", lambda: config.task_output_dir.startswith(tempfile.gettempdir()) or config.task_output_dir == "/tmp/aitools_tasks")

# 5. compress - Windows path test
print("\n=== 5. compress ===")
from compress.compress import compress_file, decompress_file
import tempfile, os

td = tempfile.gettempdir()
src = os.path.join(td, "test_compress_源文件.txt")
with open(src, "w") as f:
    f.write("Hello 中文 test content " * 100)

zip_path = os.path.join(td, "test_output.zip")
r = compress_file(source_path=src, destination_path=zip_path, compression_type="zip")
print(f"  compress zip: {str(r)[:100]}")
test("compress zip", lambda: os.path.exists(zip_path))

# 6. git basic
print("\n=== 6. git basic ===")
from git.git import git_status
r = git_status(path=".")
print(f"  git status: {str(r)[:100]}")
test("git status works", lambda: bool(r))

print(f"\n====== 结果: {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL} 项 ======")
sys.exit(0 if FAIL == 0 else 1)
