#!/usr/bin/env python3
"""
SendMessageTool 测试
"""

import json
import sys
import os
import tempfile
import shutil

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interaction.send_message_tool import send_message_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "send_message"
    assert "parameters" in TOOL_DEF["function"]
    assert "to" in TOOL_DEF["function"]["parameters"]["properties"]
    assert "message" in TOOL_DEF["function"]["parameters"]["properties"]
    assert "summary" in TOOL_DEF["function"]["parameters"]["properties"]
    
    # 检查TOOL_CALL_MAP
    assert "send_message" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["send_message"] == send_message_tool

def test_send_text_message():
    """测试发送文本消息"""
    result = send_message_tool(
        to="alice",
        message="Hello, this is a test message",
        summary="Test message summary"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "messageId" in result_dict
    assert result_dict["to"] == "alice"
    assert result_dict["summary"] == "Test message summary"
    assert result_dict["messageType"] == "text"
    assert "durationMs" in result_dict

def test_send_structured_message():
    """测试发送结构化消息"""
    structured_msg = {
        "type": "shutdown_request",
        "reason": "System maintenance"
    }
    
    result = send_message_tool(
        to="*",
        message=structured_msg,
        summary="Broadcast shutdown request"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["to"] == "*"
    assert result_dict["messageType"] == "structured"
    assert "note" in result_dict

def test_send_message_broadcast():
    """测试广播消息"""
    result = send_message_tool(
        to="*",
        message="Broadcast message to all teammates",
        summary="Important announcement"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["to"] == "*"

def test_send_message_without_summary():
    """测试无摘要的消息发送"""
    result = send_message_tool(
        to="bob",
        message="Message without summary"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["to"] == "bob"
    assert result_dict["summary"] is None

def test_send_message_uds_peer():
    """测试发送给UDS对等节点"""
    result = send_message_tool(
        to="uds:/tmp/test.sock",
        message="Message to UDS peer",
        summary="UDS peer message"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["to"] == "uds:/tmp/test.sock"

def test_send_message_bridge_peer():
    """测试发送给桥接对等节点"""
    result = send_message_tool(
        to="bridge:session123",
        message="Message to bridge peer",
        summary="Bridge peer message"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["to"] == "bridge:session123"

def test_error_handling():
    """测试错误处理（模拟异常）"""
    # 这里我们无法轻易触发异常，但确保函数能处理异常情况
    # 通过传递无效参数测试
    try:
        # 故意传递一个不可JSON序列化的对象
        import threading
        result = send_message_tool(
            to="test",
            message={"lock": threading.Lock()},  # 不可序列化对象
            summary="Test"
        )
        result_dict = json.loads(result)
        # 即使有异常，函数也应该返回错误结果而不是崩溃
        assert "success" in result_dict
    except Exception:
        # 如果函数崩溃了，测试失败
        assert False, "Function should handle exceptions gracefully"

def test_module_exports():
    """测试模块导出"""
    from interaction.send_message_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "send_message_tool" in __all__

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_send_text_message,
        test_send_structured_message,
        test_send_message_broadcast,
        test_send_message_without_summary,
        test_send_message_uds_peer,
        test_send_message_bridge_peer,
        test_error_handling,
        test_module_exports
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__} passed")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} error: {e}")
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)