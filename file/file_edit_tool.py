#!/usr/bin/env python3
"""
FileEditTool implementation for AITools (simplified version).
Provides file editing functionality aligned with Claude Code's FileEditTool.
Simplified version - supports basic string replacement in files.
"""

import os
import json
from base import function_ai, parameters_func, property_param

# Property definitions for FileEditTool
__FILE_PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The absolute path to the file to modify.",
    t="string",
    required=True,
)

__OLD_STRING_PROPERTY__ = property_param(
    name="old_string",
    description="The text to replace.",
    t="string",
    required=True,
)

__NEW_STRING_PROPERTY__ = property_param(
    name="new_string",
    description="The text to replace it with (must be different from old_string).",
    t="string",
    required=True,
)

__REPLACE_ALL_PROPERTY__ = property_param(
    name="replace_all",
    description="Replace all occurrences of old_string (default false).",
    t="boolean",
    required=False,
)

__ENCODING_PROPERTY__ = property_param(
    name="encoding",
    description="File encoding (default: 'utf-8').",
    t="string",
    required=False,
)

# Function metadata
__FILE_EDIT_FUNCTION__ = function_ai(
    name="file_edit",
    description="Edit a file by replacing text. Simplified version of Claude Code's FileEditTool.",
    parameters=parameters_func([
        __FILE_PATH_PROPERTY__,
        __OLD_STRING_PROPERTY__,
        __NEW_STRING_PROPERTY__,
        __REPLACE_ALL_PROPERTY__,
        __ENCODING_PROPERTY__,
    ]),
)

