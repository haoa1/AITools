#!/usr/bin/env python3
"""
NotificationTool单元测试

测试Claude Code兼容的NotificationTool实现。
测试各种通知场景和配置选项。
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

from interaction.notification_tool import (
    notify_user, 
    _format_notification_message,
    _validate_parameters,
    NotificationConfig,
    _get_config
)

class TestNotificationTool:
    """NotificationTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_notification_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量以使用非交互模式
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "auto_continue"
        os.environ["NOTIFICATION_DEFAULT_BLOCKING"] = "false"
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "NOTIFICATION_INTERACTIVE",
            "NOTIFICATION_NON_INTERACTIVE_MODE",
            "NOTIFICATION_DEFAULT_LEVEL",
            "NOTIFICATION_DEFAULT_BLOCKING",
            "NOTIFICATION_DEFAULT_CONTINUE_CONDITION",
            "NOTIFICATION_DEFAULT_TIMEOUT",
            "NOTIFICATION_DEFAULT_SPECIFIC_ANSWER"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ===== Test Helper Methods =====
    
    def _call_notify_user(self, **kwargs):
        """Helper to call notify_user and parse JSON result."""
        result_str = notify_user(**kwargs)
        return json.loads(result_str)
    
    # ===== Helper Function Tests =====
    
    def test_format_notification_message(self):
        """测试通知消息格式化"""
        # Test info level
        result = _format_notification_message("Test info", "info")
        assert "[INFO] Test info" in result
        
        # Test warning level
        result = _format_notification_message("Test warning", "warning")
        assert "[WARNING] Test warning" in result
        
        # Test error level
        result = _format_notification_message("Test error", "error")
        assert "[ERROR] Test error" in result
        
        # Test success level
        result = _format_notification_message("Test success", "success")
        assert "[SUCCESS] Test success" in result
        
        # Test unknown level (falls back to info)
        result = _format_notification_message("Test unknown", "unknown")
        assert "[INFO] Test unknown" in result
    
    def test_validate_parameters_valid(self):
        """测试参数验证（有效参数）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking=False,
            continue_condition="user_input",
            timeout=30,
            specific_answer=None
        )
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_message(self):
        """测试参数验证（无效消息）"""
        errors = _validate_parameters(
            message="",  # Empty message
            level="info",
            blocking=False,
            continue_condition="user_input",
            timeout=30,
            specific_answer=None
        )
        assert len(errors) > 0
        assert "'message' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_invalid_level(self):
        """测试参数验证（无效级别）"""
        errors = _validate_parameters(
            message="Test message",
            level="invalid_level",  # Invalid level
            blocking=False,
            continue_condition="user_input",
            timeout=30,
            specific_answer=None
        )
        assert len(errors) > 0
        assert "'level' must be one of" in errors[0]
    
    def test_validate_parameters_invalid_blocking(self):
        """测试参数验证（无效阻塞参数）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking="not_a_boolean",  # Invalid boolean
            continue_condition="user_input",
            timeout=30,
            specific_answer=None
        )
        assert len(errors) > 0
        assert "'blocking' must be a boolean" in errors[0]
    
    def test_validate_parameters_invalid_continue_condition(self):
        """测试参数验证（无效继续条件）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking=False,
            continue_condition="invalid_condition",  # Invalid condition
            timeout=30,
            specific_answer=None
        )
        assert len(errors) > 0
        assert "'continue_condition' must be one of" in errors[0]
    
    def test_validate_parameters_invalid_timeout(self):
        """测试参数验证（无效超时）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking=False,
            continue_condition="user_input",
            timeout=-10,  # Negative timeout
            specific_answer=None
        )
        assert len(errors) > 0
        assert "'timeout' must be a non-negative number" in errors[0]
    
    def test_validate_parameters_missing_specific_answer(self):
        """测试参数验证（缺少特定答案）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking=False,
            continue_condition="specific_answer",  # Requires specific_answer
            timeout=30,
            specific_answer=None  # Missing!
        )
        assert len(errors) > 0
        assert "'specific_answer' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_valid_specific_answer(self):
        """测试参数验证（有效的特定答案）"""
        errors = _validate_parameters(
            message="Test message",
            level="info",
            blocking=False,
            continue_condition="specific_answer",
            timeout=30,
            specific_answer="continue"  # Valid
        )
        assert len(errors) == 0
    
    # ===== Configuration Tests =====
    
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        # Set environment variables
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "simulate"
        os.environ["NOTIFICATION_DEFAULT_LEVEL"] = "warning"
        os.environ["NOTIFICATION_DEFAULT_BLOCKING"] = "true"
        os.environ["NOTIFICATION_DEFAULT_CONTINUE_CONDITION"] = "timeout"
        os.environ["NOTIFICATION_DEFAULT_TIMEOUT"] = "60"
        os.environ["NOTIFICATION_DEFAULT_SPECIFIC_ANSWER"] = "proceed"
        
        config = NotificationConfig.from_env()
        
        assert config.interactive_mode == False
        assert config.non_interactive_mode == "simulate"
        assert config.default_level == "warning"
        assert config.default_blocking == True
        assert config.default_continue_condition == "timeout"
        assert config.default_timeout == 60
        assert config.default_specific_answer == "proceed"
    
    def test_config_default_values(self):
        """测试配置默认值"""
        # Clear environment variables to get defaults
        for key in [
            "NOTIFICATION_INTERACTIVE",
            "NOTIFICATION_NON_INTERACTIVE_MODE",
            "NOTIFICATION_DEFAULT_LEVEL",
            "NOTIFICATION_DEFAULT_BLOCKING",
            "NOTIFICATION_DEFAULT_CONTINUE_CONDITION",
            "NOTIFICATION_DEFAULT_TIMEOUT",
            "NOTIFICATION_DEFAULT_SPECIFIC_ANSWER"
        ]:
            if key in os.environ:
                del os.environ[key]
        
        config = NotificationConfig.from_env()
        
        assert config.interactive_mode == True  # Default from class
        assert config.non_interactive_mode == "auto_continue"
        assert config.default_level == "info"
        assert config.default_blocking == False
        assert config.default_continue_condition == "user_input"
        assert config.default_timeout == 30
        assert config.default_specific_answer == "continue"
    
    # ===== Core Function Tests =====
    
    @patch('interaction.notification_tool._display_notification')
    @patch('interaction.notification_tool._get_user_confirmation')
    def test_notify_user_success_non_blocking(self, mock_confirm, mock_display):
        """测试非阻塞通知成功"""
        # Configure mock
        mock_display.return_value = None
        
        # Set interactive mode for this test
        os.environ["NOTIFICATION_INTERACTIVE"] = "true"
        
        result = self._call_notify_user(
            message="Test notification",
            level="info",
            blocking=False,
            continue_condition="user_input",
            timeout=30
        )
        
        assert result["success"] == True
        assert result["message"] == "Test notification"
        assert result["level"] == "info"
        assert result["displayed"] == True
        assert result["confirmed"] == True  # Auto-confirmed for non-blocking
        assert mock_display.called
        
        # Should not call confirmation for non-blocking
        assert not mock_confirm.called
    
    @patch('interaction.notification_tool._display_notification')
    @patch('interaction.notification_tool._get_user_confirmation')
    def test_notify_user_success_blocking_user_input(self, mock_confirm, mock_display):
        """测试阻塞通知（用户输入条件）"""
        # Configure mocks
        mock_display.return_value = None
        mock_confirm.return_value = "user_response"
        
        # Set interactive mode for this test
        os.environ["NOTIFICATION_INTERACTIVE"] = "true"
        
        result = self._call_notify_user(
            message="Test blocking notification",
            level="warning",
            blocking=True,
            continue_condition="user_input",
            timeout=30
        )
        
        assert result["success"] == True
        assert result["message"] == "Test blocking notification"
        assert result["level"] == "warning"
        assert result["displayed"] == True
        assert result["confirmed"] == True
        assert result["user_response"] == "user_response"
        assert mock_display.called
        assert mock_confirm.called
    
    @patch('interaction.notification_tool._display_notification')
    def test_notify_user_non_interactive_auto_continue(self, mock_display):
        """测试非交互模式（自动继续）"""
        # Set non-interactive mode
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "auto_continue"
        
        result = self._call_notify_user(
            message="Test non-interactive notification",
            level="info",
            blocking=False
        )
        
        assert result["success"] == True
        assert result["message"] == "Test non-interactive notification"
        assert result["displayed"] == True
        assert result["confirmed"] == True  # Auto-confirmed
        
        # In non-interactive auto_continue mode, display might not be called
        # (it could just log internally)
    
    @patch('interaction.notification_tool._display_notification')
    def test_notify_user_non_interactive_simulate(self, mock_display):
        """测试非交互模式（模拟）"""
        # Set non-interactive mode with simulation
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "simulate"
        
        result = self._call_notify_user(
            message="Test non-interactive simulation",
            level="info",
            blocking=False
        )
        
        assert result["success"] == True
        assert result["message"] == "Test non-interactive simulation"
        assert result["displayed"] == True
        assert result["confirmed"] == True  # Simulated confirmation
        assert result["user_response"] == "simulated"
    
    def test_notify_user_validation_error(self):
        """测试参数验证错误"""
        result = self._call_notify_user(
            message="",  # Empty message - should fail validation
            level="info",
            blocking=False
        )
        
        assert result["success"] == False
        assert "Parameter validation failed" in result["error"]
        assert "'message' must be a non-empty string" in result["error"]
    
    @patch('interaction.notification_tool._display_notification')
    @patch('interaction.notification_tool.input')
    def test_notify_user_blocking_specific_answer(self, mock_input, mock_display):
        """测试阻塞通知（特定答案条件）"""
        # Configure mocks
        mock_display.return_value = None
        mock_input.return_value = "continue"  # User types expected answer
        
        # Set interactive mode
        os.environ["NOTIFICATION_INTERACTIVE"] = "true"
        
        result = self._call_notify_user(
            message="Test specific answer notification",
            level="info",
            blocking=True,
            continue_condition="specific_answer",
            specific_answer="continue"
        )
        
        assert result["success"] == True
        assert result["confirmed"] == True
        assert result["user_response"] == "continue"
        assert mock_input.called
        
        # Test with wrong answer
        mock_input.return_value = "wrong"
        result = self._call_notify_user(
            message="Test specific answer notification",
            level="info",
            blocking=True,
            continue_condition="specific_answer",
            specific_answer="continue"
        )
        
        assert result["success"] == True
        assert result["confirmed"] == False  # Wrong answer
        assert result["user_response"] == "wrong"
    
    
    # ===== Edge Case Tests =====
    
    def test_notify_user_all_levels(self):
        """测试所有通知级别"""
        levels = ["info", "warning", "error", "success"]
        
        for level in levels:
            with patch('interaction.notification_tool._display_notification') as mock_display:
                mock_display.return_value = None
                
                # 临时设置交互模式
                original_value = os.environ.get("NOTIFICATION_INTERACTIVE")
                os.environ["NOTIFICATION_INTERACTIVE"] = "true"
                
                try:
                    result = self._call_notify_user(
                        message=f"Test {level} notification",
                        level=level,
                        blocking=False
                    )
                    
                    assert result["success"] == True
                    assert result["level"] == level
                    assert mock_display.called
                finally:
                    # 恢复环境变量
                    if original_value is not None:
                        os.environ["NOTIFICATION_INTERACTIVE"] = original_value
                    else:
                        del os.environ["NOTIFICATION_INTERACTIVE"]
    
    @patch('interaction.notification_tool._display_notification')
    @patch('interaction.notification_tool._get_user_confirmation')
    def test_notify_user_blocking_exception_handling(self, mock_confirm, mock_display):
        """测试阻塞通知的异常处理"""
        # Make confirmation raise an exception
        mock_confirm.side_effect = Exception("Input error")
        mock_display.return_value = None
        
        # 临时设置交互模式
        original_value = os.environ.get("NOTIFICATION_INTERACTIVE")
        os.environ["NOTIFICATION_INTERACTIVE"] = "true"
        
        try:
            result = self._call_notify_user(
                message="Test notification with error",
                level="error",
                blocking=True
            )
            
            assert result["success"] == False
            assert "Unexpected error" in result["error"]
            assert "Input error" in result["error"]
            # Note: 'displayed' field is not included in error results
        finally:
            # 恢复环境变量
            if original_value is not None:
                os.environ["NOTIFICATION_INTERACTIVE"] = original_value
            else:
                del os.environ["NOTIFICATION_INTERACTIVE"]
    
    def test_notify_user_uses_config_defaults(self):
        """测试使用配置默认值"""
        # Save original environment values
        original_interactive = os.environ.get("NOTIFICATION_INTERACTIVE")
        original_level = os.environ.get("NOTIFICATION_DEFAULT_LEVEL")
        original_blocking = os.environ.get("NOTIFICATION_DEFAULT_BLOCKING")
        original_continue = os.environ.get("NOTIFICATION_DEFAULT_CONTINUE_CONDITION")
        original_timeout = os.environ.get("NOTIFICATION_DEFAULT_TIMEOUT")
        
        try:
            # Set custom defaults in environment
            os.environ["NOTIFICATION_INTERACTIVE"] = "true"  # Need interactive mode for display mock
            os.environ["NOTIFICATION_DEFAULT_LEVEL"] = "warning"
            os.environ["NOTIFICATION_DEFAULT_BLOCKING"] = "true"
            os.environ["NOTIFICATION_DEFAULT_CONTINUE_CONDITION"] = "timeout"
            os.environ["NOTIFICATION_DEFAULT_TIMEOUT"] = "60"
            
            with patch('interaction.notification_tool._display_notification') as mock_display:
                mock_display.return_value = None
                
                # Call with minimal parameters - use empty string for level to trigger config default
                result = self._call_notify_user(message="Test message", level="")
                
                # Should use defaults from environment
                assert result["level"] == "warning"  # From environment
                # Note: blocking parameter is passed as False by default in test setup,
                # but function should use config.default_blocking which is True from env
        finally:
            # Restore original environment values
            if original_interactive is not None:
                os.environ["NOTIFICATION_INTERACTIVE"] = original_interactive
            else:
                os.environ.pop("NOTIFICATION_INTERACTIVE", None)
                
            if original_level is not None:
                os.environ["NOTIFICATION_DEFAULT_LEVEL"] = original_level
            else:
                os.environ.pop("NOTIFICATION_DEFAULT_LEVEL", None)
                
            if original_blocking is not None:
                os.environ["NOTIFICATION_DEFAULT_BLOCKING"] = original_blocking
            else:
                os.environ.pop("NOTIFICATION_DEFAULT_BLOCKING", None)
                
            if original_continue is not None:
                os.environ["NOTIFICATION_DEFAULT_CONTINUE_CONDITION"] = original_continue
            else:
                os.environ.pop("NOTIFICATION_DEFAULT_CONTINUE_CONDITION", None)
                
            if original_timeout is not None:
                os.environ["NOTIFICATION_DEFAULT_TIMEOUT"] = original_timeout
            else:
                os.environ.pop("NOTIFICATION_DEFAULT_TIMEOUT", None)
    
    # ===== Integration Style Tests =====
    
    def test_full_notification_workflow_non_blocking(self):
        """测试完整通知工作流（非阻塞）"""
        # Set non-interactive mode for predictable testing
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "auto_continue"
        
        result_str = notify_user(
            message="Operation completed successfully",
            level="success",
            blocking=False
        )
        
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "notify_user"
        assert result["message"] == "Operation completed successfully"
        assert result["level"] == "success"
        assert "durationMs" in result
    
    def test_full_notification_workflow_blocking(self):
        """测试完整通知工作流（阻塞）- 在非交互模式下"""
        # Set non-interactive mode
        os.environ["NOTIFICATION_INTERACTIVE"] = "false"
        os.environ["NOTIFICATION_NON_INTERACTIVE_MODE"] = "auto_continue"
        
        result_str = notify_user(
            message="Please confirm before proceeding",
            level="warning",
            blocking=True,
            continue_condition="user_input"
        )
        
        result = json.loads(result_str)
        
        # In non-interactive auto_continue mode, blocking notifications
        # should still succeed (auto-confirmed)
        assert result["success"] == True
        assert result["confirmed"] == True

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])