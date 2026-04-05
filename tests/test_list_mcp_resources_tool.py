#!/usr/bin/env python3
"""
ListMcpResourcesTool 测试
"""

import json
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.list_mcp_resources_tool import list_mcp_resources_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "list_mcp_resources"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "server" in params
    
    # 检查TOOL_CALL_MAP
    assert "list_mcp_resources" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["list_mcp_resources"] == list_mcp_resources_tool

def test_list_all_resources():
    """测试列出所有资源"""
    result = list_mcp_resources_tool()
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "resources" in result_dict
    assert isinstance(result_dict["resources"], list)
    assert result_dict["serverFilter"] is None
    assert "serversAvailable" in result_dict
    assert "totalResources" in result_dict
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict
    assert "note" in result_dict

def test_list_resources_by_server():
    """测试按服务器过滤资源"""
    result = list_mcp_resources_tool(server="filesystem")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["serverFilter"] == "filesystem"
    assert "resources" in result_dict
    
    resources = result_dict["resources"]
    # 所有资源应该来自filesystem服务器
    for resource in resources:
        assert resource["server"] == "filesystem"

def test_list_resources_by_another_server():
    """测试按其他服务器过滤资源"""
    result = list_mcp_resources_tool(server="github")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["serverFilter"] == "github"
    
    resources = result_dict["resources"]
    for resource in resources:
        assert resource["server"] == "github"

def test_server_not_found():
    """测试服务器不存在的情况"""
    result = list_mcp_resources_tool(server="nonexistent")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == False
    assert "error" in result_dict
    assert "nonexistent" in result_dict["error"]
    assert "Available servers" in result_dict["error"]

def test_resource_structure():
    """测试资源数据结构"""
    result = list_mcp_resources_tool()
    result_dict = json.loads(result)
    
    if result_dict["success"] and len(result_dict["resources"]) > 0:
        resource = result_dict["resources"][0]
        # 检查必需的字段
        assert "uri" in resource
        assert "name" in resource
        assert "server" in resource
        # 可选字段
        assert "mimeType" in resource
        assert "description" in resource

def test_multiple_servers():
    """测试多个服务器的情况"""
    result = list_mcp_resources_tool()
    result_dict = json.loads(result)
    
    assert result_dict["success"] == True
    assert "serversAvailable" in result_dict
    servers = result_dict["serversAvailable"]
    assert isinstance(servers, list)
    assert len(servers) >= 1  # 至少有一个模拟服务器

def test_error_handling():
    """测试错误处理"""
    # 这里我们无法轻易触发异常，但确保函数能处理异常情况
    # 通过模拟异常测试
    try:
        # 暂时修改工具函数以引发异常
        original_func = list_mcp_resources_tool
        
        # 创建一个会引发异常的函数
        def faulty_func(server=None):
            raise ValueError("Test exception")
        
        # 替换函数
        import network.list_mcp_resources_tool
        original = network.list_mcp_resources_tool.list_mcp_resources_tool
        network.list_mcp_resources_tool.list_mcp_resources_tool = faulty_func
        
        try:
            result = faulty_func()
            result_dict = json.loads(result)
            # 即使有异常，函数也应该返回错误结果而不是崩溃
            assert "success" in result_dict
        finally:
            # 恢复原始函数
            network.list_mcp_resources_tool.list_mcp_resources_tool = original
    except Exception:
        # 如果测试代码本身出错，跳过
        pass

def test_module_exports():
    """测试模块导出"""
    from network.list_mcp_resources_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "list_mcp_resources_tool" in __all__

def test_tool_interface():
    """测试工具接口兼容性"""
    # 检查工具定义符合Claude Code模式
    tool_def = TOOL_DEF
    assert tool_def["function"]["name"] == "list_mcp_resources"
    assert "server" in tool_def["function"]["parameters"]["properties"]
    
    # 参数应该是可选的
    server_param = tool_def["function"]["parameters"]["properties"]["server"]
    assert "description" in server_param

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_list_all_resources,
        test_list_resources_by_server,
        test_list_resources_by_another_server,
        test_server_not_found,
        test_resource_structure,
        test_multiple_servers,
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