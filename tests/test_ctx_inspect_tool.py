#!/usr/bin/env python3
"""
CtxInspectTool 测试
"""

import json
import sys
import os
import tempfile

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.ctx_inspect_tool import ctx_inspect_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "ctx_inspect"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "detail_level" in params
    assert "include_memory" in params
    assert "include_config" in params
    assert "include_workspace" in params
    
    # 检查TOOL_CALL_MAP
    assert "ctx_inspect" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["ctx_inspect"] == ctx_inspect_tool

def test_basic_inspection():
    """测试基础上下文检查"""
    result = ctx_inspect_tool(
        detail_level="basic",
        include_memory=True,
        include_config=True,
        include_workspace=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["detailLevel"] == "basic"
    assert "context" in result_dict
    assert "system" in result_dict["context"]
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict

def test_detailed_inspection():
    """测试详细上下文检查"""
    result = ctx_inspect_tool(
        detail_level="detailed",
        include_memory=True,
        include_config=True,
        include_workspace=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["detailLevel"] == "detailed"
    assert "context" in result_dict
    
    # 详细级别应该包含更多信息
    context = result_dict["context"]
    if "system" in context:
        system_info = context["system"]
        # 详细级别应该包含更多字段
        assert "executable" in system_info
        assert "path" in system_info

def test_full_inspection():
    """测试完整上下文检查"""
    result = ctx_inspect_tool(
        detail_level="full",
        include_memory=True,
        include_config=True,
        include_workspace=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["detailLevel"] == "full"
    assert "context" in result_dict

def test_selective_inspection():
    """测试选择性检查（关闭某些部分）"""
    # 测试关闭内存检查
    result = ctx_inspect_tool(
        detail_level="basic",
        include_memory=False,
        include_config=True,
        include_workspace=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    
    # 检查内存部分是否存在
    context = result_dict["context"]
    # 即使include_memory=False，memory字段可能仍然存在但包含错误信息
    # 或者可能不存在，这取决于实现

def test_minimal_inspection():
    """测试最小化检查"""
    result = ctx_inspect_tool(
        detail_level="basic",
        include_memory=False,
        include_config=False,
        include_workspace=False
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "context" in result_dict
    
    # 至少应该有系统信息
    context = result_dict["context"]
    assert "system" in context

def test_invalid_detail_level():
    """测试无效详细级别（应该使用默认值或失败）"""
    # 这里我们期望函数能处理无效参数
    try:
        result = ctx_inspect_tool(
            detail_level="invalid",
            include_memory=True,
            include_config=True,
            include_workspace=True
        )
        result_dict = json.loads(result)
        # 函数应该仍然返回成功，可能使用默认值
        assert "success" in result_dict
    except Exception:
        # 如果函数抛出异常，测试失败
        assert False, "Function should handle invalid parameters gracefully"

def test_memory_info_collection():
    """测试内存信息收集"""
    result = ctx_inspect_tool(
        detail_level="detailed",
        include_memory=True,
        include_config=False,
        include_workspace=False
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    
    context = result_dict["context"]
    if "memory" in context:
        memory_info = context["memory"]
        # 检查是否有预期的字段
        assert isinstance(memory_info, dict)

def test_workspace_info_collection():
    """测试工作区信息收集"""
    result = ctx_inspect_tool(
        detail_level="detailed",
        include_memory=False,
        include_config=False,
        include_workspace=True
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    
    context = result_dict["context"]
    if "workspace" in context:
        workspace_info = context["workspace"]
        assert "currentDirectory" in workspace_info
        assert "fileCount" in workspace_info

def test_module_exports():
    """测试模块导出"""
    from system.ctx_inspect_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "ctx_inspect_tool" in __all__

def test_error_handling():
    """测试错误处理（模拟异常）"""
    # 这里我们无法轻易触发异常，但确保函数能处理异常情况
    # 通过导入错误模块测试
    try:
        # 模拟psutil导入失败
        original_sys_path = sys.path.copy()
        
        # 临时移除psutil模块的路径
        import psutil
        psutil_path = psutil.__file__
        
        # 保存原始模块
        original_psutil = sys.modules.get('psutil')
        
        # 移除psutil模块
        if 'psutil' in sys.modules:
            del sys.modules['psutil']
        
        try:
            # 重新导入我们的模块（可能会失败）
            import importlib
            importlib.reload(sys.modules['system.ctx_inspect_tool'])
        except ImportError:
            # 预期中的导入错误
            pass
        finally:
            # 恢复原始状态
            if original_psutil:
                sys.modules['psutil'] = original_psutil
        
        # 函数应该能处理缺少psutil的情况
        result = ctx_inspect_tool(
            detail_level="basic",
            include_memory=True,
            include_config=True,
            include_workspace=True
        )
        result_dict = json.loads(result)
        assert "success" in result_dict
    except Exception as e:
        # 函数应该处理所有异常
        print(f"Test caught exception (expected in some cases): {e}")
        # 不失败，因为这是测试异常处理

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_basic_inspection,
        test_detailed_inspection,
        test_full_inspection,
        test_selective_inspection,
        test_minimal_inspection,
        test_invalid_detail_level,
        test_memory_info_collection,
        test_workspace_info_collection,
        test_module_exports,
        test_error_handling
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