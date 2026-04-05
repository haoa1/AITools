#!/usr/bin/env python3
"""
TaskOutputTool implementation for AITools (Claude Code compatible version - simplified).
Provides task output retrieval functionality aligned with Claude Code's TaskOutputTool.
Based on analysis of Claude Code source: restored-src/src/tools/TaskOutputTool/TaskOutputTool.tsx
Simplified version focusing on basic task output retrieval.
"""

import os
import sys
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__TASK_OUTPUT_TASK_ID_PROPERTY__ = property_param(
    name="task_id",
    description="The task ID to get output from.",
    t="string",
    required=True
)

__TASK_OUTPUT_BLOCK_PROPERTY__ = property_param(
    name="block",
    description="Whether to wait for completion (default: true).",
    t="boolean",
    required=False
)

__TASK_OUTPUT_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Max wait time in milliseconds (default: 30000, max: 600000).",
    t="number",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__TASK_OUTPUT_TOOL_FUNCTION__ = function_ai(
    name="task_output_tool",
    description="Get output from a task by its ID. Can wait for completion if task is still running.",
    parameters=parameters_func([
        __TASK_OUTPUT_TASK_ID_PROPERTY__,
        __TASK_OUTPUT_BLOCK_PROPERTY__,
        __TASK_OUTPUT_TIMEOUT_PROPERTY__,
    ]),
)

tools = [__TASK_OUTPUT_TOOL_FUNCTION__]

# ============================================================================
# Configuration and Constants
# ============================================================================

class TaskOutputConfig:
    """Task output tool configuration."""
    
    def __init__(self):
        # 默认是否阻塞等待
        self.default_block = True
        
        # 默认超时时间（毫秒）
        self.default_timeout = 30000
        
        # 最大超时时间（毫秒）
        self.max_timeout = 600000
        
        # 任务输出目录（用于模拟任务输出）
        self.task_output_dir = "/tmp/aitools_tasks"
        
        # 是否启用模拟模式（当没有真实任务管理器时）
        self.simulation_mode = True
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Read from environment variables
        block = os.environ.get("TASK_OUTPUT_DEFAULT_BLOCK", "true").lower()
        config.default_block = block in ("true", "1", "yes")
        
        try:
            config.default_timeout = int(os.environ.get(
                "TASK_OUTPUT_DEFAULT_TIMEOUT",
                "30000"
            ))
        except ValueError:
            config.default_timeout = 30000
        
        try:
            config.max_timeout = int(os.environ.get(
                "TASK_OUTPUT_MAX_TIMEOUT",
                "600000"
            ))
        except ValueError:
            config.max_timeout = 600000
        
        config.task_output_dir = os.environ.get(
            "TASK_OUTPUT_DIR",
            "/tmp/aitools_tasks"
        )
        
        simulation = os.environ.get("TASK_OUTPUT_SIMULATION_MODE", "true").lower()
        config.simulation_mode = simulation in ("true", "1", "yes")
        
        return config

def _get_config() -> TaskOutputConfig:
    """Get current configuration (re-read environment variables each time)."""
    return TaskOutputConfig.from_env()

# ============================================================================
# Helper Functions
# ============================================================================

def _validate_parameters(
    task_id: str, 
    block: bool, 
    timeout: int
) -> List[str]:
    """Validate input parameters and return list of errors (empty if valid)."""
    errors = []
    
    if not task_id or not isinstance(task_id, str):
        errors.append("'task_id' must be a non-empty string")
    
    if block is not None and not isinstance(block, bool):
        errors.append("'block' must be a boolean or None")
    
    if timeout is not None:
        if not isinstance(timeout, (int, float)) or timeout < 0:
            errors.append("'timeout' must be a non-negative number")
        else:
            # Only check max timeout if timeout is valid number
            config = _get_config()
            if timeout > config.max_timeout:
                errors.append(f"'timeout' must not exceed {config.max_timeout} ms")
    
    return errors

