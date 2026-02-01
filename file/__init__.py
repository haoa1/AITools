"""
File operations module for AITools.

This module provides comprehensive file system operations including:
- Reading files with various methods
- Writing and appending to files
- Deleting files and file content
- Replacing content in files
- Comparing files
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "File system operations module"

# Import all file operation functions
from .read import (
    read_file,
    read_file_by_offset,
    read_start_lines,
    read_tail_lines,
    get_file_size,
    read_line_context,
    read_lines_range,
)

from .write import (
    write_file,
    append_to_file,
    write_at_offset,
)

from .delete import (
    delete_file,
    delete_lines,
    delete_at_offset,
)

from .replace import (
    replace_in_file,
    replace_lines,
    replace_with_regex,
)

from .compare import compare_files

# List of all exported functions
__all__ = [
    'read_file',
    'read_file_by_offset',
    'read_start_lines',
    'read_tail_lines',
    'get_file_size',
    'read_line_context',
    'read_lines_range',
    'write_file',
    'append_to_file',
    'write_at_offset',
    'delete_file',
    'delete_lines',
    'delete_at_offset',
    'replace_in_file',
    'replace_lines',
    'replace_with_regex',
    'compare_files',
]