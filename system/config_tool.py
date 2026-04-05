"""
Claude Code兼容的ConfigTool简化实现。

基于Claude Code的ConfigTool.ts（467行TypeScript代码）分析：
- 输入：setting（配置项名称），value（可选，配置值）
- 输出：success、operation、setting、value、previousValue、error等字段
- 功能：获取或设置配置项

简化策略：
1. 使用JSON文件存储配置（.aitools_config.json）
2. 支持有限的配置项（theme、verbose等）
3. 简化验证逻辑，忽略复杂平台特定功能
4. 保持与Claude Code接口的兼容性

注意：这是简化版本，不包含复杂的权限检查、语音模式、实时同步等功能。
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from base import function_ai, parameters_func, property_param

# ===== 数据结构定义 =====

@dataclass
class SettingConfig:
    """配置项定义"""
    type: str  # 'boolean', 'string', 'number'
    description: str
    default: Any
    options: Optional[List[str]] = None
    validate_func: Optional[callable] = None

# ===== 输入参数定义 =====

__SETTING_PROPERTY__ = property_param(
    name="setting",
    description="The setting key (e.g., 'theme', 'verbose', 'editor_mode')",
    t="string",
    required=True,
)

__VALUE_PROPERTY__ = property_param(
    name="value",
    description="The new value. Omit to get current value. Can be string, boolean, or number.",
    t="string",
    required=False,
)

# ===== 工具函数定义 =====

__CONFIG_TOOL_FUNCTION__ = function_ai(
    name="config",
    description="Get or set Claude Code compatible configuration settings (simplified version).",
    parameters=parameters_func([
        __SETTING_PROPERTY__,
        __VALUE_PROPERTY__,
    ]),
)

tools = [__CONFIG_TOOL_FUNCTION__]

# ===== 支持的配置项定义 =====

# 配置项定义
SUPPORTED_SETTINGS: Dict[str, SettingConfig] = {
    "theme": SettingConfig(
        type="string",
        description="Color theme for the UI",
        default="auto",
        options=["light", "dark", "auto"]
    ),
    "verbose": SettingConfig(
        type="boolean",
        description="Show detailed debug output",
        default=False,
    ),
    "editor_mode": SettingConfig(
        type="string",
        description="Key binding mode for editor",
        default="default",
        options=["default", "vim", "emacs"]
    ),
    "auto_compact_enabled": SettingConfig(
        type="boolean",
        description="Auto-compact when context is full",
        default=True,
    ),
    "auto_memory_enabled": SettingConfig(
        type="boolean",
        description="Enable auto-memory feature",
        default=False,
    ),
    "show_turn_duration": SettingConfig(
        type="boolean",
        description="Show turn duration message after responses",
        default=True,
    ),
    "terminal_progress_bar_enabled": SettingConfig(
        type="boolean",
        description="Show progress bars in terminal",
        default=True,
    ),
    "default_model": SettingConfig(
        type="string",
        description="Default AI model to use",
        default="claude-3-5-sonnet",
        options=["claude-3-5-sonnet", "claude-3-opus", "claude-3-sonnet", "gpt-4"]
    ),
    "thinking_enabled": SettingConfig(
        type="boolean",
        description="Enable thinking mode for AI",
        default=False,
    ),
    "preferred_notif_channel": SettingConfig(
        type="string",
        description="Preferred notification channel",
        default="terminal",
        options=["terminal", "desktop", "none"]
    ),
}

# ===== 配置存储管理 =====

_CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".aitools_config.json")

def _load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not os.path.exists(_CONFIG_FILE_PATH):
        # 返回默认配置
        default_config = {}
        for key, config in SUPPORTED_SETTINGS.items():
            default_config[key] = config.default
        return default_config
    
    try:
        with open(_CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 确保所有支持的配置项都有值
        for key, setting_config in SUPPORTED_SETTINGS.items():
            if key not in config:
                config[key] = setting_config.default
        
        return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load config file: {e}")
        # 返回默认配置
        default_config = {}
        for key, config in SUPPORTED_SETTINGS.items():
            default_config[key] = config.default
        return default_config

def _save_config(config: Dict[str, Any]) -> bool:
    """保存配置文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(_CONFIG_FILE_PATH), exist_ok=True)
        
        with open(_CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except (IOError, TypeError) as e:
        print(f"Error: Failed to save config file: {e}")
        return False

def _get_current_config() -> Dict[str, Any]:
    """获取当前配置（带缓存）"""
    # 简单实现，每次都重新加载
    return _load_config()

def _update_config(setting: str, value: Any) -> bool:
    """更新单个配置项"""
    config = _load_config()
    
    if setting not in SUPPORTED_SETTINGS:
        return False
    
    config[setting] = value
    return _save_config(config)

# ===== 验证函数 =====

def _validate_setting_value(setting: str, value: Any) -> tuple[bool, Optional[str]]:
    """验证配置项和值"""
    # 检查配置项是否支持
    if setting not in SUPPORTED_SETTINGS:
        return False, f"Unknown setting: '{setting}'"
    
    config = SUPPORTED_SETTINGS[setting]
    
    # 类型检查
    if config.type == "boolean":
        if isinstance(value, bool):
            return True, None
        elif isinstance(value, str):
            lower = value.lower().strip()
            if lower in ["true", "false", "1", "0", "yes", "no"]:
                return True, None
        return False, f"{setting} requires true or false"
    
    elif config.type == "string":
        if not isinstance(value, str):
            return False, f"{setting} requires a string value"
        
        # 检查选项限制
        if config.options and value not in config.options:
            return False, f"Invalid value '{value}'. Options: {', '.join(config.options)}"
        
        return True, None
    
    elif config.type == "number":
        if not isinstance(value, (int, float)):
            # 尝试转换字符串为数字
            try:
                float(value)
                return True, None
            except (ValueError, TypeError):
                return False, f"{setting} requires a number"
        return True, None
    
    return False, f"Unsupported setting type: {config.type}"

def _coerce_value(setting: str, value: Any) -> Any:
    """将值转换为正确的类型"""
    if setting not in SUPPORTED_SETTINGS:
        return value
    
    config = SUPPORTED_SETTINGS[setting]
    
    if config.type == "boolean":
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            lower = value.lower().strip()
            if lower in ["true", "1", "yes"]:
                return True
            elif lower in ["false", "0", "no"]:
                return False
        elif isinstance(value, (int, float)):
            return bool(value)
    
    elif config.type == "number":
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            try:
                if "." in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                pass
    
    # 对于字符串或其他类型，直接返回
    return value

# ===== 核心实现函数 =====

def config(setting: str, value: Optional[str] = None) -> str:
    """
    获取或设置配置项（Claude Code ConfigTool的简化版本）。
    
    参数:
        setting: 配置项名称（如'theme'、'verbose'等）
        value: 配置值（可选，如果省略则是get操作）
    
    返回:
        JSON格式的结果，包含success、operation、setting、value等字段
    """
    start_time = time.time()
    
    try:
        # 1. 验证配置项
        if setting not in SUPPORTED_SETTINGS:
            result = {
                "success": False,
                "error": f"Unknown setting: '{setting}'",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        config_info = SUPPORTED_SETTINGS[setting]
        current_config = _get_current_config()
        
        # 2. GET操作（value为None或空字符串）
        if value is None or (isinstance(value, str) and value.strip() == ""):
            current_value = current_config.get(setting, config_info.default)
            
            # 格式化显示值
            display_value = current_value
            if config_info.type == "boolean":
                display_value = "true" if current_value else "false"
            
            result = {
                "success": True,
                "operation": "get",
                "setting": setting,
                "value": display_value,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3. SET操作
        # 3.1 获取当前值
        previous_value = current_config.get(setting, config_info.default)
        
        # 3.2 验证和转换值
        # 首先将字符串值转换为适当类型
        raw_value = value
        
        # 尝试推断类型
        if config_info.type == "boolean":
            if isinstance(value, str):
                lower = value.lower().strip()
                if lower in ["true", "1", "yes"]:
                    raw_value = True
                elif lower in ["false", "0", "no"]:
                    raw_value = False
        elif config_info.type == "number":
            if isinstance(value, str):
                try:
                    if "." in value:
                        raw_value = float(value)
                    else:
                        raw_value = int(value)
                except ValueError:
                    pass
        
        # 验证值
        is_valid, error_msg = _validate_setting_value(setting, raw_value)
        if not is_valid:
            result = {
                "success": False,
                "operation": "set",
                "setting": setting,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3.3 更新配置
        final_value = _coerce_value(setting, raw_value)
        success = _update_config(setting, final_value)
        
        if not success:
            result = {
                "success": False,
                "operation": "set",
                "setting": setting,
                "error": "Failed to save configuration",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3.4 返回成功结果
        result = {
            "success": True,
            "operation": "set",
            "setting": setting,
            "previousValue": previous_value,
            "newValue": final_value,
            "durationMs": int((time.time() - start_time) * 1000)
        }
        
        # 添加一些输出信息
        print(f"Config: Set '{setting}' from '{previous_value}' to '{final_value}'")
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # 捕获所有其他异常
        result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)

# ===== 工具注册 =====
__all__ = ["tools", "config", "SUPPORTED_SETTINGS"]