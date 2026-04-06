#!/usr/bin/env python3
"""
FileReadTool implementation for AITools.
Provides file reading functionality aligned with Claude Code's FileReadTool.
Focuses on text file reading with Claude Code compatibility.
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Union

# AITools decorators
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS (matching Claude Code's FileReadTool interface)
# ============================================================================

__FILE_PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The absolute path to the file to read.",
    t="string",
    required=True
)

__OFFSET_PROPERTY__ = property_param(
    name="offset",
    description="The line number to start reading from. Only provide if the file is too large to read at once",
    t="integer",
    required=False
)

__LIMIT_PROPERTY__ = property_param(
    name="limit",
    description="The number of lines to read. Only provide if the file is too large to read at once.",
    t="integer",
    required=False
)

__ENCODING_PROPERTY__ = property_param(
    name="encoding",
    description="File encoding (default: 'utf-8'). Use for text files only.",
    t="string",
    required=False
)

# ============================================================================
# FUNCTION DEFINITION
# ============================================================================

__FILE_READ_FUNCTION__ = function_ai(
    name="read",
    description="Read a file with text file support. Simplified version of Claude Code's FileReadTool.",
    parameters=parameters_func([
        __FILE_PATH_PROPERTY__,
        __OFFSET_PROPERTY__,
        __LIMIT_PROPERTY__,
        __ENCODING_PROPERTY__,
    ])
)

def _read(file_path: str, offset: int = 1, limit: int = 0, mode: str = "r") -> str:
    if mode not in ("r", "rb"):
        return f"Error: Invalid mode '{mode}'. Use 'r' or 'rb'."
    if offset < 1:
        return f"Error: Offset must be at least 1: {offset}"
    if limit < 0:
        return f"Error: Limit cannot be negative: {limit}"

    try:
        # Line-based reading only makes sense for text mode
        if mode == "rb":
            return "Error: Binary mode ('rb') not supported for line-based reading. Use text mode ('r')."
        
        # Convert 1-indexed offset to 0-indexed for internal processing
        offset_0 = offset - 1
        
        # Try UTF-8 encoding first, fallback to latin-1
        lines = []
        lines_collected = 0
        current_line = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if current_line >= offset_0:
                        if limit == 0 or lines_collected < limit:
                            lines.append(line)
                            lines_collected += 1
                        else:
                            break
                    current_line += 1
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    if current_line >= offset_0:
                        if limit == 0 or lines_collected < limit:
                            lines.append(line)
                            lines_collected += 1
                        else:
                            break
                    current_line += 1
        
        # If offset is beyond total lines, return empty string
        if current_line <= offset_0 and lines_collected == 0:
            return ""
        
        return ''.join(lines)
        
    except Exception as e:
        return f"Error: Unexpected error when reading file: {str(e)}"

# ============================================================================
# MAIN FUNCTION IMPLEMENTATION
# ============================================================================

def read(
    file_path: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    encoding: str = "utf-8"
) -> str:
    """
    Read a text file with Claude Code compatibility.
    
    This tool mimics Claude Code's FileReadTool functionality for reading
    text files with line range support.
    
    Args:
        file_path: The absolute path to the file to read
        offset: The line number to start reading from (1-indexed)
        limit: The number of lines to read (0 or None = read to end)
        encoding: File encoding (default: utf-8)
        
    Returns:
        JSON string matching Claude Code's format:
        {
            "type": "text",
            "file": {
                "filePath": "path/to/file",
                "content": "file content",
                "numLines": 10,
                "startLine": 1,
                "totalLines": 100
            }
        }
        or error message if operation fails
    """
    try:
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return json.dumps({
                "error": True,
                "message": "File path must be a non-empty string",
                "error_code": 1
            }, indent=2)
        
        # Normalize path
        normalized_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            suggestion = suggest_similar_file(normalized_path)
            return json.dumps({
                "error": True,
                "message": f"File does not exist: {normalized_path}",
                "filePath": normalized_path,
                "suggestion": suggestion,
                "error_code": 2
            }, indent=2)
        
        # Check if it's a file
        if not os.path.isfile(normalized_path):
            return json.dumps({
                "error": True,
                "message": f"Path is not a file: {normalized_path}",
                "filePath": normalized_path,
                "error_code": 3
            }, indent=2)
        
        # Check read permission
        if not os.access(normalized_path, os.R_OK):
            return json.dumps({
                "error": True,
                "message": f"No read permission for file: {normalized_path}",
                "filePath": normalized_path,
                "error_code": 4
            }, indent=2)
        
        # Check file size (warning for large files)
        file_size = os.path.getsize(normalized_path)
        size_formatted = format_file_size(file_size)
        
        # Warn for very large files
        if file_size > 50 * 1024 * 1024:  # 50MB
            return json.dumps({
                "warning": True,
                "message": f"File is very large ({size_formatted}). Reading may be slow.",
                "filePath": normalized_path,
                "fileSize": file_size,
                "sizeFormatted": size_formatted,
                "suggestion": "Consider using offset and limit parameters to read specific portions"
            }, indent=2)
        
        # Set default values for offset and limit
        actual_offset = offset if offset is not None else 1
        actual_limit = limit if limit is not None else 0
        
        # Validate offset and limit
        if actual_offset < 1:
            return json.dumps({
                "error": True,
                "message": f"Offset must be at least 1: {actual_offset}",
                "error_code": 5
            }, indent=2)
        
        if actual_limit < 0:
            return json.dumps({
                "error": True,
                "message": f"Limit cannot be negative: {actual_limit}",
                "error_code": 6
            }, indent=2)
        
        # Try to read the file using AITools read function
        try:
            # First, get total lines to calculate actual line ranges
            total_lines = count_file_lines(normalized_path, encoding)
            
            # Use AITools read function
            content = _read(
                file_path=normalized_path,
                offset=actual_offset,
                limit=actual_limit,
                mode="r"
            )
            
            # If content is empty and offset is beyond total lines
            if not content and actual_offset > total_lines:
                return json.dumps({
                    "error": True,
                    "message": f"Offset ({actual_offset}) exceeds total lines ({total_lines})",
                    "filePath": normalized_path,
                    "totalLines": total_lines,
                    "error_code": 7
                }, indent=2)
            
            # Remove trailing newline if present (common when reading files)
            if content and content.endswith('\n'):
                content = content.rstrip('\n')
            
            # Calculate actual lines read
            lines_read = len(content.splitlines()) if content else 0
            actual_end_line = actual_offset + lines_read - 1 if lines_read > 0 else actual_offset
            
            # Build Claude Code compatible response
            response = {
                "type": "text",
                "file": {
                    "filePath": normalized_path,
                    "content": content,
                    "numLines": lines_read,
                    "startLine": actual_offset,
                    "totalLines": total_lines
                },
                "metadata": {
                    "fileSize": file_size,
                    "sizeFormatted": size_formatted,
                    "encoding": encoding,
                    "modifiedTime": os.path.getmtime(normalized_path),
                    "offset": actual_offset,
                    "limit": actual_limit if actual_limit > 0 else "end of file"
                }
            }
            
            return json.dumps(response, indent=2)
            
        except UnicodeDecodeError:
            # Try with different encoding or return error
            return json.dumps({
                "error": True,
                "message": f"Encoding error with '{encoding}'. File may be binary or use different encoding.",
                "filePath": normalized_path,
                "suggestion": "Try different encoding or check if file is text-based",
                "error_code": 8
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Unexpected error reading file: {str(e)}",
            "filePath": file_path,
            "error_code": 99
        }, indent=2)


def count_file_lines(file_path: str, encoding: str = "utf-8") -> int:
    """
    Count total lines in a file efficiently.
    
    Args:
        file_path: Path to the file
        encoding: File encoding
        
    Returns:
        Total number of lines in the file
    """
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding=encoding) as f:
            line_count = 0
            for _ in f:
                line_count += 1
            return line_count
    except UnicodeDecodeError:
        # Try latin-1 as fallback
        with open(file_path, 'r', encoding='latin-1') as f:
            line_count = 0
            for _ in f:
                line_count += 1
            return line_count


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


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
                full_path = os.path.join(directory, f)
                if os.path.isfile(full_path):
                    similar.append(f)
        
        if similar:
            return f"Similar files in directory: {', '.join(similar[:3])}"
        else:
            return f"No similar files found in {directory}"
            
    except Exception:
        return "Cannot list directory contents"


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    try:
        stats = os.stat(file_path)
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": stats.st_size,
            "sizeFormatted": format_file_size(stats.st_size),
            "modified": stats.st_mtime,
            "created": stats.st_ctime,
            "accessed": stats.st_atime,
            "isFile": os.path.isfile(file_path),
            "isDir": os.path.isdir(file_path),
            "exists": os.path.exists(file_path),
            "extension": os.path.splitext(file_path)[1],
            "permissions": {
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "executable": os.access(file_path, os.X_OK)
            }
        }
    except Exception as e:
        return {"error": str(e)}


def read_file_with_line_numbers(file_path: str, offset: int = 1, limit: int = 0) -> str:
    """
    Read file with line numbers in the output.
    
    Args:
        file_path: Path to the file
        offset: Starting line (1-indexed)
        limit: Number of lines to read (0 = all)
        
    Returns:
        Formatted string with line numbers
    """
    try:
        content = aitools_read_file(file_path, offset, limit, "r")
        if not content:
            return f"No content found at offset {offset}"
        
        lines = content.splitlines()
        result_lines = []
        
        for i, line in enumerate(lines, start=offset):
            # Format: [line number] content
            result_lines.append(f"[{i:4d}] {line}")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# TOOL REGISTRATION
# ============================================================================

# List of all tools
tools = [
    __FILE_READ_FUNCTION__,
]

# Map function names to implementations
TOOL_CALL_MAP = {
    "read": read,
}


if __name__ == "__main__":
    # Test the FileReadTool
    print("Testing FileReadTool (Claude Code compatible)...")
    print("=" * 60)
    
    # Create a test file
    test_file = "test_file_read_tool.txt"
    test_content = """This is a test file for FileReadTool.
