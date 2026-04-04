#!/usr/bin/env python3
"""
FileWriteTool implementation for AITools (simplified version).
Provides file writing functionality aligned with Claude Code's FileWriteTool.
Simplified version - supports basic file writing with create/update distinction.
"""

import os
import json
from base import function_ai, parameters_func, property_param

# Property definitions for FileWriteTool
__FILE_PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The absolute path to the file to write (must be absolute, not relative).",
    t="string",
    required=True,
)

__CONTENT_PROPERTY__ = property_param(
    name="content",
    description="The content to write to the file.",
    t="string",
    required=True,
)

__MODE_PROPERTY__ = property_param(
    name="mode",
    description="Write mode: 'w' for overwrite (default), 'a' for append.",
    t="string",
    required=False,
)

__ENCODING_PROPERTY__ = property_param(
    name="encoding",
    description="File encoding (default: 'utf-8').",
    t="string",
    required=False,
)

# Function metadata
__FILE_WRITE_FUNCTION__ = function_ai(
    name="file_write",
    description="Write a file to the local filesystem. Simplified version of Claude Code's FileWriteTool.",
    parameters=parameters_func([
        __FILE_PATH_PROPERTY__,
        __CONTENT_PROPERTY__,
        __MODE_PROPERTY__,
        __ENCODING_PROPERTY__,
    ]),
)

tools = [__FILE_WRITE_FUNCTION__]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def file_write(file_path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> str:
    """
    Write content to a file with basic create/update distinction.
    
    Simplified version of Claude Code's FileWriteTool that supports:
    1. Basic file writing (overwrite and append modes)
    2. Create vs update operation type detection
    3. Permission and path validation
    4. JSON-formatted output with metadata
    
    Args:
        file_path: Absolute path to the file to write
        content: Content to write to the file
        mode: Write mode - 'w' for overwrite, 'a' for append (default: 'w')
        encoding: File encoding (default: 'utf-8')
        
    Returns:
        JSON-formatted operation result with metadata
    """
    try:
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            return json.dumps({
                "error": "File path must be a non-empty string",
                "success": False
            }, indent=2)
        
        if not content or not isinstance(content, str):
            return json.dumps({
                "error": "Content must be a non-empty string",
                "success": False
            }, indent=2)
        
        if mode not in ["w", "a"]:
            return json.dumps({
                "error": f"Invalid mode '{mode}'. Use 'w' (overwrite) or 'a' (append).",
                "success": False
            }, indent=2)
        
        # Normalize and expand path
        normalized_path = os.path.normpath(file_path)
        
        # Check if path is absolute (simplified requirement)
        if not os.path.isabs(normalized_path):
            return json.dumps({
                "error": f"File path should be absolute: {normalized_path}",
                "suggestion": "Use os.path.abspath() to convert relative paths",
                "success": False
            }, indent=2)
        
        # Check if file already exists
        file_exists = os.path.exists(normalized_path)
        
        # Determine operation type
        if mode == "w":
            operation_type = "create" if not file_exists else "update"
        else:  # mode == "a"
            operation_type = "append"
            if not file_exists:
                # For append mode, creating a new file is still "create"
                operation_type = "create"
        
        # Check write permission for parent directory
        parent_dir = os.path.dirname(normalized_path)
        if parent_dir and not os.path.exists(parent_dir):
            # Try to create parent directory
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                return json.dumps({
                    "error": f"Cannot create parent directory: {str(e)}",
                    "parent_dir": parent_dir,
                    "success": False
                }, indent=2)
        
        # Check if parent directory is writable
        if os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
            return json.dumps({
                "error": f"No write permission for directory: {parent_dir}",
                "directory": parent_dir,
                "success": False
            }, indent=2)
        
        # If file exists and we're not appending, check if it's writable
        if file_exists and mode == "w" and not os.access(normalized_path, os.W_OK):
            return json.dumps({
                "error": f"No write permission for file: {normalized_path}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Get original content for update operations (simplified - no diff)
        original_content = None
        if file_exists and mode == "w":
            try:
                with open(normalized_path, 'r', encoding=encoding) as f:
                    original_content = f.read()
            except Exception:
                # If we can't read original content, still proceed with write
                original_content = "[cannot read original content]"
        
        # Write the file
        try:
            if mode == "a":
                write_mode = "a"
            else:
                write_mode = "w"
            
            with open(normalized_path, write_mode, encoding=encoding) as f:
                f.write(content)
            
            # Get file stats after writing
            file_stats = os.stat(normalized_path)
            file_size = file_stats.st_size
            
            # Calculate content statistics
            content_length = len(content)
            line_count = content.count('\n') + 1 if content else 0
            
            # Build response
            response = {
                "success": True,
                "type": operation_type,
                "filePath": normalized_path,
                "fileName": os.path.basename(normalized_path),
                "contentLength": content_length,
                "contentPreview": content[:100] + ("..." if len(content) > 100 else ""),
                "lineCount": line_count,
                "fileSize": file_size,
                "sizeFormatted": format_file_size(file_size),
                "encoding": encoding,
                "mode": mode,
                "modifiedTime": file_stats.st_mtime,
                "summary": f"{operation_type.capitalize()}d file {os.path.basename(normalized_path)} ({content_length} chars, {line_count} lines)"
            }
            
            # Add original content info for updates
            if operation_type == "update" and original_content:
                original_length = len(original_content)
                original_lines = original_content.count('\n') + 1 if original_content else 0
                response["originalInfo"] = {
                    "length": original_length,
                    "lineCount": original_lines,
                    "sizeChange": content_length - original_length,
                    "lineChange": line_count - original_lines
                }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Error writing to file: {str(e)}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "file_write": file_write
}


if __name__ == "__main__":
    # Test the file_write function
    print("Testing FileWriteTool (simplified)...")
    print("-" * 60)
    
    # Create test directory
    test_dir = "test_write_dir"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "test_write_file.txt")
    
    try:
        # Test 1: Create new file
        print("1. Creating new file:")
        content1 = "Line 1: This is a test file\nLine 2: Created by FileWriteTool\n"
        result = file_write(test_file, content1)
        print(json.dumps(json.loads(result), indent=2)[:300] + "..." if len(result) > 300 else result)
        
        # Test 2: Update existing file
        print("\n2. Updating existing file:")
        content2 = "Line 1: Updated content\nLine 2: This is an update\nLine 3: New line added\n"
        result = file_write(test_file, content2)
        data = json.loads(result)
        print(f"Success: {data.get('success')}")
        print(f"Type: {data.get('type')}")
        print(f"Summary: {data.get('summary')}")
        
        # Test 3: Append to file
        print("\n3. Appending to file:")
        content3 = "Line 4: Appended content\nLine 5: More appended lines\n"
        result = file_write(test_file, content3, mode="a")
        data = json.loads(result)
        print(f"Success: {data.get('success')}")
        print(f"Type: {data.get('type')}")
        
        # Test 4: Invalid path
        print("\n4. Invalid path (relative):")
        result = file_write("relative_path.txt", "test")
        data = json.loads(result)
        print(f"Error: {data.get('error', 'No error')}")
        
        # Test 5: Invalid mode
        print("\n5. Invalid mode:")
        result = file_write("/tmp/test.txt", "test", mode="x")
        data = json.loads(result)
        print(f"Error: {data.get('error', 'No error')}")
        
    finally:
        # Cleanup
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\nCleaned up test directory: {test_dir}")
    
    print("-" * 60)
    print("Test completed!")