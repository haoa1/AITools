"""
File operations module for AITools.

This module provides comprehensive file system operations including:
- Reading files with various methods
- Writing files (overwrite only)
- Deleting files and file content
- Editing files by replacing text
- Comparing files
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "File system operations module"

# Import all file operation functions
from .read import (
    read_file,
)

from .write import (
    write_file,
)

from .delete import (
    delete_file,
    delete_lines,
    delete_at_offset,
)

from .replace import (
    edit_file,
)

from .compare import compare_files

from .search import glob

# List of all exported functions
__all__ = [
    "read_file",
    "write_file",
    "delete_file",
    "delete_lines",
    "delete_at_offset",
    "edit_file",
    "compare_files",
    "glob",
]
