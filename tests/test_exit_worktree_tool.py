#!/usr/bin/env python3
"""
Unit tests for ExitWorktreeTool.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from system.exit_worktree_tool import exit_worktree_tool, ExitWorktreeConfig


class TestExitWorktreeTool(unittest.TestCase):
    """Test cases for ExitWorktreeTool"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment
        self.original_env = os.environ.copy()
        
        # Set environment variables for testing
        os.environ["EXIT_WORKTREE_INTERACTIVE"] = "false"  # Disable interactive output for tests
        os.environ["EXIT_WORKTREE_BASE_PATH"] = tempfile.mkdtemp()  # Use temp directory
        os.environ["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"] = "false"  # Disable for easier testing
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_exit_worktree_keep_action(self):
        """Test exiting worktree with keep action"""
        result = exit_worktree_tool(action="keep")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertEqual(data.get("action"), "keep")
        self.assertIn("worktreePath", data)
        self.assertIn("Kept worktree", data.get("message", ""))
    
    def test_exit_worktree_remove_action(self):
        """Test exiting worktree with remove action"""
        # Create a temporary directory to act as worktree
        temp_dir = tempfile.mkdtemp(dir=os.environ["EXIT_WORKTREE_BASE_PATH"])
        original_cwd = os.getcwd()
        
        try:
            os.chdir(temp_dir)
            result = exit_worktree_tool(action="remove", discard_changes=True)
            data = json.loads(result)
            
            self.assertTrue(data.get("success", True))
            self.assertEqual(data.get("action"), "remove")
            self.assertIn("Removed worktree", data.get("message", ""))
            self.assertIn("discardedFiles", data)
        finally:
            os.chdir(original_cwd)
    
    def test_exit_worktree_invalid_action(self):
        """Test exiting worktree with invalid action"""
        result = exit_worktree_tool(action="invalid_action")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn('must be "keep" or "remove"', data.get("error", ""))
    
    def test_exit_worktree_remove_without_discard_when_required(self):
        """Test remove action without discard_changes when required"""
        os.environ["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"] = "true"
        
        result = exit_worktree_tool(action="remove")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("discard_changes must be true", data.get("error", ""))
        
        del os.environ["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"]
    
    def test_exit_worktree_remove_disabled(self):
        """Test when remove action is disabled by configuration"""
        os.environ["EXIT_WORKTREE_ALLOW_REMOVE"] = "false"
        
        result = exit_worktree_tool(action="remove", discard_changes=True)
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("removal is disabled", data.get("error", ""))
        
        del os.environ["EXIT_WORKTREE_ALLOW_REMOVE"]
    
    def test_exit_worktree_disabled_tool(self):
        """Test when tool is disabled by configuration"""
        os.environ["EXIT_WORKTREE_ENABLED"] = "false"
        
        result = exit_worktree_tool(action="keep")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("ExitWorktreeTool is disabled", data.get("error", ""))
        
        del os.environ["EXIT_WORKTREE_ENABLED"]
    
    def test_exit_worktree_config_overrides(self):
        """Test configuration overrides from environment variables"""
        # Test various config options
        test_configs = [
            ("EXIT_WORKTREE_ENABLED", "false", False),
            ("EXIT_WORKTREE_INTERACTIVE", "false", False),
            ("EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE", "false", False),
            ("EXIT_WORKTREE_ALLOW_REMOVE", "false", False),
        ]
        
        for env_var, value, expected_value in test_configs:
            os.environ[env_var] = value
            config = ExitWorktreeConfig.from_env()
            
            config_key = env_var
            self.assertEqual(config.get(config_key), expected_value)
            
            # Clean up
            del os.environ[env_var]
    
    def test_exit_worktree_response_structure(self):
        """Test that response matches Claude Code expected structure"""
        # Test with keep action
        result = exit_worktree_tool(action="keep")
        data = json.loads(result)
        
        # Required fields by Claude Code
        required_fields = ["action", "originalCwd", "worktreePath", "message"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Always present optional fields
        always_present_fields = ["worktreeBranch", "tmuxSessionName"]
        for field in always_present_fields:
            self.assertIn(field, data)
        
        # Action-specific optional fields (only for remove)
        if data["action"] == "remove":
            remove_fields = ["discardedFiles", "discardedCommits"]
            for field in remove_fields:
                self.assertIn(field, data)
        
        # Field types and values
        self.assertIn(data["action"], ["keep", "remove"])
        self.assertIsInstance(data["originalCwd"], str)
        self.assertIsInstance(data["worktreePath"], str)
        self.assertIsInstance(data["message"], str)
    
    def test_exit_worktree_interactive_mode(self):
        """Test interactive mode (mostly just ensure it doesn't crash)"""
        os.environ["EXIT_WORKTREE_INTERACTIVE"] = "true"
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            result = exit_worktree_tool(action="keep")
            data = json.loads(result)
            
            # Should still succeed
            self.assertTrue(data.get("success", True))
            
            # Should have printed something in interactive mode
            self.assertTrue(mock_print.called)
        
        del os.environ["EXIT_WORKTREE_INTERACTIVE"]
    
    def test_exit_worktree_exception_handling(self):
        """Test exception handling in tool"""
        # Mock os.getcwd to raise exception
        with patch('os.getcwd', side_effect=OSError("Mocked OS error")):
            result = exit_worktree_tool(action="keep")
            data = json.loads(result)
            
            self.assertFalse(data.get("success", True))
            self.assertIn("Exit worktree failed", data.get("error", ""))
    
    def test_exit_worktree_remove_refuses_without_discard_when_files_exist(self):
        """Test remove action refuses when files exist and discard_changes=False"""
        os.environ["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"] = "true"
        
        # Create a temporary directory with a file
        temp_dir = tempfile.mkdtemp(dir=os.environ["EXIT_WORKTREE_BASE_PATH"])
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        original_cwd = os.getcwd()
        
        try:
            os.chdir(temp_dir)
            result = exit_worktree_tool(action="remove", discard_changes=False)
            data = json.loads(result)
            
            self.assertFalse(data.get("success", True))
            self.assertIn("has files", data.get("error", ""))
        finally:
            os.chdir(original_cwd)
        
        del os.environ["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"]


if __name__ == "__main__":
    unittest.main()