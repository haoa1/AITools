#!/usr/bin/env python3
"""
ConfirmDialogTool单元测试

测试Claude Code兼容的ConfirmDialogTool实现。
测试各种确认场景和配置选项。
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

from interaction.confirm_dialog_tool import (
    confirm_dialog, 
    _format_confirmation_message,
    _validate_parameters,
    ConfirmDialogConfig,
    _get_config
)

class TestConfirmDialogTool:
    """ConfirmDialogTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_confirm_dialog_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量以使用非交互模式
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "false"
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "auto_confirm"
        os.environ["CONFIRM_DIALOG_DEFAULT_BLOCKING"] = "true"
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "CONFIRM_DIALOG_INTERACTIVE",
            "CONFIRM_DIALOG_NON_INTERACTIVE_MODE",
            "CONFIRM_DIALOG_DEFAULT_TITLE",
            "CONFIRM_DIALOG_DEFAULT_RESPONSE",
            "CONFIRM_DIALOG_DEFAULT_BLOCKING",
            "CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION",
            "CONFIRM_DIALOG_DEFAULT_TIMEOUT"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ===== Test Helper Methods =====
    
    def _call_confirm_dialog(self, **kwargs):
        """Helper to call confirm_dialog and parse JSON result."""
        result_str = confirm_dialog(**kwargs)
        return json.loads(result_str)
    
    # ===== Helper Function Tests =====
    
    def test_format_confirmation_message(self):
        """测试确认消息格式化"""
        # Test with title
        result = _format_confirmation_message(
            message="Are you sure?",
            title="Important",
            default="none"
        )
        assert "=== Important ===" in result
        assert "Are you sure?" in result
        assert "Confirm? (y/n):" in result
        
        # Test without title
        result = _format_confirmation_message(
            message="Proceed?",
            title="",
            default="yes"
        )
        assert "=== " not in result  # No title
        assert "Proceed?" in result
        assert "Confirm? (Y/n):" in result  # Default yes
        
        # Test with default no
        result = _format_confirmation_message(
            message="Cancel operation?",
            title="Warning",
            default="no"
        )
        assert "=== Warning ===" in result
        assert "Cancel operation?" in result
        assert "Confirm? (y/N):" in result  # Default no
    
    def test_validate_parameters_valid(self):
        """测试参数验证（有效）"""
        errors = _validate_parameters(
            message="Test message",
            title="Test title",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_message(self):
        """测试参数验证（无效消息）"""
        # Empty message
        errors = _validate_parameters(
            message="",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        assert "'message' must be a non-empty string" in errors[0]
        
        # Non-string message
        errors = _validate_parameters(
            message=None,
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        assert "'message' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_invalid_default(self):
        """测试参数验证（无效默认值）"""
        errors = _validate_parameters(
            message="Test",
            title="Test",
            default="invalid",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        assert "'default' must be one of: yes, no, none" in errors[0]
    
    def test_validate_parameters_invalid_blocking(self):
        """测试参数验证（无效阻塞参数）"""
        errors = _validate_parameters(
            message="Test",
            title="Test",
            default="yes",
            blocking="invalid",
            require_confirmation=True,
            timeout=30
        )
        assert "'blocking' must be a boolean" in errors[0]
    
    def test_validate_parameters_invalid_require_confirmation(self):
        """测试参数验证（无效确认要求参数）"""
        errors = _validate_parameters(
            message="Test",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation="invalid",
            timeout=30
        )
        assert "'require_confirmation' must be a boolean" in errors[0]
    
    def test_validate_parameters_invalid_timeout(self):
        """测试参数验证（无效超时）"""
        errors = _validate_parameters(
            message="Test",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=-1
        )
        assert "'timeout' must be a non-negative number" in errors[0]
        
        errors = _validate_parameters(
            message="Test",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout="invalid"
        )
        assert "'timeout' must be a non-negative number" in errors[0]
    
    # ===== Configuration Tests =====
    
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        # Set custom environment variables
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "false"
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "auto_reject"
        os.environ["CONFIRM_DIALOG_DEFAULT_TITLE"] = "Custom Title"
        os.environ["CONFIRM_DIALOG_DEFAULT_RESPONSE"] = "no"
        os.environ["CONFIRM_DIALOG_DEFAULT_BLOCKING"] = "false"
        os.environ["CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION"] = "false"
        os.environ["CONFIRM_DIALOG_DEFAULT_TIMEOUT"] = "60"
        
        config = ConfirmDialogConfig.from_env()
        
        assert config.interactive_mode == False
        assert config.non_interactive_mode == "auto_reject"
        assert config.default_title == "Custom Title"
        assert config.default_response == "no"
        assert config.default_blocking == False
        assert config.default_require_confirmation == False
        assert config.default_timeout == 60
    
    def test_config_default_values(self):
        """测试配置默认值"""
        # Clear environment variables
        for key in [
            "CONFIRM_DIALOG_INTERACTIVE",
            "CONFIRM_DIALOG_NON_INTERACTIVE_MODE",
            "CONFIRM_DIALOG_DEFAULT_TITLE",
            "CONFIRM_DIALOG_DEFAULT_RESPONSE",
            "CONFIRM_DIALOG_DEFAULT_BLOCKING",
            "CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION",
            "CONFIRM_DIALOG_DEFAULT_TIMEOUT"
        ]:
            if key in os.environ:
                del os.environ[key]
        
        config = ConfirmDialogConfig.from_env()
        
        assert config.interactive_mode == True
        assert config.non_interactive_mode == "auto_confirm"
        assert config.default_title == "Confirmation"
        assert config.default_response == "none"
        assert config.default_blocking == True
        assert config.default_require_confirmation == True
        assert config.default_timeout == 30
    
    # ===== Core Function Tests =====
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    @patch('interaction.confirm_dialog_tool._get_user_confirmation')
    def test_confirm_dialog_success_yes(self, mock_confirm, mock_display):
        """测试确认对话框成功（用户选择是）"""
        # Configure mocks
        mock_display.return_value = None
        mock_confirm.return_value = "yes"
        
        # Set interactive mode for this test
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="none",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["message"] == "Are you sure?"
        assert result["title"] == "Test"
        assert result["confirmed"] == True
        assert result["user_response"] == "yes"
        assert mock_display.called
        assert mock_confirm.called
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    @patch('interaction.confirm_dialog_tool._get_user_confirmation')
    def test_confirm_dialog_success_no(self, mock_confirm, mock_display):
        """测试确认对话框成功（用户选择否）"""
        # Configure mocks
        mock_display.return_value = None
        mock_confirm.return_value = "no"
        
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="none",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == False
        assert result["user_response"] == "no"
    
    def test_confirm_dialog_non_interactive_auto_confirm(self):
        """测试非交互模式自动确认"""
        # Already set in setup: interactive=false, non_interactive_mode=auto_confirm
        
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="none",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == True
        assert result["user_response"] == "yes"
        assert result["used_default"] == True
    
    def test_confirm_dialog_non_interactive_auto_reject(self):
        """测试非交互模式自动拒绝"""
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "auto_reject"
        
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="none",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == False
        assert result["user_response"] == "no"
        assert result["used_default"] == True
    
    def test_confirm_dialog_non_interactive_simulate(self):
        """测试非交互模式模拟"""
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "simulate"
        
        # Test with default yes
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == True
        assert result["user_response"] == "yes"
        assert result["used_default"] == True
        
        # Test with default no
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="no",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == False
        assert result["user_response"] == "no"
        assert result["used_default"] == True
    
    def test_confirm_dialog_validation_error(self):
        """测试确认对话框验证错误"""
        result = self._call_confirm_dialog(
            message="",  # Empty message - should fail validation
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == False
        assert "'message' must be a non-empty string" in result["error"]
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    def test_confirm_dialog_non_blocking(self, mock_display):
        """测试非阻塞确认对话框"""
        mock_display.return_value = None
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        # Test with default yes
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="yes",
            blocking=False,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == True
        assert result["user_response"] == "yes"
        assert result["used_default"] == True
        assert mock_display.called
        
        # Test with default no
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="no",
            blocking=False,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        assert result["confirmed"] == False
        assert result["user_response"] == "no"
        assert result["used_default"] == True
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    def test_confirm_dialog_no_require_confirmation(self, mock_display):
        """测试不需要确认的情况"""
        mock_display.return_value = None
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=False,  # 不需要确认
            timeout=30
        )
        
        # Should use auto behavior when require_confirmation is False
        assert result["success"] == True
        assert result["confirmed"] == True  # Default yes
        assert result["user_response"] == "yes"
        assert result["used_default"] == True
        assert not mock_display.called  # Should not display when no confirmation required
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    @patch('interaction.confirm_dialog_tool._get_user_confirmation')
    def test_confirm_dialog_default_response_handling(self, mock_confirm, mock_display):
        """测试默认响应处理"""
        mock_display.return_value = None
        mock_confirm.return_value = "yes"
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        # Test with default yes
        result = self._call_confirm_dialog(
            message="Are you sure?",
            title="Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == True
        # User said yes (mocked), should be confirmed
        assert result["confirmed"] == True
        assert mock_display.called
        
        # Verify prompt format for default yes
        call_args = mock_display.call_args[0]
        assert call_args[0] == "Are you sure?"  # message
        assert call_args[1] == "Test"  # title
        assert call_args[2] == "yes"  # default
    
    @patch('interaction.confirm_dialog_tool._display_confirmation')
    @patch('interaction.confirm_dialog_tool._get_user_confirmation')
    def test_confirm_dialog_exception_handling(self, mock_confirm, mock_display):
        """测试异常处理"""
        # Make confirmation raise an exception
        mock_confirm.side_effect = Exception("Input error")
        mock_display.return_value = None
        
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
        
        result = self._call_confirm_dialog(
            message="Test confirmation with error",
            title="Error Test",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        assert result["success"] == False
        assert "Unexpected error" in result["error"]
        assert "Input error" in result["error"]
    
    def test_confirm_dialog_uses_config_defaults(self):
        """测试使用配置默认值"""
        # Save original environment values
        original_interactive = os.environ.get("CONFIRM_DIALOG_INTERACTIVE")
        original_title = os.environ.get("CONFIRM_DIALOG_DEFAULT_TITLE")
        original_response = os.environ.get("CONFIRM_DIALOG_DEFAULT_RESPONSE")
        original_blocking = os.environ.get("CONFIRM_DIALOG_DEFAULT_BLOCKING")
        original_require = os.environ.get("CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION")
        original_timeout = os.environ.get("CONFIRM_DIALOG_DEFAULT_TIMEOUT")
        
        try:
            # Set custom defaults in environment
            os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "true"
            os.environ["CONFIRM_DIALOG_DEFAULT_TITLE"] = "Custom Title"
            os.environ["CONFIRM_DIALOG_DEFAULT_RESPONSE"] = "no"
            os.environ["CONFIRM_DIALOG_DEFAULT_BLOCKING"] = "false"
            os.environ["CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION"] = "false"
            os.environ["CONFIRM_DIALOG_DEFAULT_TIMEOUT"] = "60"
            
            with patch('interaction.confirm_dialog_tool._display_confirmation') as mock_display:
                mock_display.return_value = None
                
                # Call with minimal parameters
                result = self._call_confirm_dialog(message="Test message")
                
                # Should use defaults from environment
                assert result["title"] == "Custom Title"  # From environment
                # Note: other defaults are used internally
        finally:
            # Restore original environment values
            if original_interactive is not None:
                os.environ["CONFIRM_DIALOG_INTERACTIVE"] = original_interactive
            else:
                os.environ.pop("CONFIRM_DIALOG_INTERACTIVE", None)
                
            if original_title is not None:
                os.environ["CONFIRM_DIALOG_DEFAULT_TITLE"] = original_title
            else:
                os.environ.pop("CONFIRM_DIALOG_DEFAULT_TITLE", None)
                
            if original_response is not None:
                os.environ["CONFIRM_DIALOG_DEFAULT_RESPONSE"] = original_response
            else:
                os.environ.pop("CONFIRM_DIALOG_DEFAULT_RESPONSE", None)
                
            if original_blocking is not None:
                os.environ["CONFIRM_DIALOG_DEFAULT_BLOCKING"] = original_blocking
            else:
                os.environ.pop("CONFIRM_DIALOG_DEFAULT_BLOCKING", None)
                
            if original_require is not None:
                os.environ["CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION"] = original_require
            else:
                os.environ.pop("CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION", None)
                
            if original_timeout is not None:
                os.environ["CONFIRM_DIALOG_DEFAULT_TIMEOUT"] = original_timeout
            else:
                os.environ.pop("CONFIRM_DIALOG_DEFAULT_TIMEOUT", None)
    
    # ===== Integration Style Tests =====
    
    def test_full_workflow_confirmation(self):
        """测试完整确认工作流"""
        # Set non-interactive mode for predictable testing
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "false"
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "auto_confirm"
        
        result_str = confirm_dialog(
            message="Delete all files?",
            title="Dangerous Operation",
            default="no",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "confirm_dialog"
        assert "durationMs" in result
        assert result["message"] == "Delete all files?"
        assert result["title"] == "Dangerous Operation"
        # In non-interactive auto_confirm mode, should be confirmed
        assert result["confirmed"] == True
    
    def test_full_workflow_rejection(self):
        """测试完整拒绝工作流"""
        os.environ["CONFIRM_DIALOG_INTERACTIVE"] = "false"
        os.environ["CONFIRM_DIALOG_NON_INTERACTIVE_MODE"] = "auto_reject"
        
        result_str = confirm_dialog(
            message="Proceed with installation?",
            title="Installation",
            default="yes",
            blocking=True,
            require_confirmation=True,
            timeout=30
        )
        
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "confirm_dialog"
        assert result["message"] == "Proceed with installation?"
        # In non-interactive auto_reject mode, should be rejected even with default yes
        assert result["confirmed"] == False