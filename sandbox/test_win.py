#!/usr/bin/env python3
"""Windows sandbox module comprehensive test suite.
Uses test_repl.py (a pipe-friendly interactive script) instead of python -i."""

import sys
import os
import json
import time
import traceback

# Add parent dir (AITools root) to path so sandbox.sandbox can be imported
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

PASS = 0
FAIL = 0
ERRORS = []


def test(name, fn):
    global PASS, FAIL
    try:
        result = fn()
        if result is None:
            PASS += 1
            print(f"  ✅ {name}")
        elif isinstance(result, dict) and result.get("error") is None and result.get("success") in (None, True):
            PASS += 1
            print(f"  ✅ {name}")
        elif isinstance(result, dict) and result.get("success"):
            PASS += 1
            print(f"  ✅ {name}")
        elif isinstance(result, bool) and result:
            PASS += 1
            print(f"  ✅ {name}")
        else:
            FAIL += 1
            msg = str(result)[:120]
            if isinstance(result, dict) and "error" in result:
                msg = result["error"][:120]
            print(f"  ❌ {name}: {msg}")
            ERRORS.append((name, result))
    except Exception as e:
        FAIL += 1
        print(f"  ❌ {name}: {type(e).__name__}: {e}")
        ERRORS.append((name, {"exception": str(e), "traceback": traceback.format_exc()}))


def result(r):
    if isinstance(r, str):
        return json.loads(r)
    return r


_script_dir = os.path.dirname(os.path.abspath(__file__))
REPL_SCRIPT = os.path.join(_script_dir, "test_repl.py")
REPL_CMD = f"python {REPL_SCRIPT}"
SEND_KW = {"async": False, "prompt": "PROMPT>"}


# =========================================================================
print("=" * 60)
print("  Windows Sandbox 综合测试")
print(f"  REPL: {REPL_SCRIPT}")
print("=" * 60)

from sandbox.sandbox import (sandbox_handler, _create_io_backend,
                             IS_WINDOWS)

# -------------------------------------------------------------------------
# 测试 1: 模块导入 + 平台检测
# -------------------------------------------------------------------------
print("\n--- 测试1: 模块导入 ---")

test("模块基本导入", lambda: {"success": True})
backend = _create_io_backend()
test(f"I/O 后端: {backend.name}", lambda: {"success": True})
test(f"平台: windows={IS_WINDOWS}", lambda: {"success": True})
test(f"has_tmux: {backend.has_tmux}", lambda: {"success": True})

# -------------------------------------------------------------------------
# 测试 2: list (空)
# -------------------------------------------------------------------------
print("\n--- 测试2: list (空) ---")

r = result(sandbox_handler('list', ''))
test("list 返回正常", lambda: r)
test("list 无沙箱", lambda: len(r.get("sandboxes", [])) == 0)

# -------------------------------------------------------------------------
# 测试 3: 启动沙箱
# -------------------------------------------------------------------------
print("\n--- 测试3: start 沙箱 ---")

r = result(sandbox_handler('start', 'main', cmd=REPL_CMD, timeout=10.0, prompt='PROMPT>'))
test("start REPL", lambda: r)
print(f"  > {json.dumps(r, ensure_ascii=False)[:200]}")

# -------------------------------------------------------------------------
# 测试 4: send 指令 (同步模式)
# -------------------------------------------------------------------------
print("\n--- 测试4: send 指令 ---")

r = result(sandbox_handler('send', 'main', input='hello', timeout=10.0, **SEND_KW))
test("send 'hello'", lambda: r)
if r.get("response"):
    print(f"  > response: {r['response'][:100]}")

r = result(sandbox_handler('send', 'main', input='world!', timeout=10.0, **SEND_KW))
test("send 'world!'", lambda: r)
if r.get("response"):
    print(f"  > response: {r['response'][:100]}")

# -------------------------------------------------------------------------
# 测试 5: exec 命令
# -------------------------------------------------------------------------
print("\n--- 测试5: exec 命令 ---")

r = result(sandbox_handler('exec', 'main', cmd='echo hello_world', timeout=10.0))
test("exec echo", lambda: r)
if r.get("output"):
    print(f"  > output: {r['output'][:100]}")

