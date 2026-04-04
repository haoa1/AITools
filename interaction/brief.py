#!/usr/bin/env python3
"""
BriefTool implementation for AITools.
Provides functionality to generate briefs/summaries from content, aligned with Claude Code's BriefTool.
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

# AITools decorators - same pattern as other tools
from base import function_ai, parameters_func, property_param

__BRIEF_PROPERTY_ONE__ = property_param(
    name="content",
    description="The content to generate a brief from. Can be text, markdown, code, or other content.",
    t="string",
    required=True,
)

__BRIEF_PROPERTY_TWO__ = property_param(
    name="title",
    description="Optional title for the brief. If not provided, will be auto-generated.",
    t="string",
)

__BRIEF_PROPERTY_THREE__ = property_param(
    name="detail_level",
    description="Level of detail for the brief: 'concise' (short summary), 'standard' (balanced), 'detailed' (comprehensive).",
    t="string",
    enum=["concise", "standard", "detailed"]
)

__BRIEF_PROPERTY_FOUR__ = property_param(
    name="max_length",
    description="Maximum length of the brief in characters. 0 means no limit.",
    t="number",
)

__BRIEF_PROPERTY_FIVE__ = property_param(
    name="include_structure",
    description="Whether to include a structured format with sections.",
    t="boolean",
)

__BRIEF_PROPERTY_SIX__ = property_param(
    name="focus_areas",
    description="Optional comma-separated list of focus areas to emphasize in the brief.",
    t="string",
)

@function_ai(
    name="brief",
    description="Generate a brief/summary from the given content, similar to Claude Code's BriefTool.",
    category="interaction"
)
def brief(
    content: str,
    title: str = "",
    detail_level: str = "standard",
    max_length: int = 0,
    include_structure: bool = True,
    focus_areas: str = ""
) -> str:
    """
    Generate a brief or summary from content.
    
    This tool mimics Claude Code's BriefTool functionality by creating structured
    summaries and briefs from various types of content.
    
    Args:
        content: The input content to summarize
        title: Optional title for the brief
        detail_level: Level of detail (concise, standard, detailed)
        max_length: Maximum character length (0 = unlimited)
        include_structure: Whether to use structured format with sections
        focus_areas: Comma-separated focus areas to emphasize
        
    Returns:
        A formatted brief/summary of the content
    """
    try:
        # Validate inputs
        if not content or not isinstance(content, str):
            return "Error: Content must be a non-empty string."
        
        if max_length < 0:
            return "Error: max_length must be 0 (unlimited) or positive."
        
        # Generate title if not provided
        if not title:
            title = generate_title(content)
        
        # Process focus areas
        focus_list = []
        if focus_areas:
            focus_list = [area.strip() for area in focus_areas.split(",") if area.strip()]
        
        # Generate the brief based on detail level
        if detail_level == "concise":
            brief_text = generate_concise_brief(content, focus_list)
        elif detail_level == "detailed":
            brief_text = generate_detailed_brief(content, focus_list)
        else:  # standard
            brief_text = generate_standard_brief(content, focus_list)
        
        # Apply length limit if specified
        if max_length > 0 and len(brief_text) > max_length:
            brief_text = brief_text[:max_length] + "... [truncated]"
        
        # Format the final output
        if include_structure:
            return format_structured_brief(title, brief_text, detail_level, focus_list)
        else:
            return format_simple_brief(title, brief_text)
            
    except Exception as e:
        return f"Error generating brief: {str(e)}"


def generate_title(content: str) -> str:
    """
    Generate an appropriate title based on content.
    """
    # Simple title generation - can be enhanced
    lines = content.strip().split('\n')
    first_line = lines[0].strip() if lines else ""
    
    # If first line looks like a heading or title, use it
    if first_line and len(first_line) < 100 and not first_line.startswith((' ', '\t')):
        # Clean up the title
        title = first_line.strip('#*_- ')
        if title:
            return title
    
    # Generate based on content type or length
    content_type = detect_content_type(content)
    if content_type == "code":
        return "Code Summary"
    elif content_type == "markdown":
        return "Document Summary"
    elif content_type == "log":
        return "Log Analysis"
    elif content_type == "data":
        return "Data Summary"
    else:
        return f"Content Brief ({datetime.now().strftime('%Y-%m-%d %H:%M')})"


def detect_content_type(content: str) -> str:
    """
    Detect the type of content.
    """
    lines = content.split('\n')
    if len(lines) > 0:
        # Check for code indicators
        if any(line.strip().startswith(('def ', 'class ', 'import ', 'from ', '#!', '//', '/*', '*/', 'function ')) for line in lines[:10]):
            return "code"
        
        # Check for markdown
        if any(line.strip().startswith(('#', '##', '###', '- ', '* ', '> ', '```')) for line in lines[:10]):
            return "markdown"
        
        # Check for log/data
        if any(':' in line and '=' not in line and len(line.split(':')) == 2 for line in lines[:5]):
            return "data"
        
        # Check for timestamps (log files)
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\d{2}/\d{2}/\d{4}'
        if any(re.search(timestamp_pattern, line) for line in lines[:5]):
            return "log"
    
    return "text"


def generate_concise_brief(content: str, focus_areas: List[str]) -> str:
    """
    Generate a concise brief (short summary).
    """
    # Simple summary based on first/last lines and key points
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return "No content to summarize."
    
    # For very short content
    if len(lines) <= 3:
        return content
    
    # Extract key information
    summary_parts = []
    
    # Focus on focus areas if specified
    if focus_areas:
        for area in focus_areas:
            # Look for lines containing focus area keywords
            matching_lines = [line for line in lines if area.lower() in line.lower()]
            if matching_lines:
                summary_parts.append(f"• {area.capitalize()}: Found {len(matching_lines)} references")
    
    # Otherwise, create a general summary
    if not summary_parts:
        # Take first few lines as summary for concise version
        first_lines = lines[:3]
        if len(lines) > 5:
            last_lines = lines[-2:]
            summary_parts.append("Key points from content:")
            summary_parts.extend([f"- {line[:100]}{'...' if len(line) > 100 else ''}" for line in first_lines])
            summary_parts.append(f"... (showing {len(lines)} total lines)")
            summary_parts.extend([f"- {line[:100]}{'...' if len(line) > 100 else ''}" for line in last_lines])
        else:
            summary_parts.extend([f"- {line[:150]}{'...' if len(line) > 150 else ''}" for line in lines])
    
    return '\n'.join(summary_parts)


def generate_standard_brief(content: str, focus_areas: List[str]) -> str:
    """
    Generate a standard brief (balanced detail).
    """
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return "No content to summarize."
    
    summary_parts = []
    content_type = detect_content_type(content)
    
    # Add content type info
    summary_parts.append(f"Content type: {content_type}")
    summary_parts.append(f"Total lines: {len(lines)}")
    summary_parts.append(f"Total characters: {len(content)}")
    
    # Process based on content type
    if content_type == "code":
        # Count functions, classes, imports
        functions = sum(1 for line in lines if line.startswith('def '))
        classes = sum(1 for line in lines if line.startswith('class '))
        imports = sum(1 for line in lines if line.startswith(('import ', 'from ')))
        
        summary_parts.append(f"Code analysis: {functions} functions, {classes} classes, {imports} imports")
        
        # Show key code structures
        if functions > 0:
            func_names = [line.split('def ')[1].split('(')[0].strip() for line in lines if line.startswith('def ')]
            summary_parts.append(f"Functions: {', '.join(func_names[:5])}{'...' if len(func_names) > 5 else ''}")
    
    elif content_type == "markdown":
        # Count headings
        headings = [line for line in lines if line.startswith('#')]
        summary_parts.append(f"Headings: {len(headings)} section(s)")
        if headings:
            summary_parts.append("Main sections: " + ", ".join([h.strip('# ')[:50] for h in headings[:3]]))
    
    # Add content highlights
    if lines:
        summary_parts.append("\nKey content highlights:")
        # Show representative lines
        sample_size = min(5, len(lines))
        step = max(1, len(lines) // sample_size)
        for i in range(0, len(lines), step):
            if len(summary_parts) < 15:  # Limit output size
                line = lines[i]
                if len(line) > 150:
                    line = line[:150] + "..."
                summary_parts.append(f"- {line}")
    
    return '\n'.join(summary_parts)


def generate_detailed_brief(content: str, focus_areas: List[str]) -> str:
    """
    Generate a detailed brief (comprehensive analysis).
    """
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    if not lines:
        return "No content to summarize."
    
    summary_parts = []
    content_type = detect_content_type(content)
    
    # Comprehensive analysis
    summary_parts.append(f"=== DETAILED ANALYSIS ===")
    summary_parts.append(f"Content Type: {content_type}")
    summary_parts.append(f"Total Lines: {len(lines)}")
    summary_parts.append(f"Total Characters: {len(content)}")
    summary_parts.append(f"Non-empty Lines: {len([l for l in lines if l])}")
    summary_parts.append(f"Average Line Length: {sum(len(l) for l in lines) // max(1, len(lines))}")
    
    # Focus areas analysis
    if focus_areas:
        summary_parts.append(f"\n=== FOCUS AREAS ANALYSIS ===")
        for area in focus_areas:
            matching_lines = [line for line in lines if area.lower() in line.lower()]
            summary_parts.append(f"\n{area.upper()}:")
            summary_parts.append(f"  • Found {len(matching_lines)} references")
            if matching_lines:
                summary_parts.append(f"  • Example references:")
                for line in matching_lines[:3]:
                    summary_parts.append(f"    - {line[:100]}{'...' if len(line) > 100 else ''}")
    
    # Content structure analysis
    summary_parts.append(f"\n=== CONTENT STRUCTURE ===")
    
    if content_type == "code":
        # Detailed code analysis
        functions = [(i+1, line.split('def ')[1].split('(')[0].strip()) 
                    for i, line in enumerate(lines) if line.startswith('def ')]
        classes = [(i+1, line.split('class ')[1].split('(')[0].strip().split(':')[0]) 
                  for i, line in enumerate(lines) if line.startswith('class ')]
        
        summary_parts.append(f"Functions: {len(functions)}")
        for line_num, func_name in functions[:5]:
            summary_parts.append(f"  • Line {line_num}: {func_name}()")
        if len(functions) > 5:
            summary_parts.append(f"  • ... and {len(functions) - 5} more functions")
        
        summary_parts.append(f"\nClasses: {len(classes)}")
        for line_num, class_name in classes[:3]:
            summary_parts.append(f"  • Line {line_num}: class {class_name}")
    
    elif content_type == "markdown":
        # Markdown structure
        headings = []
        for i, line in enumerate(lines):
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                heading_text = line.lstrip('#').strip()
                headings.append((i+1, level, heading_text))
        
        summary_parts.append(f"Headings: {len(headings)}")
        for line_num, level, text in headings:
            indent = "  " * (level - 1)
            summary_parts.append(f"{indent}• Line {line_num}: {'#'*level} {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Content samples
    summary_parts.append(f"\n=== CONTENT SAMPLES ===")
    summary_parts.append("Beginning of content:")
    for i in range(min(3, len(lines))):
        summary_parts.append(f"[{i+1}] {lines[i][:100]}{'...' if len(lines[i]) > 100 else ''}")
    
    if len(lines) > 6:
        summary_parts.append("\nMiddle of content:")
        mid_idx = len(lines) // 2
        for i in range(mid_idx, min(mid_idx + 2, len(lines))):
            summary_parts.append(f"[{i+1}] {lines[i][:100]}{'...' if len(lines[i]) > 100 else ''}")
    
    if len(lines) > 3:
        summary_parts.append("\nEnd of content:")
        for i in range(max(0, len(lines)-3), len(lines)):
            summary_parts.append(f"[{i+1}] {lines[i][:100]}{'...' if len(lines[i]) > 100 else ''}")
    
    return '\n'.join(summary_parts)


def format_structured_brief(title: str, brief_text: str, detail_level: str, focus_areas: List[str]) -> str:
    """
    Format the brief in a structured way.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    structured = f"""
{'=' * 70}
BRIEF: {title}
{'=' * 70}

Generated: {timestamp}
Detail Level: {detail_level.upper()}
Focus Areas: {', '.join(focus_areas) if focus_areas else 'None specified'}

{'=' * 70}
SUMMARY
{'=' * 70}

{brief_text}

{'=' * 70}
END OF BRIEF
{'=' * 70}
"""
    return structured.strip()


def format_simple_brief(title: str, brief_text: str) -> str:
    """
    Format the brief in a simple way.
    """
    return f"Brief: {title}\n\n{brief_text}"


# Export tools
tools = [brief]
TOOL_CALL_MAP = {
    "brief": brief
}

if __name__ == "__main__":
    # Test the brief function
    test_content = """# Project Documentation
    
## Overview
This project implements a new AI tool system for content processing.

## Features
- Natural language processing
- Content summarization
- Multi-format support

## Implementation Details
The system uses Python 3.8+ and requires the following dependencies:
- numpy
- pandas
- scikit-learn

## Usage
To use the system, import the main module and call the process() function."""

    print("Testing BriefTool...")
    print("-" * 60)
    
    # Test concise brief
    print("1. Concise Brief:")
    print(brief(test_content, detail_level="concise", include_structure=True))
    print("-" * 60)
    
    # Test standard brief  
    print("\n2. Standard Brief:")
    print(brief(test_content, detail_level="standard", include_structure=False))
    print("-" * 60)
    
    # Test detailed brief
    print("\n3. Detailed Brief with focus areas:")
    print(brief(test_content, detail_level="detailed", focus_areas="implementation,features", include_structure=True))
    print("-" * 60)