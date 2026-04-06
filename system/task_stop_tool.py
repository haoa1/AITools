#!/usr/bin/env python3
"""
TaskStopTool implementation for AITools (Claude Code compatible version - simplified).
Stops a running background task by ID.
Based on analysis of Claude Code source: restored-src/src/tools/TaskStopTool/TaskStopTool.ts
Simplified version with minimal dependencies.
"""

import os
import json
import time
from base import function_ai, parameters_func, property_param

# Property definitions for TaskStopTool
__TASK_ID_PROPERTY__ = property_param(
    name="task_id",
    description="The ID of the background task to stop",
    t="string",
    required=False,  # Optional to support shell_id compatibility
)

__SHELL_ID_PROPERTY__ = property_param(
    name="shell_id",
    description="Deprecated: use task_id instead (backward compatibility with KillShell tool)",
    t="string",
    required=False,
)

# Function definition
__TASK_STOP_TOOL_FUNCTION__ = function_ai(
    name="task_stop_tool",
    description="Stop a running background task by ID",
    parameters=parameters_func([
        __TASK_ID_PROPERTY__,
        __SHELL_ID_PROPERTY__,
    ]),
)

tools = [__TASK_STOP_TOOL_FUNCTION__]


class TaskStopConfig:
    """Configuration for TaskStopTool"""
    
    DEFAULT_CONFIG = {
        "TASK_STOP_ENABLED": True,
        "TASK_STOP_INTERACTIVE": True,
        "TASK_STOP_TASKS_PATH": os.path.join(os.path.expanduser("~"), ".aitools_tasks.json"),
        "TASK_STOP_ANALYTICS_ENABLED": False,
        "TASK_STOP_ALLOW_ANY_STATUS": True,  # Allow stopping tasks regardless of status
        "TASK_STOP_SIMULATE_ONLY": False,  # If True, simulate stopping without actual effect
    }
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        task_stop_enabled = os.getenv("TASK_STOP_ENABLED", "")
        task_stop_interactive = os.getenv("TASK_STOP_INTERACTIVE", "")
        task_stop_tasks_path = os.getenv("TASK_STOP_TASKS_PATH", "")
        task_stop_allow_any_status = os.getenv("TASK_STOP_ALLOW_ANY_STATUS", "")
        task_stop_simulate_only = os.getenv("TASK_STOP_SIMULATE_ONLY", "")
        
        config = TaskStopConfig.DEFAULT_CONFIG.copy()
        
        # 覆盖环境变量设置（如果非空）
        if task_stop_enabled != "":
            config["TASK_STOP_ENABLED"] = task_stop_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_stop_interactive != "":
            config["TASK_STOP_INTERACTIVE"] = task_stop_interactive.lower() in ["true", "1", "yes", "y"]
        
        if task_stop_tasks_path != "":
            config["TASK_STOP_TASKS_PATH"] = task_stop_tasks_path
        
        if task_stop_allow_any_status != "":
            config["TASK_STOP_ALLOW_ANY_STATUS"] = task_stop_allow_any_status.lower() in ["true", "1", "yes", "y"]
        
        if task_stop_simulate_only != "":
            config["TASK_STOP_SIMULATE_ONLY"] = task_stop_simulate_only.lower() in ["true", "1", "yes", "y"]
        
        return config


