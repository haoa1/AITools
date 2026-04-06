#!/usr/bin/env python3
"""
Unit tests for EnterWorktreeTool.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from system.enter_worktree_tool import enter_worktree_tool, EnterWorktreeConfig, validate_worktree_name


class TestEnterWorktreeTool(unittest.TestCase):
    """Test cases for EnterWorktreeTool"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment
        self.original_env = os.environ.copy()
        
        # Set environment variables for testing
        os.environ["ENTER_WORKTREE_INTERACTIVE"] = "false"  # Disable interactive output for tests
        os.environ["ENTER_WORKTREE_BASE_PATH"] = tempfile.mkdtemp()  # Use temp directory
        os.environ["ENTER_WORKTREE_VALIDATE_NAME"] = "true"  # Enable validation for tests
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_enter_worktree_random_name(self):
        """Test entering worktree with random name (no name provided)"""
        result = enter_worktree_tool()
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertIn("worktreePath", data)
        self.assertIn("message", data)
        # Path should exist (or at least be a valid path)
        self.assertIsInstance(data.get("worktreePath"), str)
        self.assertGreater(len(data.get("worktreePath", "")), 0)
    
    def test_enter_worktree_with_name(self):
        """Test entering worktree with specific name"""
        result = enter_worktree_tool(name="test_worktree")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertIn("test_worktree", data.get("worktreePath", ""))
        self.assertIn("test_worktree", data.get("message", ""))
    
    def test_enter_worktree_name_validation_valid(self):
        """Test valid worktree names"""
        valid_names = [
            "test",
            "test-worktree",
            "test.worktree",
            "test_worktree",
            "test123",
            "segment1/segment2",
            "a.b/c-d/e_f"
        ]
        
        for name in valid_names:
            is_valid, msg = validate_worktree_name(name)
            self.assertTrue(is_valid, f"Name '{name}' should be valid: {msg}")
    
    def test_enter_worktree_name_validation_invalid(self):
        """Test invalid worktree names"""
        invalid_cases = [
            ("test@worktree", "Invalid character"),
            ("test#worktree", "Invalid character"),
            ("test worktree", "Invalid character"),
            ("", "Name is optional"),  # Empty is actually allowed (means optional)
            ("a" * 65, "too long"),
            ("test//worktree", "Segment cannot be empty"),
            ("/test", "Segment cannot be empty"),
            ("test/", "Segment cannot be empty"),
        ]
        
        for name, expected_error in invalid_cases:
            is_valid, msg = validate_worktree_name(name)
            if name == "":  # Empty name is actually allowed (means optional)
                self.assertTrue(is_valid, f"Empty name should be valid: {msg}")
            else:
                self.assertFalse(is_valid, f"Name '{name}' should be invalid")
                # Check if expected error is in message (case-insensitive)
                self.assertTrue(expected_error.lower() in msg.lower() or 
                               any(keyword in msg.lower() for keyword in ["invalid", "too long", "empty", "segment"]),
                               f"Expected error about '{expected_error}' not found in: {msg}")
    
    def test_enter_worktree_disabled_tool(self):
        """Test when tool is disabled by configuration"""
        os.environ["ENTER_WORKTREE_ENABLED"] = "false"
        
        result = enter_worktree_tool(name="test")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("EnterWorktreeTool is disabled", data.get("error", ""))
        
        del os.environ["ENTER_WORKTREE_ENABLED"]
    
    def test_enter_worktree_max_worktrees(self):
        """Test maximum worktrees limit"""
        os.environ["ENTER_WORKTREE_MAX_WORKTREES"] = "0"  # No worktrees allowed
        
        result = enter_worktree_tool(name="test_max_limit")
        data = json.loads(result)
        
        # Should fail because max worktrees is 0
        self.assertFalse(data.get("success", True))
        self.assertIn("Maximum number of worktrees reached", data.get("error", ""))
        
        del os.environ["ENTER_WORKTREE_MAX_WORKTREES"]
    
    def test_enter_worktree_existing_worktree(self):
        """Test entering an existing worktree (should succeed)"""
        # First create a worktree
        result1 = enter_worktree_tool(name="existing_test")
        data1 = json.loads(result1)
        self.assertTrue(data1.get("success", True))
        
        # Try to enter it again
        result2 = enter_worktree_tool(name="existing_test")
        data2 = json.loads(result2)
        
        self.assertTrue(data2.get("success", True))
        self.assertEqual(data1.get("worktreePath"), data2.get("worktreePath"))
    
    def test_enter_worktree_config_overrides(self):
        """Test configuration overrides from environment variables"""
        # Test various config options
        test_configs = [
            ("ENTER_WORKTREE_ENABLED", "false", False),
            ("ENTER_WORKTREE_INTERACTIVE", "false", False),
            ("ENTER_WORKTREE_VALIDATE_NAME", "false", False),
            ("ENTER_WORKTREE_MAX_WORKTREES", "5", 5),
        ]
        
        for env_var, value, expected_value in test_configs:
            os.environ[env_var] = value
            config = EnterWorktreeConfig.from_env()
            
            config_key = env_var
            self.assertEqual(config.get(config_key), expected_value)
            
            # Clean up
            del os.environ[env_var]
    
    def test_enter_worktree_response_structure(self):
        """Test that response matches Claude Code expected structure"""
        result = enter_worktree_tool(name="test_structure")
        data = json.loads(result)
        
        # Required fields by Claude Code
        required_fields = ["worktreePath", "message"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Optional field
        self.assertIn("worktreeBranch", data)  # Present but may be None
        
        # Field types
        self.assertIsInstance(data["worktreePath"], str)
        self.assertIsInstance(data["message"], str)
        
        # worktreeBranch should be None in our simplified implementation
        self.assertIsNone(data.get("worktreeBranch"))
    
    def test_enter_worktree_interactive_mode(self):
        """Test interactive mode (mostly just ensure it doesn't crash)"""
        os.environ["ENTER_WORKTREE_INTERACTIVE"] = "true"
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            result = enter_worktree_tool(name="test_interactive")
            data = json.loads(result)
            
            # Should still succeed
            self.assertTrue(data.get("success", True))
            
            # Should have printed something in interactive mode
            self.assertTrue(mock_print.called)
        
        del os.environ["ENTER_WORKTREE_INTERACTIVE"]
    
    def test_enter_worktree_exception_handling(self):
        """Test exception handling in tool"""
        # Mock os.makedirs to raise exception
        with patch('os.makedirs', side_effect=OSError("Mocked OS error")):
            result = enter_worktree_tool(name="test_exception")
            data = json.loads(result)
            
            self.assertFalse(data.get("success", True))
            self.assertIn("Enter worktree failed", data.get("error", ""))
    
    def test_enter_worktree_without_validation(self):
        """Test entering worktree with validation disabled"""
        os.environ["ENTER_WORKTREE_VALIDATE_NAME"] = "false"
        
        # Should accept name that would normally be invalid
        result = enter_worktree_tool(name="test@invalid#name")
        data = json.loads(result)
        
        # Should succeed when validation is disabled
        self.assertTrue(data.get("success", True))
        
        del os.environ["ENTER_WORKTREE_VALIDATE_NAME"]
    
    def test_enter_worktree_base_path_override(self):
        """Test custom base path override"""
        custom_path = tempfile.mkdtemp()
        os.environ["ENTER_WORKTREE_BASE_PATH"] = custom_path
        
        result = enter_worktree_tool(name="custom_path_test")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertIn(custom_path, data.get("worktreePath", ""))
        
        del os.environ["ENTER_WORKTREE_BASE_PATH"]


if __name__ == "__main__":
    unittest.main()