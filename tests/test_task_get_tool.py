#!/usr/bin/env python3
"""
TaskGetTool单元测试

测试Claude Code兼容的TaskGetTool简化实现。
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.task_get_tool import task_get, TaskGetConfig
# 导入TaskCreateTool以创建测试任务
from system.task_create_tool import task_create as create_task

class TestTaskGetTool:
    """TaskGetTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_task_get_tool_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置测试存储路径（与TaskCreateTool共享）
        self.test_storage_path = os.path.join(self.test_dir, "test_tasks.json")
        
        # 清理可能存在的旧环境变量并设置新值
        self.old_env_vars = {}
        env_vars_to_set = {
            "TASK_GET_STORAGE_PATH": self.test_storage_path,
            "TASK_GET_ANALYTICS_ENABLED": "false",
            "TASK_GET_ENABLED": "true",
            "TASK_GET_INTERACTIVE": "true",
            # 同时设置TaskCreateTool的环境变量以确保兼容
            "TASK_CREATE_STORAGE_PATH": self.test_storage_path,
            "TASK_CREATE_ENABLED": "true",
            "TASK_CREATE_ANALYTICS_ENABLED": "false"
        }
        
        for key, value in env_vars_to_set.items():
            if key in os.environ:
                self.old_env_vars[key] = os.environ[key]
            os.environ[key] = value
        
        # 确保任务文件不存在
        if os.path.exists(self.test_storage_path):
            os.remove(self.test_storage_path)
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 恢复原始环境变量
        for key, value in self.old_env_vars.items():
            os.environ[key] = value
        
        # 删除我们设置的环境变量（如果不在原始变量中）
        env_vars_to_clean = [
            "TASK_GET_STORAGE_PATH",
            "TASK_GET_ANALYTICS_ENABLED",
            "TASK_GET_ENABLED",
            "TASK_GET_INTERACTIVE",
            "TASK_CREATE_STORAGE_PATH",
            "TASK_CREATE_ENABLED",
            "TASK_CREATE_ANALYTICS_ENABLED"
        ]
        
        for key in env_vars_to_clean:
            if key in os.environ and key not in self.old_env_vars:
                del os.environ[key]
    
    def test_task_get_existing_task(self):
        """测试获取现有任务"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test Task",
            description="This is a test task description."
        )
        task_id = create_result["task"]["id"]
        
        # 然后获取该任务
        get_result = task_get(taskId=task_id)
        
        # 验证返回结果
        assert "task" in get_result
        assert get_result["task"] is not None
        assert get_result["task"]["id"] == task_id
        assert get_result["task"]["subject"] == "Test Task"
        assert get_result["task"]["description"] == "This is a test task description."
        assert get_result["task"]["status"] == "todo"
        assert "blocks" in get_result["task"]
        assert "blockedBy" in get_result["task"]
    
    def test_task_get_non_existing_task(self):
        """测试获取不存在的任务"""
        result = task_get(taskId="non-existent-task-id")
        
        # 验证返回结果为null
        assert "task" in result
        assert result["task"] is None
    
    def test_task_get_task_with_metadata(self):
        """测试获取带有元数据的任务"""
        metadata = json.dumps({"priority": "high", "tags": ["urgent"]})
        
        # 创建带有元数据的任务
        create_result = create_task(
            subject="Task with metadata",
            description="Testing metadata retrieval",
            metadata=metadata
        )
        task_id = create_result["task"]["id"]
        
        # 获取任务
        get_result = task_get(taskId=task_id)
        
        # 验证返回结果
        assert "task" in get_result
        assert get_result["task"] is not None
        assert get_result["task"]["id"] == task_id
        assert get_result["task"]["subject"] == "Task with metadata"
    
    def test_task_get_task_with_active_form(self):
        """测试获取带有活动形式的任务"""
        # 创建带有活动形式的任务
        create_result = create_task(
            subject="Task with active form",
            description="Testing active form retrieval",
            activeForm="Running tests"
        )
        task_id = create_result["task"]["id"]
        
        # 获取任务
        get_result = task_get(taskId=task_id)
        
        # 验证返回结果
        assert "task" in get_result
        assert get_result["task"] is not None
        assert get_result["task"]["subject"] == "Task with active form"
    
    def test_task_get_validation_empty_task_id(self):
        """测试空任务ID验证"""
        try:
            task_get(taskId="")
            assert False, "Should have raised ValueError for empty taskId"
        except ValueError as e:
            assert "taskid" in str(e).lower() or "id" in str(e).lower()
    
    def test_task_get_validation_long_task_id(self):
        """测试长任务ID验证"""
        long_task_id = "x" * 101  # 超过100字符限制
        
        try:
            task_get(taskId=long_task_id)
            assert False, "Should have raised ValueError for long taskId"
        except ValueError as e:
            assert "taskid" in str(e).lower() or "id" in str(e).lower()
            assert "100" in str(e) or "most" in str(e).lower()
    
    def test_task_get_interactive_mode(self):
        """测试交互模式输出"""
        # 创建一个任务
        create_result = create_task(
            subject="Interactive test task",
            description="Testing interactive mode output"
        )
        task_id = create_result["task"]["id"]
        
        with patch('builtins.print') as mock_print:
            # 临时设置为交互模式（默认就是true，这里明确设置）
            os.environ["TASK_GET_INTERACTIVE"] = "true"
            
            result = task_get(taskId=task_id)
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出中包含任务信息
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "Interactive test task" in output or "Task Found" in output
            
            del os.environ["TASK_GET_INTERACTIVE"]
    
    def test_task_get_non_interactive_mode(self):
        """测试非交互模式输出"""
        # 创建一个任务
        create_result = create_task(
            subject="Non-interactive test task",
            description="Testing non-interactive mode output"
        )
        task_id = create_result["task"]["id"]
        
        with patch('builtins.print') as mock_print:
            # 临时设置为非交互模式
            os.environ["TASK_GET_INTERACTIVE"] = "false"
            
            result = task_get(taskId=task_id)
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出格式
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "[TASK_GET]" in output or "Non-interactive test task" in output
            
            del os.environ["TASK_GET_INTERACTIVE"]
    
    def test_task_get_disabled_tool(self):
        """测试禁用工具"""
        # 临时禁用工具
        os.environ["TASK_GET_ENABLED"] = "false"
        
        try:
            task_get(taskId="some-task-id")
            assert False, "Should have raised RuntimeError for disabled tool"
        except RuntimeError as e:
            assert "enabled" in str(e).lower() or "disabled" in str(e).lower()
        
        del os.environ["TASK_GET_ENABLED"]
    
    def test_task_get_multiple_tasks(self):
        """测试获取多个任务"""
        task_ids = []
        
        # 创建3个任务
        for i in range(3):
            create_result = create_task(
                subject=f"Task {i}",
                description=f"Description {i}"
            )
            task_ids.append(create_result["task"]["id"])
        
        # 分别获取每个任务
        for i, task_id in enumerate(task_ids):
            result = task_get(taskId=task_id)
            assert "task" in result
            assert result["task"] is not None
            assert result["task"]["id"] == task_id
            assert result["task"]["subject"] == f"Task {i}"
    
    def test_task_get_config_overrides(self):
        """测试配置覆盖"""
        # 设置自定义存储路径
        custom_storage = os.path.join(self.test_dir, "custom_tasks.json")
        os.environ["TASK_GET_STORAGE_PATH"] = custom_storage
        os.environ["TASK_CREATE_STORAGE_PATH"] = custom_storage  # 同时设置创建工具的路径
        
        # 在新的存储中创建任务
        create_result = create_task(
            subject="Config test task",
            description="Testing config overrides"
        )
        task_id = create_result["task"]["id"]
        
        # 验证自定义存储路径
        assert os.path.exists(custom_storage)
        
        # 获取任务
        result = task_get(taskId=task_id)
        assert "task" in result
        assert result["task"] is not None
        assert result["task"]["id"] == task_id
        
        # 清理环境变量
        del os.environ["TASK_GET_STORAGE_PATH"]
        del os.environ["TASK_CREATE_STORAGE_PATH"]
    
    def test_task_get_analytics_disabled(self):
        """测试分析禁用（默认情况）"""
        # 默认情况下分析应该是禁用的
        config = TaskGetConfig.from_env()
        assert not config["TASK_GET_ANALYTICS_ENABLED"]
        
        # 创建一个任务
        create_result = create_task(
            subject="Analytics test",
            description="Testing with analytics disabled"
        )
        task_id = create_result["task"]["id"]
        
        # 应该能够正常获取任务而不会崩溃
        result = task_get(taskId=task_id)
        assert "task" in result
    
    def test_task_get_storage_file_not_exist(self):
        """测试存储文件不存在的情况"""
        # 删除存储文件（如果存在）
        if os.path.exists(self.test_storage_path):
            os.remove(self.test_storage_path)
        
        # 尝试获取不存在的任务（应该返回null）
        result = task_get(taskId="some-non-existent-id")
        assert "task" in result
        assert result["task"] is None
    
    def test_task_get_corrupted_storage_file(self):
        """测试损坏的存储文件"""
        # 创建损坏的JSON文件
        with open(self.test_storage_path, 'w') as f:
            f.write("invalid json content")
        
        # 尝试获取任务（应该返回null并显示警告）
        with patch('builtins.print') as mock_print:
            result = task_get(taskId="some-id")
            
            # 应该显示警告
            assert mock_print.called
            # 返回null
            assert "task" in result
            assert result["task"] is None
    
    def test_task_get_task_fields_completeness(self):
        """测试任务字段完整性"""
        # 创建完整的任务
        metadata = json.dumps({
            "priority": "high",
            "estimated_time": "2 hours"
        })
        
        create_result = create_task(
            subject="Complete task",
            description="Testing all fields",
            activeForm="Processing data",
            metadata=metadata
        )
        task_id = create_result["task"]["id"]
        
        # 获取任务
        result = task_get(taskId=task_id)
        
        # 验证所有必需字段都存在
        assert "task" in result
        task = result["task"]
        assert task is not None
        assert "id" in task
        assert "subject" in task
        assert "description" in task
        assert "status" in task
        assert "blocks" in task
        assert "blockedBy" in task
        
        # 验证字段值
        assert task["id"] == task_id
        assert task["subject"] == "Complete task"
        assert task["description"] == "Testing all fields"
        assert task["status"] == "todo"
        assert task["blocks"] == []
        assert task["blockedBy"] == []
    
    def test_task_get_response_structure(self):
        """测试响应结构（与Claude Code兼容）"""
        # 创建一个任务
        create_result = create_task(
            subject="Structure test",
            description="Testing response structure"
        )
        task_id = create_result["task"]["id"]
        
        # 获取任务
        result = task_get(taskId=task_id)
        
        # 验证响应结构
        assert isinstance(result, dict)
        assert "task" in result
        
        # 任务存在时的结构
        if result["task"] is not None:
            task = result["task"]
            assert isinstance(task, dict)
            assert "id" in task and isinstance(task["id"], str)
            assert "subject" in task and isinstance(task["subject"], str)
            assert "description" in task and isinstance(task["description"], str)
            assert "status" in task and isinstance(task["status"], str)
            assert "blocks" in task and isinstance(task["blocks"], list)
            assert "blockedBy" in task and isinstance(task["blockedBy"], list)
        else:
            # 任务不存在时的结构
            assert result["task"] is None
    
    def test_task_get_with_invalid_task_id_format(self):
        """测试无效任务ID格式"""
        # 创建有效的任务
        create_result = create_task(
            subject="Valid task",
            description="For testing"
        )
        valid_task_id = create_result["task"]["id"]
        
        # 使用部分ID（短ID）应该也能工作（如果匹配）
        short_id = valid_task_id[:8]
        result = task_get(taskId=short_id)
        
        # 可能找不到（因为需要完整ID），但不应崩溃
        assert "task" in result
    
    def test_task_get_empty_storage(self):
        """测试空存储"""
        # 确保存储文件为空（新创建）
        assert not os.path.exists(self.test_storage_path) or os.path.getsize(self.test_storage_path) == 0
        
        # 尝试获取任务
        result = task_get(taskId="any-id")
        assert "task" in result
        assert result["task"] is None