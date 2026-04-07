#!/usr/bin/env python3
"""
BriefTool implementation for AITools (Claude Code compatible version).
Send messages to the user with markdown formatting and optional status.
Simplified version focusing on cross-platform terminal output.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__BRIEF_MESSAGE_PROPERTY__ = property_param(
    name="message",
    description="The message for the user. Supports markdown formatting.",
    t="string",
    required=True
)

__BRIEF_ATTACHMENTS_PROPERTY__ = property_param(
    name="attachments",
    description="Optional file paths (absolute or relative to cwd) to attach as JSON string array. Use for photos, screenshots, diffs, logs, or any file the user should see alongside your message.",
    t="string",
    required=False
)

__BRIEF_STATUS_PROPERTY__ = property_param(
    name="status",
    description="Use 'proactive' when you're surfacing something the user hasn't asked for and needs to see now — task completion while they're away, a blocker you hit, an unsolicited status update. Use 'normal' when replying to something the user just said. Must be 'normal' or 'proactive'.",
    t="string",
    required=False
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class BriefConfig:
    """BriefTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        brief_enabled = os.getenv("BRIEF_ENABLED", "")
        brief_interactive = os.getenv("BRIEF_INTERACTIVE", "")
        brief_non_interactive_mode = os.getenv("BRIEF_NON_INTERACTIVE_MODE", "")
        
        config = {
            "BRIEF_ENABLED": True,  # 默认启用
            "BRIEF_INTERACTIVE": True,  # 默认交互模式
            "BRIEF_NON_INTERACTIVE_MODE": "print",  # 非交互模式行为
            "BRIEF_MAX_ATTACHMENT_SIZE_MB": 10,  # 最大附件大小(MB)
            "BRIEF_ALLOWED_IMAGE_EXTENSIONS": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg"],
            "BRIEF_ANALYTICS_ENABLED": False,  # 默认禁用分析
        }
        
        # 覆盖环境变量设置（如果非空）
        if brief_enabled != "":
            config["BRIEF_ENABLED"] = brief_enabled.lower() in ["true", "1", "yes", "y"]
        
        if brief_interactive != "":
            config["BRIEF_INTERACTIVE"] = brief_interactive.lower() in ["true", "1", "yes", "y"]
        
        if brief_non_interactive_mode != "":
            config["BRIEF_NON_INTERACTIVE_MODE"] = brief_non_interactive_mode
        
        return config

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_parameters(message: str, attachments: Optional[str], status: str) -> List[str]:
    """验证BriefTool参数"""
    errors = []
    
    # 验证消息
    if not message or not isinstance(message, str):
        errors.append("'message' must be a non-empty string")
    
    # 验证附件（JSON字符串）
    if attachments is not None:
        if not isinstance(attachments, str):
            errors.append("'attachments' must be a JSON string")
        else:
            try:
                parsed = json.loads(attachments)
                if not isinstance(parsed, list):
                    errors.append("'attachments' must be a JSON array of strings")
                else:
                    for i, attachment in enumerate(parsed):
                        if not isinstance(attachment, str):
                            errors.append(f"Attachment at index {i} must be a string")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in attachments: {str(e)}")
    
    # 验证状态
    if status not in ["normal", "proactive"]:
        errors.append("'status' must be one of: normal, proactive")
    
    return errors

def _format_message(message: str, status: str) -> str:
    """格式化消息用于显示"""
    status_prefix = "🔔 " if status == "proactive" else "💬 "
    return f"{status_prefix}{message}"

def _resolve_attachments(attachments_json: str, config: Dict) -> List[Dict]:
    """解析附件元数据（从JSON字符串）"""
    # 解析JSON
    attachments = json.loads(attachments_json)
    if not isinstance(attachments, list):
        raise ValueError("Attachments must be a JSON array")
    
    resolved = []
    
    for attachment in attachments:
        if not isinstance(attachment, str):
            raise ValueError(f"Attachment must be a string, got {type(attachment)}")
        
        if not os.path.exists(attachment):
            raise FileNotFoundError(f"Attachment not found: {attachment}")
        
        # 检查文件大小限制
        stat_info = os.stat(attachment)
        max_size_bytes = config["BRIEF_MAX_ATTACHMENT_SIZE_MB"] * 1024 * 1024
        
        if stat_info.st_size > max_size_bytes:
            size_mb = stat_info.st_size / (1024 * 1024)
            max_mb = config["BRIEF_MAX_ATTACHMENT_SIZE_MB"]
            raise ValueError(f"Attachment {attachment} is too large: {size_mb:.1f} MB > {max_mb} MB limit")
        
        # 检查文件类型（是否为图片）
        is_image = False
        ext = os.path.splitext(attachment)[1].lower()
        if ext in config["BRIEF_ALLOWED_IMAGE_EXTENSIONS"]:
            is_image = True
        
        resolved.append({
            "path": os.path.abspath(attachment),
            "size": stat_info.st_size,
            "is_image": is_image,
            "filename": os.path.basename(attachment)
        })
    
    return resolved