def _get_simulated_task_output(task_id: str, block: bool, timeout: int) -> Dict[str, Any]:
    """
    Get simulated task output (for when no real task manager is available).
    
    Args:
        task_id: Task ID
        block: Whether to block
        timeout: Timeout in ms
    
    Returns:
        Simulated task output
    """
    # Simulate different task states based on task_id
    import random
    
    # Generate deterministic but varied output based on task_id hash
    task_hash = hash(task_id) % 100
    
    # Task type distribution
    if task_hash < 40:
        task_type = "bash"
        status = "completed"
        exit_code = 0
        output = f"Command executed successfully.\nTask ID: {task_id}\nTimestamp: {time.time()}"
    elif task_hash < 70:
        task_type = "agent"
        status = "completed" if block else "running"
        exit_code = None
        output = f"Agent task completed.\nTask ID: {task_id}\nResult: Simulated agent output"
        prompt = "Simulated agent prompt"
        result = "Simulated agent result"
    elif task_hash < 90:
        task_type = "shell"
        status = "failed"
        exit_code = 1
        output = f"Command failed with exit code 1.\nTask ID: {task_id}\nError: Simulated error"
        error = "Simulated command failure"
    else:
        task_type = "unknown"
        status = "pending"
        exit_code = None
        output = f"Task pending.\nTask ID: {task_id}"
    
    # Build result
    result = {
        "task_id": task_id,
        "task_type": task_type,
        "status": status,
        "description": f"Simulated {task_type} task",
        "output": output,
    }
    
    if exit_code is not None:
        result["exitCode"] = exit_code
    
    if task_hash < 70 and task_type == "agent":
        result["prompt"] = prompt
        result["result"] = result.get("result", "Simulated agent result")
    
    if task_hash >= 70 and task_hash < 90:
        result["error"] = error
    
    # If blocking, simulate some delay
    if block:
        # Simulate processing time (0-2 seconds)
        delay = min(timeout / 1000.0, 2.0) * (task_hash / 100.0)
        time.sleep(delay)
    
    return result

def _read_task_output_file(task_id: str, config: TaskOutputConfig) -> Optional[Dict[str, Any]]:
    """
    Read task output from file (if task manager writes output to files).
    
    Args:
        task_id: Task ID
        config: Configuration
    
    Returns:
        Task output dict or None if not found
    """
    import os.path
    
    output_file = os.path.join(config.task_output_dir, f"{task_id}.json")
    
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    return None

# ============================================================================
# Core Implementation
# ============================================================================

def task_output_tool(
    task_id: str,
    block: bool = None,
    timeout: int = None
) -> str:
    """
    Main task output function - gets output from a task by ID.
    
    Args:
        task_id: The task ID to get output from
        block: Whether to wait for completion
        timeout: Max wait time in milliseconds
    
    Returns:
        JSON string with task output results
    """
    start_time = time.time()
    
    try:
        config = _get_config()
        
        # Use defaults if parameters not provided
        if block is None:
            block = config.default_block
        if timeout is None:
            timeout = config.default_timeout
        
        # Convert timeout from ms to seconds for Python
        timeout_seconds = timeout / 1000.0
        
        # Validate parameters
        errors = _validate_parameters(task_id, block, timeout)
        if errors:
            result = {
                "success": False,
                "error": f"Parameter validation failed: {'; '.join(errors)}",
                "task_id": task_id,
                "block": block,
                "timeout": timeout,
                "operation": "task_output_tool",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # Prepare result structure
        result = {
            "success": True,
            "task_id": task_id,
            "block": block,
            "timeout": timeout,
            "output_available": False,
            "task_completed": False,
            "wait_time_ms": 0,
            "elapsed_time": 0
        }
        
        # Try to get real task output first (if task manager is available)
        task_output = None
        
        # Check if we have a task manager module
        try:
            # Try to import and use real task manager
            from system.task_manager import get_task_output as real_get_task_output
            task_output = real_get_task_output(task_id, block, timeout_seconds)
        except ImportError:
            # Task manager not available, use simulation
            pass
        except Exception as e:
            # Task manager error, fall back to simulation
            print(f"Task manager error: {e}", file=sys.stderr)
        
        # If no real task output, try reading from file
        if task_output is None:
            task_output = _read_task_output_file(task_id, config)
        
        # If still no task output, use simulation
        if task_output is None and config.simulation_mode:
            task_output = _get_simulated_task_output(task_id, block, timeout)
        
        if task_output:
            result["output_available"] = True
            result["task_output"] = task_output
            
            # Check if task is completed
            status = task_output.get("status", "").lower()
            result["task_completed"] = status in ("completed", "failed", "stopped")
            
            # Add task metadata to result
            for key in ["task_type", "status", "description", "exitCode", "error"]:
                if key in task_output:
                    result[key] = task_output[key]
        else:
            result["output_available"] = False
            result["error"] = f"Task '{task_id}' not found or no output available"
        
        result["elapsed_time"] = time.time() - start_time
        result["wait_time_ms"] = int(result["elapsed_time"] * 1000)
        
        # Add metadata for Claude Code compatibility
        result["operation"] = "task_output_tool"
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Handle unexpected errors
        error_result = {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "operation": "task_output_tool",
            "task_id": task_id,
            "block": block,
            "timeout": timeout,
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ============================================================================
# Tool Registration
# ============================================================================

__all__ = ["tools", "task_output_tool", "TaskOutputConfig"]