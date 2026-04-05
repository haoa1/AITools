#!/usr/bin/env python3
"""
SnipTool 测试
"""

import json
import sys
import os
import tempfile
import shutil

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.snip_tool import snip_tool, TOOL_DEF, TOOL_CALL_MAP

def test_tool_definitions():
    """测试工具定义是否正确"""
    assert TOOL_DEF["type"] == "function"
    assert TOOL_DEF["function"]["name"] == "snip"
    assert "parameters" in TOOL_DEF["function"]
    
    params = TOOL_DEF["function"]["parameters"]["properties"]
    assert "action" in params
    assert "name" in params
    assert "description" in params
    assert "include_files" in params
    assert "metadata" in params
    
    # 检查TOOL_CALL_MAP
    assert "snip" in TOOL_CALL_MAP
    assert TOOL_CALL_MAP["snip"] == snip_tool

def test_list_snapshots():
    """测试列出快照"""
    result = snip_tool(action="list")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["action"] == "list"
    assert "snapshots" in result_dict
    assert "count" in result_dict
    assert "timestamp" in result_dict
    assert "durationMs" in result_dict

def test_save_snapshot():
    """测试保存快照"""
    result = snip_tool(
        action="save",
        name="test_snapshot_1",
        description="Test snapshot description"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["action"] == "save"
    assert "snapshot" in result_dict
    assert result_dict["snapshot"]["name"] == "test_snapshot_1"
    assert "id" in result_dict["snapshot"]
    assert "created" in result_dict["snapshot"]
    assert "note" in result_dict

def test_save_snapshot_with_files():
    """测试保存带文件的快照"""
    # 创建一个测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        test_file = f.name
    
    try:
        result = snip_tool(
            action="save",
            name="test_snapshot_with_files",
            description="Snapshot with files",
            include_files=[test_file, "*.txt"]
        )
        
        result_dict = json.loads(result)
        assert result_dict["success"] == True
        assert result_dict["action"] == "save"
        assert "snapshot" in result_dict
        assert "files_count" in result_dict["snapshot"]
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_save_snapshot_no_name():
    """测试保存快照但没有名称"""
    result = snip_tool(action="save")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == False
    assert "error" in result_dict
    assert "Snapshot name is required" in result_dict["error"]

def test_load_snapshot():
    """测试加载快照"""
    # 先保存一个快照
    save_result = snip_tool(
        action="save",
        name="test_load_snapshot",
        description="Snapshot to load"
    )
    save_dict = json.loads(save_result)
    
    # 然后加载它
    result = snip_tool(
        action="load",
        name="test_load_snapshot"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert result_dict["action"] == "load"
    assert "snapshot" in result_dict
    assert "note" in result_dict

def test_load_nonexistent_snapshot():
    """测试加载不存在的快照"""
    result = snip_tool(
        action="load",
        name="nonexistent_snapshot_xyz123"
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == False
    assert "error" in result_dict
    assert "not found" in result_dict["error"].lower()

def test_duplicate_snapshot_name():
    """测试重复的快照名称"""
    # 第一次保存
    result1 = snip_tool(
        action="save",
        name="duplicate_test",
        description="First snapshot"
    )
    result1_dict = json.loads(result1)
    assert result1_dict["success"] == True
    
    # 第二次保存相同名称
    result2 = snip_tool(
        action="save",
        name="duplicate_test",
        description="Second snapshot"
    )
    result2_dict = json.loads(result2)
    assert result2_dict["success"] == False
    assert "already exists" in result2_dict["error"]

def test_snapshot_with_metadata():
    """测试带元数据的快照"""
    metadata = {
        "project": "test_project",
        "version": "1.0",
        "tags": ["test", "snapshot"]
    }
    
    result = snip_tool(
        action="save",
        name="test_with_metadata",
        description="Snapshot with metadata",
        metadata=metadata
    )
    
    result_dict = json.loads(result)
    assert result_dict["success"] == True
    assert "snapshot" in result_dict

def test_invalid_action():
    """测试无效的操作"""
    result = snip_tool(action="invalid_action")
    
    result_dict = json.loads(result)
    assert result_dict["success"] == False
    assert "error" in result_dict
    assert "Unknown action" in result_dict["error"]

def test_module_exports():
    """测试模块导出"""
    from system.snip_tool import __all__
    assert "tools" in __all__
    assert "TOOL_CALL_MAP" in __all__
    assert "snip_tool" in __all__

def test_tool_interface():
    """测试工具接口兼容性"""
    # 检查工具定义符合Claude Code模式
    tool_def = TOOL_DEF
    assert tool_def["function"]["name"] == "snip"
    
    # 检查参数约束
    action_param = tool_def["function"]["parameters"]["properties"]["action"]
    assert "enum" in action_param
    assert set(action_param["enum"]) == {"save", "load", "list"}

def test_snapshot_directory_creation():
    """测试快照目录创建"""
    # 测试快照存储目录是否会被创建
    snapshots_dir = os.path.expanduser("~/.aitools/snapshots")
    
    # 先删除目录（如果存在）
    if os.path.exists(snapshots_dir):
        shutil.rmtree(snapshots_dir)
    
    # 执行列出操作（应该创建目录）
    result = snip_tool(action="list")
    result_dict = json.loads(result)
    
    assert result_dict["success"] == True
    # 目录应该已被创建
    assert os.path.exists(snapshots_dir)

if __name__ == "__main__":
    # 运行所有测试
    test_functions = [
        test_tool_definitions,
        test_list_snapshots,
        test_save_snapshot,
        test_save_snapshot_with_files,
        test_save_snapshot_no_name,
        test_load_snapshot,
        test_load_nonexistent_snapshot,
        test_duplicate_snapshot_name,
        test_snapshot_with_metadata,
        test_invalid_action,
        test_module_exports,
        test_tool_interface,
        test_snapshot_directory_creation
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