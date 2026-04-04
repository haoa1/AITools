#!/usr/bin/env python3
"""
FileEditTool implementation for AITools (Claude Code compatible version).
Provides file editing functionality aligned with Claude Code's FileEditTool.
Based on analysis of Claude Code source: restored-src/src/tools/FileEditTool/types.ts
"""

import os
import json
import difflib
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
    description="Edit a file by replacing text. Compatible with Claude Code's FileEditTool.",
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


def generate_structured_patch(original_content: str, new_content: str):
    """
    Generate structured patch similar to Claude Code's structuredPatch format.
    Returns a list of hunk objects.
    """
    if original_content == new_content:
        return []
    
    # Create unified diff
    diff = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='original',
        tofile='new',
        lineterm='\n'
    ))
    
    if not diff:
        return []
    
    # Parse diff to create structured patch
    # This is a simplified version - Claude Code has more detailed parsing
    original_lines = original_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    # Create a simple hunk representation
    hunk = {
        "oldStart": 1,
        "oldLines": len(original_lines),
        "newStart": 1,
        "newLines": len(new_lines),
        "lines": diff[2:] if len(diff) > 2 else diff  # Skip header lines
    }
    
    return [hunk]


def file_edit(file_path: str, old_string: str, new_string: str, 
              replace_all: bool = False, encoding: str = "utf-8") -> str:
    """
    Edit a file by replacing old_string with new_string.
    
    Claude Code compatible version based on FileEditTool/types.ts:
    - filePath: The file path that was edited
    - oldString: The original string that was replaced
    - newString: The new string that replaced it
    - originalFile: The original file contents before editing
    - structuredPatch: Diff patch showing the changes
    - userModified: Whether the user modified the proposed changes (always False for our implementation)
    - replaceAll: Whether all occurrences were replaced
    
    Args:
        file_path: Absolute path to the file to edit
        old_string: The text to replace
        new_string: The text to replace it with
        replace_all: Whether to replace all occurrences (default: False)
        encoding: File encoding (default: 'utf-8')
        
    Returns:
        JSON-formatted operation result matching Claude Code's FileEditOutput
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
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Check if it's a file
        if not os.path.isfile(normalized_path):
            return json.dumps({
                "error": f"Path is not a file: {normalized_path}",
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Check read permission
        if not os.access(normalized_path, os.R_OK):
            return json.dumps({
                "error": f"No read permission for file: {normalized_path}",
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Check write permission
        if not os.access(normalized_path, os.W_OK):
            return json.dumps({
                "error": f"No write permission for file: {normalized_path}",
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Check file size (warning for large files)
        file_size = os.path.getsize(normalized_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return json.dumps({
                "warning": f"File is large ({format_file_size(file_size)}). Editing may be slow.",
                "filePath": normalized_path,
                "fileSize": file_size,
                "sizeFormatted": format_file_size(file_size),
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
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": f"Cannot read file: {str(e)}",
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Check if old_string exists in the file
        if old_string not in original_content:
            return json.dumps({
                "error": f"Old string not found in file: {normalized_path}",
                "filePath": normalized_path,
                "oldString": old_string[:50] + ("..." if len(old_string) > 50 else ""),
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
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Write the file
        try:
            with open(normalized_path, 'w', encoding=encoding) as f:
                f.write(new_content)
        except Exception as e:
            return json.dumps({
                "error": f"Cannot write to file: {str(e)}",
                "filePath": normalized_path,
                "success": False
            }, indent=2)
        
        # Generate structured patch
        structured_patch = generate_structured_patch(original_content, new_content)
        
        # Build Claude Code compatible response
        response = {
            "filePath": normalized_path,
            "oldString": old_string,
            "newString": new_string,
            "originalFile": original_content,
            "structuredPatch": structured_patch,
            "userModified": False,  # Our implementation doesn't support user modifications
            "replaceAll": replace_all
        }
        
        # Add metadata (not part of Claude Code spec but useful)
        response["_metadata"] = {
            "success": True,
            "fileName": os.path.basename(normalized_path),
            "originalLength": len(original_content),
            "newLength": len(new_content),
            "occurrenceCount": occurrence_count,
            "replacementCount": replacement_count,
            "encoding": encoding,
            "fileSize": os.path.getsize(normalized_path) if os.path.exists(normalized_path) else 0
        }
        
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
    import tempfile
    
    print("Testing FileEditTool (Claude Code compatible)...")
    print("-" * 60)
    
    # Create test file
    test_content = """Line 1: Hello World
Line 2: Hello again
Line 3: Goodbye World
Line 4: Hello one more time
Line 5: Final line
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    try:
        # Test 1: Replace first occurrence
        print("1. Replace first occurrence of 'Hello':")
        result = file_edit(test_file, "Hello", "Greetings")
        data = json.loads(result)
        
        print(f"Success: {'error' not in data and ('_metadata' in data and data['_metadata'].get('success') == True)}")
        print(f"File path: {data.get('filePath')}")
        print(f"Old string: {data.get('oldString')}")
        print(f"New string: {data.get('newString')}")
        print(f"Has originalFile: {'originalFile' in data}")
        print(f"Has structuredPatch: {'structuredPatch' in data}")
        print(f"userModified: {data.get('userModified')}")
        print(f"replaceAll: {data.get('replaceAll')}")
        
        # Test 2: Replace all occurrences
        print("\n2. Replace all occurrences of 'World':")
        result2 = file_edit(test_file, "World", "Universe", replace_all=True)
        data2 = json.loads(result2)
        print(f"replaceAll: {data2.get('replaceAll')}")
        
        # Test 3: Check Claude Code compatibility
        print("\n3. Claude Code compatibility check:")
        expected_fields = ["filePath", "oldString", "newString", "originalFile", "structuredPatch", "userModified", "replaceAll"]
        missing_fields = [field for field in expected_fields if field not in data]
        
        if missing_fields:
            print(f"  Missing fields: {missing_fields}")
        else:
            print("  All expected fields present ✓")
            
    finally:
        # Cleanup
        os.unlink(test_file)
        print(f"\nCleaned up test file: {test_file}")