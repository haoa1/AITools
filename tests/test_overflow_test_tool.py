#!/usr/bin/env python3
"""
OverflowTestTool 测试
"""

import json
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.overflow_test_tool import overflow_test_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "overflow_test"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "size_kb" in params
    assert "test_type" in params
    assert "include_metadata" in params
    
    # 检查TOOL_CALL_MAP
    assert "overflow_test" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["overflow_test"] == overflow_test_tool

def test_default_parameters():
    """测试默认参数"""
    result = overflow_test_tool()
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "testType" in result_dict
    assert "requestedSizeKB" in result_dict
    assert "actualSizeKB" in result_dict
    assert "dataSizeBytes" in result_dict
    assert "testDataPreview" in result_dict
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict

def test_text_test_type():
    """测试文本类型测试"""
    result = overflow_test_tool(
        size_kb=5,
        test_type="text",
        include_metadata=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["testType"] == "text"
    assert result_dict["requestedSizeKB"] == 5
    assert "metadata" in result_dict

def test_json_test_type():
    """测试JSON类型测试"""
    result = overflow_test_tool(
        size_kb=3,
        test_type="json",
        include_metadata=False
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["testType"] == "json"
    assert result_dict["requestedSizeKB"] == 3
    assert "metadata" not in result_dict  # 应该没有元数据

def test_mixed_test_type():
    """测试混合类型测试"""
    result = overflow_test_tool(
        size_kb=2,
        test_type="mixed",
        include_metadata=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["testType"] == "mixed"
    assert result_dict["requestedSizeKB"] == 2
    assert "metadata" in result_dict

def test_large_size():
    """测试大尺寸数据"""
    result = overflow_test_tool(
        size_kb=80,  # 较大但不超过限制
        test_type="text",
        include_metadata=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["requestedSizeKB"] == 80
    # 可能包含警告
    if "warning" in result_dict:
        assert "Large test data" in result_dict["warning"]

def test_size_limiting():
    """测试尺寸限制"""
    # 测试超过最大限制的尺寸
    result = overflow_test_tool(
        size_kb=200,  # 超过100KB限制
        test_type="text",
        include_metadata=False
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    # 应该被限制到100KB
    assert result_dict["requestedSizeKB"] == 200  # 请求的尺寸
    # 实际尺寸应该被限制
    assert result_dict["actualSizeKB"] <= 100  # 实际应该<=100KB

def test_data_preview():
    """测试数据预览"""
    result = overflow_test_tool(
        size_kb=1,
        test_type="text",
        include_metadata=False
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "testDataPreview" in result_dict
    preview = result_dict["testDataPreview"]
    assert isinstance(preview, str)
    # 预览应该被截断（如果数据很大）
    if len(preview) > 503:  # 500个字符 + "..."
        assert preview.endswith("...")

def test_error_handling():
    """测试错误处理"""
    # 测试无效参数
    try:
        # 函数应该处理无效参数
        result = overflow_test_tool(
            size_kb=-1,  # 无效尺寸
            test_type="invalid_type",  # 无效类型
            include_metadata=True
        )
        result_dict = json.loads(result)
        # 应该仍然返回结果（可能使用默认值）
        assert "success" in result_dict
    except Exception:
        # 函数不应该崩溃
        assert False, "Function should handle invalid parameters gracefully"

def test_module_exports():
    """测试模块导出"""
    from system.overflow_test_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "overflow_test_tool" in __all__

def test_tool_interface():
    """测试工具接口兼容性"""
    # 检查工具定义符合Claude Code模式
    tool_def = TOOL_DEF
    assert tool_def["function"]["name"] == "overflow_test"
    
    # 检查参数约束
    size_param = tool_def["function"]["parameters"]["properties"]["size_kb"]
    assert "minimum" in size_param
    assert "maximum" in size_param
    
    type_param = tool_def["function"]["parameters"]["properties"]["test_type"]
    assert "enum" in type_param

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_default_parameters,
        test_text_test_type,
        test_json_test_type,
        test_mixed_test_type,
        test_large_size,
        test_size_limiting,
        test_data_preview,
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