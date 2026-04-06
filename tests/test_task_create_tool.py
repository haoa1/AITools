#!/usr/bin/env python3
"""
TaskCreateTool单元测试

测试Claude Code兼容的TaskCreateTool简化实现。
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

from system.task_create_tool import task_create, TaskCreateConfig

class TestTaskCreateTool:
    """TaskCreateTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_task_create_tool_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 保存原始存储路径并设置测试路径
        self.test_storage_path = os.path.join(self.test_dir, "test_tasks.json")
        
        # 清理可能存在的旧环境变量
        self.old_env_vars = {}
        env_vars_to_set = {
            "TASK_CREATE_STORAGE_PATH": self.test_storage_path,
            "TASK_CREATE_ANALYTICS_ENABLED": "false",
            "TASK_CREATE_ENABLED": "true",  # 确保启用
            "TASK_CREATE_INTERACTIVE": "true",  # 默认交互模式
            "TASK_CREATE_DEFAULT_STATUS": "todo",
            "TASK_CREATE_MAX_TASKS": "1000"
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
            "TASK_CREATE_STORAGE_PATH",
            "TASK_CREATE_ANALYTICS_ENABLED",
            "TASK_CREATE_ENABLED",
            "TASK_CREATE_INTERACTIVE",
            "TASK_CREATE_DEFAULT_STATUS",
            "TASK_CREATE_MAX_TASKS"
        ]
        
        for key in env_vars_to_clean:
            if key in os.environ and key not in self.old_env_vars:
                del os.environ[key]
    
    def test_task_create_basic(self):
        """测试基本任务创建"""
        result = task_create(
            subject="Test Task",
            description="This is a test task description."
        )
        
        # 验证返回结果
        assert "task" in result
        assert "id" in result["task"]
        assert "subject" in result["task"]
        assert result["task"]["subject"] == "Test Task"
        
        # 验证任务文件已创建
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        assert os.path.exists(storage_path)
        
        # 验证文件内容
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        assert "tasks" in tasks_data
        assert result["task"]["id"] in tasks_data["tasks"]
        
        task = tasks_data["tasks"][result["task"]["id"]]
        assert task["subject"] == "Test Task"
        assert task["description"] == "This is a test task description."
        assert task["status"] == "todo"  # 默认状态
    
    def test_task_create_with_active_form(self):
        """测试带有active_form的任务创建"""
        result = task_create(
            subject="Task with active form",
            description="Testing active form functionality",
            activeForm="Running tests"
        )
        
        # 验证返回结果
        assert "task" in result
        assert result["task"]["subject"] == "Task with active form"
        
        # 验证任务文件中包含active_form
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result["task"]["id"]]
        assert task["active_form"] == "Running tests"
    
    def test_task_create_with_metadata(self):
        """测试带有metadata的任务创建"""
        metadata = json.dumps({
            "priority": "high",
            "tags": ["urgent", "backend"],
            "estimated_hours": 2
        })
        
        result = task_create(
            subject="Task with metadata",
            description="Testing metadata functionality",
            metadata=metadata
        )
        
        # 验证返回结果
        assert "task" in result
        
        # 验证任务文件中包含metadata
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result["task"]["id"]]
        assert "metadata" in task
        assert task["metadata"]["priority"] == "high"
        assert "urgent" in task["metadata"]["tags"]
        assert task["metadata"]["estimated_hours"] == 2
    
    def test_task_create_with_all_parameters(self):
        """测试所有参数的任务创建"""
        metadata = json.dumps({"priority": "medium"})
        
        result = task_create(
            subject="Complete task",
            description="Testing all parameters together",
            activeForm="Processing data",
            metadata=metadata
        )
        
        # 验证返回结果
        assert "task" in result
        assert result["task"]["subject"] == "Complete task"
        
        # 验证任务文件包含所有字段
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result["task"]["id"]]
        assert task["subject"] == "Complete task"
        assert task["description"] == "Testing all parameters together"
        assert task["active_form"] == "Processing data"
        assert task["metadata"]["priority"] == "medium"
        assert task["status"] == "todo"
    
    def test_task_create_validation_empty_subject(self):
        """测试空主题验证"""
        try:
            task_create(
                subject="",
                description="This should fail"
            )
            assert False, "Should have raised ValueError for empty subject"
        except ValueError as e:
            assert "subject" in str(e).lower()
    
    def test_task_create_validation_empty_description(self):
        """测试空描述验证"""
        try:
            task_create(
                subject="Valid subject",
                description=""
            )
            assert False, "Should have raised ValueError for empty description"
        except ValueError as e:
            assert "description" in str(e).lower()
    
    def test_task_create_validation_long_subject(self):
        """测试长主题验证"""
        long_subject = "x" * 201  # 超过200字符限制
        
        try:
            task_create(
                subject=long_subject,
                description="Valid description"
            )
            assert False, "Should have raised ValueError for long subject"
        except ValueError as e:
            assert "subject" in str(e).lower()
            assert "200" in str(e) or "most" in str(e).lower()
    
    def test_task_create_validation_long_description(self):
        """测试长描述验证"""
        long_description = "x" * 5001  # 超过5000字符限制
        
        try:
            task_create(
                subject="Valid subject",
                description=long_description
            )
            assert False, "Should have raised ValueError for long description"
        except ValueError as e:
            assert "description" in str(e).lower()
            assert "5000" in str(e) or "most" in str(e).lower()
    
    def test_task_create_validation_invalid_metadata_json(self):
        """测试无效metadata JSON验证"""
        invalid_metadata = "not a valid json"
        
        try:
            task_create(
                subject="Valid subject",
                description="Valid description",
                metadata=invalid_metadata
            )
            assert False, "Should have raised ValueError for invalid JSON"
        except ValueError as e:
            assert "json" in str(e).lower() or "metadata" in str(e).lower()
    
    def test_task_create_validation_metadata_not_object(self):
        """测试metadata不是对象的验证"""
        invalid_metadata = json.dumps(["list", "not", "object"])
        
        try:
            task_create(
                subject="Valid subject",
                description="Valid description",
                metadata=invalid_metadata
            )
            assert False, "Should have raised ValueError for non-object metadata"
        except ValueError as e:
            assert "object" in str(e).lower() or "metadata" in str(e).lower()
    
    def test_task_create_max_tasks_limit(self):
        """测试任务数量限制"""
        # 设置较小的任务限制以便测试
        os.environ["TASK_CREATE_MAX_TASKS"] = "5"
        
        # 首先创建4个任务（最大限制-1）
        for i in range(4):
            task_create(
                subject=f"Task {i}",
                description=f"Description {i}"
            )
        
        # 第5个任务应该成功（达到限制）
        result = task_create(
            subject="Last allowed task",
            description="This should succeed"
        )
        assert "task" in result
        
        # 第6个任务应该失败（超过限制）
        try:
            task_create(
                subject="One too many",
                description="This should fail"
            )
            assert False, "Should have raised RuntimeError for task limit"
        except RuntimeError as e:
            assert "limit" in str(e).lower() or "maximum" in str(e).lower()
        
        # 恢复原始限制
        del os.environ["TASK_CREATE_MAX_TASKS"]
    
    def test_task_create_interactive_mode(self):
        """测试交互模式输出"""
        with patch('builtins.print') as mock_print:
            # 临时设置为交互模式
            os.environ["TASK_CREATE_INTERACTIVE"] = "true"
            
            result = task_create(
                subject="Interactive task",
                description="Testing interactive mode"
            )
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出中包含任务信息
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "Interactive task" in output or "Task Created" in output
            
            del os.environ["TASK_CREATE_INTERACTIVE"]
    
    def test_task_create_non_interactive_mode(self):
        """测试非交互模式输出"""
        with patch('builtins.print') as mock_print:
            # 临时设置为非交互模式
            os.environ["TASK_CREATE_INTERACTIVE"] = "false"
            
            result = task_create(
                subject="Non-interactive task",
                description="Testing non-interactive mode"
            )
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出格式
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "[TASK_CREATE]" in output or "Non-interactive task" in output
            
            del os.environ["TASK_CREATE_INTERACTIVE"]
    
    def test_task_create_disabled_tool(self):
        """测试禁用工具"""
        # 临时禁用工具
        os.environ["TASK_CREATE_ENABLED"] = "false"
        
        try:
            task_create(
                subject="Should fail",
                description="Tool is disabled"
            )
            assert False, "Should have raised RuntimeError for disabled tool"
        except RuntimeError as e:
            assert "enabled" in str(e).lower() or "disabled" in str(e).lower()
        
        del os.environ["TASK_CREATE_ENABLED"]
    
    def test_task_create_multiple_tasks(self):
        """测试创建多个任务"""
        task_ids = set()
        
        for i in range(5):
            result = task_create(
                subject=f"Task {i}",
                description=f"Description {i}"
            )
            task_id = result["task"]["id"]
            task_ids.add(task_id)
        
        # 验证所有任务ID都是唯一的
        assert len(task_ids) == 5
        
        # 验证文件中的所有任务
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        assert len(tasks_data["tasks"]) == 5
        for task_id in task_ids:
            assert task_id in tasks_data["tasks"]
    
    def test_task_create_timestamp_fields(self):
        """测试任务时间戳字段"""
        result = task_create(
            subject="Timestamp test",
            description="Testing timestamps"
        )
        
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result["task"]["id"]]
        
        # 验证时间戳字段存在且格式正确
        assert "created_at" in task
        assert "updated_at" in task
        assert "T" in task["created_at"]  # ISO格式包含'T'
        assert "T" in task["updated_at"]
        
        # 验证文件级别时间戳
        assert "created_at" in tasks_data
        assert "updated_at" in tasks_data
    
    def test_task_create_config_overrides(self):
        """测试配置覆盖"""
        # 设置自定义配置
        custom_storage = os.path.join(self.test_dir, "custom_tasks.json")
        os.environ["TASK_CREATE_STORAGE_PATH"] = custom_storage
        os.environ["TASK_CREATE_DEFAULT_STATUS"] = "in_progress"
        
        result = task_create(
            subject="Config test",
            description="Testing config overrides"
        )
        
        # 验证自定义存储路径
        assert os.path.exists(custom_storage)
        
        # 验证自定义状态
        with open(custom_storage, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result["task"]["id"]]
        assert task["status"] == "in_progress"
        
        # 清理环境变量
        del os.environ["TASK_CREATE_STORAGE_PATH"]
        del os.environ["TASK_CREATE_DEFAULT_STATUS"]
    
    def test_task_create_analytics_disabled(self):
        """测试分析禁用（默认情况）"""
        # 默认情况下分析应该是禁用的
        config = TaskCreateConfig.from_env()
        assert not config["TASK_CREATE_ANALYTICS_ENABLED"]
        
        # 应该能够正常创建任务而不会崩溃
        result = task_create(
            subject="Analytics test",
            description="Testing with analytics disabled"
        )
        assert "task" in result
    
    def test_task_create_metadata_edge_cases(self):
        """测试metadata边界情况"""
        # 空对象
        result1 = task_create(
            subject="Empty metadata",
            description="Testing empty metadata object",
            metadata=json.dumps({})
        )
        assert "task" in result1
        
        # 复杂嵌套对象
        complex_metadata = json.dumps({
            "nested": {
                "deep": {
                    "value": 42
                }
            },
            "array": [1, 2, 3],
            "null_value": None,
            "boolean": True,
            "number": 123.45
        })
        
        result2 = task_create(
            subject="Complex metadata",
            description="Testing complex nested metadata",
            metadata=complex_metadata
        )
        assert "task" in result2
        
        # 验证复杂metadata被正确存储
        config = TaskCreateConfig.from_env()
        storage_path = config["TASK_CREATE_STORAGE_PATH"]
        
        with open(storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        task = tasks_data["tasks"][result2["task"]["id"]]
        assert "metadata" in task
        assert task["metadata"]["nested"]["deep"]["value"] == 42
        assert task["metadata"]["array"] == [1, 2, 3]
        assert task["metadata"]["null_value"] is None
        assert task["metadata"]["boolean"] is True
        assert task["metadata"]["number"] == 123.45