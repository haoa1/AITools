#!/usr/bin/env python3
"""
FileWriteTool implementation for AITools.
Provides file writing functionality aligned with Claude Code's FileWriteTool.
Focuses on Claude Code compatibility with create/update distinction and simple diff.
"""

import os
import json
import difflib
import sys
from typing import Dict, List, Any, Optional, Tuple

# AITools decorators
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS (matching Claude Code's FileWriteTool interface)
# ============================================================================

__FILE_PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The absolute path to the file to write (must be absolute, not relative).",
    t="string",
    required=True
)

__CONTENT_PROPERTY__ = property_param(
    name="content",
    description="The content to write to the file.",
    t="string",
    required=True
)

# ============================================================================
# FUNCTION DEFINITION
# ============================================================================

__FILE_WRITE_FUNCTION__ = function_ai(
    name="write",
    description="Write a file to the local filesystem. Claude Code compatible version.",
    parameters=parameters_func([
        __FILE_PATH_PROPERTY__,
        __CONTENT_PROPERTY__,
    ])
)

# ============================================================================
# MAIN FUNCTION IMPLEMENTATION
# ============================================================================

def write(
    file_path: str,
    content: str
) -> str:
    """
    Write content to a file with Claude Code compatibility.
    
    This tool mimics Claude Code's FileWriteTool functionality for writing
    files with create/update distinction and simple diff output.
    
    Args:
        file_path: The absolute path to the file to write
        content: The content to write to the file
        
    Returns:
        JSON string matching Claude Code's format:
        {
            "type": "create" or "update",
            "filePath": "path/to/file",
            "content": "content written",
            "structuredPatch": [hunk objects...],
            "originalFile": "original content" or null
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
        
        if not content or not isinstance(content, str):
            return json.dumps({
                "error": True,
                "message": "Content must be a non-empty string",
                "error_code": 2
            }, indent=2)
        
        # Normalize path
        normalized_path = os.path.normpath(file_path)
        
        # Check if path is absolute (Claude Code requires absolute paths)
        if not os.path.isabs(normalized_path):
            # Try to make it absolute
            normalized_path = os.path.abspath(normalized_path)
        
        # Check if file already exists
        file_exists = os.path.exists(normalized_path)
        
        # Determine operation type (create or update)
        operation_type = "create" if not file_exists else "update"
        
        # Read original content for update operations
        original_content = None
        if file_exists:
            try:
                with open(normalized_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except UnicodeDecodeError:
                # Try latin-1 as fallback
                try:
                    with open(normalized_path, 'r', encoding='latin-1') as f:
                        original_content = f.read()
                except Exception as e:
                    # If we can't read, treat as binary or inaccessible
                    original_content = None
            except Exception as e:
                original_content = None
        
        # Check write permission
        if file_exists and not os.access(normalized_path, os.W_OK):
            return json.dumps({
                "error": True,
                "message": f"No write permission for file: {normalized_path}",
                "filePath": normalized_path,
                "error_code": 3
            }, indent=2)
        
        # Check parent directory write permission
        parent_dir = os.path.dirname(normalized_path)
        if parent_dir and not os.path.exists(parent_dir):
            # Try to create parent directory
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except Exception as e:
                return json.dumps({
                    "error": True,
                    "message": f"Cannot create parent directory: {str(e)}",
                    "parentDir": parent_dir,
                    "error_code": 4
                }, indent=2)
        
        if os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
            return json.dumps({
                "error": True,
                "message": f"No write permission for directory: {parent_dir}",
                "directory": parent_dir,
                "error_code": 5
            }, indent=2)
        
        # Write the file using AITools write function or direct write
        try:
            # Use simple write for compatibility
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Calculate simple diff for structuredPatch
            structured_patch = []
            if original_content is not None and original_content != content:
                # Create a simple diff
                diff = list(difflib.unified_diff(
                    original_content.splitlines(keepends=True),
                    content.splitlines(keepends=True),
                    fromfile='original',
                    tofile='new',
                    lineterm='\n'
                ))
                
                if diff:
                    # Create a simple hunk representation
                    # This is a simplified version of Claude Code's structuredPatch
                    hunk = {
                        "oldStart": 1,
                        "oldLines": len(original_content.splitlines()),
                        "newStart": 1,
                        "newLines": len(content.splitlines()),
                        "lines": diff[2:] if len(diff) > 2 else diff  # Skip header lines
                    }
                    structured_patch.append(hunk)
            
            # Build Claude Code compatible response
            response = {
                "type": operation_type,
                "filePath": normalized_path,
                "content": content,
                "structuredPatch": structured_patch,
                "originalFile": original_content
            }
            
            # Add metadata (not part of Claude Code spec but useful)
            response["_metadata"] = {
                "contentLength": len(content),
                "lineCount": content.count('\n') + 1 if content else 0,
                "fileSize": os.path.getsize(normalized_path) if os.path.exists(normalized_path) else 0,
                "encoding": "utf-8"
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": True,
                "message": f"Error writing to file: {str(e)}",
                "filePath": normalized_path,
                "error_code": 6
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": True,
            "message": f"Unexpected error: {str(e)}",
            "error_code": 99
        }, indent=2)


def generate_simple_diff(original: str, new: str) -> List[Dict[str, Any]]:
    """
    Generate a simplified diff between original and new content.
    
    Args:
        original: Original content
        new: New content
        
    Returns:
        List of hunk objects
    """
    if original == new:
        return []
    
    orig_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(orig_lines, new_lines, lineterm='\n'))
    
    if not diff:
        return []
    
    # Parse diff into hunks
    hunks = []
    current_hunk = None
    old_start = 1
    new_start = 1
    
    for line in diff[2:]:  # Skip header lines
        if line.startswith('@@'):
            # Hunk header: @@ -old_start,old_lines +new_start,new_lines @@
            if current_hunk:
                hunks.append(current_hunk)
            
            import re
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if match:
                old_start = int(match.group(1))
                old_lines = int(match.group(2)) if match.group(2) else 1
                new_start = int(match.group(3))
                new_lines = int(match.group(4)) if match.group(4) else 1
                
                current_hunk = {
                    "oldStart": old_start,
                    "oldLines": old_lines,
                    "newStart": new_start,
                    "newLines": new_lines,
                    "lines": []
                }
        elif current_hunk:
            current_hunk["lines"].append(line)
    
    if current_hunk:
        hunks.append(current_hunk)
    
    return hunks


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information."""
    try:
        stats = os.stat(file_path)
        return {
            "path": file_path,
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "created": stats.st_ctime,
            "exists": os.path.exists(file_path),
            "isFile": os.path.isfile(file_path)
        }
    except Exception:
        return {}


