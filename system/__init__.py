"""
System monitoring and control module for AITools.
Provides tools for monitoring system resources, controlling execution, configuration management, and todo list management.
"""

from .monitor import tools as monitor_tools, TOOL_CALL_MAP as monitor_map
from .sleep import tools as sleep_tools, TOOL_CALL_MAP as sleep_map
from .todo import tools as todo_tools, TOOL_CALL_MAP as todo_map


from .task_stop import tools as task_stop_tools, TOOL_CALL_MAP as task_stop_map
from .task_manager import task_manager, TaskStatus, Task, create_test_task
from .finish import tools as finish_tools, TOOL_CALL_MAP as finish_map
from .config_tool import tools as config_tools
from .exit_worktree_tool import tools as exit_worktree_tools, TOOL_CALL_MAP as exit_worktree_map
from .ctx_inspect_tool import tools as ctx_inspect_tools, TOOL_CALL_MAP as ctx_inspect_map
from .overflow_test_tool import tools as overflow_test_tools, TOOL_CALL_MAP as overflow_test_map
from .terminal_capture_tool import tools as terminal_capture_tools, TOOL_CALL_MAP as terminal_capture_map
from .snip_tool import tools as snip_tools, TOOL_CALL_MAP as snip_map

# Combine tools and TOOL_CALL_MAPs
tools = (task_stop_tools + config_tools + finish_tools + exit_worktree_tools + ctx_inspect_tools + overflow_test_tools + terminal_capture_tools + snip_tools)
TOOL_CALL_MAP = {**task_stop_map}
TOOL_CALL_MAP.update(finish_map)
TOOL_CALL_MAP.update(exit_worktree_map)
TOOL_CALL_MAP.update(ctx_inspect_map)
TOOL_CALL_MAP.update(overflow_test_map)
TOOL_CALL_MAP.update(terminal_capture_map)
TOOL_CALL_MAP.update(snip_map)
# Export task manager utilities

__all__ = [
    'tools', 
    'TOOL_CALL_MAP',
]