Line 2: Testing line range functionality.
Line 3: This file has multiple lines.
Line 4: To demonstrate offset and limit parameters.
Line 5: Each line is numbered for clarity.
Line 6: This is the sixth line.
Line 7: Almost done with the test.
Line 8: Second to last line.
Line 9: Final line of the test file.
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        print(f"Created test file: {test_file}")
        print(f"File size: {format_file_size(os.path.getsize(test_file))}")
        print(f"Total lines: {count_file_lines(test_file)}")
        
        print("\n" + "=" * 60)
        print("Test 1: Read entire file...")
        result1 = read(test_file)
        data1 = json.loads(result1)
        if data1.get("type") == "text":
            print(f"✓ Successfully read {data1['file']['numLines']} lines")
            print(f"  Content preview: {data1['file']['content'][:100]}...")
        
        print("\nTest 2: Read with offset (line 3)...")
        result2 = read(test_file, offset=3)
        data2 = json.loads(result2)
        if data2.get("type") == "text":
            print(f"✓ Read from line {data2['file']['startLine']}, got {data2['file']['numLines']} lines")
        
        print("\nTest 3: Read with offset and limit (lines 2-5)...")
        result3 = read(test_file, offset=2, limit=4)
        data3 = json.loads(result3)
        if data3.get("type") == "text":
            print(f"✓ Read lines {data3['file']['startLine']}-{data3['file']['startLine'] + data3['file']['numLines'] - 1}")
            print(f"  Content: {data3['file']['content'][:80]}...")
        
        print("\nTest 4: Read with line numbers display...")
        line_numbers_result = read_file_with_line_numbers(test_file, offset=3, limit=3)
        print(line_numbers_result[:200] + "..." if len(line_numbers_result) > 200 else line_numbers_result)
        
        print("\nTest 5: Error handling - non-existent file...")
        result5 = read("non_existent_file.txt")
        data5 = json.loads(result5)
        if data5.get("error"):
            print(f"✓ Correctly handled error: {data5['message']}")
        
        print("\nTest 6: Error handling - offset beyond total lines...")
        result6 = read(test_file, offset=100)
        data6 = json.loads(result6)
        if data6.get("error"):
            print(f"✓ Correctly handled error: {data6['message']}")
        
        print("\nTest 7: Get file info...")
        file_info = get_file_info(test_file)
        print(f"  Name: {file_info['name']}")
        print(f"  Size: {file_info['sizeFormatted']}")
        print(f"  Extension: {file_info['extension']}")
        
        print("\n" + "=" * 60)
        print("FileReadTool test completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")