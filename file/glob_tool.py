#!/usr/bin/env python3
"""
GlobTool implementation for AITools (Claude Code compatible version - simplified).
Provides glob pattern matching functionality aligned with Claude Code's GlobTool.
Based on analysis of Claude Code source: restored-src/src/tools/GlobTool/GlobTool.ts
Simplified version focusing on basic glob pattern matching.
"""

import os
import glob as pyglob
import json
import time
from base import function_ai, parameters_func, property_param

# Property definitions for GlobTool
__PATTERN_PROPERTY__ = property_param(
    name="pattern",
    description="The glob pattern to match files against",
    t="string",
    required=True,
)

__PATH_PROPERTY__ = property_param(
    name="path",
    description="The directory to search in. If not specified, the current working directory will be used.",
    t="string",
    required=False,
)

# Function metadata
__GLOB_TOOL_FUNCTION__ = function_ai(
    name="glob",
    description="Find files by name pattern or wildcard. Compatible with Claude Code's GlobTool (simplified version).",
    parameters=parameters_func([
        __PATTERN_PROPERTY__,
        __PATH_PROPERTY__,
    ]),
)

tools = [__GLOB_TOOL_FUNCTION__]


def glob(pattern: str, path: str = None) -> str:
    """
    Find files by name pattern or wildcard.
    
    Claude Code compatible version based on GlobTool.ts:
    - pattern: The glob pattern to match files against (required)
    - path: The directory to search in (optional, defaults to current directory)
    
    Returns JSON matching Claude Code's GlobTool output schema (simplified).
    
    Core functionality in Claude Code:
    1. Uses glob pattern matching to find files
    2. Supports wildcards (*, ?, [], etc.)
    3. Limits results to 100 files by default (truncated flag)
    4. Returns relative paths under current directory
    5. Includes execution time statistics
    
    Simplified implementation:
    1. Uses Python's glob.glob() for pattern matching
    2. Supports basic glob patterns (no extended features)
    3. Limits results to 100 files (configurable)
    4. Returns relative paths where possible
    5. Includes execution timing
    """
    try:
        # Validate inputs
        if not pattern or not isinstance(pattern, str):
            return json.dumps({
                "error": "Pattern must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Determine search directory
        search_dir = path or os.getcwd()
        
        # Validate directory exists
        if not os.path.exists(search_dir):
            return json.dumps({
                "error": f"Directory does not exist: {search_dir}",
                "success": False
            }, indent=2)
        
        if not os.path.isdir(search_dir):
            return json.dumps({
                "error": f"Path is not a directory: {search_dir}",
                "success": False
            }, indent=2)
        
        # Record start time
        start_time = time.time()
        
        # Change to search directory for glob to work correctly
        original_cwd = os.getcwd()
        os.chdir(search_dir)
        
        try:
            # Perform glob search with limit
            max_results = 100  # Default limit from Claude Code
            all_files = []
            
            # Use glob to find files matching pattern
            # Note: recursive glob (**) requires Python 3.5+ with recursive=True
            if "**" in pattern and hasattr(pyglob, "iglob"):
                # Handle recursive pattern
                for file_path in pyglob.iglob(pattern, recursive=True):
                    all_files.append(file_path)
                    if len(all_files) >= max_results * 2:  # Allow some extra for sorting
                        break
            else:
                # Non-recursive pattern
                all_files = pyglob.glob(pattern)
            
            # Sort files for consistent results
            all_files.sort()
            
            # Apply limit and check for truncation
            truncated = len(all_files) > max_results
            result_files = all_files[:max_results]
            
            # Make paths relative to original search directory
            # For display purposes, keep them relative to search_dir
            # In Claude Code, they're made relative to current working directory
            final_files = []
            for file_path in result_files:
                # Ensure it's a string (glob returns strings)
                file_str = str(file_path)
                # Convert to relative path if it's absolute
                if os.path.isabs(file_str):
                    try:
                        file_str = os.path.relpath(file_str, search_dir)
                    except:
                        # If relpath fails, use the original
                        pass
                final_files.append(file_str)
            
        finally:
            # Restore original directory
            os.chdir(original_cwd)
        
        # Calculate execution time
        end_time = time.time()
        duration_ms = int((end_time - start_time) * 1000)
        
        # Build Claude Code compatible response
        response = {
            "durationMs": duration_ms,
            "numFiles": len(final_files),
            "filenames": final_files,
            "truncated": truncated,
            "_metadata": {
                "success": True,
                "simplifiedImplementation": True,
                "pattern": pattern,
                "searchDirectory": search_dir,
                "maxResults": max_results,
                "note": "Basic glob implementation. Does not include advanced permission checking or UNC path handling."
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Glob search failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "glob": glob
}


if __name__ == "__main__":
    # Test the glob function
    print("Testing GlobTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Create some test files
    import tempfile
    import shutil
    
    test_dir = tempfile.mkdtemp()
    print(f"1. Created test directory: {test_dir}")
    
    try:
        # Create test files
        test_files = [
            "test1.txt",
            "test2.txt",
            "test3.md",
            "data.json",
            "image.png",
            "subdir/test4.txt",
            "subdir/test5.md"
        ]
        
        for file_name in test_files:
            file_path = os.path.join(test_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(f"Content for {file_name}")
        
        print(f"   Created {len(test_files)} test files")
        
        # Test 1: Basic glob pattern
        print("\n2. Basic glob pattern (*.txt):")
        result = glob(pattern="*.txt", path=test_dir)
        data = json.loads(result)
        
        print(f"   Success: {'error' not in data}")
        print(f"   Duration: {data.get('durationMs')}ms")
        print(f"   Num files: {data.get('numFiles')}")
        print(f"   Files found: {data.get('filenames')}")
        print(f"   Truncated: {data.get('truncated')}")
        
        # Test 2: Check Claude Code compatibility
        print("\n3. Claude Code compatibility check:")
        expected_fields = ["durationMs", "numFiles", "filenames", "truncated"]
        
        missing_fields = [field for field in expected_fields if field not in data]
        
        if missing_fields:
            print(f"   Missing required fields: {missing_fields}")
        else:
            print("   All required fields present ✓")
        
        # Test 3: Different pattern
        print("\n4. Different pattern (*.md):")
        result3 = glob(pattern="*.md", path=test_dir)
        data3 = json.loads(result3)
        print(f"   Num files: {data3.get('numFiles')}")
        print(f"   Files: {data3.get('filenames')}")
        
        # Test 4: Pattern with subdirectory
        print("\n5. Pattern with subdirectory (subdir/*.txt):")
        result4 = glob(pattern="subdir/*.txt", path=test_dir)
        data4 = json.loads(result4)
        print(f"   Num files: {data4.get('numFiles')}")
        print(f"   Files: {data4.get('filenames')}")
        
        # Test 5: No matches
        print("\n6. Pattern with no matches (*.py):")
        result5 = glob(pattern="*.py", path=test_dir)
        data5 = json.loads(result5)
        print(f"   Num files: {data5.get('numFiles')}")
        print(f"   Files: {data5.get('filenames')}")
        
        # Test 6: Error handling - invalid directory
        print("\n7. Error handling (invalid directory):")
        result6 = glob(pattern="*.txt", path="/nonexistent/directory")
        data6 = json.loads(result6)
        print(f"   Has error: {'error' in data6}")
        
        # Test 7: Default path (current directory)
        print("\n8. Default path (current directory):")
        # Create a test file in current directory
        with open("test_glob_current.txt", 'w') as f:
            f.write("Test file")
        
        try:
            result7 = glob(pattern="test_glob_*.txt")
            data7 = json.loads(result7)
            print(f"   Num files: {data7.get('numFiles')}")
            print(f"   At least one file: {data7.get('numFiles', 0) > 0}")
        finally:
            # Clean up test file
            if os.path.exists("test_glob_current.txt"):
                os.remove("test_glob_current.txt")
        
    finally:
        # Clean up test directory
        shutil.rmtree(test_dir)
        print(f"\n9. Cleaned up test directory: {test_dir}")
    
    print("\n" + "=" * 60)
    print("GlobTool test completed.")