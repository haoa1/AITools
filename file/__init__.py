"""
File operations module for AITools.

This module provides comprehensive file system operations including:
- Reading files with various methods
- Writing files (overwrite only)
- Deleting files and file content
- Editing files by replacing text
- Comparing files
- Searching files with grep and glob patterns
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "File system operations module"

from .file_write_tool import (
    tools as write_tools, TOOL_CALL_MAP as write_tool_map
)

from .file_edit_tool import (
    tools as edit_tools, TOOL_CALL_MAP as edit_tool_map
)

from .glob_tool import tools as glob_tool, TOOL_CALL_MAP as glob_tool_map
from .grep_tool import tools as grep_tool, TOOL_CALL_MAP as grep_tool_map


# from .notebook_edit import notebook_edit
from .file_read_tool import (
    tools as read_tools, TOOL_CALL_MAP as read_tool_map
)


tools = read_tools + write_tools + edit_tools + glob_tool + grep_tool

TOOL_CALL_MAP = {**read_tool_map, **write_tool_map, **edit_tool_map, **glob_tool_map, **grep_tool_map}
# List of all exported functions
__all__ = [
    "tools",
    "TOOL_CALL_MAP",
]
