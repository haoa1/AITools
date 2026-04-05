#!/usr/bin/env python3
"""
ConfirmDialogTool implementation for AITools (Claude Code compatible version).
Provides simple yes/no confirmation dialogs for user interaction.
Simplified implementation focusing on cross-platform terminal compatibility.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__CONFIRM_MESSAGE_PROPERTY__ = property_param(
    name="message",
    description="The confirmation message to display to the user.",
    t="string",
    required=True
)

__CONFIRM_TITLE_PROPERTY__ = property_param(
    name="title",
    description="Optional title for the confirmation dialog (default: 'Confirmation').",
    t="string",
    required=False
)

__CONFIRM_DEFAULT_PROPERTY__ = property_param(
    name="default",
    description="Default response: 'yes', 'no', or 'none' (default: 'none').",
    t="string",
    required=False
)

__CONFIRM_BLOCKING_PROPERTY__ = property_param(
    name="blocking",
    description="Whether to block execution until user responds (default: true).",
    t="boolean",
    required=False
)

__CONFIRM_REQUIRE_CONFIRMATION_PROPERTY__ = property_param(
    name="require_confirmation",
    description="Whether to require explicit confirmation (default: true). If false, uses default response automatically.",
    t="boolean",
    required=False
)

__CONFIRM_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Timeout in seconds for blocking confirmation (default: 30).",
    t="number",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__CONFIRM_FUNCTION__ = function_ai(
    name="confirm_dialog",
    description="Display a confirmation dialog to the user with yes/no options.",
    parameters=parameters_func([
        __CONFIRM_MESSAGE_PROPERTY__,
        __CONFIRM_TITLE_PROPERTY__,
        __CONFIRM_DEFAULT_PROPERTY__,
        __CONFIRM_BLOCKING_PROPERTY__,
        __CONFIRM_REQUIRE_CONFIRMATION_PROPERTY__,
        __CONFIRM_TIMEOUT_PROPERTY__,
    ]),
)

tools = [__CONFIRM_FUNCTION__]

# ============================================================================
# Configuration and Constants
# ============================================================================

VALID_DEFAULTS = ["yes", "no", "none"]

class ConfirmDialogConfig:
    """Confirm dialog tool configuration."""
    
    def __init__(self):
        # 是否启用交互模式（默认为True）
        self.interactive_mode = True
        
        # 非交互模式下的默认行为
        # "auto_confirm": 自动确认（使用默认值）
        # "auto_reject": 自动拒绝
        # "simulate": 使用模拟确认
        self.non_interactive_mode = "auto_confirm"
        
        # 默认确认标题
        self.default_title = "Confirmation"
        
        # 默认响应
        self.default_response = "none"
        
        # 默认是否阻塞
        self.default_blocking = True
        
        # 默认是否需要确认
        self.default_require_confirmation = True
        
        # 默认超时时间（秒）
        self.default_timeout = 30
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Read from environment variables
        interactive = os.environ.get("CONFIRM_DIALOG_INTERACTIVE", "true").lower()
        config.interactive_mode = interactive in ("true", "1", "yes")
        
        config.non_interactive_mode = os.environ.get(
            "CONFIRM_DIALOG_NON_INTERACTIVE_MODE", 
            "auto_confirm"
        )
        
        config.default_title = os.environ.get(
            "CONFIRM_DIALOG_DEFAULT_TITLE", 
            "Confirmation"
        )
        
        config.default_response = os.environ.get(
            "CONFIRM_DIALOG_DEFAULT_RESPONSE",
            "none"
        )
        if config.default_response not in VALID_DEFAULTS:
            config.default_response = "none"
        
        blocking = os.environ.get("CONFIRM_DIALOG_DEFAULT_BLOCKING", "true").lower()
        config.default_blocking = blocking in ("true", "1", "yes")
        
        require_conf = os.environ.get("CONFIRM_DIALOG_DEFAULT_REQUIRE_CONFIRMATION", "true").lower()
        config.default_require_confirmation = require_conf in ("true", "1", "yes")
        
        try:
            config.default_timeout = int(os.environ.get(
                "CONFIRM_DIALOG_DEFAULT_TIMEOUT",
                "30"
            ))
        except ValueError:
            config.default_timeout = 30
        
        return config

def _get_config() -> ConfirmDialogConfig:
    """Get current configuration (re-read environment variables each time)."""
    return ConfirmDialogConfig.from_env()

# ============================================================================
# Helper Functions
# ============================================================================

def _format_confirmation_message(message: str, title: str, default: str) -> str:
    """Format confirmation message for display."""
    lines = []
    
    if title:
        lines.append(f"=== {title} ===")
    
    lines.append(message)
    lines.append("")
    
    # Add prompt based on default
    if default == "yes":
        lines.append("Confirm? (Y/n): ")
    elif default == "no":
        lines.append("Confirm? (y/N): ")
    else:
        lines.append("Confirm? (y/n): ")
    
    return "\n".join(lines)

def _display_confirmation(message: str, title: str, default: str) -> None:
    """Display confirmation dialog to the user."""
    formatted_message = _format_confirmation_message(message, title, default)
    print(formatted_message, file=sys.stderr, flush=True)

def _get_user_confirmation(default: str = "none") -> str:
    """
    Get user confirmation input.
    
    Args:
        default: Default response ("yes", "no", "none")
    
    Returns:
        "yes" or "no" based on user input
    """
    try:
        # Read user input
        response = input().strip().lower()
        
        # Handle empty response (use default)
        if not response:
            if default == "yes":
                return "yes"
            elif default == "no":
                return "no"
            else:
                # No default, ask again or treat as no?
                return "no"
        
        # Parse response
        if response in ("y", "yes", "1", "true"):
            return "yes"
        elif response in ("n", "no", "0", "false"):
            return "no"
        else:
            # Invalid input, use default or ask again?
            if default == "yes":
                return "yes"
            elif default == "no":
                return "no"
            else:
                return "no"  # Default to no for invalid input
    
    except EOFError:
        # Handle non-interactive environments
        if default == "yes":
            return "yes"
        elif default == "no":
            return "no"
        else:
            return "no"  # Default to no in non-interactive

def _validate_parameters(
    message: str, 
    title: str, 
    default: str, 
    blocking: bool, 
    require_confirmation: bool,
    timeout: int
) -> List[str]:
    """Validate input parameters and return list of errors (empty if valid)."""
    errors = []
    
    if not message or not isinstance(message, str):
        errors.append("'message' must be a non-empty string")
    
    if title and not isinstance(title, str):
        errors.append("'title' must be a string or empty")
    
    if default not in VALID_DEFAULTS:
        errors.append(f"'default' must be one of: {', '.join(VALID_DEFAULTS)}")
    
    if not isinstance(blocking, bool):
        errors.append("'blocking' must be a boolean")
    
    if not isinstance(require_confirmation, bool):
        errors.append("'require_confirmation' must be a boolean")
    
    if not isinstance(timeout, (int, float)) or timeout < 0:
        errors.append("'timeout' must be a non-negative number")
    
    return errors

# ============================================================================
# Core Implementation
# ============================================================================

def confirm_dialog(
    message: str,
    title: str = "",
    default: str = "none",
    blocking: bool = True,
    require_confirmation: bool = True,
    timeout: int = 30
) -> str:
    """
    Main confirmation dialog function - displays confirmation dialog to user.
    
    Args:
        message: The confirmation message to display
        title: Optional title for the dialog
        default: Default response: 'yes', 'no', or 'none'
        blocking: Whether to block execution until user responds
        require_confirmation: Whether to require explicit confirmation
        timeout: Timeout in seconds for blocking confirmation
    
    Returns:
        JSON string with confirmation results
    """
    start_time = time.time()
    
    try:
        config = _get_config()
        
        # Use defaults if parameters not provided
        if not title:
            title = config.default_title
        if not default or default not in VALID_DEFAULTS:
            default = config.default_response
        if blocking is None:
            blocking = config.default_blocking
        if require_confirmation is None:
            require_confirmation = config.default_require_confirmation
        if timeout is None:
            timeout = config.default_timeout
        
        # Validate parameters
        errors = _validate_parameters(
            message, title, default, blocking, require_confirmation, timeout
        )
        if errors:
            result = {
                "success": False,
                "error": f"Parameter validation failed: {'; '.join(errors)}",
                "message": message,
                "title": title,
                "default": default,
                "blocking": blocking,
                "require_confirmation": require_confirmation,
                "timeout": timeout,
                "operation": "confirm_dialog",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # Prepare result structure
        result = {
            "success": True,
            "message": message,
            "title": title,
            "confirmed": False,
            "user_response": None,
            "timed_out": False,
            "used_default": False,
            "elapsed_time": 0
        }
        
        # Check if we're in interactive mode
        interactive_mode = config.interactive_mode
        
        if not interactive_mode or not require_confirmation:
            # Non-interactive mode or confirmation not required
            if config.non_interactive_mode == "auto_confirm":
                # Auto-confirm
                result["confirmed"] = True
                result["used_default"] = True
                result["user_response"] = "yes"
            elif config.non_interactive_mode == "auto_reject":
                # Auto-reject
                result["confirmed"] = False
                result["used_default"] = True
                result["user_response"] = "no"
            else:
                # Simulate based on default
                if default == "yes":
                    result["confirmed"] = True
                    result["user_response"] = "yes"
                elif default == "no":
                    result["confirmed"] = False
                    result["user_response"] = "no"
                else:
                    # No default, reject
                    result["confirmed"] = False
                    result["user_response"] = "no"
                result["used_default"] = True
            
            # Add metadata and return
            result["operation"] = "confirm_dialog"
            result["durationMs"] = int((time.time() - start_time) * 1000)
            return json.dumps(result, ensure_ascii=False)
        
        # Display the confirmation dialog
        _display_confirmation(message, title, default)
        result["displayed"] = True
        
        # Handle blocking confirmations
        if blocking:
            # Get user confirmation
            response = _get_user_confirmation(default)
            result["user_response"] = response
            result["confirmed"] = (response == "yes")
        else:
            # Non-blocking confirmation
            # In non-blocking mode with interactive, we still need to show dialog
            # but we can't wait for response. We'll use default.
            if default == "yes":
                result["confirmed"] = True
                result["user_response"] = "yes"
            elif default == "no":
                result["confirmed"] = False
                result["user_response"] = "no"
            else:
                # No default, reject for non-blocking
                result["confirmed"] = False
                result["user_response"] = "no"
            result["used_default"] = True
        
        result["elapsed_time"] = time.time() - start_time
        
        # Add metadata for Claude Code compatibility
        result["operation"] = "confirm_dialog"
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Handle unexpected errors
        error_result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "operation": "confirm_dialog",
            "message": message,
            "title": title,
            "default": default,
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ============================================================================
# Tool Registration
# ============================================================================

__all__ = ["tools", "confirm_dialog", "ConfirmDialogConfig"]