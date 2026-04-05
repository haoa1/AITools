#!/usr/bin/env python3
"""
EnterPlanModeTool implementation for AITools (Claude Code compatible version - simplified).
Provides plan mode entry functionality aligned with Claude Code's EnterPlanModeTool.
Based on analysis of Claude Code source: restored-src/src/tools/EnterPlanModeTool/EnterPlanModeTool.ts
Simplified version focusing on basic plan mode entry.
"""

import os
import json
import time
from base import function_ai, parameters_func, property_param

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__ENTER_PLAN_MODE_TOOL_FUNCTION__ = function_ai(
    name="enter_plan_mode_tool",
    description="Requests permission to enter plan mode for complex tasks requiring exploration and design. Compatible with Claude Code's EnterPlanModeTool (simplified version).",
    parameters=parameters_func([]),  # No parameters needed
)

tools = [__ENTER_PLAN_MODE_TOOL_FUNCTION__]

# ============================================================================
# Configuration and Constants
# ============================================================================

class EnterPlanModeConfig:
    """Enter plan mode tool configuration."""
    
    def __init__(self):
        # 是否启用交互模式（默认为True）
        self.interactive_mode = True
        
        # 非交互模式下的默认行为
        # "auto_enter": 自动进入计划模式
        # "auto_reject": 自动拒绝进入计划模式
        # "simulate": 使用模拟确认
        self.non_interactive_mode = "auto_enter"
        
        # 默认确认消息
        self.default_message = "Plan mode entered successfully"
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Read from environment variables
        interactive = os.environ.get("ENTER_PLAN_MODE_INTERACTIVE", "true").lower()
        config.interactive_mode = interactive in ("true", "1", "yes")
        
        config.non_interactive_mode = os.environ.get(
            "ENTER_PLAN_MODE_NON_INTERACTIVE_MODE", 
            "auto_enter"
        )
        
        config.default_message = os.environ.get(
            "ENTER_PLAN_MODE_DEFAULT_MESSAGE", 
            "Plan mode entered successfully"
        )
        
        return config

def _get_config() -> EnterPlanModeConfig:
    """Get current configuration (re-read environment variables each time)."""
    return EnterPlanModeConfig.from_env()

# ============================================================================
# Core Implementation
# ============================================================================

def enter_plan_mode_tool() -> str:
    """
    Main enter plan mode function - requests permission to enter plan mode.
    
    Returns:
        JSON string with operation results
    """
    start_time = time.time()
    
    try:
        config = _get_config()
        
        # Prepare result structure
        result = {
            "success": True,
            "message": "",
            "plan_mode_entered": False,
            "permission_granted": False,
            "requires_confirmation": True,
            "elapsed_time": 0
        }
        
        # Check if we're in interactive mode
        interactive_mode = config.interactive_mode
        
        if not interactive_mode:
            # Non-interactive mode
            if config.non_interactive_mode == "auto_enter":
                # Auto-enter plan mode
                result["plan_mode_entered"] = True
                result["permission_granted"] = True
                result["requires_confirmation"] = False
                result["message"] = config.default_message
            elif config.non_interactive_mode == "auto_reject":
                # Auto-reject plan mode entry
                result["plan_mode_entered"] = False
                result["permission_granted"] = False
                result["requires_confirmation"] = False
                result["message"] = "Plan mode entry rejected (non-interactive mode)"
            else:
                # Simulate entry
                result["plan_mode_entered"] = True
                result["permission_granted"] = True
                result["requires_confirmation"] = False
                result["message"] = config.default_message
            
            # Add metadata and return
            result["operation"] = "enter_plan_mode_tool"
            result["durationMs"] = int((time.time() - start_time) * 1000)
            return json.dumps(result, ensure_ascii=False)
        
        # Interactive mode - in simplified version, we auto-enter
        # In a full implementation, this would request user confirmation
        result["plan_mode_entered"] = True
        result["permission_granted"] = True
        result["requires_confirmation"] = True
        result["message"] = config.default_message
        
        result["elapsed_time"] = time.time() - start_time
        
        # Add metadata for Claude Code compatibility
        result["operation"] = "enter_plan_mode_tool"
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Handle unexpected errors
        error_result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "operation": "enter_plan_mode_tool",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ============================================================================
# Tool Registration
# ============================================================================

__all__ = ["tools", "enter_plan_mode_tool", "EnterPlanModeConfig"]