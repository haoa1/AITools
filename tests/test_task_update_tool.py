#!/usr/bin/env python3
"""
TaskUpdateTool单元测试

测试Claude Code兼容的TaskUpdateTool简化实现。
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

from system.task_update_tool import task_update, TaskUpdateConfig
# 导入TaskCreateTool以创建测试任务
from system.task_create_tool import task_create as create_task

class TestTaskUpdateTool:
    """TaskUpdateTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_task_update_tool_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置测试存储路径（与其他任务工具共享）
        self.test_storage_path = os.path.join(self.test_dir, "test_tasks.json")
        
        # 清理可能存在的旧环境变量并设置新值
        self.old_env_vars = {}
        env_vars_to_set = {
            "TASK_UPDATE_STORAGE_PATH": self.test_storage_path,
            "TASK_UPDATE_ANALYTICS_ENABLED": "false",
            "TASK_UPDATE_ENABLED": "true",
            "TASK_UPDATE_INTERACTIVE": "true",
            "TASK_UPDATE_ALLOW_DELETE": "true",
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
            "TASK_UPDATE_STORAGE_PATH",
            "TASK_UPDATE_ANALYTICS_ENABLED",
            "TASK_UPDATE_ENABLED",
            "TASK_UPDATE_INTERACTIVE",
            "TASK_UPDATE_ALLOW_DELETE",
            "TASK_CREATE_STORAGE_PATH",
            "TASK_CREATE_ENABLED",
            "TASK_CREATE_ANALYTICS_ENABLED"
        ]
        
        for key in env_vars_to_clean:
            if key in os.environ and key not in self.old_env_vars:
                del os.environ[key]
    
    def test_task_update_subject(self):
        """测试更新任务主题"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Original subject",
            description="Original description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新主题
        update_result = task_update(
            taskId=task_id,
            subject="Updated subject"
        )
        
        # 验证返回结果
        assert "success" in update_result
        assert update_result["success"] is True
        assert "taskId" in update_result
        assert update_result["taskId"] == task_id
        assert "updatedFields" in update_result
        assert "subject" in update_result["updatedFields"]
        assert "error" not in update_result
    
    def test_task_update_description(self):
        """测试更新任务描述"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test task",
            description="Original description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新描述
        update_result = task_update(
            taskId=task_id,
            description="Updated description"
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        assert "description" in update_result["updatedFields"]
    
    def test_task_update_active_form(self):
        """测试更新活动形式"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新活动形式
        update_result = task_update(
            taskId=task_id,
            activeForm="Running tests"
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        assert "activeForm" in update_result["updatedFields"]
    
    def test_task_update_remove_active_form(self):
        """测试移除活动形式"""
        # 首先创建一个带有活动形式的任务
        create_result = create_task(
            subject="Test task",
            description="Test description",
            activeForm="Original active form"
        )
        task_id = create_result["task"]["id"]
        
        # 移除活动形式（设置为空字符串）
        update_result = task_update(
            taskId=task_id,
            activeForm=""
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        assert "activeForm" in update_result["updatedFields"]
    
    def test_task_update_status(self):
        """测试更新任务状态"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新状态
        update_result = task_update(
            taskId=task_id,
            status="in_progress"
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        assert "status" in update_result["updatedFields"]
        assert "statusChange" in update_result
        assert update_result["statusChange"]["from"] == "todo"
        assert update_result["statusChange"]["to"] == "in_progress"
    
    def test_task_update_multiple_fields(self):
        """测试更新多个字段"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Original subject",
            description="Original description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新多个字段
        update_result = task_update(
            taskId=task_id,
            subject="Updated subject",
            description="Updated description",
            status="done"
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        updated_fields = update_result["updatedFields"]
        assert "subject" in updated_fields
        assert "description" in updated_fields
        assert "status" in updated_fields
        assert len(updated_fields) == 3
    
    def test_task_update_no_changes(self):
        """测试无变化的更新"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        # 使用相同值更新（应该没有变化）
        update_result = task_update(
            taskId=task_id,
            subject="Test task",  # 相同值
            description="Test description"  # 相同值
        )
        
        # 验证返回结果（应该成功但无更新字段或只有"no changes"）
        assert "success" in update_result
        # 可能返回False或True但updated_fields包含"no changes"
    
    def test_task_update_delete(self):
        """测试删除任务"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Task to delete",
            description="This task will be deleted"
        )
        task_id = create_result["task"]["id"]
        
        # 删除任务
        update_result = task_update(
            taskId=task_id,
            status="deleted"
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        assert "deleted" in update_result["updatedFields"]
    
    def test_task_update_with_metadata(self):
        """测试更新元数据"""
        # 首先创建一个任务
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        # 更新元数据
        metadata = json.dumps({
            "priority": "high",
            "tags": ["urgent", "backend"]
        })
        
        update_result = task_update(
            taskId=task_id,
            metadata=metadata
        )
        
        # 验证返回结果
        assert update_result["success"] is True
        # 检查元数据字段是否在更新字段中
        updated_fields = update_result["updatedFields"]
        # 元数据字段可能以"metadata.priority"等形式出现
        metadata_updates = [f for f in updated_fields if f.startswith("metadata.")]
        assert len(metadata_updates) > 0
    
    def test_task_update_modify_metadata(self):
        """测试修改现有元数据"""
        # 首先创建一个带有元数据的任务
        initial_metadata = json.dumps({"priority": "low", "category": "test"})
        create_result = create_task(
            subject="Test task",
            description="Test description",
            metadata=initial_metadata
        )
        task_id = create_result["task"]["id"]
        
        # 修改元数据
        updated_metadata = json.dumps({
            "priority": "high",  # 更新
            "category": "test",  # 不变
            "new_field": "value"  # 新增
        })
        
        update_result = task_update(
            taskId=task_id,
            metadata=updated_metadata
        )
        
        # 验证返回结果
        assert update_result["success"] is True
    
    def test_task_update_remove_metadata_key(self):
        """测试移除元数据键（设置为null）"""
        # 首先创建一个带有元数据的任务
        initial_metadata = json.dumps({"priority": "high", "category": "test"})
        create_result = create_task(
            subject="Test task",
            description="Test description",
            metadata=initial_metadata
        )
        task_id = create_result["task"]["id"]
        
        # 移除一个元数据键（设置为null）
        metadata_to_remove = json.dumps({"priority": None, "category": "test"})
        
        update_result = task_update(
            taskId=task_id,
            metadata=metadata_to_remove
        )
        
        # 验证返回结果
        assert update_result["success"] is True
    
    def test_task_update_validation_empty_task_id(self):
        """测试空任务ID验证"""
        try:
            task_update(taskId="")
            assert False, "Should have raised ValueError for empty taskId"
        except ValueError as e:
            assert "taskid" in str(e).lower() or "id" in str(e).lower()
    
    def test_task_update_validation_long_task_id(self):
        """测试长任务ID验证"""
        long_task_id = "x" * 101  # 超过100字符限制
        
        try:
            task_update(taskId=long_task_id)
            assert False, "Should have raised ValueError for long taskId"
        except ValueError as e:
            assert "taskid" in str(e).lower() or "id" in str(e).lower()
            assert "100" in str(e) or "most" in str(e).lower()
    
    def test_task_update_validation_long_subject(self):
        """测试长主题验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        long_subject = "x" * 201  # 超过200字符限制
        
        try:
            task_update(taskId=task_id, subject=long_subject)
            assert False, "Should have raised ValueError for long subject"
        except ValueError as e:
            assert "subject" in str(e).lower()
            assert "200" in str(e) or "most" in str(e).lower()
    
    def test_task_update_validation_long_description(self):
        """测试长描述验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        long_description = "x" * 5001  # 超过5000字符限制
        
        try:
            task_update(taskId=task_id, description=long_description)
            assert False, "Should have raised ValueError for long description"
        except ValueError as e:
            assert "description" in str(e).lower()
            assert "5000" in str(e) or "most" in str(e).lower()
    
    def test_task_update_validation_long_active_form(self):
        """测试长活动形式验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        long_active_form = "x" * 101  # 超过100字符限制
        
        try:
            task_update(taskId=task_id, activeForm=long_active_form)
            assert False, "Should have raised ValueError for long activeForm"
        except ValueError as e:
            assert "activeform" in str(e).lower() or "active" in str(e).lower()
            assert "100" in str(e) or "most" in str(e).lower()
    
    def test_task_update_validation_invalid_status(self):
        """测试无效状态验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        try:
            task_update(taskId=task_id, status="invalid_status")
            assert False, "Should have raised ValueError for invalid status"
        except ValueError as e:
            assert "status" in str(e).lower()
            assert "todo" in str(e) or "in_progress" in str(e) or "done" in str(e) or "deleted" in str(e)
    
    def test_task_update_validation_invalid_metadata_json(self):
        """测试无效metadata JSON验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        invalid_metadata = "not a valid json"
        
        try:
            task_update(taskId=task_id, metadata=invalid_metadata)
            assert False, "Should have raised ValueError for invalid JSON"
        except ValueError as e:
            assert "json" in str(e).lower() or "metadata" in str(e).lower()
    
    def test_task_update_validation_metadata_not_object(self):
        """测试metadata不是对象的验证"""
        create_result = create_task(
            subject="Test task",
            description="Test description"
        )
        task_id = create_result["task"]["id"]
        
        invalid_metadata = json.dumps(["list", "not", "object"])
        
        try:
            task_update(taskId=task_id, metadata=invalid_metadata)
            assert False, "Should have raised ValueError for non-object metadata"
        except ValueError as e:
            assert "object" in str(e).lower() or "metadata" in str(e).lower()
    
    def test_task_update_nonexistent_task(self):
        """测试更新不存在的任务"""
        result = task_update(taskId="non-existent-task-id", subject="New subject")
        
        # 验证返回结果为失败
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower() or "task" in result["error"].lower()
    
    def test_task_update_interactive_mode(self):
        """测试交互模式输出"""
        # 创建一个任务
        create_result = create_task(
            subject="Interactive test task",
            description="Testing interactive mode output"
        )
        task_id = create_result["task"]["id"]
        
        with patch('builtins.print') as mock_print:
            # 临时设置为交互模式（默认就是true，这里明确设置）
            os.environ["TASK_UPDATE_INTERACTIVE"] = "true"
            
            result = task_update(taskId=task_id, subject="Updated subject")
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出中包含任务信息
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "Task updated" in output or "Updated" in output
            
            del os.environ["TASK_UPDATE_INTERACTIVE"]
    
    def test_task_update_non_interactive_mode(self):
        """测试非交互模式输出"""
        # 创建一个任务
        create_result = create_task(
            subject="Non-interactive test task",
            description="Testing non-interactive mode output"
        )
        task_id = create_result["task"]["id"]
        
        with patch('builtins.print') as mock_print:
            # 临时设置为非交互模式
            os.environ["TASK_UPDATE_INTERACTIVE"] = "false"
            
            result = task_update(taskId=task_id, subject="Updated subject")
            
            # 验证有打印输出
            assert mock_print.called
            # 检查输出格式
            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)
            assert "[TASK_UPDATE]" in output or "Updated" in output
            
            del os.environ["TASK_UPDATE_INTERACTIVE"]
    
    def test_task_update_disabled_tool(self):
        """测试禁用工具"""
        # 临时禁用工具
        os.environ["TASK_UPDATE_ENABLED"] = "false"
        
        try:
            task_update(taskId="some-task-id", subject="New subject")
            assert False, "Should have raised RuntimeError for disabled tool"
        except RuntimeError as e:
            assert "enabled" in str(e).lower() or "disabled" in str(e).lower()
        
        del os.environ["TASK_UPDATE_ENABLED"]
    
    def test_task_update_delete_disabled(self):
        """测试禁用删除功能"""
        # 创建一个任务
        create_result = create_task(
            subject="Task to delete",
            description="Testing delete when disabled"
        )
        task_id = create_result["task"]["id"]
        
        # 临时禁用删除
        os.environ["TASK_UPDATE_ALLOW_DELETE"] = "false"
        
        try:
            task_update(taskId=task_id, status="deleted")
            assert False, "Should have raised RuntimeError for disabled delete"
        except RuntimeError as e:
            assert "delete" in str(e).lower() or "allowed" in str(e).lower()
        
        del os.environ["TASK_UPDATE_ALLOW_DELETE"]
    
    def test_task_update_config_overrides(self):
        """测试配置覆盖"""
        # 设置自定义存储路径
        custom_storage = os.path.join(self.test_dir, "custom_tasks.json")
        os.environ["TASK_UPDATE_STORAGE_PATH"] = custom_storage
        os.environ["TASK_CREATE_STORAGE_PATH"] = custom_storage  # 同时设置创建工具的路径
        
        # 在新的存储中创建任务
        create_result = create_task(
            subject="Config test task",
            description="Testing config overrides"
        )
        task_id = create_result["task"]["id"]
        
        # 验证自定义存储路径
        assert os.path.exists(custom_storage)
        
        # 更新任务
        result = task_update(taskId=task_id, subject="Updated subject")
        assert "success" in result
        assert result["success"] is True
        
        # 清理环境变量
        del os.environ["TASK_UPDATE_STORAGE_PATH"]
        del os.environ["TASK_CREATE_STORAGE_PATH"]
    
    def test_task_update_analytics_disabled(self):
        """测试分析禁用（默认情况）"""
        # 默认情况下分析应该是禁用的
        config = TaskUpdateConfig.from_env()
        assert not config["TASK_UPDATE_ANALYTICS_ENABLED"]
        
        # 创建一个任务
        create_result = create_task(
            subject="Analytics test",
            description="Testing with analytics disabled"
        )
        task_id = create_result["task"]["id"]
        
        # 应该能够正常更新任务而不会崩溃
        result = task_update(taskId=task_id, subject="Updated subject")
        assert "success" in result
    
    def test_task_update_storage_file_not_exist(self):
        """测试存储文件不存在的情况"""
        # 删除存储文件（如果存在）
        if os.path.exists(self.test_storage_path):
            os.remove(self.test_storage_path)
        
        # 尝试更新任务（应该失败）
        result = task_update(taskId="some-id", subject="New subject")
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
    
    def test_task_update_corrupted_storage_file(self):
        """测试损坏的存储文件"""
        # 创建损坏的JSON文件
        with open(self.test_storage_path, 'w') as f:
            f.write("invalid json content")
        
        # 尝试更新任务（应该失败）
        with patch('builtins.print') as mock_print:
            result = task_update(taskId="some-id", subject="New subject")
            
            # 应该显示警告
            assert mock_print.called
            # 返回失败
            assert "success" in result
            assert result["success"] is False
    
    def test_task_update_response_structure(self):
        """测试响应结构（与Claude Code兼容）"""
        # 创建一个任务
        create_result = create_task(
            subject="Structure test",
            description="Testing response structure"
        )
        task_id = create_result["task"]["id"]
        
        # 更新任务
        result = task_update(taskId=task_id, subject="Updated subject", status="in_progress")
        
        # 验证响应结构
        assert isinstance(result, dict)
        assert "success" in result and isinstance(result["success"], bool)
        assert "taskId" in result and isinstance(result["taskId"], str)
        assert "updatedFields" in result and isinstance(result["updatedFields"], list)
        assert "verificationNudgeNeeded" in result and result["verificationNudgeNeeded"] is False
        
        # 如果成功，可能包含statusChange
        if result["success"] and "status" in result["updatedFields"]:
            assert "statusChange" in result
            assert isinstance(result["statusChange"], dict)
            assert "from" in result["statusChange"]
            assert "to" in result["statusChange"]
        
        # 如果失败，包含error
        if not result["success"]:
            assert "error" in result and isinstance(result["error"], str)
    
    def test_task_update_empty_storage(self):
        """测试空存储"""
        # 确保存储文件为空（新创建）
        assert not os.path.exists(self.test_storage_path) or os.path.getsize(self.test_storage_path) == 0
        
        # 尝试更新任务
        result = task_update(taskId="any-id", subject="New subject")
        assert "success" in result
        assert result["success"] is False
        assert "error" in result
    
    def test_task_update_all_status_transitions(self):
        """测试所有状态转换"""
        # 创建一个任务
        create_result = create_task(
            subject="Status transition test",
            description="Testing all status transitions"
        )
        task_id = create_result["task"]["id"]
        
        # 测试状态转换：todo -> in_progress -> done
        status_sequence = ["in_progress", "done"]
        
        for new_status in status_sequence:
            result = task_update(taskId=task_id, status=new_status)
            assert result["success"] is True
            assert "status" in result["updatedFields"]
            assert "statusChange" in result
            assert result["statusChange"]["to"] == new_status