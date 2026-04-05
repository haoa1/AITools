#!/usr/bin/env python3
"""
EnterPlanModeTool单元测试

测试Claude Code兼容的EnterPlanModeTool实现。
测试计划模式进入的各种场景和配置选项。
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

from system.enter_plan_mode_tool import (
    enter_plan_mode_tool, 
    EnterPlanModeConfig,
    _get_config
)

class TestEnterPlanModeTool:
    """EnterPlanModeTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_enter_plan_mode_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量以使用非交互模式
        os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "false"
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_enter"
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "ENTER_PLAN_MODE_INTERACTIVE",
            "ENTER_PLAN_MODE_NON_INTERACTIVE_MODE",
            "ENTER_PLAN_MODE_DEFAULT_MESSAGE"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ===== Test Helper Methods =====
    
    def _call_enter_plan_mode(self):
        """Helper to call enter_plan_mode_tool and parse JSON result."""
        result_str = enter_plan_mode_tool()
        return json.loads(result_str)
    
    # ===== Configuration Tests =====
    
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        # Set custom environment variables
        os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "false"
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_reject"
        os.environ["ENTER_PLAN_MODE_DEFAULT_MESSAGE"] = "Custom message"
        
        config = EnterPlanModeConfig.from_env()
        
        assert config.interactive_mode == False
        assert config.non_interactive_mode == "auto_reject"
        assert config.default_message == "Custom message"
    
    def test_config_default_values(self):
        """测试配置默认值"""
        # Clear environment variables
        for key in [
            "ENTER_PLAN_MODE_INTERACTIVE",
            "ENTER_PLAN_MODE_NON_INTERACTIVE_MODE",
            "ENTER_PLAN_MODE_DEFAULT_MESSAGE"
        ]:
            if key in os.environ:
                del os.environ[key]
        
        config = EnterPlanModeConfig.from_env()
        
        assert config.interactive_mode == True
        assert config.non_interactive_mode == "auto_enter"
        assert config.default_message == "Plan mode entered successfully"
    
    # ===== Core Function Tests =====
    
    def test_enter_plan_mode_non_interactive_auto_enter(self):
        """测试非交互模式自动进入"""
        # Already set in setup: interactive=false, non_interactive_mode=auto_enter
        
        result = self._call_enter_plan_mode()
        
        assert result["success"] == True
        assert result["plan_mode_entered"] == True
        assert result["permission_granted"] == True
        assert result["requires_confirmation"] == False
        assert "Plan mode entered successfully" in result["message"]
    
    def test_enter_plan_mode_non_interactive_auto_reject(self):
        """测试非交互模式自动拒绝"""
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_reject"
        
        result = self._call_enter_plan_mode()
        
        assert result["success"] == True
        assert result["plan_mode_entered"] == False
        assert result["permission_granted"] == False
        assert result["requires_confirmation"] == False
        assert "Plan mode entry rejected" in result["message"]
    
    def test_enter_plan_mode_non_interactive_simulate(self):
        """测试非交互模式模拟"""
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "simulate"
        
        result = self._call_enter_plan_mode()
        
        assert result["success"] == True
        assert result["plan_mode_entered"] == True
        assert result["permission_granted"] == True
        assert result["requires_confirmation"] == False
        assert "Plan mode entered successfully" in result["message"]
    
    def test_enter_plan_mode_interactive(self):
        """测试交互模式"""
        os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "true"
        
        result = self._call_enter_plan_mode()
        
        assert result["success"] == True
        assert result["plan_mode_entered"] == True
        assert result["permission_granted"] == True
        assert result["requires_confirmation"] == True
        assert "Plan mode entered successfully" in result["message"]
    
    def test_enter_plan_mode_uses_config_defaults(self):
        """测试使用配置默认值"""
        # Save original environment values
        original_interactive = os.environ.get("ENTER_PLAN_MODE_INTERACTIVE")
        original_mode = os.environ.get("ENTER_PLAN_MODE_NON_INTERACTIVE_MODE")
        original_message = os.environ.get("ENTER_PLAN_MODE_DEFAULT_MESSAGE")
        
        try:
            # Set custom defaults in environment
            os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "false"
            os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_reject"
            os.environ["ENTER_PLAN_MODE_DEFAULT_MESSAGE"] = "Custom success message"
            
            result = self._call_enter_plan_mode()
            
            # Should use defaults from environment
            assert result["plan_mode_entered"] == False  # auto_reject
            assert "Custom success message" not in result["message"]  # Not used for auto_reject
        finally:
            # Restore original environment values
            if original_interactive is not None:
                os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = original_interactive
            else:
                os.environ.pop("ENTER_PLAN_MODE_INTERACTIVE", None)
                
            if original_mode is not None:
                os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = original_mode
            else:
                os.environ.pop("ENTER_PLAN_MODE_NON_INTERACTIVE_MODE", None)
                
            if original_message is not None:
                os.environ["ENTER_PLAN_MODE_DEFAULT_MESSAGE"] = original_message
            else:
                os.environ.pop("ENTER_PLAN_MODE_DEFAULT_MESSAGE", None)
    
    def test_enter_plan_mode_exception_handling(self):
        """测试异常处理"""
        # Temporarily break the config loading to simulate an error
        with patch('system.enter_plan_mode_tool.EnterPlanModeConfig.from_env') as mock_from_env:
            mock_from_env.side_effect = Exception("Config error")
            
            result = self._call_enter_plan_mode()
            
            assert result["success"] == False
            assert "Unexpected error" in result["error"]
            assert "Config error" in result["error"]
            assert result["operation"] == "enter_plan_mode_tool"
    
    # ===== Integration Style Tests =====
    
    def test_full_workflow_enter_plan_mode(self):
        """测试完整进入计划模式工作流"""
        # Set non-interactive mode for predictable testing
        os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "false"
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_enter"
        
        result_str = enter_plan_mode_tool()
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "enter_plan_mode_tool"
        assert "durationMs" in result
        assert result["plan_mode_entered"] == True
        assert result["permission_granted"] == True
    
    def test_full_workflow_reject_plan_mode(self):
        """测试完整拒绝进入计划模式工作流"""
        os.environ["ENTER_PLAN_MODE_INTERACTIVE"] = "false"
        os.environ["ENTER_PLAN_MODE_NON_INTERACTIVE_MODE"] = "auto_reject"
        
        result_str = enter_plan_mode_tool()
        result = json.loads(result_str)
        
        assert result["success"] == True
        assert result["operation"] == "enter_plan_mode_tool"
        assert result["plan_mode_entered"] == False
        assert result["permission_granted"] == False
    
    def test_metadata_included(self):
        """测试元数据包含"""
        result = self._call_enter_plan_mode()
        
        # Check that all expected metadata fields are present
        assert "operation" in result
        assert result["operation"] == "enter_plan_mode_tool"
        assert "durationMs" in result
        assert isinstance(result["durationMs"], int)
        assert result["durationMs"] >= 0
    
    def test_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        result = self._call_enter_plan_mode()
        
        # Check Claude Code compatibility fields
        assert "success" in result  # Standard success indicator
        assert "message" in result  # Status message
        assert "operation" in result  # Operation name
        assert "durationMs" in result  # Duration in milliseconds
    
    def test_response_structure(self):
        """测试响应结构"""
        result = self._call_enter_plan_mode()
        
        # Check that response has all required fields
        required_fields = [
            "success", "message", "plan_mode_entered", 
            "permission_granted", "requires_confirmation",
            "elapsed_time", "operation", "durationMs"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"