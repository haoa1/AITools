#!/usr/bin/env python3
"""
Tests for GlobTool (Claude Code compatible version - simplified).
"""

import os
import sys
import json
import tempfile
import shutil
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.glob_tool import glob_tool


class TestGlobTool(unittest.TestCase):
    """Test suite for GlobTool."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory with test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = [
            "test1.txt",
            "test2.txt",
            "test3.md",
            "data.json",
            "image.png",
            "subdir/test4.txt",
            "subdir/test5.md",
            "subdir/nested/test6.py",
            "another/sub/test7.txt"
        ]
        
        for file_name in self.test_files:
            file_path = os.path.join(self.test_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(f"Content for {file_name}")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_basic_glob_pattern(self):
        """Test basic glob pattern matching."""
        result = glob_tool(pattern="*.txt", path=self.test_dir)
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check required fields
        self.assertIn("durationMs", data)
        self.assertIn("numFiles", data)
        self.assertIn("filenames", data)
        self.assertIn("truncated", data)
        
        # Check values
        self.assertIsInstance(data["durationMs"], int)
        self.assertIsInstance(data["numFiles"], int)
        self.assertIsInstance(data["filenames"], list)
        self.assertIsInstance(data["truncated"], bool)
        
        # Should find txt files in root directory
        self.assertEqual(data["numFiles"], 2)
        self.assertIn("test1.txt", data["filenames"])
        self.assertIn("test2.txt", data["filenames"])
        self.assertFalse(data["truncated"])
    
    def test_glob_with_subdirectory_pattern(self):
        """Test glob pattern with subdirectory."""
        result = glob_tool(pattern="subdir/*.txt", path=self.test_dir)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["numFiles"], 1)
        self.assertIn("subdir/test4.txt", data["filenames"])
    
    def test_glob_with_different_patterns(self):
        """Test various glob patterns."""
        # Test .md files
        result = glob_tool(pattern="*.md", path=self.test_dir)
        data = json.loads(result)
        self.assertEqual(data["numFiles"], 1)
        self.assertIn("test3.md", data["filenames"])
        
        # Test .json file
        result = glob_tool(pattern="*.json", path=self.test_dir)
        data = json.loads(result)
        self.assertEqual(data["numFiles"], 1)
        self.assertIn("data.json", data["filenames"])
        
        # Test all files
        result = glob_tool(pattern="*", path=self.test_dir)
        data = json.loads(result)
        self.assertGreaterEqual(data["numFiles"], 5)  # At least 5 files in root
    
    def test_glob_with_no_matches(self):
        """Test glob pattern with no matches."""
        result = glob_tool(pattern="*.py", path=self.test_dir)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["numFiles"], 0)
        self.assertEqual(data["filenames"], [])
        self.assertFalse(data["truncated"])
    
    def test_glob_with_default_path(self):
        """Test glob with default path (current directory)."""
        # Create a test file in current directory
        test_file = "test_default_path_glob.txt"
        with open(test_file, 'w') as f:
            f.write("Test file")
        
        try:
            result = glob_tool(pattern="test_default_path_*.txt")
            data = json.loads(result)
            
            self.assertNotIn("error", data)
            self.assertGreaterEqual(data["numFiles"], 1)
            
            # Check that filenames are relative
            if data["filenames"]:
                self.assertIsInstance(data["filenames"][0], str)
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_glob_error_handling(self):
        """Test error handling for invalid inputs."""
        # Invalid directory
        result = glob_tool(pattern="*.txt", path="/nonexistent/directory/12345")
        data = json.loads(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        
        # Invalid pattern (empty string)
        result = glob_tool(pattern="", path=self.test_dir)
        data = json.loads(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        
        # Non-directory path (use a file instead)
        file_path = os.path.join(self.test_dir, "test1.txt")
        result = glob_tool(pattern="*.txt", path=file_path)
        data = json.loads(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
    
    def test_glob_claude_code_compatibility(self):
        """Test that output matches Claude Code's GlobTool format."""
        result = glob_tool(pattern="*.txt", path=self.test_dir)
        data = json.loads(result)
        
        # Required fields from Claude Code GlobTool output schema
        required_fields = ["durationMs", "numFiles", "filenames", "truncated"]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing Claude Code field: {field}")
        
        # Type checking
        self.assertIsInstance(data["durationMs"], int)
        self.assertIsInstance(data["numFiles"], int)
        self.assertIsInstance(data["filenames"], list)
        self.assertIsInstance(data["truncated"], bool)
        
        # All filenames should be strings
        for filename in data["filenames"]:
            self.assertIsInstance(filename, str)
    
    def test_glob_metadata_included(self):
        """Test that metadata is included in response."""
        result = glob_tool(pattern="*.txt", path=self.test_dir)
        data = json.loads(result)
        
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        
        self.assertIn("success", metadata)
        self.assertIn("simplifiedImplementation", metadata)
        self.assertIn("pattern", metadata)
        self.assertIn("searchDirectory", metadata)
        self.assertIn("maxResults", metadata)
        
        self.assertTrue(metadata["success"])
        self.assertTrue(metadata["simplifiedImplementation"])
        self.assertEqual(metadata["pattern"], "*.txt")
        self.assertEqual(metadata["searchDirectory"], self.test_dir)
        self.assertEqual(metadata["maxResults"], 100)
    
    def test_glob_result_truncation(self):
        """Test that results are truncated when exceeding limit."""
        # Create many files to test truncation
        many_files_dir = tempfile.mkdtemp()
        try:
            # Create more than 100 files
            for i in range(150):
                file_path = os.path.join(many_files_dir, f"test_{i:03d}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"File {i}")
            
            result = glob_tool(pattern="*.txt", path=many_files_dir)
            data = json.loads(result)
            
            self.assertNotIn("error", data)
            self.assertEqual(data["numFiles"], 100)  # Limited to 100
            self.assertTrue(data["truncated"])
            
        finally:
            shutil.rmtree(many_files_dir)
    
    def test_glob_with_recursive_pattern(self):
        """Test glob with recursive pattern (**)."""
        # Note: Python's glob supports ** with recursive=True
        # Create a test directory structure
        test_dir = tempfile.mkdtemp()
        try:
            # Create nested files
            os.makedirs(os.path.join(test_dir, "a", "b", "c"), exist_ok=True)
            with open(os.path.join(test_dir, "a", "test1.txt"), 'w') as f:
                f.write("test1")
            with open(os.path.join(test_dir, "a", "b", "test2.txt"), 'w') as f:
                f.write("test2")
            with open(os.path.join(test_dir, "a", "b", "c", "test3.txt"), 'w') as f:
                f.write("test3")
            
            # Test recursive pattern (if supported)
            result = glob_tool(pattern="**/*.txt", path=test_dir)
            data = json.loads(result)
            
            # Should find at least some files
            self.assertNotIn("error", data)
            self.assertGreaterEqual(data["numFiles"], 1)
            
        finally:
            shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()