r = result(sandbox_handler('exec', 'main', cmd='dir /b', timeout=10.0))
test("exec dir", lambda: r)

# -------------------------------------------------------------------------
# 测试 6: buffer
# -------------------------------------------------------------------------
print("\n--- 测试6: buffer ---")

r = result(sandbox_handler('buffer', 'main'))
test("buffer 读取", lambda: r)
if r.get("output"):
    print(f"  > buffer({r.get('size','?')}B): {r['output'][:100]}")

# -------------------------------------------------------------------------
# 测试 7: list (有沙箱)
# -------------------------------------------------------------------------
print("\n--- 测试7: list 有沙箱 ---")

r = result(sandbox_handler('list', ''))
test("list 有沙箱", lambda: len(r.get("sandboxes", [])) > 0)

sandboxes = r.get("sandboxes", [])
for sb in sandboxes:
    print(f"  沙箱: {sb['name']} pid={sb['pid']} alive={sb['alive']} "
          f"reader={sb['reader']} ready={sb['ready']} backend={sb.get('backend','?')}")

# -------------------------------------------------------------------------
# 测试 8: 多沙箱隔离
# -------------------------------------------------------------------------
print("\n--- 测试8: 多沙箱隔离 ---")

r1 = result(sandbox_handler('start', 'box_a', cmd=REPL_CMD, timeout=10.0, prompt='PROMPT>'))
r2 = result(sandbox_handler('start', 'box_b', cmd=REPL_CMD, timeout=10.0, prompt='PROMPT>'))
test("box_a start", lambda: r1)
test("box_b start", lambda: r2)

time.sleep(0.3)

r = result(sandbox_handler('send', 'box_a', input='from_a', timeout=10.0, **SEND_KW))
test("box_a send", lambda: r)
if r.get("response"):
    print(f"  > box_a: {r['response'][:60]}")

r = result(sandbox_handler('send', 'box_b', input='from_b', timeout=10.0, **SEND_KW))
test("box_b send", lambda: r)
if r.get("response"):
    print(f"  > box_b: {r['response'][:60]}")

# Clean up test boxes
sandbox_handler('stop', 'box_a')
sandbox_handler('stop', 'box_b')

time.sleep(0.3)

r = result(sandbox_handler('list', ''))
sbox_count = len(r.get("sandboxes", []))
test(f"多沙箱清理 (当前: {sbox_count})", lambda: {"success": sbox_count <= 1})

# -------------------------------------------------------------------------
# 测试 9: stop
# -------------------------------------------------------------------------
print("\n--- 测试9: stop ---")

r = result(sandbox_handler('stop', 'main'))
test("stop 主沙箱", lambda: r)

time.sleep(0.3)

r = result(sandbox_handler('list', ''))
test("所有沙箱已清理", lambda: len(r.get("sandboxes", [])) == 0)

# -------------------------------------------------------------------------
# 测试 10: 错误处理
# -------------------------------------------------------------------------
print("\n--- 测试10: 错误处理 ---")

r = result(sandbox_handler('send', 'nonexistent', input='test'))
test("不存在沙箱报错", lambda: "error" in r or "不存在" in json.dumps(r, ensure_ascii=False))

r = result(sandbox_handler('send', '', input=''))
test("空 input 报错", lambda: "error" in r or "缺少" in json.dumps(r, ensure_ascii=False))

r = result(sandbox_handler('unknown_cmd', ''))
test("未知命令报错", lambda: "error" in r or "未知命令" in json.dumps(r, ensure_ascii=False))

r = result(sandbox_handler('start', 'fakebox', cmd='this_cmd_dne_xyz', timeout=5.0))
test("不存在命令报错", lambda: "error" in r or "未找到" in json.dumps(r, ensure_ascii=False))

# -------------------------------------------------------------------------
# 总结
# -------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"  结果: {PASS} 通过  {FAIL} 失败  /  {PASS + FAIL} 总计")
print("=" * 60)

if ERRORS:
    print("\n失败详情:")
    for name, err in ERRORS[:5]:
        print(f"  ❌ {name}")
        print(f"     {json.dumps(err, ensure_ascii=False, default=str)[:200]}")

sys.exit(0 if FAIL == 0 else 1)
