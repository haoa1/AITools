#!/usr/bin/env python3
"""
TodoWriteTool单元测试

测试Claude Code兼容的TodoWriteTool简化实现。
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.todo_write_tool import todo_write, _parse_todos_input, _check_verification_nudge_needed

class TestTodoWriteTool:
    """TodoWriteTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_todo_write_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 清理可能的残留存储文件
        if os.path.exists(".todo_storage.json"):
            os.remove(".todo_storage.json")
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_sample_todos_json(self) -> str:
        """创建示例待办事项JSON"""
        sample_todos = [
            {
                "content": "Implement feature X",
                "status": "pending",
                "activeForm": "development"
            },
            {
                "content": "Write tests for feature X",
                "status": "in_progress",
                "activeForm": "testing"
            },
            {
                "content": "Document feature X",
                "status": "pending",
                "activeForm": "documentation"
            }
        ]
        return json.dumps(sample_todos)
    
    def test_todo_write_basic_functionality(self):
        """测试基本功能"""
        todos_json = self._create_sample_todos_json()
        result = todo_write(todos_json)
        data = json.loads(result)
        
        assert "oldTodos" in data
        assert "newTodos" in data
        assert "durationMs" in data
        assert data["durationMs"] >= 0
        
        # 验证新待办事项正确返回
        new_todos = data["newTodos"]
        assert len(new_todos) == 3
        assert new_todos[0]["content"] == "Implement feature X"
        assert new_todos[0]["status"] == "pending"
        assert new_todos[0]["activeForm"] == "development"
        
        # 验证旧待办事项初始为空
        old_todos = data["oldTodos"]
        assert len(old_todos) == 0
    
    def test_todo_write_update_existing_todos(self):
        """测试更新现有待办事项"""
        # 第一次调用：创建初始待办事项
        initial_todos = [
            {
                "content": "Task 1",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task 2",
                "status": "in_progress",
                "activeForm": "work"
            }
        ]
        result1 = todo_write(json.dumps(initial_todos))
        data1 = json.loads(result1)
        
        # 验证第一次调用
        assert len(data1["oldTodos"]) == 0
        assert len(data1["newTodos"]) == 2
        
        # 第二次调用：更新待办事项
        updated_todos = [
            {
                "content": "Task 1",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task 2",
                "status": "completed",  # 更新状态
                "activeForm": "work"
            },
            {
                "content": "Task 3",
                "status": "pending",  # 新增任务
                "activeForm": "work"
            }
        ]
        result2 = todo_write(json.dumps(updated_todos))
        data2 = json.loads(result2)
        
        # 验证第二次调用
        assert len(data2["oldTodos"]) == 2  # 应该包含旧的待办事项
        assert len(data2["newTodos"]) == 3
        assert data2["newTodos"][1]["status"] == "completed"  # 任务2状态已更新
    
    def test_todo_write_all_completed_clears_storage(self):
        """测试全部完成时清空存储"""
        # 创建包含未完成任务的待办事项
        todos = [
            {
                "content": "Task A",
                "status": "in_progress",
                "activeForm": "work"
            },
            {
                "content": "Task B",
                "status": "pending",
                "activeForm": "work"
            }
        ]
        result1 = todo_write(json.dumps(todos))
        data1 = json.loads(result1)
        
        # 验证有未完成任务时存储保持
        assert len(data1["newTodos"]) == 2
        
        # 更新所有任务为已完成
        completed_todos = [
            {
                "content": "Task A",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task B",
                "status": "completed",
                "activeForm": "work"
            }
        ]
        result2 = todo_write(json.dumps(completed_todos))
        data2 = json.loads(result2)
        
        # 验证返回的新待办事项仍然是完整的
        assert len(data2["newTodos"]) == 2
        assert all(t["status"] == "completed" for t in data2["newTodos"])
        
        # 第三次调用：存储应该被清空，所以旧待办事项应该为空
        new_todos = [
            {
                "content": "Task C",
                "status": "pending",
                "activeForm": "work"
            }
        ]
        result3 = todo_write(json.dumps(new_todos))
        data3 = json.loads(result3)
        
        # 由于全部完成后存储被清空，旧待办事项应该为空
        assert len(data3["oldTodos"]) == 0
    
    def test_todo_write_verification_nudge_simple(self):
        """测试验证提醒（简单条件）"""
        # 创建3个已完成的任务，没有验证项
        todos = [
            {
                "content": "Implement feature",
                "status": "completed",
                "activeForm": "dev"
            },
            {
                "content": "Test feature",
                "status": "completed",
                "activeForm": "test"
            },
            {
                "content": "Document feature",
                "status": "completed",
                "activeForm": "doc"
            }
        ]
        result = todo_write(json.dumps(todos))
        data = json.loads(result)
        
        # 应该包含verificationNudgeNeeded
        assert "verificationNudgeNeeded" in data
        assert data["verificationNudgeNeeded"] is True
    
    def test_todo_write_no_verification_nudge_with_verification_item(self):
        """测试有验证项时不触发提醒"""
        # 创建3个已完成的任务，包含验证项
        todos = [
            {
                "content": "Implement feature",
                "status": "completed",
                "activeForm": "dev"
            },
            {
                "content": "Verify implementation",
                "status": "completed",  # 包含"verif"
                "activeForm": "verify"
            },
            {
                "content": "Document feature",
                "status": "completed",
                "activeForm": "doc"
            }
        ]
        result = todo_write(json.dumps(todos))
        data = json.loads(result)
        
        # 不应该包含verificationNudgeNeeded
        assert "verificationNudgeNeeded" not in data
    
    def test_todo_write_no_verification_nudge_insufficient_items(self):
        """测试任务数量不足时不触发提醒"""
        # 创建2个已完成的任务
        todos = [
            {
                "content": "Task 1",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task 2",
                "status": "completed",
                "activeForm": "work"
            }
        ]
        result = todo_write(json.dumps(todos))
        data = json.loads(result)
        
        # 不应该包含verificationNudgeNeeded（数量<3）
        assert "verificationNudgeNeeded" not in data
    
    def test_todo_write_no_verification_nudge_not_all_completed(self):
        """测试有未完成任务时不触发提醒"""
        # 创建3个任务，但有一个未完成
        todos = [
            {
                "content": "Task 1",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task 2",
                "status": "completed",
                "activeForm": "work"
            },
            {
                "content": "Task 3",
                "status": "in_progress",  # 未完成
                "activeForm": "work"
            }
        ]
        result = todo_write(json.dumps(todos))
        data = json.loads(result)
        
        # 不应该包含verificationNudgeNeeded（不是全部完成）
        assert "verificationNudgeNeeded" not in data
    
    def test_todo_write_invalid_json_input(self):
        """测试无效JSON输入"""
        result = todo_write("invalid json")
        data = json.loads(result)
        
        assert "error" in data
        assert "oldTodos" in data
        assert "newTodos" in data
        assert len(data["oldTodos"]) == 0
        assert len(data["newTodos"]) == 0
        assert "durationMs" in data
    
    def test_todo_write_empty_todos_list(self):
        """测试空待办事项列表"""
        result = todo_write("[]")
        data = json.loads(result)
        
        assert "error" not in data
        assert len(data["oldTodos"]) == 0
        assert len(data["newTodos"]) == 0
    
    def test_todo_write_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_todos = [
            {
                "content": "Task without status",  # 缺少status
                "activeForm": "work"
            }
        ]
        result = todo_write(json.dumps(invalid_todos))
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 'status'" in data["error"]
    
    def test_todo_write_invalid_status_value(self):
        """测试无效状态值"""
        invalid_todos = [
            {
                "content": "Task with invalid status",
                "status": "invalid_status",  # 无效状态
                "activeForm": "work"
            }
        ]
        result = todo_write(json.dumps(invalid_todos))
        data = json.loads(result)
        
        assert "error" in data
        assert "invalid status" in data["error"].lower()
    
    def test_todo_write_empty_content_field(self):
        """测试空content字段"""
        invalid_todos = [
            {
                "content": "",  # 空content
                "status": "pending",
                "activeForm": "work"
            }
        ]
        result = todo_write(json.dumps(invalid_todos))
        data = json.loads(result)
        
        assert "error" in data
        assert "non-empty 'content'" in data["error"]
    
    def test_todo_write_empty_activeform_field(self):
        """测试空activeForm字段"""
        invalid_todos = [
            {
                "content": "Task",
                "status": "pending",
                "activeForm": ""  # 空activeForm
            }
        ]
        result = todo_write(json.dumps(invalid_todos))
        data = json.loads(result)
        
        assert "error" in data
        assert "non-empty 'activeForm'" in data["error"]
    
    def test_todo_write_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        # 测试标准待办事项结构
        todos = [
            {
                "content": "Implement user authentication",
                "status": "in_progress",
                "activeForm": "development"
            },
            {
                "content": "Write unit tests",
                "status": "pending",
                "activeForm": "testing"
            }
        ]
        result = todo_write(json.dumps(todos))
        data = json.loads(result)
        
        # 检查必需字段
        assert "oldTodos" in data
        assert "newTodos" in data
        assert "durationMs" in data
        
        # 检查数据类型
        assert isinstance(data["oldTodos"], list)
        assert isinstance(data["newTodos"], list)
        assert isinstance(data["durationMs"], int)
        
        # 检查新待办事项结构
        for todo in data["newTodos"]:
            assert "content" in todo
            assert "status" in todo
            assert "activeForm" in todo
            assert todo["status"] in ["pending", "in_progress", "completed"]
    
    def test_todo_write_persistence_across_calls(self):
        """测试跨调用持久性"""
        # 第一次调用
        todos1 = [
            {
                "content": "Persistent task",
                "status": "pending",
                "activeForm": "work"
            }
        ]
        result1 = todo_write(json.dumps(todos1))
        data1 = json.loads(result1)
        
        # 第二次调用（应该能看到第一次的旧待办事项）
        todos2 = [
            {
                "content": "Updated task",
                "status": "completed",
                "activeForm": "work"
            }
        ]
        result2 = todo_write(json.dumps(todos2))
        data2 = json.loads(result2)
        
        # 验证持久性
        assert len(data2["oldTodos"]) == 1
        assert data2["oldTodos"][0]["content"] == "Persistent task"
        assert data2["oldTodos"][0]["status"] == "pending"
    
    def test_parse_todos_input_valid(self):
        """测试_parse_todos_input函数（有效输入）"""
        valid_json = self._create_sample_todos_json()
        parsed = _parse_todos_input(valid_json)
        
        assert len(parsed) == 3
        assert parsed[0]["content"] == "Implement feature X"
        assert parsed[0]["status"] == "pending"
        assert parsed[0]["activeForm"] == "development"
    
    def test_parse_todos_input_invalid(self):
        """测试_parse_todos_input函数（无效输入）"""
        # 无效JSON
        try:
            _parse_todos_input("invalid")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        # 非列表JSON
        try:
            _parse_todos_input('{"not": "a list"}')
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_check_verification_nudge_needed(self):
        """测试_check_verification_nudge_needed函数"""
        # 案例1：3个已完成，无验证项
        todos1 = [
            {"content": "Task 1", "status": "completed", "activeForm": "work"},
            {"content": "Task 2", "status": "completed", "activeForm": "work"},
            {"content": "Task 3", "status": "completed", "activeForm": "work"},
        ]
        assert _check_verification_nudge_needed(todos1) is True
        
        # 案例2：3个已完成，有验证项
        todos2 = [
            {"content": "Task 1", "status": "completed", "activeForm": "work"},
            {"content": "Verify task", "status": "completed", "activeForm": "work"},
            {"content": "Task 3", "status": "completed", "activeForm": "work"},
        ]
        assert _check_verification_nudge_needed(todos2) is False
        
        # 案例3：2个已完成
        todos3 = [
            {"content": "Task 1", "status": "completed", "activeForm": "work"},
            {"content": "Task 2", "status": "completed", "activeForm": "work"},
        ]
        assert _check_verification_nudge_needed(todos3) is False
        
        # 案例4：3个任务，有未完成
        todos4 = [
            {"content": "Task 1", "status": "completed", "activeForm": "work"},
            {"content": "Task 2", "status": "completed", "activeForm": "work"},
            {"content": "Task 3", "status": "in_progress", "activeForm": "work"},
        ]
        assert _check_verification_nudge_needed(todos4) is False

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])