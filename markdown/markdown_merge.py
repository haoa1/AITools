"""
Markdown merge module - contains function for merging multiple markdown files.
"""

import os
from typing import List, Optional

# Import helper functions from base module
from .markdown_base import _read_file_content, _write_file_content

def merge_markdown_files(markdown_files: List[str], output_path: Optional[str] = None, separator: str = '---') -> str:
    '''
    Merge multiple markdown files into one.
    
    :param markdown_files: List of markdown file paths to merge
    :type markdown_files: list
    :param output_path: Path to save merged markdown file
    :type output_path: str
    :param separator: Separator text between merged files (default: '---')
    :type separator: str
    :return: Merged content or success message
    :rtype: str
    '''
    try:
        if not markdown_files:
            return "Error: No markdown files provided to merge."
        
        merged_content = []
        
        for file_path in markdown_files:
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
            
            try:
                content = _read_file_content(file_path)
                merged_content.append(content)
                
                # Add separator between files (except after the last one)
                if file_path != markdown_files[-1] and separator:
                    merged_content.append(f"\n{separator}\n")
            
            except Exception as e:
                return f"Error reading file {file_path}: {str(e)}"
        
        final_content = ''.join(merged_content)
        
        if output_path:
            result = _write_file_content(output_path, final_content)
            return f"Successfully merged {len(markdown_files)} files into {output_path}\n\nMerged content preview (first 1000 characters):\n{final_content[:1000]}..."
        
        return final_content
    
    except Exception as e:
        return f"Error merging markdown files: {str(e)}"

__all__ = ["merge_markdown_files"]