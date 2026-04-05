"""
System management module for AITools.
Provides tools for task management, monitoring, configuration, and other system operations.
"""

from .task_stop import tools as task_stop_tools, TOOL_CALL_MAP as task_stop_map
from .task_manager import task_manager, TaskStatus, Task, create_test_task
from .finish import tools as finish_tools, TOOL_CALL_MAP as finish_map
from .config_tool import tools as config_tools
from .exit_worktree_tool import tools as exit_worktree_tools, TOOL_CALL_MAP as exit_worktree_map
from .ctx_inspect_tool import tools as ctx_inspect_tools, TOOL_CALL_MAP as ctx_inspect_map

# Combine tools and TOOL_CALL_MAPs
tools = (task_stop_tools + config_tools + finish_tools + exit_worktree_tools + ctx_inspect_tools)
TOOL_CALL_MAP = {**task_stop_map}
TOOL_CALL_MAP.update(finish_map)
TOOL_CALL_MAP.update(exit_worktree_map)
TOOL_CALL_MAP.update(ctx_inspect_map)
# Export task manager utilities
__all__ = [
    'tools', 
    'TOOL_CALL_MAP',
]