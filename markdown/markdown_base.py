"""
Markdown base module - contains property definitions, function definitions, and helper functions.
"""

from base import function_ai, parameters_func, property_param
from typing import List, Dict, Any, Optional
import os
import re
import json

# Module metadata
__module_metadata__ = {
    "name": "markdown",
    "version": "1.0.0",
    "description": "Markdown file operations including reading, writing, parsing, and conversion",
    "author": "AITools Team",
    "dependencies": [],
    "tags": ["markdown", "documentation", "formatting", "html"]
}

# Property definitions for markdown operations
__MARKDOWN_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path to the markdown file.",
    t="string"
)

__MARKDOWN_PROPERTY_TWO__ = property_param(
    name="content",
    description="The markdown content to write.",
    t="string"
)

__MARKDOWN_PROPERTY_THREE__ = property_param(
    name="markdown_text",
    description="Markdown text content to process.",
    t="string"
)

__MARKDOWN_PROPERTY_4__ = property_param(
    name="output_format",
    description="Output format for conversion: 'html', 'json', 'plaintext'.",
    t="string"
)

__MARKDOWN_PROPERTY_5__ = property_param(
    name="include_metadata",
    description="Whether to include metadata in output.",
    t="boolean"
)

__MARKDOWN_PROPERTY_6__ = property_param(
    name="encoding",
    description="File encoding to use for reading/writing.",
    t="string"
)

__MARKDOWN_PROPERTY_7__ = property_param(
    name="mode",
    description="File mode: 'r' for read, 'w' for write, 'a' for append.",
    t="string"
)

__MARKDOWN_PROPERTY_8__ = property_param(
    name="html_output_path",
    description="Path to save HTML output file.",
    t="string"
)

__MARKDOWN_PROPERTY_9__ = property_param(
    name="include_css",
    description="Whether to include CSS styling in HTML output.",
    t="boolean"
)

__MARKDOWN_PROPERTY_10__ = property_param(
    name="toc_depth",
    description="Maximum heading depth for table of contents (1-6).",
    t="integer"
)

__MARKDOWN_PROPERTY_11__ = property_param(
    name="language_filter",
    description="Filter code blocks by programming language (e.g., 'python', 'javascript').",
    t="string"
)

__MARKDOWN_PROPERTY_12__ = property_param(
    name="markdown_files",
    description="List of markdown file paths to merge.",
    t="array"
)

__MARKDOWN_PROPERTY_13__ = property_param(
    name="separator",
    description="Separator text between merged files.",
    t="string"
)

__MARKDOWN_PROPERTY_14__ = property_param(
    name="strict_validation",
    description="Whether to perform strict markdown syntax validation.",
    t="boolean"
)

# Function definitions
__MARKDOWN_READ_FUNCTION__ = function_ai(
    name="read_markdown_file",
    description="Read a markdown file and return its content.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_ONE__,
        property_param(
            name="encoding",
            description="File encoding (default: 'utf-8').",
            t="string",
            required=False
        )
    ])
)

__MARKDOWN_WRITE_FUNCTION__ = function_ai(
    name="write_markdown_file",
    description="Write content to a markdown file.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_ONE__,
        __MARKDOWN_PROPERTY_TWO__,
        property_param(
            name="mode",
            description="File mode: 'w' for write (overwrite), 'a' for append.",
            t="string",
            required=False
        ),
        property_param(
            name="encoding",
            description="File encoding (default: 'utf-8').",
            t="string",
            required=False
        )
    ])
)

__MARKDOWN_PARSE_FUNCTION__ = function_ai(
    name="parse_markdown",
    description="Parse markdown text and extract structure (headings, lists, code blocks, etc.).",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_THREE__,
        property_param(
            name="include_metadata",
            description="Whether to include metadata in output.",
            t="boolean",
            required=False
        )
    ])
)

__MARKDOWN_CONVERT_HTML_FUNCTION__ = function_ai(
    name="convert_markdown_to_html",
    description="Convert markdown text to HTML.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_THREE__,
        property_param(
            name="html_output_path",
            description="Path to save HTML output file (optional).",
            t="string",
            required=False
        ),
        property_param(
            name="include_css",
            description="Whether to include CSS styling in HTML output.",
            t="boolean",
            required=False
        )
    ])
)

