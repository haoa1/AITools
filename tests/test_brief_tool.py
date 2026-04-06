#!/usr/bin/env python3
"""
BriefTool单元测试

测试Claude Code兼容的BriefTool实现。
测试各种消息发送场景和附件处理。
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interaction.brief_tool import (
    brief, 
    _validate_parameters,
    _format_message,
    _resolve_attachments,
    _send_brief_message,
    _get_config,
    BriefConfig
)

class TestBriefTool:
    """BriefTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_brief_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 创建测试文件
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Test content")
        
        self.test_image = os.path.join(self.test_dir, "test.png")
        with open(self.test_image, "wb") as f:
            f.write(b"fake png data" * 100)  # 约1.3KB
        
        # 设置环境变量以使用非交互模式
        os.environ["BRIEF_INTERACTIVE"] = "false"
        os.environ["BRIEF_NON_INTERACTIVE_MODE"] = "print"
        os.environ["BRIEF_ENABLED"] = "true"
        
        # 清理可能影响测试的其他环境变量
        for key in ["BRIEF_ANALYTICS_ENABLED", "BRIEF_MAX_ATTACHMENT_SIZE_MB"]:
            if key in os.environ:
                del os.environ[key]
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "BRIEF_INTERACTIVE",
            "BRIEF_NON_INTERACTIVE_MODE",
            "BRIEF_ENABLED",
            "BRIEF_ANALYTICS_ENABLED",
            "BRIEF_MAX_ATTACHMENT_SIZE_MB"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ============================================================================
    # 参数验证测试
    # ============================================================================
    
    def test_validate_parameters_valid(self):
        """测试参数验证（有效）"""
        # 无附件
        errors = _validate_parameters(
            message="Test message",
            attachments=None,
            status="normal"
        )
        assert len(errors) == 0
        
        # 有附件（JSON字符串）
        attachments_json = json.dumps([self.test_file])
        errors = _validate_parameters(
            message="Test message",
            attachments=attachments_json,
            status="proactive"
        )
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_message(self):
        """测试参数验证（无效消息）"""
        # 空消息
        errors = _validate_parameters(
            message="",
            attachments=None,
            status="normal"
        )
        assert "'message' must be a non-empty string" in errors[0]
        
        # 非字符串消息
        errors = _validate_parameters(
            message=None,
            attachments=None,
            status="normal"
        )
        assert "'message' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_invalid_status(self):
        """测试参数验证（无效状态）"""
        errors = _validate_parameters(
            message="Test message",
            attachments=None,
            status="invalid"
        )
        assert "'status' must be one of: normal, proactive" in errors[0]
    
    def test_validate_parameters_invalid_attachments(self):
        """测试参数验证（无效附件）"""
        # 附件不是字符串（应该是JSON字符串）
        errors = _validate_parameters(
            message="Test message",
            attachments=["not", "a", "string"],
            status="normal"
        )
        assert "'attachments' must be a JSON string" in errors[0]
        
        # 无效JSON
        errors = _validate_parameters(
            message="Test message",
            attachments="not valid json",
            status="normal"
        )
        assert "Invalid JSON in attachments" in errors[0]
        
        # JSON不是数组
        errors = _validate_parameters(
            message="Test message",
            attachments='{"key": "value"}',
            status="normal"
        )
        assert "'attachments' must be a JSON array of strings" in errors[0]
        
        # 数组包含非字符串
        errors = _validate_parameters(
            message="Test message",
            attachments='["path.txt", 123]',
            status="normal"
        )
        assert "Attachment at index 1 must be a string" in errors[0]
    
    # ============================================================================
    # 配置测试
    # ============================================================================
    
    def test_config_from_env(self):
        """测试从环境变量创建配置"""
        # 保存原始环境变量
        original_enabled = os.environ.get("BRIEF_ENABLED")
        original_interactive = os.environ.get("BRIEF_INTERACTIVE")
        original_mode = os.environ.get("BRIEF_NON_INTERACTIVE_MODE")
        
        try:
            # 清理环境变量以测试默认值
            for key in ["BRIEF_ENABLED", "BRIEF_INTERACTIVE", "BRIEF_NON_INTERACTIVE_MODE"]:
                if key in os.environ:
                    del os.environ[key]
            
            # 测试默认值
            config = BriefConfig.from_env()
            assert config["BRIEF_ENABLED"] == True
            assert config["BRIEF_INTERACTIVE"] == True
            assert config["BRIEF_NON_INTERACTIVE_MODE"] == "print"
            
            # 测试环境变量覆盖
            os.environ["BRIEF_ENABLED"] = "false"
            os.environ["BRIEF_INTERACTIVE"] = "false"
            os.environ["BRIEF_NON_INTERACTIVE_MODE"] = "silent"
            
            config = BriefConfig.from_env()
            assert config["BRIEF_ENABLED"] == False
            assert config["BRIEF_INTERACTIVE"] == False
            assert config["BRIEF_NON_INTERACTIVE_MODE"] == "silent"
            
            # 测试空字符串使用默认值
            os.environ["BRIEF_ENABLED"] = ""
            config = BriefConfig.from_env()
            assert config["BRIEF_ENABLED"] == True  # 应该使用默认值
        finally:
            # 恢复原始环境变量
            if original_enabled is not None:
                os.environ["BRIEF_ENABLED"] = original_enabled
            else:
                if "BRIEF_ENABLED" in os.environ:
                    del os.environ["BRIEF_ENABLED"]
                    
            if original_interactive is not None:
                os.environ["BRIEF_INTERACTIVE"] = original_interactive
            else:
                if "BRIEF_INTERACTIVE" in os.environ:
                    del os.environ["BRIEF_INTERACTIVE"]
                    
            if original_mode is not None:
                os.environ["BRIEF_NON_INTERACTIVE_MODE"] = original_mode
            else:
                if "BRIEF_NON_INTERACTIVE_MODE" in os.environ:
                    del os.environ["BRIEF_NON_INTERACTIVE_MODE"]
    
    def test_get_config(self):
        """测试获取配置函数"""
        config = _get_config()
        assert isinstance(config, dict)
        assert "BRIEF_ENABLED" in config
        assert "BRIEF_INTERACTIVE" in config
    
    # ============================================================================
    # 辅助函数测试
    # ============================================================================
    
    def test_format_message(self):
        """测试消息格式化"""
        # 正常状态
        formatted = _format_message("Hello", "normal")
        assert "💬" in formatted
        assert "Hello" in formatted
        
        # 主动状态
        formatted = _format_message("Alert", "proactive")
        assert "🔔" in formatted
        assert "Alert" in formatted
    
    def test_resolve_attachments(self):
        """测试附件解析"""
        config = _get_config()
        
        # 单个文件
        attachments_json = json.dumps([self.test_file])
        resolved = _resolve_attachments(attachments_json, config)
        
        assert len(resolved) == 1
        assert resolved[0]["filename"] == "test.txt"
        assert resolved[0]["size"] > 0
        assert resolved[0]["is_image"] == False
        
        # 图片文件
        attachments_json = json.dumps([self.test_image])
        resolved = _resolve_attachments(attachments_json, config)
        
        assert len(resolved) == 1
        assert resolved[0]["filename"] == "test.png"
        assert resolved[0]["is_image"] == True
    
    def test_resolve_attachments_file_not_found(self):
        """测试附件解析 - 文件不存在"""
        config = _get_config()
        attachments_json = json.dumps(["/nonexistent/file.txt"])
        
        with pytest.raises(FileNotFoundError, match="Attachment not found"):
            _resolve_attachments(attachments_json, config)
    
    def test_resolve_attachments_size_limit(self):
        """测试附件解析 - 大小限制"""
        # 创建大文件
        large_file = os.path.join(self.test_dir, "large.bin")
        with open(large_file, "wb") as f:
            f.write(b"x" * (11 * 1024 * 1024))  # 11MB，超过10MB默认限制
        
        config = _get_config()
        config["BRIEF_MAX_ATTACHMENT_SIZE_MB"] = 10  # 确保限制为10MB
        
        attachments_json = json.dumps([large_file])
        with pytest.raises(ValueError, match="too large"):
            _resolve_attachments(attachments_json, config)
    
    # ============================================================================
    # 主函数测试
    # ============================================================================
    
    def test_brief_simple_message(self):
        """测试简单消息发送"""
        # 使用patch模拟_send_brief_message以避免实际输出
        with patch('interaction.brief_tool._send_brief_message') as mock_send:
            result = brief("Test message")
            
            # 验证调用
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            assert call_args[0] == "Test message"  # 消息
            assert call_args[1] is None  # 无附件
            assert isinstance(call_args[2], dict)  # 配置
            
            # 验证结果
            assert "message" in result
            assert result["message"] == "Test message"
            assert "sentAt" in result
            assert "attachments" not in result  # 无附件
    
    def test_brief_with_attachments(self):
        """测试带附件的消息"""
        attachments_json = json.dumps([self.test_file])
        
        with patch('interaction.brief_tool._send_brief_message') as mock_send:
            result = brief(
                message="Test message with attachment",
                attachments=attachments_json,
                status="normal"
            )
            
            # 验证调用
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0]
            assert call_args[0] == "Test message with attachment"
            assert call_args[1] is not None  # 有附件
            assert len(call_args[1]) == 1  # 一个附件
            
            # 验证结果
            assert "attachments" in result
            assert len(result["attachments"]) == 1
            assert result["attachments"][0]["filename"] == "test.txt"
    
    def test_brief_proactive_status(self):
        """测试主动状态消息"""
        with patch('interaction.brief_tool._send_brief_message') as mock_send:
            result = brief(
                message="Proactive alert",
                status="proactive"
            )
            
            mock_send.assert_called_once()
            assert result["message"] == "Proactive alert"
    
    def test_brief_disabled(self):
        """测试brief禁用"""
        os.environ["BRIEF_ENABLED"] = "false"
        
        with pytest.raises(RuntimeError, match="Brief tool is not enabled"):
            brief("Test message")
    
    def test_brief_validation_error(self):
        """测试参数验证失败"""
        with pytest.raises(ValueError, match="Parameter validation failed"):
            brief("", status="normal")  # 空消息
    
    def test_brief_attachment_not_found(self):
        """测试附件不存在"""
        attachments_json = json.dumps(["/nonexistent/file.txt"])
        
        with pytest.raises(FileNotFoundError, match="Attachment not found"):
            brief(
                message="Test",
                attachments=attachments_json
            )
    
    # ============================================================================
    # 输出测试
    # ============================================================================
    
    def test_send_brief_message_interactive(self):
        """测试交互模式消息发送"""
        config = {
            "BRIEF_INTERACTIVE": True,
            "BRIEF_NON_INTERACTIVE_MODE": "print"
        }
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            _send_brief_message("Test message", None, config)
        
        output = f.getvalue()
        assert "Test message" in output  # 消息应该被打印出来
        assert "💬" in output  # 交互模式应该使用表情符号
    
    def test_send_brief_message_non_interactive_print(self):
        """测试非交互模式print行为"""
        config = {
            "BRIEF_INTERACTIVE": False,
            "BRIEF_NON_INTERACTIVE_MODE": "print"
        }
        
        # 测试标准输出
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            _send_brief_message("Test message", None, config)
        
        output = f.getvalue()
        assert "BRIEF MESSAGE" in output
        assert "Test message" in output
    
    def test_send_brief_message_non_interactive_log(self):
        """测试非交互模式log行为"""
        config = {
            "BRIEF_INTERACTIVE": False,
            "BRIEF_NON_INTERACTIVE_MODE": "log"
        }
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            _send_brief_message("Test message", None, config)
        
        output = f.getvalue()
        assert "[BRIEF]" in output
        assert "Test message" in output
    
    def test_send_brief_message_non_interactive_silent(self):
        """测试非交互模式silent行为"""
        config = {
            "BRIEF_INTERACTIVE": False,
            "BRIEF_NON_INTERACTIVE_MODE": "silent"
        }
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            _send_brief_message("Test message", None, config)
        
        output = f.getvalue()
        assert output == ""  # 应该无输出
    
    def test_send_brief_message_with_attachments(self):
        """测试带附件的消息发送"""
        config = {
            "BRIEF_INTERACTIVE": False,
            "BRIEF_NON_INTERACTIVE_MODE": "print"
        }
        
        attachments = [{
            "filename": "test.txt",
            "size": 1024,
            "is_image": False
        }]
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            _send_brief_message("Test message", attachments, config)
        
        output = f.getvalue()
        assert "Attachments" in output or "attachment" in output
        assert "test.txt" in output
    
    # ============================================================================
    # 集成测试
    # ============================================================================
    
    def test_full_workflow_brief_message(self):
        """完整工作流测试 - 简单消息"""
        os.environ["BRIEF_INTERACTIVE"] = "false"
        os.environ["BRIEF_NON_INTERACTIVE_MODE"] = "log"
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = brief("Integration test message")
        
        output = f.getvalue()
        assert "[BRIEF]" in output or "Integration test message" in output
        
        # 验证结果结构
        assert "message" in result
        assert result["message"] == "Integration test message"
        assert "sentAt" in result
        assert isinstance(result["sentAt"], str)
    
    def test_full_workflow_brief_with_attachments(self):
        """完整工作流测试 - 带附件消息"""
        os.environ["BRIEF_INTERACTIVE"] = "false"
        os.environ["BRIEF_NON_INTERACTIVE_MODE"] = "print"
        
        attachments_json = json.dumps([self.test_file])
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = brief(
                message="Message with attachment",
                attachments=attachments_json,
                status="normal"
            )
        
        output = f.getvalue()
        assert "Message with attachment" in output
        assert "Attachments" in output or "attachment" in output
        
        # 验证结果
        assert "attachments" in result
        assert len(result["attachments"]) == 1
        assert result["attachments"][0]["filename"] == "test.txt"
    
    def test_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        # 测试函数装饰器属性
        from interaction.brief_tool import __BRIEF_FUNCTION__
        # __BRIEF_FUNCTION__的结构是 {'function': {...}}
        assert 'function' in __BRIEF_FUNCTION__
        function_def = __BRIEF_FUNCTION__['function']
        assert function_def.get('name') == 'brief'
        
        # 测试参数定义
        params = function_def.get('parameters', {})
        properties = params.get('properties', {})
        assert 'message' in properties
        assert 'attachments' in properties
        assert 'status' in properties
        
        # 测试必需参数
        required = params.get('required', [])
        assert 'message' in required
    
    def test_response_structure(self):
        """测试响应结构"""
        with patch('interaction.brief_tool._send_brief_message'):
            result = brief("Test")
            
            # 基本字段
            assert isinstance(result, dict)
            assert "message" in result
            assert "sentAt" in result
            
            # 可选字段
            # attachments字段可能不存在（当没有附件时）
            
            # 时间戳格式
            import re
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$'
            assert re.match(iso_pattern, result["sentAt"]) is not None