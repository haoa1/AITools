#!/usr/bin/env python3
"""
TaskStopTool implementation for AITools.
Provides functionality to stop running tasks, aligned with Claude Code's TaskStopTool.
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional

# AITools decorators
from base import function_ai, parameters_func, property_param

# Import task manager
from .task_manager import task_manager, TaskStatus

# ============================================================================
# PROPERTY DEFINITIONS (matching Claude Code's TaskStopTool interface)
# ============================================================================

__TASK_STOP_PROPERTY_ONE__ = property_param(
    name="task_id",
    description="The ID of the background task to stop. Required unless shell_id is provided.",
    t="string",
    required=False  # Made optional to match Claude Code schema
)

__TASK_STOP_PROPERTY_TWO__ = property_param(
    name="shell_id",
    description="Deprecated: use task_id instead. For backward compatibility with KillShell tool.",
    t="string",
    required=False
)

__TASK_STOP_PROPERTY_THREE__ = property_param(
    name="create_demo",
    description="Optional: Create a demo task if no task exists (for testing).",
    t="boolean",
    required=False
)

__TASK_STOP_PROPERTY_FOUR__ = property_param(
    name="force",
    description="Optional: Force stop even if task is not running.",
    t="boolean",
    required=False
)

# ============================================================================
# FUNCTION DEFINITION
# ============================================================================

__TASK_STOP_FUNCTION__ = function_ai(
    name="task_stop",
    description="Stop a running background task by ID, similar to Claude Code's TaskStopTool.",
    parameters=parameters_func([
        __TASK_STOP_PROPERTY_ONE__,
        __TASK_STOP_PROPERTY_TWO__,
        __TASK_STOP_PROPERTY_THREE__,
        __TASK_STOP_PROPERTY_FOUR__,
    ])
)

# ============================================================================
# MAIN FUNCTION IMPLEMENTATION
# ============================================================================

def task_stop(
    task_id: str = "",
    shell_id: str = "",
    create_demo: bool = False,
    force: bool = False
) -> str:
    """
    Stop a running background task.
    
    This tool mimics Claude Code's TaskStopTool functionality for stopping
    running tasks in a simplified task management system.
    
    Args:
        task_id: The ID of the background task to stop
        shell_id: Deprecated alias for task_id (for backward compatibility)
        create_demo: Create a demo task if no tasks exist (for testing)
        force: Force stop even if task is not running
        
    Returns:
        JSON string with operation result, matching Claude Code's format:
        {
            "message": "Status message",
            "task_id": "ID of stopped task",
            "task_type": "Type of stopped task",
            "command": "Command/description of stopped task"
        }
        or error message if operation fails
    """
    try:
        # Determine which ID to use (task_id takes precedence over shell_id)
        target_id = task_id if task_id else shell_id
        
        # If no ID provided and create_demo is True, create a demo task
        if not target_id and create_demo:
            return create_and_stop_demo_task(force)
        
        # Validate input
        if not target_id:
            return json.dumps({
                "error": True,
                "message": "Missing required parameter: task_id",
                "error_code": 1
            }, indent=2)
        
        # Get the task
        task = task_manager.get_task(target_id)
        
        if not task:
            return json.dumps({
                "error": True,
                "message": f"No task found with ID: {target_id}",
                "error_code": 1
            }, indent=2)
        
        # Check task status
        task_status = task.status.value
        task_type = task.task_type
        task_command = task.command or task.description or "Unknown command"
        
        # Handle different statuses
        if task_status == TaskStatus.RUNNING.value:
            # Stop the running task
            success = task_manager.stop_task(target_id)
            if success:
                return json.dumps({
                    "message": f"Successfully stopped task {target_id}",
                    "task_id": target_id,
                    "task_type": task_type,
                    "command": task_command
                }, indent=2)
            else:
                return json.dumps({
                    "error": True,
                    "message": f"Failed to stop task {target_id}",
                    "error_code": 2
                }, indent=2)
        
        elif task_status == TaskStatus.STOPPED.value:
            if force:
                # Task already stopped, but force was requested
                return json.dumps({
                    "message": f"Task {target_id} was already stopped (force flag ignored)",
                    "task_id": target_id,
                    "task_type": task_type,
                    "command": task_command
                }, indent=2)
            else:
                return json.dumps({
                    "error": True,
                    "message": f"Task {target_id} is not running (status: {task_status})",
                    "error_code": 3
                }, indent=2)
        
        elif task_status in [TaskStatus.COMPLETED.value, TaskStatus.FAILED.value]:
            if force:
                # Task is completed/failed, force flag doesn't apply
                return json.dumps({
                    "error": True,
                    "message": f"Task {target_id} has already completed (status: {task_status})",
                    "error_code": 4
                }, indent=2)
            else:
                return json.dumps({
                    "error": True,
                    "message": f"Task {target_id} has already completed (status: {task_status})",
                    "error_code": 4
                }, indent=2)
        
        elif task_status == TaskStatus.PENDING.value:
            if force:
                # Stop pending task
                success = task_manager.stop_task(target_id)
                if success:
                    return json.dumps({
                        "message": f"Stopped pending task {target_id} (force stop)",
                        "task_id": target_id,
                        "task_type": task_type,
                        "command": task_command
                    }, indent=2)
                else:
                    return json.dumps({
                        "error": True,
                        "message": f"Failed to stop pending task {target_id}",
                        "error_code": 2
                    }, indent=2)
            else:
                return json.dumps({
                    "error": True,
                    "message": f"Task {target_id} is not running (status: {task_status})",
                    "error_code": 3
                }, indent=2)
        
        else:
            # Unknown status
            return json.dumps({
                "error": True,
                "message": f"Task {target_id} has unknown status: {task_status}",
                "error_code": 5
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Error stopping task: {str(e)}",
            "error_code": 99
        }, indent=2)


def create_and_stop_demo_task(force: bool = False) -> str:
    """
    Create a demo task and stop it (for testing).
    
    Args:
        force: Whether to force stop
        
    Returns:
        JSON response
    """
    try:
        # Create a demo task
        from .task_manager import create_test_task
        demo_id = create_test_task(
            task_type="demo",
            description="Demo task for TaskStopTool testing",
            command="echo 'This is a demo task'",
            start=True
        )
        
        # Stop the demo task
        task = task_manager.get_task(demo_id)
        if not task:
            return json.dumps({
                "error": True,
                "message": "Failed to create demo task",
                "error_code": 6
            }, indent=2)
        
        task_manager.stop_task(demo_id)
        
        return json.dumps({
            "message": f"Created and stopped demo task {demo_id}",
            "task_id": demo_id,
            "task_type": "demo",
            "command": "echo 'This is a demo task'"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Error creating demo task: {str(e)}",
            "error_code": 99
        }, indent=2)


def list_tasks() -> str:
    """
    Helper function to list all tasks (not part of the main tool).
    
    Returns:
        Formatted string with task information
    """
    try:
        tasks = task_manager.get_all_tasks()
        
        if not tasks:
            return "No tasks found."
        
        result = ["Task List:"]
        result.append("-" * 60)
        result.append(f"{'ID':<10} {'Type':<15} {'Status':<12} {'Description'}")
        result.append("-" * 60)
        
        for task in tasks:
            desc = task.get('description', '')[:40]
            if len(task.get('description', '')) > 40:
                desc += "..."
            
            result.append(f"{task['task_id']:<10} {task['task_type']:<15} "
                         f"{task['status']:<12} {desc}")
        
        result.append(f"\nTotal tasks: {len(tasks)}")
        
        # Count by status
        status_counts = {}
        for task in tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        result.append("Status counts:")
        for status, count in sorted(status_counts.items()):
            result.append(f"  {status}: {count}")
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error listing tasks: {str(e)}"


def reset_tasks() -> str:
    """
    Helper function to reset all tasks (not part of the main tool).
    
    Returns:
        Confirmation message
    """
    try:
        task_count = len(task_manager.get_all_tasks())
        task_manager.reset()
        return f"Reset task manager. Removed {task_count} tasks."
    except Exception as e:
        return f"Error resetting tasks: {str(e)}"


# ============================================================================
# TOOL REGISTRATION
# ============================================================================

# List of all tools
tools = [
    __TASK_STOP_FUNCTION__,
]

# Map function names to implementations
TOOL_CALL_MAP = {
    "task_stop": task_stop,
}


if __name__ == "__main__":
    # Test the TaskStopTool
    print("Testing TaskStopTool...")
    print("=" * 60)
    
    # Create some test tasks first
    from task_manager import create_test_task
    
    print("Creating test tasks...")
    running_id = create_test_task("bash", "Running task", "sleep 100", start=True)
    stopped_id = create_test_task("process", "Already stopped", "echo 'done'", start=True)
    task_manager.stop_task(stopped_id)
    pending_id = create_test_task("monitor", "Pending task", "monitor.py", start=False)
    
    print(f"Created tasks:")
    print(f"  Running: {running_id}")
    print(f"  Stopped: {stopped_id}")
    print(f"  Pending: {pending_id}")
    
    print("\n" + list_tasks())
    
    print("\n" + "=" * 60)
    print("Test 1: Stop running task...")
    result1 = task_stop(task_id=running_id)
    print(result1)
    
    print("\nTest 2: Try to stop already stopped task...")
    result2 = task_stop(task_id=stopped_id)
    print(result2)
    
    print("\nTest 3: Stop pending task with force...")
    result3 = task_stop(task_id=pending_id, force=True)
    print(result3)
    
    print("\nTest 4: Create and stop demo task...")
    result4 = task_stop(create_demo=True)
    print(result4)
    
    print("\nTest 5: Missing task_id...")
    result5 = task_stop()
    print(result5)
    
    print("\nTest 6: Non-existent task...")
    result6 = task_stop(task_id="nonexistent123")
    print(result6)
    
    print("\n" + "=" * 60)
    print("Final task list:")
    print(list_tasks())
    
    # Reset
    print(f"\n{reset_tasks()}")
    
    print("\nTaskStopTool test completed!")