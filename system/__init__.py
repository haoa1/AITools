"""
System management module for AITools.
Provides tools for task management, monitoring, configuration, and other system operations.
"""

from .task_stop import tools as task_stop_tools, TOOL_CALL_MAP as task_stop_map
from .task_manager import task_manager, TaskStatus, Task, create_test_task

# Combine tools and TOOL_CALL_MAPs
tools = task_stop_tools
TOOL_CALL_MAP = {**task_stop_map}

# Export task manager utilities
__all__ = [
    'tools', 
    'TOOL_CALL_MAP',
    'task_manager',
    'TaskStatus', 
    'Task', 
    'create_test_task'
]