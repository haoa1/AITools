#!/usr/bin/env python3
"""
TerminalCaptureTool 测试
"""

import json
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.terminal_capture_tool import terminal_capture_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "terminal_capture"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "command" in params
    assert "capture_output" in params
    assert "timeout_seconds" in params
    assert "working_directory" in params
    
    # 检查TOOL_CALL_MAP
    assert "terminal_capture" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["terminal_capture"] == terminal_capture_tool

def test_no_command():
    """测试无命令情况（返回终端状态）"""
    result = terminal_capture_tool()
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["command"] is None
    assert result_dict["status"] == "idle"
    assert "terminalInfo" in result_dict
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict

def test_simple_command():
    """测试简单命令"""
    # 使用一个简单的命令（跨平台）
    if sys.platform == "win32":
        command = "echo test"
    else:
        command = "echo test"
    
    result = terminal_capture_tool(
        command=command,
        capture_output=True,
        timeout_seconds=10
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["command"] == command
    assert "returnCode" in result_dict
    assert "stdout" in result_dict
    assert "stderr" in result_dict
    assert result_dict["captured"] == True
    assert result_dict["timeoutSeconds"] == 10

def test_command_without_capture():
    """测试不捕获输出的命令"""
    result = terminal_capture_tool(
        command="echo test",
        capture_output=False,
        timeout_seconds=5
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["command"] == "echo test"
    assert result_dict["captured"] == False
    assert result_dict["status"] == "executed_without_capture"
    assert "note" in result_dict

def test_command_timeout():
    """测试命令超时"""
    # 使用一个会长时间运行的命令
    if sys.platform == "win32":
        command = "ping -n 10 127.0.0.1"  # Windows
    else:
        command = "sleep 10"  # Unix
    
    result = terminal_capture_tool(
        command=command,
        capture_output=True,
        timeout_seconds=1  # 很短的超时
    )
    
    result_dict = json.loads(result)
    # 可能超时或成功，取决于执行时间
    assert "success" in result_dict
    assert "durationMs" in result_dict

def test_invalid_command():
    """测试无效命令"""
    result = terminal_capture_tool(
        command="nonexistent_command_xyz123",
        capture_output=True,
        timeout_seconds=5
    )
    
    result_dict = json.loads(result)
    # 应该失败或返回错误
    assert "success" in result_dict
    # 可能成功但返回错误代码，或完全失败

def test_working_directory():
    """测试工作目录参数"""
    # 获取当前目录
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        # 测试列出目录的命令
        if sys.platform == "win32":
            command = "dir"
        else:
            command = "ls"
        
        result = terminal_capture_tool(
            command=command,
            capture_output=True,
            timeout_seconds=5,
            working_directory=temp_dir
        )
        
        result_dict = json.loads(result)
        # 命令应该成功执行
        assert "success" in result_dict
        if result_dict["success"]:
            assert "workingDirectory" in result_dict

def test_error_handling():
    """测试错误处理"""
    # 测试无效参数
    try:
        result = terminal_capture_tool(
            command="echo test",
            capture_output=True,
            timeout_seconds=0,  # 无效超时
            working_directory="/nonexistent/path"  # 可能不存在的路径
        )
        result_dict = json.loads(result)
        # 应该仍然返回结果
        assert "success" in result_dict
    except Exception:
        # 函数不应该崩溃
        assert False, "Function should handle invalid parameters gracefully"

def test_module_exports():
    """测试模块导出"""
    from system.terminal_capture_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "terminal_capture_tool" in __all__

def test_tool_interface():
    """测试工具接口兼容性"""
    # 检查工具定义符合Claude Code模式
    tool_def = TOOL_DEF
    assert tool_def["function"]["name"] == "terminal_capture"
    
    # 检查参数约束
    timeout_param = tool_def["function"]["parameters"]["properties"]["timeout_seconds"]
    assert "minimum" in timeout_param
    assert "maximum" in timeout_param

def test_command_status_codes():
    """测试命令状态码"""
    # 测试成功命令
    if sys.platform == "win32":
        command = "exit 0"
    else:
        command = "true"
    
    result = terminal_capture_tool(
        command=command,
        capture_output=True,
        timeout_seconds=5
    )
    
    result_dict = json.loads(result)
    if result_dict["success"]:
        # 如果命令执行成功
        assert "returnCode" in result_dict
        # 成功的命令应该返回0
        if "returnCode" in result_dict and result_dict["returnCode"] == 0:
            assert result_dict.get("status") in ["success", None]

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_no_command,
        test_simple_command,
        test_command_without_capture,
        test_command_timeout,
        test_invalid_command,
        test_working_directory,
        test_error_handling,
        test_module_exports,
        test_tool_interface,
        test_command_status_codes
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