# ============================================================================
# TOOL REGISTRATION
# ============================================================================

# List of all tools
tools = [
    __FILE_WRITE_FUNCTION__,
]

# Map function names to implementations
TOOL_CALL_MAP = {
    "write": write,
}


if __name__ == "__main__":
    # Test the FileWriteTool
    print("Testing FileWriteTool (Claude Code compatible)...")
    print("=" * 60)
    
    import tempfile
    import shutil
    
    # Create a test directory
    test_dir = tempfile.mkdtemp(prefix="test_file_write_")
    
    try:
        test_file = os.path.join(test_dir, "test_file.txt")
        
        print(f"Test directory: {test_dir}")
        print(f"Test file: {test_file}")
        
        # Test 1: Create new file
        print("\n" + "=" * 60)
        print("Test 1: Create new file")
        print("=" * 60)
        
        content1 = "This is a new file created by FileWriteTool.\nLine 2: Testing create operation.\nLine 3: End of file."
        result1 = write(test_file, content1)
        data1 = json.loads(result1)
        
        print(f"Type: {data1.get('type')}")
        print(f"File path: {data1.get('filePath')}")
        print(f"Content length: {len(data1.get('content', ''))}")
        print(f"Original file: {data1.get('originalFile')}")
        print(f"Structured patch: {len(data1.get('structuredPatch', []))} hunks")
        
        assert data1["type"] == "create", "Expected type 'create' for new file"
        assert data1["filePath"] == test_file, "File path mismatch"
        assert data1["originalFile"] is None, "Original file should be null for create"
        
        # Test 2: Update existing file
        print("\n" + "=" * 60)
        print("Test 2: Update existing file")
        print("=" * 60)
        
        content2 = "This is an updated file.\nLine 2: Updated content.\nLine 3: New line added.\nLine 4: Another new line."
        result2 = write(test_file, content2)
        data2 = json.loads(result2)
        
        print(f"Type: {data2.get('type')}")
        print(f"Original file length: {len(data2.get('originalFile', '')) if data2.get('originalFile') else 0}")
        print(f"New content length: {len(data2.get('content', ''))}")
        print(f"Structured patch: {len(data2.get('structuredPatch', []))} hunks")
        if data2.get("structuredPatch"):
            print(f"First hunk: {json.dumps(data2['structuredPatch'][0], indent=2)[:200]}...")
        
        assert data2["type"] == "update", "Expected type 'update' for existing file"
        assert data2["originalFile"] == content1, "Original content mismatch"
        assert len(data2["structuredPatch"]) > 0, "Should have diff for update"
        
        # Test 3: Error handling - non-existent parent directory (with auto-create)
        print("\n" + "=" * 60)
        print("Test 3: Auto-create parent directory")
        print("=" * 60)
        
        nested_file = os.path.join(test_dir, "nested", "dir", "test.txt")
        result3 = write(nested_file, "Test content for nested file")
        data3 = json.loads(result3)
        
        print(f"Success: {'error' not in data3}")
        print(f"Type: {data3.get('type')}")
        assert os.path.exists(nested_file), "Nested file should be created"
        
        # Test 4: Error handling - permission error (simulated)
        print("\n" + "=" * 60)
        print("Test 4: Error handling")
        print("=" * 60)
        
        # Try to write to root directory (likely to fail)
        root_file = "/test_no_permission.txt"
        result4 = write(root_file, "Should fail")
        data4 = json.loads(result4)
        
        if data4.get("error"):
            print(f"✓ Correctly handled error: {data4.get('message', '')[:50]}...")
        else:
            print(f"Note: Write to {root_file} succeeded (might have permissions)")
        
        # Test 5: Claude Code format validation
        print("\n" + "=" * 60)
        print("Test 5: Claude Code format validation")
        print("=" * 60)
        
        # Check required fields
        required_fields = ["type", "filePath", "content", "structuredPatch", "originalFile"]
        for field in required_fields:
            assert field in data1, f"Missing required field: {field}"
            print(f"✓ Field present: {field}")
        
        # Check type values
        assert data1["type"] in ["create", "update"], f"Invalid type: {data1['type']}"
        print(f"✓ Type is valid: {data1['type']}")
        
        print("\n✓ All Claude Code format requirements met")
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up test directory: {test_dir}")