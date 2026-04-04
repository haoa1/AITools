#!/usr/bin/env python3
"""
Tests for FileEditTool (Claude Code compatible version).
"""

import os
import sys
import json
import tempfile
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.file_edit_tool import file_edit


class TestFileEditTool(unittest.TestCase):
    """Test suite for FileEditTool."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test file
        self.test_content = """# Test file for FileEditTool
Line 1: Hello World
Line 2: This is a test file
Line 3: Replace this text
Line 4: Another line
Line 5: End of file"""
        
        self.test_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        )
        self.test_file.write(self.test_content)
        self.test_file.close()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_simple_replacement(self):
        """Test replacing a single occurrence."""
        result = file_edit(self.test_file.name, "Replace this text", "REPLACED TEXT")
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check Claude Code compatibility fields
        self.assertIn("filePath", data)
        self.assertIn("oldString", data)
        self.assertIn("newString", data)
        self.assertIn("originalFile", data)
        self.assertIn("structuredPatch", data)
        self.assertIn("userModified", data)
        self.assertIn("replaceAll", data)
        
        # Check values
        self.assertEqual(data["oldString"], "Replace this text")
        self.assertEqual(data["newString"], "REPLACED TEXT")
        self.assertEqual(data["userModified"], False)
        self.assertEqual(data["replaceAll"], False)
        
        # Verify the file was actually modified
        with open(self.test_file.name, 'r', encoding='utf-8') as f:
            modified_content = f.read()
        self.assertIn("REPLACED TEXT", modified_content)
        self.assertNotIn("Replace this text", modified_content)
    
    def test_replace_all_occurrences(self):
        """Test replacing all occurrences of a string."""
        # First, modify file to have multiple occurrences
        with open(self.test_file.name, 'a', encoding='utf-8') as f:
            f.write("\nLine 6: Hello again\nLine 7: Hello World once more")
        
        result = file_edit(self.test_file.name, "Hello", "Greetings", replace_all=True)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertTrue(data["replaceAll"])
        
        # Check that all occurrences were replaced
        with open(self.test_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have no "Hello" and multiple "Greetings"
        self.assertNotIn("Hello", content)
        self.assertIn("Greetings", content)
    
    def test_string_not_found(self):
        """Test error when old string is not found."""
        result = file_edit(self.test_file.name, "NONEXISTENT TEXT", "NEW TEXT")
        data = json.loads(result)
        
        # Should have an error
        self.assertTrue("error" in data or ("_metadata" in data and data["_metadata"].get("success") == False))
    
    def test_identical_strings(self):
        """Test error when old and new strings are identical."""
        result = file_edit(self.test_file.name, "Hello", "Hello")
        data = json.loads(result)
        
        # Should have an error
        self.assertTrue("error" in data or ("_metadata" in data and data["_metadata"].get("success") == False))
    
    def test_nonexistent_file(self):
        """Test error when file doesn't exist."""
        result = file_edit("/nonexistent/path/file.txt", "test", "new")
        data = json.loads(result)
        
        # Should have an error
        self.assertTrue("error" in data or ("_metadata" in data and data["_metadata"].get("success") == False))
    
    def test_structured_patch_generation(self):
        """Test that structuredPatch is generated correctly."""
        result = file_edit(self.test_file.name, "Line 3: Replace this text", "Line 3: MODIFIED TEXT")
        data = json.loads(result)
        
        self.assertIn("structuredPatch", data)
        structured_patch = data["structuredPatch"]
        
        # Should have at least one hunk
        if data["originalFile"] != data.get("newString", ""):  # If content actually changed
            self.assertGreater(len(structured_patch), 0)
            
            # Check hunk structure
            hunk = structured_patch[0]
            self.assertIn("oldStart", hunk)
            self.assertIn("oldLines", hunk)
            self.assertIn("newStart", hunk)
            self.assertIn("newLines", hunk)
            self.assertIn("lines", hunk)
    
    def test_original_file_preserved(self):
        """Test that originalFile contains the original content."""
        result = file_edit(self.test_file.name, "Replace this text", "NEW TEXT")
        data = json.loads(result)
        
        self.assertIn("originalFile", data)
        self.assertEqual(data["originalFile"], self.test_content)
    
    def test_claude_code_compatibility(self):
        """Test that output matches Claude Code's FileEditTool format."""
        result = file_edit(self.test_file.name, "test", "TEST")
        data = json.loads(result)
        
        # Main fields from Claude Code's FileEditOutput
        expected_fields = [
            "filePath", "oldString", "newString", 
            "originalFile", "structuredPatch", 
            "userModified", "replaceAll"
        ]
        
        for field in expected_fields:
            self.assertIn(field, data, f"Missing Claude Code field: {field}")
        
        # Type checking
        self.assertIsInstance(data["filePath"], str)
        self.assertIsInstance(data["oldString"], str)
        self.assertIsInstance(data["newString"], str)
        self.assertIsInstance(data["originalFile"], str)
        self.assertIsInstance(data["structuredPatch"], list)
        self.assertIsInstance(data["userModified"], bool)
        self.assertIsInstance(data["replaceAll"], bool)


if __name__ == "__main__":
    unittest.main()