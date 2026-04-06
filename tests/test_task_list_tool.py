#!/usr/bin/env python3
"""
TaskListTool单元测试

测试Claude Code兼容的TaskListTool简化实现。
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

from system.task_list_tool import task_list, TaskListConfig
# 导入TaskCreateTool以创建测试任务
from system.task_create_tool import task_create as create_task

class TestTaskListTool:
    """TaskListTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_task_list_tool_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置测试存储路径（与TaskCreateTool共享）
        self.test_storage_path = os.path.join(self.test_dir, "test_tasks.json")
        
        # 清理可能存在的旧环境变量并设置新值
        self.old_env_vars = {}
        env_vars_to_set = {
            "TASK_LIST_STORAGE_PATH": self.test_storage_path,
            "TASK_LIST_ANALYTICS_ENABLED": "false",
            "TASK_LIST_ENABLED": "true",
            "TASK_LIST_INTERACTIVE": "true",
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
            "TASK_LIST_STORAGE_PATH",
            "TASK_LIST_ANALYTICS_ENABLED",
            "TASK_LIST_ENABLED",
            "TASK_LIST_INTERACTIVE",
            "TASK_CREATE_STORAGE_PATH",
            "TASK_CREATE_ENABLED",
            "TASK_CREATE_ANALYTICS_ENABLED"
        ]
        
        for key in env_vars_to_clean:
            if key in os.environ and key not in self.old_env_vars:
                del os.environ[key]
    
    def test_task_list_empty(self):
        """测试空任务列表"""
        result = task_list()
        
        # 验证返回结果
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 0
    
    def test_task_list_single_task(self):
        """测试单个任务列表"""
        # 创建一个任务
        create_result = create_task(
            subject="Test Task",
            description="This is a test task description."
        )
        
        # 列出任务
        result = task_list()
        
        # 验证返回结果
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 1
        
        task = result["tasks"][0]
        assert "id" in task
        assert "subject" in task
        assert "status" in task
        assert "owner" in task
        assert "blockedBy" in task
        
        assert task["subject"] == "Test Task"
        assert task["status"] == "todo"
        assert task["owner"] is None
        assert task["blockedBy"] == []
    
    def test_task_list_multiple_tasks(self):
        """测试多个任务列表"""
        # 创建3个任务
        task_subjects = []
        for i in range(3):
            create_result = create_task(
                subject=f"Task {i}",
                description=f"Description {i}"
            )
            task_subjects.append(f"Task {i}")
        
        # 列出任务
        result = task_list()
        
        # 验证返回结果
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 3
        
        # 验证任务按创建时间排序（最新的在前）
        returned_subjects = [task["subject"] for task in result["tasks"]]
        # 由于按创建时间降序排序，顺序应与创建顺序相反
        assert returned_subjects == ["Task 2", "Task 1", "Task 0"]
    
    def test_task_list_with_different_statuses(self):
        """测试不同状态的任务列表"""
        # 创建不同状态的任务（通过直接修改存储文件）
        task_ids = []
        for i, status in enumerate(["todo", "in_progress", "done"]):
            create_result = create_task(
                subject=f"Task {status}",
                description=f"Description for {status} task"
            )
            task_ids.append(create_result["task"]["id"])
        
        # 直接修改存储文件以设置状态（因为TaskCreateTool只创建todo状态）
        with open(self.test_storage_path, 'r') as f:
            tasks_data = json.load(f)
        
        # 设置不同的状态
        statuses = ["todo", "in_progress", "done"]
        for i, task_id in enumerate(task_ids):
            if task_id in tasks_data["tasks"]:
                tasks_data["tasks"][task_id]["status"] = statuses[i]
        
        with open(self.test_storage_path, 'w') as f:
            json.dump(tasks_data, f, indent=2)
        
        # 列出任务
        result = task_list()
        
        # 验证返回结果包含正确的状态
        assert "tasks" in result
        assert len(result["tasks"]) == 3
        
        statuses_returned = [task["status"] for task in result["tasks"]]
        assert set(statuses_returned) == set(["todo", "in_progress", "done"])
    
    def test_task_list_interactive_mode(self):
        """测试交互模式输出"""
        # 创建2个任务
        for i in range(2):
            create_task(
                subject=f"Interactive Task {i}",
                description=f"Testing interactive mode {i}"
            )
        
        with patch('builtins.print') as mock_print:
            # 临时设置为交互模式（默认就是true，这里明确设置）
            os.environ["TASK_LIST_INTERACTIVE"] = "true"
            
            result = task_list()
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出中包含任务列表信息
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "Task List" in output or "tasks" in output
            
            del os.environ["TASK_LIST_INTERACTIVE"]
    
    def test_task_list_non_interactive_mode(self):
        """测试非交互模式输出"""
        # 创建2个任务
        for i in range(2):
            create_task(
                subject=f"Non-interactive Task {i}",
                description=f"Testing non-interactive mode {i}"
            )
        
        with patch('builtins.print') as mock_print:
            # 临时设置为非交互模式
            os.environ["TASK_LIST_INTERACTIVE"] = "false"
            
            result = task_list()
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出格式
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "[TASK_LIST]" in output or "Found" in output
            
            del os.environ["TASK_LIST_INTERACTIVE"]
    
    def test_task_list_disabled_tool(self):
        """测试禁用工具"""
        # 临时禁用工具
        os.environ["TASK_LIST_ENABLED"] = "false"
        
        try:
            task_list()
            assert False, "Should have raised RuntimeError for disabled tool"
        except RuntimeError as e:
            assert "enabled" in str(e).lower() or "disabled" in str(e).lower()
        
        del os.environ["TASK_LIST_ENABLED"]
    
    def test_task_list_max_tasks_limit(self):
        """测试任务数量限制"""
        # 设置较小的显示限制
        os.environ["TASK_LIST_MAX_TASKS"] = "3"
        
        # 创建5个任务
        for i in range(5):
            create_task(
                subject=f"Task {i}",
                description=f"Description {i}"
            )
        
        # 列出任务
        result = task_list()
        
        # 验证只返回3个任务（限制）
        assert "tasks" in result
        assert len(result["tasks"]) == 3  # 应该只返回3个，尽管有5个任务
        
        del os.environ["TASK_LIST_MAX_TASKS"]
    
    def test_task_list_config_overrides(self):
        """测试配置覆盖"""
        # 设置自定义存储路径
        custom_storage = os.path.join(self.test_dir, "custom_tasks.json")
        os.environ["TASK_LIST_STORAGE_PATH"] = custom_storage
        os.environ["TASK_CREATE_STORAGE_PATH"] = custom_storage  # 同时设置创建工具的路径
        
        # 在新的存储中创建任务
        create_task(
            subject="Config test task",
            description="Testing config overrides"
        )
        
        # 验证自定义存储路径
        assert os.path.exists(custom_storage)
        
        # 列出任务
        result = task_list()
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["subject"] == "Config test task"
        
        # 清理环境变量
        del os.environ["TASK_LIST_STORAGE_PATH"]
        del os.environ["TASK_CREATE_STORAGE_PATH"]
    
    def test_task_list_analytics_disabled(self):
        """测试分析禁用（默认情况）"""
        # 默认情况下分析应该是禁用的
        config = TaskListConfig.from_env()
        assert not config["TASK_LIST_ANALYTICS_ENABLED"]
        
        # 创建一个任务
        create_task(
            subject="Analytics test",
            description="Testing with analytics disabled"
        )
        
        # 应该能够正常列出任务而不会崩溃
        result = task_list()
        assert "tasks" in result
    
    def test_task_list_storage_file_not_exist(self):
        """测试存储文件不存在的情况"""
        # 删除存储文件（如果存在）
        if os.path.exists(self.test_storage_path):
            os.remove(self.test_storage_path)
        
        # 尝试列出任务（应该返回空列表）
        result = task_list()
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 0
    
    def test_task_list_corrupted_storage_file(self):
        """测试损坏的存储文件"""
        # 创建损坏的JSON文件
        with open(self.test_storage_path, 'w') as f:
            f.write("invalid json content")
        
        # 尝试列出任务（应该返回空列表并显示警告）
        with patch('builtins.print') as mock_print:
            result = task_list()
            
            # 应该显示警告
            assert mock_print.called
            # 返回空列表
            assert "tasks" in result
            assert isinstance(result["tasks"], list)
            assert len(result["tasks"]) == 0
    
    def test_task_list_response_structure(self):
        """测试响应结构（与Claude Code兼容）"""
        # 创建2个任务
        for i in range(2):
            create_task(
                subject=f"Structure Test {i}",
                description=f"Testing response structure {i}"
            )
        
        # 列出任务
        result = task_list()
        
        # 验证响应结构
        assert isinstance(result, dict)
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        
        # 验证每个任务的结构
        for task in result["tasks"]:
            assert isinstance(task, dict)
            assert "id" in task and isinstance(task["id"], str)
            assert "subject" in task and isinstance(task["subject"], str)
            assert "status" in task and isinstance(task["status"], str)
            assert "owner" in task  # 可能为None
            assert "blockedBy" in task and isinstance(task["blockedBy"], list)
    
    def test_task_list_empty_storage(self):
        """测试空存储"""
        # 确保存储文件为空（新创建）
        assert not os.path.exists(self.test_storage_path) or os.path.getsize(self.test_storage_path) == 0
        
        # 列出任务
        result = task_list()
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) == 0
    
    def test_task_list_large_number_of_tasks(self):
        """测试大量任务"""
        # 创建10个任务
        for i in range(10):
            create_task(
                subject=f"Large Task {i}",
                description=f"Testing large number of tasks {i}"
            )
        
        # 列出任务
        result = task_list()
        
        # 验证返回所有任务
        assert "tasks" in result
        assert len(result["tasks"]) == 10
        
        # 验证排序（最新的在前）
        subjects = [task["subject"] for task in result["tasks"]]
        expected_subjects = [f"Large Task {i}" for i in range(9, -1, -1)]  # 从9到0
        assert subjects == expected_subjects
    
    def test_task_list_with_metadata_tasks(self):
        """测试带有元数据的任务列表"""
        # 创建带有元数据的任务
        metadata = json.dumps({"priority": "high", "category": "test"})
        
        create_task(
            subject="Task with metadata",
            description="Testing metadata in task list",
            metadata=metadata
        )
        
        # 列出任务
        result = task_list()
        
        # 验证任务被正确列出（不检查元数据，因为响应中不包含）
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["subject"] == "Task with metadata"
    
    def test_task_list_dummy_parameter(self):
        """测试虚拟参数处理"""
        # 创建任务
        create_task(
            subject="Dummy param test",
            description="Testing dummy parameter handling"
        )
        
        # 使用虚拟参数调用
        result = task_list(_dummy="ignored_value")
        
        # 验证正常返回
        assert "tasks" in result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["subject"] == "Dummy param test"