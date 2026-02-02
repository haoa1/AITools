"""
Markdown validation module - contains markdown syntax validation function.
"""

import re
import json
from typing import List, Dict, Any

# Import helper functions from base module
from .markdown_base import _extract_headings_from_text

def validate_markdown_syntax(markdown_text: str, strict_validation: bool = False) -> str:
    '''
    Validate markdown syntax and check for common errors.
    
    :param markdown_text: Markdown text to validate
    :type markdown_text: str
    :param strict_validation: Whether to perform strict markdown syntax validation
    :type strict_validation: bool
    :return: JSON string with validation results
    :rtype: str
    '''
    try:
        validation_results = {
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "statistics": {},
            "is_valid": True
        }
        
        lines = markdown_text.split('\n')
        
        # Statistics
        validation_results["statistics"] = {
            "total_lines": len(lines),
            "non_empty_lines": sum(1 for line in lines if line.strip()),
            "total_characters": len(markdown_text)
        }
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for heading spacing issues
            if re.match(r'^#{1,6}[^#\s]', line):
                validation_results["errors"].append({
                    "line": i,
                    "message": f"Heading missing space after # symbols: '{line[:50]}...'",
                    "type": "syntax_error"
                })
                validation_results["is_valid"] = False
            
            # Check for unclosed code blocks
            if line.startswith('```') and i > 1:
                # Count backticks on this line
                backtick_count = len(line) - len(line.lstrip('`'))
                if backtick_count != 3:
                    validation_results["warnings"].append({
                        "line": i,
                        "message": f"Code block delimiter has {backtick_count} backticks instead of 3",
                        "type": "format_warning"
                    })
            
            # Check for broken links
            link_matches = re.findall(r'\[([^\]]+)\]\([^\)]*$', line)
            for _ in link_matches:
                validation_results["errors"].append({
                    "line": i,
                    "message": "Unclosed link syntax",
                    "type": "syntax_error"
                })
                validation_results["is_valid"] = False
            
            # Check for broken images
            image_matches = re.findall(r'!\[([^\]]*)\]\([^\)]*$', line)
            for _ in image_matches:
                validation_results["errors"].append({
                    "line": i,
                    "message": "Unclosed image syntax",
                    "type": "syntax_error"
                })
                validation_results["is_valid"] = False
            
            # Check for list consistency
            if strict_validation:
                if re.match(r'^[\-\*\+]\s*[^\s]', line) and not re.match(r'^[\-\*\+]\s+', line):
                    validation_results["warnings"].append({
                        "line": i,
                        "message": "List item should have exactly one space after bullet",
                        "type": "format_warning"
                    })
        
        # Check for balanced code blocks
        code_block_lines = [i+1 for i, line in enumerate(lines) if line.strip().startswith('```')]
        if len(code_block_lines) % 2 != 0:
            validation_results["errors"].append({
                "line": code_block_lines[-1] if code_block_lines else 0,
                "message": "Unclosed code block (odd number of ``` markers)",
                "type": "syntax_error"
            })
            validation_results["is_valid"] = False
        
        # Check for heading hierarchy (strict validation only)
        if strict_validation:
            headings = _extract_headings_from_text(markdown_text)
            
            if headings:
                # Check if first heading is h1
                if headings[0]["level"] != 1:
                    validation_results["suggestions"].append({
                        "line": headings[0]["line_number"],
                        "message": "Consider starting with an H1 heading (# Heading)",
                        "type": "style_suggestion"
                    })
                
                # Check for heading level jumps
                for j in range(1, len(headings)):
                    level_diff = headings[j]["level"] - headings[j-1]["level"]
                    if level_diff > 1:
                        validation_results["warnings"].append({
                            "line": headings[j]["line_number"],
                            "message": f"Heading jumps from H{headings[j-1]['level']} to H{headings[j]['level']} (should increase by only 1 level at a time)",
                            "type": "structure_warning"
                        })
        
        # Add summary
        validation_results["summary"] = {
            "total_errors": len(validation_results["errors"]),
            "total_warnings": len(validation_results["warnings"]),
            "total_suggestions": len(validation_results["suggestions"]),
            "validation_passed": validation_results["is_valid"] and len(validation_results["errors"]) == 0
        }
        
        return json.dumps(validation_results, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Error validating markdown syntax: {str(e)}"

__all__ = ["validate_markdown_syntax"]