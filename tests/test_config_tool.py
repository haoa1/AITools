#!/usr/bin/env python3
"""
ConfigTool单元测试

测试Claude Code兼容的ConfigTool简化实现。
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.config_tool import config, SUPPORTED_SETTINGS

class TestConfigTool:
    """ConfigTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_config_tool_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 保存原始配置路径并设置测试路径
        self.original_config_path = None
        if hasattr(sys.modules['system.config_tool'], '_CONFIG_FILE_PATH'):
            self.original_config_path = sys.modules['system.config_tool']._CONFIG_FILE_PATH
            # 修改为测试目录中的路径
            test_config_path = os.path.join(self.test_dir, ".aitools_config.json")
            sys.modules['system.config_tool']._CONFIG_FILE_PATH = test_config_path
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 恢复原始配置路径
        if self.original_config_path:
            sys.modules['system.config_tool']._CONFIG_FILE_PATH = self.original_config_path
    
    def test_config_get_existing_setting(self):
        """测试获取现有配置项"""
        # 先设置一个值
        set_result = config("theme", "dark")
        set_data = json.loads(set_result)
        assert set_data["success"] is True
        
        # 然后获取
        get_result = config("theme")
        data = json.loads(get_result)
        
        assert data["success"] is True
        assert data["operation"] == "get"
        assert data["setting"] == "theme"
        assert data["value"] == "dark"
        assert "durationMs" in data
        assert data["durationMs"] >= 0
    
    def test_config_get_default_value(self):
        """测试获取默认值（配置项不存在于文件中）"""
        result = config("verbose")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "get"
        assert data["setting"] == "verbose"
        # verbose的默认值是False，应该返回"false"字符串
        assert data["value"] == "false"
    
    def test_config_set_boolean_true(self):
        """测试设置布尔值为true"""
        result = config("verbose", "true")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "set"
        assert data["setting"] == "verbose"
        assert data["newValue"] is True
        assert data["previousValue"] is False
    
    def test_config_set_boolean_false(self):
        """测试设置布尔值为false"""
        # 先设置为true
        config("verbose", "true")
        
        # 再设置为false
        result = config("verbose", "false")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "set"
        assert data["setting"] == "verbose"
        assert data["newValue"] is False
        assert data["previousValue"] is True
    
    def test_config_set_string_with_options(self):
        """测试设置字符串值（带选项限制）"""
        result = config("theme", "light")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "set"
        assert data["setting"] == "theme"
        assert data["newValue"] == "light"
    
    def test_config_set_invalid_option(self):
        """测试设置无效的选项值"""
        result = config("theme", "invalid_theme")
        data = json.loads(result)
        
        assert data["success"] is False
        assert data["operation"] == "set"
        assert data["setting"] == "theme"
        assert "error" in data
        assert "Invalid value" in data["error"]
        assert "Options:" in data["error"]
    
    def test_config_unknown_setting(self):
        """测试未知的配置项"""
        result = config("unknown_setting")
        data = json.loads(result)
        
        assert data["success"] is False
        assert "error" in data
        assert "Unknown setting" in data["error"]
    
    def test_config_set_unknown_setting(self):
        """测试设置未知的配置项"""
        result = config("unknown_setting", "some_value")
        data = json.loads(result)
        
        assert data["success"] is False
        assert "error" in data
        assert "Unknown setting" in data["error"]
    
    def test_config_boolean_variants(self):
        """测试布尔值的多种表示形式"""
        # 测试各种true表示
        true_variants = ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]
        for variant in true_variants:
            result = config("verbose", variant)
            data = json.loads(result)
            assert data["success"] is True
            assert data["newValue"] is True
        
        # 测试各种false表示
        false_variants = ["false", "False", "FALSE", "0", "no", "No", "NO"]
        for variant in false_variants:
            result = config("verbose", variant)
            data = json.loads(result)
            assert data["success"] is True
            assert data["newValue"] is False
    
    def test_config_invalid_boolean(self):
        """测试无效的布尔值"""
        result = config("verbose", "not_a_boolean")
        data = json.loads(result)
        
        assert data["success"] is False
        assert "error" in data
        assert "requires true or false" in data["error"]
    
    def test_config_get_all_supported_settings(self):
        """测试所有支持的配置项都能获取"""
        for setting in SUPPORTED_SETTINGS.keys():
            result = config(setting)
            data = json.loads(result)
            
            assert data["success"] is True
            assert data["operation"] == "get"
            assert data["setting"] == setting
            assert "value" in data
    
    def test_config_persistence(self):
        """测试配置持久化"""
        # 设置一个值
        config("theme", "dark")
        
        # 模拟重新加载配置
        # 通过直接调用函数来验证
        result = config("theme")
        data = json.loads(result)
        assert data["value"] == "dark"
    
    def test_config_empty_value_string(self):
        """测试空值字符串（应该触发get操作）"""
        # 先设置一个值
        config("theme", "dark")
        
        # 使用空字符串应该触发get操作
        result = config("theme", "")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "get"
        assert data["value"] == "dark"
    
    def test_config_none_value(self):
        """测试None值（应该触发get操作）"""
        # 这个测试需要在调用时显式传递None
        # 先设置一个值
        config("theme", "dark")
        
        # 模拟传递None
        result = config("theme", None)
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "get"
        assert data["value"] == "dark"
    
    def test_config_default_model_setting(self):
        """测试default_model配置项"""
        result = config("default_model", "claude-3-5-sonnet")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["operation"] == "set"
        assert data["setting"] == "default_model"
        assert data["newValue"] == "claude-3-5-sonnet"
    
    def test_config_editor_mode(self):
        """测试editor_mode配置项"""
        # 测试有效值
        for mode in ["default", "vim", "emacs"]:
            result = config("editor_mode", mode)
            data = json.loads(result)
            assert data["success"] is True
            assert data["newValue"] == mode
        
        # 测试无效值
        result = config("editor_mode", "invalid_mode")
        data = json.loads(result)
        assert data["success"] is False
        assert "error" in data
    
    def test_config_auto_compact_enabled(self):
        """测试auto_compact_enabled配置项"""
        result = config("auto_compact_enabled", "true")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["newValue"] is True
    
    def test_config_show_turn_duration(self):
        """测试show_turn_duration配置项"""
        result = config("show_turn_duration", "false")
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["newValue"] is False
    
    def test_config_preferred_notif_channel(self):
        """测试preferred_notif_channel配置项"""
        # 测试有效值
        for channel in ["terminal", "desktop", "none"]:
            result = config("preferred_notif_channel", channel)
            data = json.loads(result)
            assert data["success"] is True
            assert data["newValue"] == channel
        
        # 测试无效值
        result = config("preferred_notif_channel", "invalid_channel")
        data = json.loads(result)
        assert data["success"] is False
    
    def test_config_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        # 测试GET操作
        result = config("theme")
        data = json.loads(result)
        
        # 检查必需字段
        assert "success" in data
        assert "operation" in data
        assert "setting" in data
        assert "value" in data
        assert "durationMs" in data
        
        # 检查数据类型
        assert isinstance(data["success"], bool)
        assert isinstance(data["operation"], str)
        assert isinstance(data["setting"], str)
        assert isinstance(data["durationMs"], int)
        
        # 测试SET操作
        result = config("theme", "dark")
        data = json.loads(result)
        
        # 检查SET操作的特有字段
        assert "newValue" in data
        assert "previousValue" in data
    
    def test_config_error_handling(self):
        """测试错误处理"""
        # 测试无效JSON配置文件的处理
        # 创建损坏的配置文件
        config_path = os.path.join(self.test_dir, ".aitools_config.json")
        with open(config_path, 'w') as f:
            f.write("invalid json content")
        
        # 应该能够处理错误并返回默认值
        result = config("theme")
        data = json.loads(result)
        # 可能成功（使用默认值）或失败，取决于实现
        # 至少不应该崩溃
    
    def test_config_multiple_operations(self):
        """测试多个连续操作"""
        # 设置多个配置项
        config("theme", "dark")
        config("verbose", "true")
        config("editor_mode", "vim")
        
        # 验证所有设置都生效
        result = config("theme")
        data = json.loads(result)
        assert data["value"] == "dark"
        
        result = config("verbose")
        data = json.loads(result)
        assert data["value"] == "true"
        
        result = config("editor_mode")
        data = json.loads(result)
        assert data["value"] == "vim"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])