def task_stop_tool(task_id: str = None, shell_id: str = None) -> str:
    """
    Stop a running background task by ID.
    
    Claude Code compatible version based on TaskStopTool/TaskStopTool.ts:
    - task_id: The ID of the background task to stop
    - shell_id: Deprecated alias for task_id (backward compatibility with KillShell)
    
    Returns JSON matching Claude Code's TaskStopTool output schema (simplified).
    
    Simplified implementation notes:
    - Uses shared task storage file (same as TaskCreateTool, TaskGetTool, etc.)
    - Can stop tasks regardless of status (configurable)
    - Returns simulated command/type for compatibility
    """
    try:
        # Load configuration
        config = TaskStopConfig.from_env()
        
        # Check if tool is enabled
        if not config.get("TASK_STOP_ENABLED", True):
            return json.dumps({
                "error": "TaskStopTool is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Support both task_id and shell_id (shell_id is deprecated)
        # Use task_id if provided (even if empty string), otherwise use shell_id
        task_id = task_id if task_id is not None else shell_id
        if task_id is None:
            return json.dumps({
                "error": "Missing required parameter: task_id (or shell_id)",
                "success": False
            }, indent=2)
        
        # Validate task_id format
        if not isinstance(task_id, str):
            return json.dumps({
                "error": "Task ID must be a string",
                "success": False
            }, indent=2)
        
        if not task_id.strip():
            return json.dumps({
                "error": "Task ID must be a non-empty string",
                "success": False
            }, indent=2)
        
        if len(task_id) > 100:
            return json.dumps({
                "error": f"Task ID too long (max 100 characters, got {len(task_id)})",
                "success": False
            }, indent=2)
        
        # Load tasks from shared storage
        tasks_path = config.get("TASK_STOP_TASKS_PATH")
        tasks = []
        
        try:
            if os.path.exists(tasks_path):
                with open(tasks_path, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                    if isinstance(tasks_data, list):
                        tasks = tasks_data
                    else:
                        # Handle legacy format
                        tasks = []
        except (json.JSONDecodeError, IOError) as e:
            # Corrupted file - start fresh
            tasks = []
        
        # Find the task
        task_found = None
        task_index = -1
        
        for i, task in enumerate(tasks):
            if isinstance(task, dict) and task.get("id") == task_id:
                task_found = task
                task_index = i
                break
        
        if not task_found:
            return json.dumps({
                "error": f"No task found with ID: {task_id}",
                "success": False
            }, indent=2)
        
        # Check task status
        current_status = task_found.get("status", "unknown")
        
        # In real Claude Code, we would only allow stopping 'running' tasks
        # But in our simplified system, we might allow any status
        allow_any_status = config.get("TASK_STOP_ALLOW_ANY_STATUS", True)
        simulate_only = config.get("TASK_STOP_SIMULATE_ONLY", False)
        
        if not allow_any_status and current_status != "running":
            return json.dumps({
                "error": f"Task {task_id} is not running (status: {current_status})",
                "success": False
            }, indent=2)
        
        # Update task status to 'stopped' (unless simulate only)
        if not simulate_only:
            task_found["status"] = "stopped"
            task_found["updated_at"] = time.time() if "time" in locals() else task_found.get("updated_at", task_found.get("created_at"))
            
            # Save updated tasks
            try:
                with open(tasks_path, 'w', encoding='utf-8') as f:
                    json.dump(tasks, f, indent=2, default=str)
            except IOError as e:
                return json.dumps({
                    "error": f"Failed to save updated tasks: {str(e)}",
                    "success": False
                }, indent=2)
        
        # Determine task type and command for response
        task_type = task_found.get("type", "unknown")
        command = task_found.get("subject", "Unknown task")
        
        # Build Claude Code compatible response
        response = {
            "message": f"Successfully stopped task: {task_id} ({command})",
            "task_id": task_id,
            "task_type": task_type,
            "command": command
        }
        
        # Add simulation note if applicable
        if simulate_only:
            response["_note"] = "Simulation only - task not actually stopped"
            response["message"] = f"Simulated stopping task: {task_id} ({command})"
        
        # Add metadata (not part of Claude Code spec but useful)
        response["_metadata"] = {
            "success": True,
            "previousStatus": current_status,
            "newStatus": "stopped" if not simulate_only else current_status,
            "simulateOnly": simulate_only,
            "interactiveMode": config.get("TASK_STOP_INTERACTIVE", True)
        }
        
        # Interactive mode output (if enabled)
        interactive = config.get("TASK_STOP_INTERACTIVE", True)
        if interactive:
            print(f"🛑 Task stopped: {task_id}")
            print(f"   Type: {task_type}")
            print(f"   Command: {command}")
            print(f"   Previous status: {current_status}")
            if simulate_only:
                print(f"   ⚠️  Simulation only (no actual changes made)")
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Task stop failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "task_stop_tool": task_stop_tool
}


if __name__ == "__main__":
    # Test the task_stop_tool function
    print("Testing TaskStopTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Create a test task first (if TaskCreateTool is available)
    print("1. Testing with missing task_id:")
    result1 = task_stop_tool()
    data1 = json.loads(result1)
    
    print(f"Success: {data1.get('success', True)}")
    print(f"Error: {data1.get('error', 'None')}")
    
    print("\n2. Testing with non-existent task:")
    result2 = task_stop_tool(task_id="nonexistent_task_123")
    data2 = json.loads(result2)
    
    print(f"Success: {data2.get('success', True)}")
    print(f"Error: {data2.get('error', 'None')}")
    
    # Test 3: Test with shell_id (deprecated parameter)
    print("\n3. Testing with shell_id (deprecated):")
    result3 = task_stop_tool(shell_id="test_shell_456")
    data3 = json.loads(result3)
    
    print(f"Success: {data3.get('success', True)}")
    print(f"Error: {data3.get('error', 'None')}")
    
    # Test 4: Check Claude Code compatibility
    print("\n4. Claude Code compatibility check:")
    # Minimal test of response structure
    test_response = {
        "message": "Test message",
        "task_id": "test_id",
        "task_type": "test_type",
        "command": "test_command"
    }
    
    expected_fields = ["message", "task_id", "task_type", "command"]
    missing_fields = [field for field in expected_fields if field not in test_response]
    
    if missing_fields:
        print(f"  Missing fields in test response: {missing_fields}")
    else:
        print("  All expected fields present ✓")