#!/usr/bin/env python3
"""
FileReadTool implementation for AITools (simplified version).
Provides file reading functionality aligned with Claude Code's FileReadTool.
Simplified version - supports basic text file reading.
"""

import os
import json
from base import function_ai, parameters_func, property_param

# Property definitions for FileReadTool
__FILE_PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The path to the file to read.",
    t="string",
    required=True,
)

__ENCODING_PROPERTY__ = property_param(
    name="encoding",
    description="File encoding (default: 'utf-8').",
    t="string",
    required=False,
)

__LINE_START_PROPERTY__ = property_param(
    name="line_start",
    description="Starting line number (1-indexed). Default: 1.",
    t="integer",
    required=False,
)

__LINE_END_PROPERTY__ = property_param(
    name="line_end",
    description="Ending line number (inclusive). Default: 0 (read to end).",
    t="integer",
    required=False,
)

# Function metadata
__FILE_READ_FUNCTION__ = function_ai(
    name="file_read",
    description="Read a file with basic text file support. Simplified version of Claude Code's FileReadTool.",
    parameters=parameters_func([
        __FILE_PATH_PROPERTY__,
        __ENCODING_PROPERTY__,
        __LINE_START_PROPERTY__,
        __LINE_END_PROPERTY__,
    ]),
)

tools = [__FILE_READ_FUNCTION__]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def file_read(file_path: str, encoding: str = "utf-8", 
             line_start: int = 1, line_end: int = 0) -> str:
    """
    Read a text file with basic line range support.
    
    Simplified version of Claude Code's FileReadTool that supports:
    1. Basic text file reading
    2. Line range selection (start/end)
    3. Encoding support
    4. Error handling
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        line_start: Starting line number (1-indexed, default: 1)
        line_end: Ending line number (0 = read to end)
        
    Returns:
        JSON-formatted file content with metadata
    """
    try:
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return json.dumps({
                "error": "File path must be a non-empty string",
                "file_path": file_path,
                "success": False
            }, indent=2)
        
        # Normalize path
        normalized_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            return json.dumps({
                "error": f"File does not exist: {normalized_path}",
                "file_path": normalized_path,
                "suggestion": suggest_similar_file(normalized_path),
                "success": False
            }, indent=2)
        
        # Check if it's a file
        if not os.path.isfile(normalized_path):
            return json.dumps({
                "error": f"Path is not a file: {normalized_path}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Check read permission
        if not os.access(normalized_path, os.R_OK):
            return json.dumps({
                "error": f"No read permission for file: {normalized_path}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Check file size (warning for large files)
        file_size = os.path.getsize(normalized_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return json.dumps({
                "warning": f"File is large ({format_file_size(file_size)}). Reading may be slow.",
                "file_path": normalized_path,
                "file_size": file_size,
                "size_formatted": format_file_size(file_size),
                "success": False,
                "suggestion": "Consider using line range parameters or a different tool"
            }, indent=2)
        
        # Read the file
        try:
            with open(normalized_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding or return error
            return json.dumps({
                "error": f"Encoding error with '{encoding}'. File may be binary or use different encoding.",
                "file_path": normalized_path,
                "suggestion": "Try different encoding or check if file is text-based",
                "success": False
            }, indent=2)
        
        # Apply line range
        total_lines = len(lines)
        
        # Validate line_start
        if line_start < 1:
            line_start = 1
        if line_start > total_lines:
            return json.dumps({
                "error": f"line_start ({line_start}) exceeds total lines ({total_lines})",
                "file_path": normalized_path,
                "total_lines": total_lines,
                "success": False
            }, indent=2)
        
        # Set line_end if not specified or 0
        if line_end == 0 or line_end > total_lines:
            line_end = total_lines
        
        # Validate line_end
        if line_end < line_start:
            return json.dumps({
                "error": f"line_end ({line_end}) is less than line_start ({line_start})",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Extract requested lines (convert to 0-indexed)
        start_idx = line_start - 1
        end_idx = line_end  # exclusive for slicing
        selected_lines = lines[start_idx:end_idx]
        
        # Calculate statistics
        selected_line_count = len(selected_lines)
        total_chars = sum(len(line) for line in selected_lines)
        
        # Format output with line numbers
        formatted_lines = []
        for i, line in enumerate(selected_lines, start=line_start):
            # Remove trailing newline for display
            line_display = line.rstrip('\n')
            formatted_lines.append({
                "line_number": i,
                "content": line_display,
                "length": len(line_display)
            })
        
        # Get file metadata
        file_stats = os.stat(normalized_path)
        
        # Build response
        response = {
            "success": True,
            "file_path": normalized_path,
            "file_name": os.path.basename(normalized_path),
            "file_size": file_size,
            "size_formatted": format_file_size(file_size),
            "total_lines": total_lines,
            "lines_read": selected_line_count,
            "line_range": {
                "start": line_start,
                "end": line_end,
                "total": total_lines
            },
            "characters_read": total_chars,
            "encoding": encoding,
            "modified_time": file_stats.st_mtime,
            "content": formatted_lines,
            "summary": f"Read {selected_line_count} lines ({total_chars} chars) from {os.path.basename(normalized_path)}"
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error reading file: {str(e)}",
            "file_path": file_path,
            "success": False
        }, indent=2)


def suggest_similar_file(file_path: str) -> str:
    """Suggest similar files if the requested file doesn't exist."""
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    if not os.path.exists(directory):
        return f"Directory does not exist: {directory}"
    
    try:
        files_in_dir = os.listdir(directory)
        
        # Find files with similar names
        similar = []
        for f in files_in_dir:
            if filename.lower() in f.lower() or f.lower() in filename.lower():
                similar.append(f)
        
        if similar:
            return f"Similar files in directory: {', '.join(similar[:3])}"
        else:
            return f"No similar files found in {directory}"
            
    except Exception:
        return "Cannot list directory contents"


def get_file_metadata(file_path: str) -> dict:
    """Get basic file metadata."""
    try:
        stats = os.stat(file_path)
        return {
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "created": stats.st_ctime,
            "accessed": stats.st_atime,
            "is_file": os.path.isfile(file_path),
            "is_dir": os.path.isdir(file_path),
            "exists": os.path.exists(file_path)
        }
    except Exception:
        return {}


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "file_read": file_read
}


if __name__ == "__main__":
    # Test the file_read function
    print("Testing FileReadTool (simplified)...")
    print("-" * 60)
    
    # Create a test file
    test_file = "test_read_file.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Line 1: This is a test file\n")
        f.write("Line 2: For testing FileReadTool\n")
        f.write("Line 3: With multiple lines\n")
        f.write("Line 4: To demonstrate functionality\n")
        f.write("Line 5: End of test file\n")
    
    try:
        # Test 1: Read entire file
        print("1. Reading entire file:")
        result = file_read(test_file)
        print(json.dumps(json.loads(result), indent=2)[:500] + "..." if len(result) > 500 else result)
        
        # Test 2: Read with line range
        print("\n2. Reading lines 2-4:")
        result = file_read(test_file, line_start=2, line_end=4)
        data = json.loads(result)
        print(f"Success: {data.get('success')}")
        print(f"Lines read: {data.get('lines_read')}")
        
        # Test 3: Non-existent file
        print("\n3. Non-existent file:")
        result = file_read("non_existent_file.txt")
        print(json.loads(result).get('error', 'No error'))
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")
    
    print("-" * 60)
    print("Test completed!")