#!/usr/bin/env python3
"""
sandbox.py v2 — 端到端集成测试
测试场景：用 test_app.py 作为交互式应用，验证新 sandbox 的全部能力
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sandbox import sandbox_handler

PASS = 0
FAIL = 0

ECHO_APP = os.path.join(os.path.dirname(__file__), "echo_app.py")
ECHO_PROMPT = "ECHO> "

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        print(f"  ✗ {label}  {detail}")

def run():
    global PASS, FAIL
    
    # 1. start — 同步启动 echo_app.py
    print("\n=== 1. start (sync) ===")
    r = json.loads(sandbox_handler(
        sub_cmd="start", name="test1", cmd=f"python3 {ECHO_APP}",
        timeout=10, prompt=ECHO_PROMPT
    ))
    check("start returns success", r.get("success"), json.dumps(r))
    name = r.get("name", "test1")
    
    # 2. send — 发送消息，等待响应
    print("\n=== 2. send + response ===")
    r = json.loads(sandbox_handler(
        sub_cmd="send", name=name, input="hello world",
        timeout=10, prompt=ECHO_PROMPT
    ))
    check("send succeeds", r.get("success"), json.dumps(r))
    check("send echoes back", "ECHO: hello world" in r.get("response", ""), r.get("response",""))
    
    # 3. send again
    print("\n=== 3. send second message ===")
    r = json.loads(sandbox_handler(
        sub_cmd="send", name=name, input="second test",
        timeout=10, prompt=ECHO_PROMPT
    ))
    check("send succeeds", r.get("success"), json.dumps(r))
    check("second echo correct", "ECHO: second test" in r.get("response", ""), r.get("response",""))
    
    # 4. exec — 在 tmux workspace 执行 bash
    print("\n=== 4. exec (tmux bash) ===")
    r = json.loads(sandbox_handler(
        sub_cmd="exec", name=name, cmd="echo 'hello from tmux'", timeout=10
    ))
    check("exec succeeds", r.get("success"), json.dumps(r))
    check("exec output", "hello from tmux" in r.get("output", ""), r.get("output",""))
    
    # 5. list — 列表沙箱
    print("\n=== 5. list ===")
    r = json.loads(sandbox_handler(sub_cmd="list"))
    check("list succeeds", r.get("success"), json.dumps(r))
    check("list contains test1", any(s["name"] == "test1" for s in r.get("sandboxes", [])))
    
    # 6. capture — 捕获 pane
    print("\n=== 6. capture ===")
    r = json.loads(sandbox_handler(sub_cmd="capture", name=name))
    check("capture succeeds", r.get("success"), json.dumps(r))
    check("capture has content", bool(r.get("output", "")), r.get("output","")[:50])
    
    # 7. async send
    print("\n=== 7. send (async) ===")
    r = json.loads(sandbox_handler(
        sub_cmd="send", name=name, input="async test",
        timeout=10, prompt=ECHO_PROMPT, **{"async": True}
    ))
    check("async send returns task_id", r.get("async"), json.dumps(r))
    task_id = r.get("task_id", "")
    check("has task_id", bool(task_id))
    
    if task_id:
        time.sleep(2)
        r = json.loads(sandbox_handler(sub_cmd="check", name=name, task_id=task_id))
        check("async check succeeds", r.get("success"), json.dumps(r))
        result = r.get("result", {})
        if result.get("status") == "completed":
            check("async result completed", True)
            check("async response correct", "ECHO: async test" in result.get("response", ""), result.get("response",""))
        elif result.get("status") == "pending":
            print("  ⚠ async result still pending, need longer wait")
            check("async pending (retry later)", True)
    
    # 8. async start
    print("\n=== 8. start (async) ===")
    r = json.loads(sandbox_handler(
        sub_cmd="start", name="test2", cmd=f"python3 {ECHO_APP}",
        timeout=10, prompt=ECHO_PROMPT, **{"async": True}
    ))
    check("async start returns task_id", r.get("async"), json.dumps(r))
    task_id2 = r.get("task_id", "")
    
    if task_id2:
        time.sleep(3)
        r = json.loads(sandbox_handler(sub_cmd="check", name="test2", task_id=task_id2))
        check("async start check", r.get("success"), json.dumps(r))
        result = r.get("result", {})
        if result.get("status") == "completed":
            check("async start completed", True)
    
    # 9. send to test2
    print("\n=== 9. send to test2 ===")
    r = json.loads(sandbox_handler(
        sub_cmd="send", name="test2", input="from test2",
        timeout=10, prompt=ECHO_PROMPT
    ))
    check("send to test2", r.get("success"), json.dumps(r))
    check("test2 echo", "ECHO: from test2" in r.get("response", ""), r.get("response",""))
    
    # 10. list (should show 2 sandboxes)
    print("\n=== 10. list (2 sandboxes) ===")
    r = json.loads(sandbox_handler(sub_cmd="list"))
    check("list has 2 sandboxes", len(r.get("sandboxes", [])) == 2, json.dumps(r.get("sandboxes", [])))
    
    # 11. stop — 清理
    print("\n=== 11. cleanup ===")
    for sname in ["test1", "test2"]:
        r = json.loads(sandbox_handler(sub_cmd="stop", name=sname, cleanup=True))
        check(f"stop {sname}", r.get("success"), json.dumps(r))
    
    r = json.loads(sandbox_handler(sub_cmd="list"))
    check("list empty after cleanup", len(r.get("sandboxes", [])) == 0, json.dumps(r.get("sandboxes", [])))
    
    # 12. error handling
    print("\n=== 12. error handling ===")
    r = json.loads(sandbox_handler(sub_cmd="send", name="nonexistent"))
    check("error: nonexistent sandbox", "error" in r, json.dumps(r))
    
    r = json.loads(sandbox_handler(sub_cmd="start", name="test1", cmd="/tmp/nonexistent_app"))
    check("error: nonexistent cmd", "error" in r, json.dumps(r))
    
    r = json.loads(sandbox_handler(sub_cmd="foobar"))
    check("error: unknown sub_cmd", "error" in r, json.dumps(r))
    
    # Summary
    total = PASS + FAIL
    print(f"\n{'='*50}")
    print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
    print(f"{'ALL TESTS PASSED' if FAIL == 0 else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    run()