__MARKDOWN_EXTRACT_TOC_FUNCTION__ = function_ai(
    name="extract_toc_from_markdown",
    description="Extract table of contents from markdown text.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_THREE__,
        property_param(
            name="toc_depth",
            description="Maximum heading depth for table of contents (1-6, default: 3).",
            t="integer",
            required=False
        )
    ])
)

__MARKDOWN_EXTRACT_CODE_BLOCKS_FUNCTION__ = function_ai(
    name="extract_code_blocks_from_markdown",
    description="Extract code blocks from markdown text.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_THREE__,
        property_param(
            name="language_filter",
            description="Filter code blocks by programming language.",
            t="string",
            required=False
        )
    ])
)

__MARKDOWN_MERGE_FUNCTION__ = function_ai(
    name="merge_markdown_files",
    description="Merge multiple markdown files into one.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_12__,
        property_param(
            name="output_path",
            description="Path to save merged markdown file.",
            t="string",
            required=False
        ),
        property_param(
            name="separator",
            description="Separator text between merged files (default: '---').",
            t="string",
            required=False
        )
    ])
)

__MARKDOWN_VALIDATE_FUNCTION__ = function_ai(
    name="validate_markdown_syntax",
    description="Validate markdown syntax and check for common errors.",
    parameters=parameters_func([
        __MARKDOWN_PROPERTY_THREE__,
        property_param(
            name="strict_validation",
            description="Whether to perform strict markdown syntax validation.",
            t="boolean",
            required=False
        )
    ])
)

# Helper functions for internal use
def _read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """Read file content with specified encoding."""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Try different encodings if utf-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

def _write_file_content(file_path: str, content: str, mode: str = 'w', encoding: str = 'utf-8') -> str:
    """Write content to file with specified mode and encoding."""
    try:
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"

def _extract_headings_from_text(markdown_text: str) -> List[Dict[str, Any]]:
    """Extract headings from markdown text."""
    headings = []
    lines = markdown_text.split('\n')
    
    for i, line in enumerate(lines, 1):
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            
            # Generate anchor slug
            slug = re.sub(r'[^\w\s-]', '', text.lower())
            slug = re.sub(r'[-\s]+', '-', slug).strip('-')
            
            headings.append({
                "level": level,
                "text": text,
                "slug": slug,
                "line_number": i
            })
    
    return headings

def _extract_code_blocks_from_text(markdown_text: str) -> List[Dict[str, Any]]:
    """Extract code blocks from markdown text."""
    code_blocks = []
    lines = markdown_text.split('\n')
    in_code_block = False
    current_block = []
    current_lang = ""
    start_line = 0
    
    for i, line in enumerate(lines, 1):
        if line.startswith('```'):
            if not in_code_block:
                # Start of code block
                in_code_block = True
                current_lang = line[3:].strip()
                current_block = []
                start_line = i
            else:
                # End of code block
                in_code_block = False
                
                code_blocks.append({
                    "language": current_lang,
                    "code": '\n'.join(current_block),
                    "start_line": start_line,
                    "end_line": i,
                    "line_count": len(current_block)
                })
            continue
        
        if in_code_block:
            current_block.append(line)
    
    return code_blocks

def _convert_line_to_html(line: str) -> str:
    """Convert a single markdown line to HTML."""
    # Convert bold and italic
    line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
    line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
    line = re.sub(r'__(.+?)__', r'<strong>\1</strong>', line)
    line = re.sub(r'_(.+?)_', r'<em>\1</em>', line)
    
    # Convert links
    line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', line)
    
    # Convert images
    line = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', line)
    
    # Convert inline code
    line = re.sub(r'`([^`]+)`', r'<code>\1</code>', line)
    
    return line

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
    
    # Helper functions
    "_read_file_content",
    "_write_file_content",
    "_extract_headings_from_text",
    "_extract_code_blocks_from_text",
    "_convert_line_to_html"
]