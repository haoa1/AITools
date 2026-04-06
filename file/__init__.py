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
    write,
)

from .file_edit_tool import (
    edit,
)

from .glob_tool import glob
from .grep_tool import grep


from .notebook_edit import notebook_edit
from .file_read_tool import (
    read,
)

# List of all exported functions
__all__ = [
    "read",
    "write",
    "edit",
    "glob",
    "grep",
    "notebook_edit",
]