def _send_brief_message(message: str, attachments: Optional[List[Dict]], config: Dict):
    """发送brief消息（实际输出）"""
    
    # 简化的输出逻辑 - 交互和非交互模式都使用相同的输出
    # 在实际的Claude Code中，交互模式会使用UI组件，这里我们简化
    
    mode = config["BRIEF_NON_INTERACTIVE_MODE"] if not config["BRIEF_INTERACTIVE"] else "print"
    
    if mode == "print":
        if config["BRIEF_INTERACTIVE"]:
            # 交互模式的简化版本
            print(f"\n💬 {message}")
        else:
            # 非交互模式
            print(f"\n=== BRIEF MESSAGE ===")
            print(message)
            print("======================")
    elif mode == "log":
        print(f"[BRIEF] {message}")
    else:  # silent
        if config["BRIEF_INTERACTIVE"]:
            # 即使交互模式设置为silent，也至少显示消息
            print(f"\n{message}")
        # 否则不输出
    
    # 显示附件信息
    if attachments and len(attachments) > 0:
        print(f"\n📎 Attachments: {len(attachments)} file(s)")
        for att in attachments:
            size_mb = att["size"] / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB" if size_mb >= 1.0 else f"{att['size'] / 1024:.1f} KB"
            type_str = "image" if att["is_image"] else "file"
            print(f"   • {att['filename']} ({size_str}, {type_str})")

def _log_analytics_event(event_name: str, event_data: Dict):
    """记录分析事件（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(event_name, event_data)
    except:
        pass  # 分析是可选的

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__BRIEF_FUNCTION__ = function_ai(
    name="brief",
    description="Send a message to the user — your primary visible output channel, but not blocked to ask user questions. Use it to surface information.",
    parameters=parameters_func([
        __BRIEF_MESSAGE_PROPERTY__,
        __BRIEF_ATTACHMENTS_PROPERTY__,
        __BRIEF_STATUS_PROPERTY__
    ]),
)

tools = [__BRIEF_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def brief(message: str, attachments: Optional[str] = None, status: str = "normal"):
    """
    Send a message to the user with optional attachments.
    
    Args:
        message: The message for the user (supports markdown)
        attachments: Optional JSON string array of file paths to attach
        status: Message status - 'normal' or 'proactive'
        
    Returns:
        Dictionary with message, attachments metadata, and timestamp
    """
    # 验证参数
    errors = _validate_parameters(message, attachments, status)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")
    
    # 获取配置
    config = BriefConfig.from_env()
    
    # 检查brief是否启用
    if not config["BRIEF_ENABLED"]:
        raise RuntimeError("Brief tool is not enabled in configuration")
    
    # 解析附件
    resolved_attachments = None
    if attachments and len(attachments) > 0:
        resolved_attachments = _resolve_attachments(attachments, config)
    
    # 生成时间戳
    sent_at = datetime.utcnow().isoformat() + "Z"
    
    # 发送消息
    try:
        _send_brief_message(message, resolved_attachments, config)
    except Exception as e:
        # 回退到最基本输出
        print(f"\n[Brief Message: {status.upper()}]")
        print(message)
        if resolved_attachments:
            print(f"[With {len(resolved_attachments)} attachment(s)]")
    
    # 记录分析事件
    if config["BRIEF_ANALYTICS_ENABLED"]:
        _log_analytics_event(
            "brief_send",
            {
                "status": status,
                "attachment_count": len(resolved_attachments) if resolved_attachments else 0,
                "message_length": len(message)
            }
        )
    
    # 准备响应数据
    response_data = {
        "message": message,
        "sentAt": sent_at
    }
    
    if resolved_attachments:
        response_data["attachments"] = resolved_attachments
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return BriefConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

TOOL_CALL_MAP = {
    "brief": brief
}