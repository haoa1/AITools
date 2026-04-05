"""
SendMessageTool - 消息发送工具
Claude Code工具复刻，简化版本。
支持向队友、广播或本地对等节点发送消息。
"""

import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# ===== 工具实现 =====

def send_message_tool(
    to: str,
    message: Union[str, Dict[str, Any]],
    summary: Optional[str] = None,
) -> str:
    """
    发送消息给指定的接收者。
    
    参数:
        to: 接收者 - 队友名称、"*"（广播）、"uds:<socket-path>"（本地对等节点）、
                   "bridge:<session-id>"（远程控制对等节点）
        message: 消息内容 - 可以是纯文本字符串或结构化消息
        summary: 摘要（5-10个词的预览，当消息为字符串时需要）
    
    返回:
        JSON字符串格式的工具结果
    """
    start_time = time.time()
    
    try:
        # 生成消息ID
        message_id = str(uuid.uuid4())[:8]
        
        # 记录消息发送
        print(f"SendMessageTool: Sending message to '{to}'")
        if summary:
            print(f"  Summary: {summary}")
        
        # 处理消息内容
        if isinstance(message, dict):
            message_type = message.get('type', 'unknown')
            print(f"  Structured message type: {message_type}")
            message_content = json.dumps(message, ensure_ascii=False, indent=2)
        else:
            message_content = str(message)
            print(f"  Text message: {message_content[:100]}...")
        
        # 简化实现：仅记录消息，不实际发送
        # 在实际Claude Code中，这会通过邮箱系统发送给队友
        
        # 构建结果
        result = {
            "success": True,
            "messageId": message_id,
            "to": to,
            "summary": summary,
            "messageType": "text" if isinstance(message, str) else "structured",
            "timestamp": int(time.time() * 1000),
            "durationMs": int((time.time() - start_time) * 1000),
            "note": "Simplified implementation - message logged but not actually delivered"
        }
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # 错误处理
        result = {
            "success": False,
            "error": f"Failed to send message: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "send_message",
        "description": "Send a message to a teammate, broadcast, or peer. Supports plain text and structured messages.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient: teammate name, '*' for broadcast, 'uds:<socket-path>' for a local peer, or 'bridge:<session-id>' for a Remote Control peer"
                },
                "message": {
                    "type": ["string", "object"],
                    "description": "Message content - plain text or structured message object"
                },
                "summary": {
                    "type": "string",
                    "description": "A 5-10 word summary shown as a preview in the UI (required when message is a string)"
                }
            },
            "required": ["to", "message"]
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "send_message": send_message_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "send_message_tool"]