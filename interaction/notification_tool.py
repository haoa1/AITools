#!/usr/bin/env python3
"""
NotificationTool implementation for AITools (Claude Code compatible version).
Provides user notification with different message levels and optional confirmation.
Simplified implementation focusing on cross-platform terminal compatibility.
"""

import os
import sys
import json
import time
import select
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__NOTIFICATION_MESSAGE_PROPERTY__ = property_param(
    name="message",
    description="The notification message to display.",
    t="string",
    required=True
)

__NOTIFICATION_LEVEL_PROPERTY__ = property_param(
    name="level",
    description="Message level: 'info', 'warning', 'error', 'success' (default: 'info').",
    t="string",
    required=False
)

__NOTIFICATION_BLOCKING_PROPERTY__ = property_param(
    name="blocking",
    description="Whether to block execution until user responds (default: false).",
    t="boolean",
    required=False
)

__NOTIFICATION_CONTINUE_CONDITION_PROPERTY__ = property_param(
    name="continue_condition",
    description="Condition to continue: 'user_input', 'timeout', 'specific_answer' (default: 'user_input').",
    t="string",
    required=False
)

__NOTIFICATION_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Timeout in seconds when continue_condition is 'timeout' (default: 30).",
    t="number",
    required=False
)

__NOTIFICATION_SPECIFIC_ANSWER_PROPERTY__ = property_param(
    name="specific_answer",
    description="Specific answer to wait for when continue_condition is 'specific_answer'.",
    t="string",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__NOTIFICATION_FUNCTION__ = function_ai(
    name="notify_user",
    description="Send a notification to the user with configurable level and blocking behavior.",
    parameters=parameters_func([
        __NOTIFICATION_MESSAGE_PROPERTY__,
        __NOTIFICATION_LEVEL_PROPERTY__,
        __NOTIFICATION_BLOCKING_PROPERTY__,
        __NOTIFICATION_CONTINUE_CONDITION_PROPERTY__,
        __NOTIFICATION_TIMEOUT_PROPERTY__,
        __NOTIFICATION_SPECIFIC_ANSWER_PROPERTY__,
    ]),
)

tools = [__NOTIFICATION_FUNCTION__]

# ============================================================================
# Configuration and Constants
# ============================================================================

VALID_LEVELS = ["info", "warning", "error", "success"]
VALID_CONTINUE_CONDITIONS = ["user_input", "timeout", "specific_answer"]

class NotificationConfig:
    """Notification tool configuration."""
    
    def __init__(self):
        # 是否启用交互模式（默认为True）
        self.interactive_mode = True
        
        # 非交互模式下的默认行为
        # "auto_continue": 自动继续（相当于非阻塞）
        # "simulate": 使用模拟确认（基于消息内容）
        self.non_interactive_mode = "auto_continue"
        
        # 默认通知级别
        self.default_level = "info"
        
        # 默认是否阻塞（等待用户确认）
        self.default_blocking = False
        
        # 默认继续条件
        self.default_continue_condition = "user_input"
        
        # 超时时间（秒），仅当continue_condition包含timeout时使用
        self.default_timeout = 30
        
        # 特定答案（当continue_condition为specific_answer时使用）
        self.default_specific_answer = "continue"
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Read from environment variables
        interactive = os.environ.get("NOTIFICATION_INTERACTIVE", "true").lower()
        config.interactive_mode = interactive in ("true", "1", "yes")
        
        config.non_interactive_mode = os.environ.get(
            "NOTIFICATION_NON_INTERACTIVE_MODE", 
            "auto_continue"
        )
        
        config.default_level = os.environ.get(
            "NOTIFICATION_DEFAULT_LEVEL", 
            "info"
        )
        
        blocking = os.environ.get("NOTIFICATION_DEFAULT_BLOCKING", "false").lower()
        config.default_blocking = blocking in ("true", "1", "yes")
        
        config.default_continue_condition = os.environ.get(
            "NOTIFICATION_DEFAULT_CONTINUE_CONDITION",
            "user_input"
        )
        
        try:
            config.default_timeout = int(os.environ.get(
                "NOTIFICATION_DEFAULT_TIMEOUT",
                "30"
            ))
        except ValueError:
            config.default_timeout = 30
        
        config.default_specific_answer = os.environ.get(
            "NOTIFICATION_DEFAULT_SPECIFIC_ANSWER",
            "continue"
        )
        
        return config

def _get_config() -> NotificationConfig:
    """Get current configuration (re-read environment variables each time)."""
    return NotificationConfig.from_env()

# ============================================================================
# Helper Functions
# ============================================================================

def _format_notification_message(message: str, level: str) -> str:
    """Format notification message with appropriate prefix and formatting."""
    prefixes = {
        "info": "[INFO]",
        "warning": "[WARNING]",
        "error": "[ERROR]",
        "success": "[SUCCESS]"
    }
    
    prefix = prefixes.get(level, "[INFO]")
    
    # Add visual formatting based on level
    formatting = {
        "info": "",  # No special formatting
        "warning": "\033[33m",  # Yellow
        "error": "\033[31m",    # Red
        "success": "\033[32m",  # Green
    }
    
    color = formatting.get(level, "")
    reset = "\033[0m" if color else ""
    
    # Create formatted message
    formatted = f"{color}{prefix} {message}{reset}"
    return formatted

def _display_notification(message: str, level: str) -> None:
    """Display notification to the user."""
    formatted_message = _format_notification_message(message, level)
    print(formatted_message, file=sys.stderr)

def _get_user_confirmation(prompt: str = "Press Enter to continue...") -> str:
    """Get user confirmation."""
    try:
        return input(prompt).strip()
    except EOFError:
        # Handle non-interactive environments (like pipes)
        return ""

def _validate_parameters(message: str, level: str, blocking: bool, 
                        continue_condition: str, timeout: int, 
                        specific_answer: Optional[str]) -> List[str]:
    """Validate input parameters and return list of errors (empty if valid)."""
    errors = []
    
    if not message or not isinstance(message, str):
        errors.append("'message' must be a non-empty string")
    
    if level not in VALID_LEVELS:
        errors.append(f"'level' must be one of: {', '.join(VALID_LEVELS)}")
    
    if not isinstance(blocking, bool):
        errors.append("'blocking' must be a boolean")
    
    if continue_condition not in VALID_CONTINUE_CONDITIONS:
        errors.append(f"'continue_condition' must be one of: {', '.join(VALID_CONTINUE_CONDITIONS)}")
    
    if not isinstance(timeout, (int, float)) or timeout < 0:
        errors.append("'timeout' must be a non-negative number")
    
    if continue_condition == "specific_answer" and (not specific_answer or not isinstance(specific_answer, str)):
        errors.append("'specific_answer' must be a non-empty string when 'continue_condition' is 'specific_answer'")
    
    return errors

# ============================================================================
# Core Implementation
# ============================================================================

def notify_user(
    message: str,
    level: str = "info",
    blocking: bool = False,
    continue_condition: str = "user_input",
    timeout: int = 30,
    specific_answer: Optional[str] = None
) -> str:
    """
    Main notification function - sends notification to user.
    
    Args:
        message: The notification message to display
        level: Message level: 'info', 'warning', 'error', 'success'
        blocking: Whether to block execution until user responds
        continue_condition: Condition to continue: 'user_input', 'timeout', 'specific_answer'
        timeout: Timeout in seconds (for 'timeout' condition)
        specific_answer: Specific answer to wait for (for 'specific_answer' condition)
    
    Returns:
        JSON string with notification results
    """
    start_time = time.time()
    
    try:
        config = _get_config()
        
        # Use defaults if parameters not provided
        if not level:
            level = config.default_level
        if blocking is None:
            blocking = config.default_blocking
        if not continue_condition:
            continue_condition = config.default_continue_condition
        if timeout is None:
            timeout = config.default_timeout
        if continue_condition == "specific_answer" and not specific_answer:
            specific_answer = config.default_specific_answer
        
        # Validate parameters
        errors = _validate_parameters(message, level, blocking, continue_condition, 
                                     timeout, specific_answer)
        if errors:
            result = {
                "success": False,
                "error": f"Parameter validation failed: {'; '.join(errors)}",
                "message": message,
                "level": level,
                "blocking": blocking,
                "continue_condition": continue_condition,
                "timeout": timeout,
                "specific_answer": specific_answer,
                "operation": "notify_user",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # Prepare result structure
        result = {
            "success": True,
            "message": message,
            "level": level,
            "displayed": False,
            "confirmed": False,
            "user_response": None,
            "timed_out": False,
            "elapsed_time": 0
        }
        
        # Check if we're in interactive mode
        interactive_mode = config.interactive_mode
        
        if not interactive_mode:
            # Non-interactive mode
            if config.non_interactive_mode == "auto_continue":
                # Just log the notification and continue
                result["displayed"] = True
                result["confirmed"] = True  # Auto-confirmed
                result["elapsed_time"] = time.time() - start_time
            else:
                # Simulate based on message content
                result["displayed"] = True
                result["confirmed"] = True  # Default to confirmed
                result["user_response"] = "simulated"
                result["elapsed_time"] = time.time() - start_time
            
            # Add metadata and return
            result["operation"] = "notify_user"
            result["durationMs"] = int((time.time() - start_time) * 1000)
            return json.dumps(result, ensure_ascii=False)
        
        # Display the notification
        _display_notification(message, level)
        result["displayed"] = True
        
        # Handle blocking notifications
        if blocking:
            if continue_condition == "user_input":
                # Wait for user input
                response = _get_user_confirmation("Press Enter to continue...")
                result["user_response"] = response
                result["confirmed"] = True
                
            elif continue_condition == "timeout":
                # Wait with timeout
                print(f"Waiting up to {timeout} seconds (press Enter to continue)...", file=sys.stderr)
                
                # Use select to wait for input with timeout
                if select.select([sys.stdin], [], [], timeout)[0]:
                    response = _get_user_confirmation()
                    result["user_response"] = response
                    result["confirmed"] = True
                else:
                    result["timed_out"] = True
                    result["confirmed"] = False
                    
            elif continue_condition == "specific_answer":
                # Wait for specific answer
                if specific_answer:
                    response = input(f"Type '{specific_answer}' to continue: ").strip()
                    result["user_response"] = response
                    result["confirmed"] = (response.lower() == specific_answer.lower())
                else:
                    result["error"] = "No specific_answer provided but continue_condition is 'specific_answer'"
                    result["success"] = False
        else:
            # Non-blocking notification
            result["confirmed"] = True  # Auto-confirmed for non-blocking
        
        result["elapsed_time"] = time.time() - start_time
        
        # Add metadata for Claude Code compatibility
        result["operation"] = "notify_user"
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Handle unexpected errors
        error_result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "operation": "notify_user",
            "message": message,
            "level": level,
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ============================================================================
# Tool Registration
# ============================================================================

__all__ = ["tools", "notify_user", "NotificationConfig"]