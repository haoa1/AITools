#!/usr/bin/env python3
"""Test shell/bash module on Windows."""
import sys, os, time, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shell.bash import bash

PASS = 0
FAIL = 0

def test(name, fn):
    global PASS, FAIL
    try:
        r = fn()
        if r:
            print(f"  PASS: {name}")
            PASS += 1
        else:
            print(f"  FAIL: {name}")
            FAIL += 1
    except Exception as e:
        print(f"  FAIL: {name} - {type(e).__name__}: {e}")
        FAIL += 1

# 1. 基础命令
print("=== 1. 基础 echo ===")
r = bash(command="echo Hello World", capture_output=True, shell=True, timeout=10)
print(f"  output: {r[:80]}")
test("echo 输出非空", lambda: bool(r.strip()))

# 2. 管道
print("\n=== 2. 管道过滤 ===")
r = bash(command="dir /b *.py | findstr sandbox", capture_output=True, shell=True, timeout=10)
print(f"  output: {r[:200]}")
test("管道过滤有结果", lambda: "sandbox" in r)

# 3. 中文路径
print("\n=== 3. 中文路径 ===")
test_dir = os.path.join(tempfile.gettempdir(), "test_plan_中文")
os.makedirs(test_dir, exist_ok=True)
test_file = os.path.join(test_dir, "中文文件.txt")
with open(test_file, "w", encoding="utf-8") as f:
    f.write("你好世界")
r = bash(command=f'type "{test_file}"', capture_output=True, shell=True, timeout=10)
print(f"  中文文件内容: {r[:60]}")
test("中文路径读取", lambda: "你好" in r)

# 4. timeout
print("\n=== 4. timeout ===")
start = time.time()
try:
    r = bash(command="ping -n 10 127.0.0.1", capture_output=True, shell=True, timeout=3)
    dur = time.time() - start
    print(f"  命令未超时(耗时{dur:.1f}s)")
except Exception as e:
    dur = time.time() - start
    print(f"  超时(耗时{dur:.1f}s): {type(e).__name__}: {e}")
    # Windows ping doesn't respect small timeout with subprocess well
test("timeout 机制", lambda: dur < 8)

# 5. 超长输出
print("\n=== 5. 超长输出 ===")
r = bash(command="for /l %i in (1,1,500) do @echo row%i", capture_output=True, shell=True, timeout=10)
lines = r.strip().split("\n")
print(f"  输出 {len(lines)} 行")
test("500行输出", lambda: len(lines) >= 500)

# 6. 错误命令
print("\n=== 6. 错误命令 ===")
r = bash(command="this_cmd_dne_xyz", capture_output=True, shell=True, timeout=5)
print(f"  错误输出: {r[:100]}")
test("错误命令返回信息", lambda: bool(r))

# 7. 空命令
print("\n=== 7. 空命令 ===")
r = bash(command="", capture_output=True, shell=True, timeout=5)
print(f"  空命令: '{r[:50]}'")

# 8. working_dir
print("\n=== 8. working_dir ===")
r = bash(command="cd", capture_output=True, shell=True, timeout=10, working_dir=test_dir)
print(f"  working_dir 输出: {r[:80]}")
test("working_dir 生效", lambda: test_dir in r)

# 9. env_vars
print("\n=== 9. env_vars ===")
r = bash(command="echo %MY_TEST_VAR%", capture_output=True, shell=True, timeout=10,
         env_vars={"MY_TEST_VAR": "hello_from_env"})
print(f"  env: {r[:60]}")
test("env_vars 生效", lambda: "hello_from_env" in r)

print(f"\n====== 结果: {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL} 项 ======")
sys.exit(0 if FAIL == 0 else 1)
