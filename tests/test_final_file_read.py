#!/usr/bin/env python3
"""
Final integration test for FileReadTool.
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test both import methods
print("Testing FileReadTool imports...")
try:
    from file.file_read_tool import file_read
    print("✓ Import from file.file_read_tool successful")
    
    from file import file_read as file_read_from_module
    print("✓ Import from file module successful")
    
    # Test that they're the same function
    assert file_read == file_read_from_module
    print("✓ Both imports refer to the same function")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Create test file
test_content = """This is a test file for FileReadTool.
It contains multiple lines of text.
Each line is numbered for testing.
Line 4: Testing offset parameter.
Line 5: Testing limit parameter.
Line 6: Final line of the test file."""

test_file = "final_test_file.txt"
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(test_content)

print(f"\nCreated test file: {test_file}")

# Test 1: Basic functionality
print("\n" + "=" * 60)
print("Test 1: Basic functionality")
print("=" * 60)

result = file_read(test_file)
data = json.loads(result)

print(f"Type: {data.get('type')}")
print(f"File path: {data['file']['filePath']}")
print(f"Lines read: {data['file']['numLines']}/{data['file']['totalLines']}")
print(f"Start line: {data['file']['startLine']}")
print(f"Content preview: {data['file']['content'][:50]}...")

assert data["type"] == "text", "Expected type 'text'"
assert data["file"]["numLines"] == 6, f"Expected 6 lines, got {data['file']['numLines']}"
assert data["file"]["totalLines"] == 6, f"Expected total 6 lines, got {data['file']['totalLines']}"
print("✓ Basic functionality test passed")

# Test 2: Offset and limit
print("\n" + "=" * 60)
print("Test 2: Offset and limit parameters")
print("=" * 60)

result = file_read(test_file, offset=3, limit=2)
data = json.loads(result)

print(f"Requested: offset=3, limit=2")
print(f"Got: lines {data['file']['startLine']}-{data['file']['startLine'] + data['file']['numLines'] - 1}")
print(f"Content: {data['file']['content']}")

assert data["file"]["startLine"] == 3, f"Expected startLine 3, got {data['file']['startLine']}"
assert data["file"]["numLines"] == 2, f"Expected 2 lines, got {data['file']['numLines']}"
expected_content = "Each line is numbered for testing.\nLine 4: Testing offset parameter."
assert data["file"]["content"] == expected_content, f"Content mismatch"
print("✓ Offset and limit test passed")

# Test 3: Claude Code format compatibility
print("\n" + "=" * 60)
print("Test 3: Claude Code format compatibility")
print("=" * 60)

# Check all required fields
required_top_level = ["type", "file"]
required_file_fields = ["filePath", "content", "numLines", "startLine", "totalLines"]

for field in required_top_level:
    assert field in data, f"Missing top-level field: {field}"
    print(f"✓ Top-level field: {field}")

for field in required_file_fields:
    assert field in data["file"], f"Missing file field: {field}"
    print(f"✓ File field: {field}")

print("✓ All Claude Code required fields present")

# Test 4: Error handling
print("\n" + "=" * 60)
print("Test 4: Error handling")
print("=" * 60)

# Non-existent file
result = file_read("non_existent_file_12345.txt")
data = json.loads(result)
assert data.get("error") == True, "Expected error for non-existent file"
print(f"✓ Non-existent file handled: {data.get('message', '')[:50]}...")

# Directory instead of file
temp_dir = "test_dir_for_file_read"
os.makedirs(temp_dir, exist_ok=True)
result = file_read(temp_dir)
data = json.loads(result)
assert data.get("error") == True, "Expected error for directory"
print(f"✓ Directory path handled: {data.get('message', '')[:50]}...")

# Invalid offset
result = file_read(test_file, offset=0)
data = json.loads(result)
assert data.get("error") == True, "Expected error for invalid offset"
print(f"✓ Invalid offset handled: {data.get('message', '')[:50]}...")

# Clean up
os.rmdir(temp_dir)
print("✓ Cleaned up test directory")

# Test 5: Integration with existing AITools read function
print("\n" + "=" * 60)
print("Test 5: Integration with AITools")
print("=" * 60)

from file import read_file as aitools_read_file

# Compare results
file_read_result = file_read(test_file, offset=2, limit=3)
file_read_data = json.loads(file_read_result)

aitools_result = aitools_read_file(test_file, offset=2, limit=3)

# Both should read the same content (file_read strips trailing newline)
expected_content_from_aitools = aitools_result.rstrip('\n') if aitools_result.endswith('\n') else aitools_result

assert file_read_data["file"]["content"] == expected_content_from_aitools, "Content mismatch between file_read and read_file"
print("✓ file_read and read_file produce compatible results")
print(f"  Both read {file_read_data['file']['numLines']} lines")

# Final cleanup
os.remove(test_file)
print(f"\n✓ Cleaned up test file: {test_file}")

print("\n" + "=" * 60)
print("🎉 All FileReadTool tests passed!")
print("=" * 60)
print("\nSummary:")
print("- Claude Code FileReadTool interface implemented")
print("- Compatible with AITools read_file function")
print("- Proper error handling")
print("- Correct output format (Claude Code compatible)")
print("- Integrated into file module")