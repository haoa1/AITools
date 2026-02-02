"""
Markdown module for AITools.

This module provides markdown file operations including reading, writing,
parsing, converting to HTML, and extracting structure from markdown files.
"""

from .markdown import (
    # Function definitions
    __MARKDOWN_READ_FUNCTION__,
    __MARKDOWN_WRITE_FUNCTION__,
    __MARKDOWN_PARSE_FUNCTION__,
    __MARKDOWN_CONVERT_HTML_FUNCTION__,
    __MARKDOWN_EXTRACT_TOC_FUNCTION__,
    __MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__,
    __MARKDOWN_MERGE_FUNCTION__,
    __MARKDOWN_VALIDATE_FUNCTION__,
    
    # Actual implementations
    read_markdown_file,
    write_markdown_file,
    parse_markdown,
    convert_markdown_to_html,
    extract_toc_from_markdown,
    extract_code_blocks_from_markdown,
    merge_markdown_files,
    validate_markdown_syntax,
    
    # Module metadata
    __module_metadata__,
    
    # Module registration
    tools,
    TOOL_CALL_MAP,
)

__all__ = [
    # Function definitions
    "__MARKDOWN_READ_FUNCTION__",
    "__MARKDOWN_WRITE_FUNCTION__",
    "__MARKDOWN_PARSE_FUNCTION__",
    "__MARKDOWN_CONVERT_HTML_FUNCTION__",
    "__MARKDOWN_EXTRACT_TOC_FUNCTION__",
    "__MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__",
    "__MARKDOWN_MERGE_FUNCTION__",
    "__MARKDOWN_VALIDATE_FUNCTION__",
    
    # Actual implementations
    "read_markdown_file",
    "write_markdown_file",
    "parse_markdown",
    "convert_markdown_to_html",
    "extract_toc_from_markdown",
    "extract_code_blocks_from_markdown",
    "merge_markdown_files",
    "validate_markdown_syntax",
    
    # Module metadata
    "__module_metadata__",
    
    # Module registration
    "tools",
    "TOOL_CALL_MAP",
]