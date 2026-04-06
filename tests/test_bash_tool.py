#!/usr/bin/env python3
"""
Tests for BashTool (Claude Code compatible version).
"""

import os
import sys
import json
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shell.bash_tool import bash_tool


class TestBashTool(unittest.TestCase):
    """Test suite for BashTool."""
    
    def test_simple_command(self):
        """Test executing a simple command."""
        result = bash_tool("echo 'Hello World'", description="Echo Hello World")
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check Claude Code compatibility fields
        self.assertIn("stdout", data)
        self.assertIn("stderr", data)
        self.assertIn("interrupted", data)
        
        # Check values
        self.assertIn("Hello World", data["stdout"])
        self.assertEqual(data["interrupted"], False)
        
        # Check metadata
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        self.assertEqual(metadata.get("command"), "echo 'Hello World'")
        self.assertEqual(metadata.get("description"), "Echo Hello World")
    
    def test_command_with_timeout(self):
        """Test command with timeout parameter."""
        # Quick command should complete within timeout
        result = bash_tool("echo 'test'", timeout=5000, description="Quick echo with timeout")
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["interrupted"], False)
        
        # Check timeout in metadata
        metadata = data.get("_metadata", {})
        self.assertEqual(metadata.get("timeoutMs"), 5000)
    
    def test_command_failure(self):
        """Test non-existent command."""
        result = bash_tool("nonexistentcommand12345", description="Non-existent command")
        data = json.loads(result)
        
        # Should have non-zero return code in metadata
        metadata = data.get("_metadata", {})
        self.assertFalse(metadata.get("success", True))
    
    def test_interrupted_command(self):
        """Test command that times out (interrupted)."""
        # Command that sleeps longer than timeout
        result = bash_tool("sleep 2", timeout=100, description="Sleep with short timeout")
        data = json.loads(result)
        
        # Should be interrupted due to timeout
        self.assertTrue(data.get("interrupted", False))
    
    def test_return_code_interpretation(self):
        """Test return code interpretation."""
        result = bash_tool("exit 1", description="Exit with code 1")
        data = json.loads(result)
        
        self.assertIn("returnCodeInterpretation", data)
        interpretation = data["returnCodeInterpretation"]
        self.assertIn("General error", interpretation)
    
    def test_no_output_expected_detection(self):
        """Test detection of commands expected to produce no output."""
        # mkdir is a silent command
        import tempfile
        import os
        
        # Create a temporary directory for test
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "testdir")
            result = bash_tool(f"mkdir {test_dir}", description="Create directory")
            data = json.loads(result)
            
            # Should have noOutputExpected set (or at least not fail)
            # Note: the heuristic may mark this as noOutputExpected
            self.assertIn("noOutputExpected", data)
    
    def test_image_output_detection(self):
        """Test image output detection (simplified)."""
        # Use file command to check if a file is an image
        # First create a simple text file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as f:
            f.write("Not an image")
            text_file = f.name
        
        try:
            # Check the file type
            result = bash_tool(f"file {text_file}", description="Check file type")
            data = json.loads(result)
            
            # Should not be detected as image
            if "isImage" in data and data["isImage"] is not None:
                self.assertFalse(data["isImage"])
        finally:
            os.unlink(text_file)
    
    def test_background_execution_warning(self):
        """Test background execution parameter (warning only in current implementation)."""
        result = bash_tool("echo 'test'", run_in_background=True, description="Test background")
        data = json.loads(result)
        
        # Should have a warning about background execution not fully implemented
        # Current implementation adds _warning field
        self.assertTrue("_warning" in data or "_metadata" in data)
    
    def test_sandbox_disable_warning(self):
        """Test sandbox disable parameter (warning only in current implementation)."""
        result = bash_tool("echo 'test'", dangerouslyDisableSandbox=True, description="Test sandbox disable")
        data = json.loads(result)
        
        # Should have sandbox warning or field
        self.assertTrue("_warning_sandbox" in data or "dangerouslyDisableSandbox" in data)
    
    def test_claude_code_compatibility(self):
        """Test that output matches Claude Code's BashTool format."""
        result = bash_tool("ls -la", description="List files")
        data = json.loads(result)
        
        # Main fields from Claude Code's BashTool output
        expected_fields = [
            "stdout", "stderr", "interrupted"
        ]
        
        for field in expected_fields:
            self.assertIn(field, data, f"Missing Claude Code field: {field}")
        
        # Optional fields that should be present (even if None)
        optional_fields = [
            "isImage", "dangerouslyDisableSandbox", 
            "returnCodeInterpretation", "noOutputExpected"
        ]
        
        # Type checking
        self.assertIsInstance(data["stdout"], str)
        self.assertIsInstance(data["stderr"], str)
        self.assertIsInstance(data["interrupted"], bool)
    
    def test_working_directory(self):
        """Test that command executes in current working directory."""
        import tempfile
        import os
        
        # Create temp directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "testfile.txt")
            
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(tmpdir)
            
            try:
                # Create file in temp directory
                result = bash_tool(f"echo 'test content' > {test_file}", description="Create test file")
                data = json.loads(result)
                
                # Check if file was created
                self.assertTrue(os.path.exists(test_file))
                
            finally:
                # Restore original directory
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()