#!/usr/bin/env python3
"""
ReadMcpResourceTool 测试
"""

import json
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.read_mcp_resource_tool import read_mcp_resource_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "read_mcp_resource"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "uri" in params
    assert TOOL_DEF["function"]["parameters"]["required"] == ["uri"]
    
    # 检查TOOL_CALL_MAP
    assert "read_mcp_resource" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["read_mcp_resource"] == read_mcp_resource_tool

def test_read_existing_resource():
    """测试读取现有资源"""
    # 测试文件系统资源
    result = read_mcp_resource_tool("file:///home/user/documents")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["uri"] == "file:///home/user/documents"
    assert "content" in result_dict
    assert "mimeType" in result_dict
    assert result_dict["mimeType"] == "text/plain"
    assert "size" in result_dict
    assert "metadata" in result_dict
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict
    assert "note" in result_dict

def test_read_github_resource():
    """测试读取GitHub资源"""
    result = read_mcp_resource_tool("github://repos/user/project1")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["uri"] == "github://repos/user/project1"
    assert result_dict["mimeType"] == "application/vnd.github.v3+json"
    
    # 内容应该是有效的JSON
    content = result_dict["content"]
    try:
        json.loads(content)
        is_valid_json = True
    except:
        is_valid_json = False
    assert is_valid_json, "GitHub resource content should be valid JSON"

def test_read_calendar_resource():
    """测试读取日历资源"""
    result = read_mcp_resource_tool("calendar://events/today")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["uri"] == "calendar://events/today"
    assert result_dict["mimeType"] == "application/calendar+json"

def test_read_weather_resource():
    """测试读取天气资源"""
    result = read_mcp_resource_tool("weather://current/local")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["uri"] == "weather://current/local"
    assert result_dict["mimeType"] == "application/json"

def test_resource_not_found():
    """测试资源不存在的情况"""
    result = read_mcp_resource_tool("nonexistent://resource/uri")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == False
    assert "error" in result_dict
    assert "not found" in result_dict["error"].lower()
    assert "Available resources" in result_dict["error"]

def test_resource_content_structure():
    """测试资源内容结构"""
    # 测试多个资源以确保一致性
    test_uris = [
        "file:///home/user/documents",
        "github://repos/user/project1",
        "calendar://events/today",
        "weather://current/local"
    ]
    
    for uri in test_uris:
        result = read_mcp_resource_tool(uri)
        result_dict = json.loads(result)
        
        if result_dict["success"]:
            # 检查必需字段
            assert "content" in result_dict
            assert "mimeType" in result_dict
            assert "size" in result_dict
            assert isinstance(result_dict["size"], int)
            
            # 检查元数据
            metadata = result_dict.get("metadata", {})
            assert isinstance(metadata, dict)

def test_error_handling():
    """测试错误处理"""
    # 测试无效URI格式
    result = read_mcp_resource_tool("invalid uri with spaces")
    
    result_dict = json.loads(result)
    # 函数应该返回错误而不是崩溃
    assert "success" in result_dict
    # 可能成功（如果在模拟数据中）或失败

def test_module_exports():
    """测试模块导出"""
    from network.read_mcp_resource_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "read_mcp_resource_tool" in __all__

def test_tool_interface():
    """测试工具接口兼容性"""
    # 检查工具定义符合Claude Code模式
    tool_def = TOOL_DEF
    assert tool_def["function"]["name"] == "read_mcp_resource"
    assert "uri" in tool_def["function"]["parameters"]["properties"]
    
    # URI应该是必需的
    assert "uri" in tool_def["function"]["parameters"]["required"]

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_read_existing_resource,
        test_read_github_resource,
        test_read_calendar_resource,
        test_read_weather_resource,
        test_resource_not_found,
        test_resource_content_structure,
        test_error_handling,
        test_module_exports,
        test_tool_interface
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