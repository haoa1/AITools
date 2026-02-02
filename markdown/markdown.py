"""
Markdown module for AITools.

This module provides markdown file operations including reading, writing,
parsing, converting to HTML, and extracting structure from markdown files.
"""

# Import all property and function definitions from base module
from .markdown_base import (
    # Module metadata
    __module_metadata__,
    
    # Property definitions
    __MARKDOWN_PROPERTY_ONE__,
    __MARKDOWN_PROPERTY_TWO__,
    __MARKDOWN_PROPERTY_THREE__,
    __MARKDOWN_PROPERTY_4__,
    __MARKDOWN_PROPERTY_5__,
    __MARKDOWN_PROPERTY_6__,
    __MARKDOWN_PROPERTY_7__,
    __MARKDOWN_PROPERTY_8__,
    __MARKDOWN_PROPERTY_9__,
    __MARKDOWN_PROPERTY_10__,
    __MARKDOWN_PROPERTY_11__,
    __MARKDOWN_PROPERTY_12__,
    __MARKDOWN_PROPERTY_13__,
    __MARKDOWN_PROPERTY_14__,
    
    # Function definitions
    __MARKDOWN_READ_FUNCTION__,
    __MARKDOWN_WRITE_FUNCTION__,
    __MARKDOWN_PARSE_FUNCTION__,
    __MARKDOWN_CONVERT_HTML_FUNCTION__,
    __MARKDOWN_EXTRACT_TOC_FUNCTION__,
    __MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__,
    __MARKDOWN_MERGE_FUNCTION__,
    __MARKDOWN_VALIDATE_FUNCTION__,
)

# Import all function implementations from submodules
from .markdown_io import (
    read_markdown_file,
    write_markdown_file,
)

from .markdown_parse import (
    parse_markdown,
    convert_markdown_to_html,
)

from .markdown_extract import (
    extract_toc_from_markdown,
    extract_code_blocks_from_markdown,
)

from .markdown_merge import (
    merge_markdown_files,
)

from .markdown_validation import (
    validate_markdown_syntax,
)

# Define tools list for module registration
tools = [
    __MARKDOWN_READ_FUNCTION__,
    __MARKDOWN_WRITE_FUNCTION__,
    __MARKDOWN_PARSE_FUNCTION__,
    __MARKDOWN_CONVERT_HTML_FUNCTION__,
    __MARKDOWN_EXTRACT_TOC_FUNCTION__,
    __MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__,
    __MARKDOWN_MERGE_FUNCTION__,
    __MARKDOWN_VALIDATE_FUNCTION__,
]

# Define tool call mapping for function execution
TOOL_CALL_MAP = {
    "read_markdown_file": read_markdown_file,
    "write_markdown_file": write_markdown_file,
    "parse_markdown": parse_markdown,
    "convert_markdown_to_html": convert_markdown_to_html,
    "extract_toc_from_markdown": extract_toc_from_markdown,
    "extract_code_blocks_from_markdown": extract_code_blocks_from_markdown,
    "merge_markdown_files": merge_markdown_files,
    "validate_markdown_syntax": validate_markdown_syntax,
}

# Re-export everything for easy import
__all__ = [
    # Module metadata
    "__module_metadata__",
    
    # Property definitions
    "__MARKDOWN_PROPERTY_ONE__",
    "__MARKDOWN_PROPERTY_TWO__",
    "__MARKDOWN_PROPERTY_THREE__",
    "__MARKDOWN_PROPERTY_4__",
    "__MARKDOWN_PROPERTY_5__",
    "__MARKDOWN_PROPERTY_6__",
    "__MARKDOWN_PROPERTY_7__",
    "__MARKDOWN_PROPERTY_8__",
    "__MARKDOWN_PROPERTY_9__",
    "__MARKDOWN_PROPERTY_10__",
    "__MARKDOWN_PROPERTY_11__",
    "__MARKDOWN_PROPERTY_12__",
    "__MARKDOWN_PROPERTY_13__",
    "__MARKDOWN_PROPERTY_14__",
    
    # Function definitions
    "__MARKDOWN_READ_FUNCTION__",
    "__MARKDOWN_WRITE_FUNCTION__",
    "__MARKDOWN_PARSE_FUNCTION__",
    "__MARKDOWN_CONVERT_HTML_FUNCTION__",
    "__MARKDOWN_EXTRACT_TOC_FUNCTION__",
    "__MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__",
    "__MARKDOWN_MERGE_FUNCTION__",
    "__MARKDOWN_VALIDATE_FUNCTION__",
    
    # Function implementations
    "read_markdown_file",
    "write_markdown_file",
    "parse_markdown",
    "convert_markdown_to_html",
    "extract_toc_from_markdown",
    "extract_code_blocks_from_markdown",
    "merge_markdown_files",
    "validate_markdown_syntax",
    
    # Module registration
    "tools",
    "TOOL_CALL_MAP",
]