tools = [__FILE_EDIT_FUNCTION__]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def file_edit(file_path: str, old_string: str, new_string: str, 
              replace_all: bool = False, encoding: str = "utf-8") -> str:
    """
    Edit a file by replacing old_string with new_string.
    
    Simplified version of Claude Code's FileEditTool that supports:
    1. Basic string replacement in files
    2. Option to replace all occurrences or just the first
    3. File validation and error handling
    4. JSON-formatted output with replacement statistics
    
    Args:
        file_path: Absolute path to the file to edit
        old_string: The text to replace
        new_string: The text to replace it with
        replace_all: Whether to replace all occurrences (default: False)
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
        
        if not old_string or not isinstance(old_string, str):
            return json.dumps({
                "error": "Old string must be a non-empty string",
                "success": False
            }, indent=2)
        
        if new_string is None or not isinstance(new_string, str):
            return json.dumps({
                "error": "New string must be a string",
                "success": False
            }, indent=2)
        
        if old_string == new_string:
            return json.dumps({
                "error": "Old string and new string must be different",
                "success": False
            }, indent=2)
        
        # Normalize path
        normalized_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            return json.dumps({
                "error": f"File does not exist: {normalized_path}",
                "file_path": normalized_path,
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
        
        # Check write permission
        if not os.access(normalized_path, os.W_OK):
            return json.dumps({
                "error": f"No write permission for file: {normalized_path}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Check file size (warning for large files)
        file_size = os.path.getsize(normalized_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return json.dumps({
                "warning": f"File is large ({format_file_size(file_size)}). Editing may be slow.",
                "file_path": normalized_path,
                "file_size": file_size,
                "size_formatted": format_file_size(file_size),
                "success": False,
                "suggestion": "Consider using a different approach for large files"
            }, indent=2)
        
        # Read the file
        try:
            with open(normalized_path, 'r', encoding=encoding) as f:
                original_content = f.read()
        except UnicodeDecodeError:
            return json.dumps({
                "error": f"Encoding error with '{encoding}'. File may be binary or use different encoding.",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": f"Cannot read file: {str(e)}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Check if old_string exists in the file
        if old_string not in original_content:
            return json.dumps({
                "error": f"Old string not found in file: {normalized_path}",
                "file_path": normalized_path,
                "old_string_preview": old_string[:50] + ("..." if len(old_string) > 50 else ""),
                "success": False,
                "suggestion": "Check for typos or different whitespace"
            }, indent=2)
        
        # Count occurrences before replacement
        occurrence_count = original_content.count(old_string)
        
        # Perform replacement
        if replace_all:
            new_content = original_content.replace(old_string, new_string)
            replacement_count = occurrence_count
        else:
            # Replace only the first occurrence
            new_content = original_content.replace(old_string, new_string, 1)
            replacement_count = 1
        
        # Check if replacement actually changed anything
        if original_content == new_content:
            return json.dumps({
                "error": "Replacement did not change file content",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Write the file
        try:
            with open(normalized_path, 'w', encoding=encoding) as f:
                f.write(new_content)
        except Exception as e:
            return json.dumps({
                "error": f"Cannot write to file: {str(e)}",
                "file_path": normalized_path,
                "success": False
            }, indent=2)
        
        # Get updated file stats
        file_stats = os.stat(normalized_path)
        
        # Calculate statistics
        original_length = len(original_content)
        new_length = len(new_content)
        original_lines = original_content.count('\n') + 1 if original_content else 0
        new_lines = new_content.count('\n') + 1 if new_content else 0
        
        # Build response
        response = {
            "success": True,
            "filePath": normalized_path,
            "fileName": os.path.basename(normalized_path),
            "oldString": old_string[:100] + ("..." if len(old_string) > 100 else ""),
            "newString": new_string[:100] + ("..." if len(new_string) > 100 else ""),
            "originalLength": original_length,
            "newLength": new_length,
            "lengthChange": new_length - original_length,
            "originalLines": original_lines,
            "newLines": new_lines,
            "lineChange": new_lines - original_lines,
            "occurrenceCount": occurrence_count,
            "replacementCount": replacement_count,
            "replaceAll": replace_all,
            "encoding": encoding,
            "fileSize": file_stats.st_size,
            "sizeFormatted": format_file_size(file_stats.st_size),
            "modifiedTime": file_stats.st_mtime,
            "summary": f"Replaced {replacement_count} occurrence(s) of '{old_string[:30]}{'...' if len(old_string) > 30 else ''}' in {os.path.basename(normalized_path)}"
        }
        
        # Add content preview for small files
        if original_length < 1000:
            response["originalPreview"] = original_content[:200] + ("..." if original_length > 200 else "")
            response["newPreview"] = new_content[:200] + ("..." if new_length > 200 else "")
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "file_edit": file_edit
}


if __name__ == "__main__":
    # Test the file_edit function
    print("Testing FileEditTool (simplified)...")
    print("-" * 60)
    
    # Create test file
    test_file = "test_edit_file.txt"
    test_content = """Line 1: Hello World
Line 2: Hello again
Line 3: Goodbye World
Line 4: Hello one more time
Line 5: Final line
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test 1: Replace first occurrence
        print("1. Replace first occurrence of 'Hello':")
        result = file_edit(test_file, "Hello", "Greetings")
        print(json.dumps(json.loads(result), indent=2)[:300] + "..." if len(result) > 300 else result)
        
        # Read file to verify
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"First line after edit: {content.splitlines()[0] if content.splitlines() else 'Empty file'}")
        
        # Test 2: Replace all occurrences
        print("\n2. Replace all occurrences of 'World':")
        result = file_edit(test_file, "World", "Universe", replace_all=True)
        data = json.loads(result)
        print(f"Success: {data.get('success')}")
        print(f"Replacement count: {data.get('replacementCount')}")
        
        # Test 3: String not found
        print("\n3. String not found:")
        result = file_edit(test_file, "NotFound", "Replacement")
        data = json.loads(result)
        print(f"Error: {data.get('error', 'No error')}")
        
        # Test 4: Same old and new string
        print("\n4. Same old and new string:")
        result = file_edit(test_file, "line", "line")
        data = json.loads(result)
        print(f"Error: {data.get('error', 'No error')}")
        
        # Test 5: Non-existent file
        print("\n5. Non-existent file:")
        result = file_edit("non_existent.txt", "test", "replacement")
        data = json.loads(result)
        print(f"Error: {data.get('error', 'No error')}")
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")
    
    print("-" * 60)
    print("Test completed!")