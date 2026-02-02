"""
Markdown extract module - contains functions for extracting TOC and code blocks.
"""

import re
import json
from typing import List, Dict, Any, Optional

# Import helper functions from base module
from .markdown_base import _extract_headings_from_text, _extract_code_blocks_from_text

def extract_toc_from_markdown(markdown_text: str, toc_depth: int = 3) -> str:
    '''
    Extract table of contents from markdown text.
    
    :param markdown_text: Markdown text to extract TOC from
    :type markdown_text: str
    :param toc_depth: Maximum heading depth for table of contents (1-6, default: 3)
    :type toc_depth: int
    :return: Markdown formatted table of contents
    :rtype: str
    '''
    try:
        headings = _extract_headings_from_text(markdown_text)
        
        # Filter by depth
        filtered_headings = [h for h in headings if h["level"] <= toc_depth]
        
        if not filtered_headings:
            return "No headings found in the markdown text."
        
        # Generate markdown TOC
        toc_markdown = "# Table of Contents\n\n"
        for item in filtered_headings:
            indent = "  " * (item["level"] - 1)
            toc_markdown += f'{indent}- [{item["text"]}](#{item["slug"]})\n'
        
        # Also provide JSON format for programmatic use
        toc_json = json.dumps({
            "toc_items": filtered_headings,
            "total_headings": len(filtered_headings),
            "max_depth": max(item["level"] for item in filtered_headings) if filtered_headings else 0,
            "toc_markdown": toc_markdown
        }, indent=2, ensure_ascii=False)
        
        return f"{toc_markdown}\n\n---\n\nJSON format:\n{toc_json}"
    
    except Exception as e:
        return f"Error extracting table of contents: {str(e)}"

def extract_code_blocks_from_markdown(markdown_text: str, language_filter: Optional[str] = None) -> str:
    '''
    Extract code blocks from markdown text.
    
    :param markdown_text: Markdown text to extract code blocks from
    :type markdown_text: str
    :param language_filter: Filter code blocks by programming language
    :type language_filter: str
    :return: JSON string with extracted code blocks
    :rtype: str
    '''
    try:
        code_blocks = _extract_code_blocks_from_text(markdown_text)
        
        # Apply language filter if specified
        if language_filter:
            filtered_blocks = [
                block for block in code_blocks 
                if language_filter.lower() in block["language"].lower()
            ]
        else:
            filtered_blocks = code_blocks
        
        # Also extract inline code snippets
        inline_code_snippets = []
        lines = markdown_text.split('\n')
        for i, line in enumerate(lines, 1):
            inline_matches = re.findall(r'`([^`]+)`', line)
            for match in inline_matches:
                inline_code_snippets.append({
                    "code": match,
                    "line_number": i + 1,
                    "type": "inline"
                })
        
        result = {
            "code_blocks": filtered_blocks,
            "inline_code_snippets": inline_code_snippets,
            "total_code_blocks": len(filtered_blocks),
            "total_inline_snippets": len(inline_code_snippets),
            "languages": list(set(block["language"] for block in filtered_blocks if block["language"]))
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Error extracting code blocks: {str(e)}"

__all__ = ["extract_toc_from_markdown", "extract_code_blocks_from_markdown"]