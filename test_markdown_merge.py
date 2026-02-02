#!/usr/bin/env python3
"""Test script for markdown merge operations."""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from markdown import (
    merge_markdown_files,
    write_markdown_file,
)

# Create test markdown files
file1_content = """# File 1

This is the first markdown file.

## Section A

Content from file 1.
"""

file2_content = """# File 2

This is the second markdown file.

## Section B

Content from file 2.
"""

file3_content = """# File 3

This is the third markdown file.

## Section C

Content from file 3.
"""

# Create temporary files
temp_files = []
try:
    for i, content in enumerate([file1_content, file2_content, file3_content], 1):
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_test{i}.md', delete=False) as f:
            f.write(content)
            temp_files.append(f.name)
            print(f"Created temporary file {i}: {f.name}")
    
    # Test merge_markdown_files without saving
    print("\nTesting merge_markdown_files (return content only)...")
    merged_result = merge_markdown_files(temp_files, separator="---")
    print(f"Merged result (first 300 chars):\n{merged_result[:300]}...")
    
    # Test merge_markdown_files with saving
    print("\nTesting merge_markdown_files (save to file)...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='_merged.md', delete=False) as f:
        output_path = f.name
    
    save_result = merge_markdown_files(temp_files, output_path=output_path, separator="***")
    print(f"Save result: {save_result}")
    
    # Verify saved file exists
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            saved_content = f.read()
        print(f"Saved file size: {len(saved_content)} characters")
        
        # Check if all files are included
        all_included = all(
            f"File {i}" in saved_content for i in range(1, 4)
        )
        if all_included:
            print("✓ All files included in merged output!")
        else:
            print("⚠ Some files missing from merged output!")
    else:
        print("⚠ Output file not created!")
    
    # Test with custom separator
    print("\nTesting with custom separator '=========='...")
    custom_result = merge_markdown_files([temp_files[0], temp_files[1]], separator="==========")
    if "==========" in custom_result:
        print("✓ Custom separator found in output!")
    else:
        print("⚠ Custom separator not found in output!")
    
    # Test error handling (non-existent file)
    print("\nTesting error handling (non-existent file)...")
    error_result = merge_markdown_files([temp_files[0], "/non/existent/file.md"])
    print(f"Error result: {error_result[:100]}...")
    
finally:
    # Clean up
    for file_path in temp_files:
        if os.path.exists(file_path):
            os.unlink(file_path)
            print(f"Cleaned up: {file_path}")
    
    if 'output_path' in locals() and os.path.exists(output_path):
        os.unlink(output_path)
        print(f"Cleaned up output file: {output_path}")

print("\nAll merge tests completed!")