#!/usr/bin/env python3
"""
TaskOutputTool单元测试

测试Claude Code兼容的TaskOutputTool实现。
测试任务输出检索的各种场景和配置选项。
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.task_output_tool import (
    task_output_tool, 
    _validate_parameters,
    _get_simulated_task_output,
    TaskOutputConfig,
    _get_config
)

class TestTaskOutputTool:
    """TaskOutputTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_task_output_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量
        os.environ["TASK_OUTPUT_DEFAULT_BLOCK"] = "true"
        os.environ["TASK_OUTPUT_SIMULATION_MODE"] = "true"
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "TASK_OUTPUT_DEFAULT_BLOCK",
            "TASK_OUTPUT_DEFAULT_TIMEOUT",
            "TASK_OUTPUT_MAX_TIMEOUT",
            "TASK_OUTPUT_DIR",
            "TASK_OUTPUT_SIMULATION_MODE"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ===== Test Helper Methods =====
    
    def _call_task_output(self, **kwargs):
        """Helper to call task_output_tool and parse JSON result."""
        result_str = task_output_tool(**kwargs)
        return json.loads(result_str)
    
    # ===== Helper Function Tests =====
    
    def test_validate_parameters_valid(self):
        """测试参数验证（有效）"""
        errors = _validate_parameters(
            task_id="test-task-123",
            block=True,
            timeout=30000
        )
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_task_id(self):
        """测试参数验证（无效任务ID）"""
        # Empty task_id
        errors = _validate_parameters(
            task_id="",
            block=True,
            timeout=30000
        )
        assert "'task_id' must be a non-empty string" in errors[0]
        
        # Non-string task_id
        errors = _validate_parameters(
            task_id=None,
            block=True,
            timeout=30000
        )
        assert "'task_id' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_invalid_block(self):
        """测试参数验证（无效阻塞参数）"""
        errors = _validate_parameters(
            task_id="test-task",
            block="invalid",
            timeout=30000
        )
        assert "'block' must be a boolean" in errors[0]
    
    def test_validate_parameters_invalid_timeout(self):
        """测试参数验证（无效超时）"""
        # Negative timeout
        errors = _validate_parameters(
            task_id="test-task",
            block=True,
            timeout=-1
        )
        assert "'timeout' must be a non-negative number" in errors[0]
        
        # Non-numeric timeout
        errors = _validate_parameters(
            task_id="test-task",
            block=True,
            timeout="invalid"
        )
        assert "'timeout' must be a non-negative number" in errors[0]
        
        # Timeout exceeding max (set max to 600000 in config)
        os.environ["TASK_OUTPUT_MAX_TIMEOUT"] = "1000"
        config = TaskOutputConfig.from_env()
        errors = _validate_parameters(
            task_id="test-task",
            block=True,
            timeout=2000  # Exceeds max of 1000
        )
        # Clean up environment
        del os.environ["TASK_OUTPUT_MAX_TIMEOUT"]
        assert "'timeout' must not exceed" in errors[0]
    
    def test_get_simulated_task_output(self):
        """测试模拟任务输出生成"""
        # Test with different task IDs to get varied output
        task_id1 = "test-task-1"
        task_id2 = "test-task-2"
        task_id3 = "test-task-3"
        
        output1 = _get_simulated_task_output(task_id1, block=True, timeout=1000)
        output2 = _get_simulated_task_output(task_id2, block=False, timeout=1000)
        output3 = _get_simulated_task_output(task_id3, block=True, timeout=1000)
        
        # Check required fields
        assert "task_id" in output1
        assert output1["task_id"] == task_id1
        assert "task_type" in output1
        assert "status" in output1
        assert "description" in output1
        assert "output" in output1
        
        # Different task IDs should produce different outputs
        assert output1["output"] != output2["output"]
        assert output1["task_id"] != output2["task_id"]
    
    # ===== Configuration Tests =====
    
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        # Set custom environment variables
        os.environ["TASK_OUTPUT_DEFAULT_BLOCK"] = "false"
        os.environ["TASK_OUTPUT_DEFAULT_TIMEOUT"] = "15000"
        os.environ["TASK_OUTPUT_MAX_TIMEOUT"] = "300000"
        os.environ["TASK_OUTPUT_DIR"] = "/custom/task/output"
        os.environ["TASK_OUTPUT_SIMULATION_MODE"] = "false"
        
        config = TaskOutputConfig.from_env()
        
        assert config.default_block == False
        assert config.default_timeout == 15000
        assert config.max_timeout == 300000
        assert config.task_output_dir == "/custom/task/output"
        assert config.simulation_mode == False
    
    def test_config_default_values(self):
        """测试配置默认值"""
        # Clear environment variables
        for key in [
            "TASK_OUTPUT_DEFAULT_BLOCK",
            "TASK_OUTPUT_DEFAULT_TIMEOUT",
            "TASK_OUTPUT_MAX_TIMEOUT",
            "TASK_OUTPUT_DIR",
            "TASK_OUTPUT_SIMULATION_MODE"
        ]:
            if key in os.environ:
                del os.environ[key]
        
        config = TaskOutputConfig.from_env()
        
        assert config.default_block == True
        assert config.default_timeout == 30000
        assert config.max_timeout == 600000
        assert config.task_output_dir == "/tmp/aitools_tasks"
        assert config.simulation_mode == True
    
    # ===== Core Function Tests =====
    
    def test_task_output_tool_success(self):
        """测试任务输出工具成功"""
        result = self._call_task_output(
            task_id="test-task-123",
            block=True,
            timeout=30000
        )
        
        assert result["success"] == True
        assert result["task_id"] == "test-task-123"
        assert result["block"] == True
        assert result["timeout"] == 30000
        assert result["output_available"] == True
        assert "task_output" in result
        assert "operation" in result
        assert result["operation"] == "task_output_tool"
    
    def test_task_output_tool_non_blocking(self):
        """测试非阻塞任务输出"""
        result = self._call_task_output(
            task_id="test-task-456",
            block=False,
            timeout=10000
        )
        
        assert result["success"] == True
        assert result["block"] == False
        assert result["timeout"] == 10000
        assert result["output_available"] == True
    
    def test_task_output_tool_validation_error(self):
        """测试任务输出工具验证错误"""
        result = self._call_task_output(
            task_id="",  # Empty task_id - should fail validation
            block=True,
            timeout=30000
        )
        
        assert result["success"] == False
        assert "'task_id' must be a non-empty string" in result["error"]
        assert result["operation"] == "task_output_tool"
    
    def test_task_output_tool_uses_config_defaults(self):
        """测试使用配置默认值"""
        # Save original environment values
        original_block = os.environ.get("TASK_OUTPUT_DEFAULT_BLOCK")
        original_timeout = os.environ.get("TASK_OUTPUT_DEFAULT_TIMEOUT")
        
        try:
            # Set custom defaults in environment
            os.environ["TASK_OUTPUT_DEFAULT_BLOCK"] = "false"
            os.environ["TASK_OUTPUT_DEFAULT_TIMEOUT"] = "15000"
            
            # Call with minimal parameters (only task_id)
            result = self._call_task_output(task_id="test-task-defaults")
            
            # Should use defaults from environment
            assert result["block"] == False  # From environment
            assert result["timeout"] == 15000  # From environment
        finally:
            # Restore original environment values
            if original_block is not None:
                os.environ["TASK_OUTPUT_DEFAULT_BLOCK"] = original_block
            else:
                os.environ.pop("TASK_OUTPUT_DEFAULT_BLOCK", None)
                
            if original_timeout is not None:
                os.environ["TASK_OUTPUT_DEFAULT_TIMEOUT"] = original_timeout
            else:
                os.environ.pop("TASK_OUTPUT_DEFAULT_TIMEOUT", None)
    
    def test_task_output_tool_simulation_mode_disabled(self):
        """测试模拟模式禁用"""
        os.environ["TASK_OUTPUT_SIMULATION_MODE"] = "false"
        
        result = self._call_task_output(
            task_id="test-task-no-sim",
            block=True,
            timeout=1000
        )
        
        # With simulation disabled and no real task manager, output may not be available
        # But the operation should still succeed
        assert result["success"] == True
        # output_available may be False since no real task manager exists
    
    @patch('system.task_output_tool._read_task_output_file')
    def test_task_output_tool_file_based(self, mock_read_file):
        """测试基于文件的任务输出"""
        # Mock file reading to return task output
        mock_read_file.return_value = {
            "task_id": "file-task-123",
            "task_type": "bash",
            "status": "completed",
            "description": "Command execution",
            "output": "Command completed successfully",
            "exitCode": 0
        }
        
        result = self._call_task_output(
            task_id="file-task-123",
            block=True,
            timeout=5000
        )
        
        assert result["success"] == True
        assert result["output_available"] == True
        assert result["task_output"]["task_id"] == "file-task-123"
        assert result["task_output"]["status"] == "completed"
        assert mock_read_file.called
    
    @patch('system.task_output_tool._get_simulated_task_output')
    def test_task_output_tool_simulated_output(self, mock_simulate):
        """测试模拟任务输出"""
        # Mock simulation to return specific output
        mock_simulate.return_value = {
            "task_id": "sim-task-123",
            "task_type": "agent",
            "status": "completed",
            "description": "Simulated agent task",
            "output": "Simulated agent output",
            "prompt": "Test prompt",
            "result": "Test result"
        }
        
        result = self._call_task_output(
            task_id="sim-task-123",
            block=False,
            timeout=10000
        )
        
        assert result["success"] == True
        assert result["output_available"] == True
        assert result["task_output"]["task_type"] == "agent"
        assert "prompt" in result["task_output"]
        assert "result" in result["task_output"]
        assert mock_simulate.called
    
    def test_task_output_tool_task_completed_status(self):
        """测试任务完成状态检测"""
        result = self._call_task_output(
            task_id="completed-task-test",
            block=True,
            timeout=5000
        )
        
        assert result["success"] == True
        assert "task_completed" in result
        # task_completed should be a boolean
        assert isinstance(result["task_completed"], bool)
        
        # Check if task_output has status that's used to determine completion
        if result["output_available"]:
            status = result["task_output"].get("status", "").lower()
            expected_completed = status in ("completed", "failed", "stopped")
            assert result["task_completed"] == expected_completed
    
    def test_task_output_tool_exception_handling(self):
        """测试异常处理"""
        # Temporarily break the config loading to simulate an error
        with patch('system.task_output_tool._get_config') as mock_get_config:
            mock_get_config.side_effect = Exception("Config error")
            
            result = self._call_task_output(
                task_id="error-task",
                block=True,
                timeout=1000
            )
            
            assert result["success"] == False
            assert "Unexpected error" in result["error"]
            assert "Config error" in result["error"]
            assert result["operation"] == "task_output_tool"
    
    # ===== Integration Style Tests =====
    
    def test_full_workflow_blocking(self):
        """测试完整阻塞工作流"""
        result_str = task_output_tool(
            task_id="workflow-task-123",
            block=True,
            timeout=30000
        )
        
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "task_output_tool"
        assert "durationMs" in result
        assert result["task_id"] == "workflow-task-123"
        assert result["block"] == True
        assert result["timeout"] == 30000
    
    def test_full_workflow_non_blocking(self):
        """测试完整非阻塞工作流"""
        result_str = task_output_tool(
            task_id="workflow-task-456",
            block=False,
            timeout=10000
        )
        
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "task_output_tool"
        assert result["block"] == False
        assert result["timeout"] == 10000
    
    def test_metadata_included(self):
        """测试元数据包含"""
        result = self._call_task_output(task_id="metadata-test")
        
        # Check that all expected metadata fields are present
        assert "operation" in result
        assert result["operation"] == "task_output_tool"
        assert "durationMs" in result
        assert isinstance(result["durationMs"], int)
        assert result["durationMs"] >= 0
        assert "elapsed_time" in result
        assert "wait_time_ms" in result
    
    def test_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        result = self._call_task_output(task_id="compatibility-test")
        
        # Check Claude Code compatibility fields
        assert "success" in result  # Standard success indicator
        assert "operation" in result  # Operation name
        assert "durationMs" in result  # Duration in milliseconds
        assert "task_id" in result  # Task ID in response
    
    def test_response_structure(self):
        """测试响应结构"""
        result = self._call_task_output(task_id="structure-test")
        
        # Check that response has all required fields
        required_fields = [
            "success", "task_id", "block", "timeout",
            "output_available", "task_completed", "wait_time_ms",
            "elapsed_time", "operation", "durationMs"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
        
        # If output is available, check task_output structure
        if result["output_available"]:
            task_output = result["task_output"]
            assert "task_id" in task_output
            assert "task_type" in task_output
            assert "status" in task_output
            assert "description" in task_output
            assert "output" in task_output