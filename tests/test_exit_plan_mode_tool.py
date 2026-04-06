#!/usr/bin/env python3
"""
Tests for ExitPlanModeV2Tool (Claude Code compatible version - simplified).
"""

import os
import sys
import json
import tempfile
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.exit_plan_mode_tool import exit_plan_mode_v2_tool


class TestExitPlanModeV2Tool(unittest.TestCase):
    """Test suite for ExitPlanModeV2Tool."""
    
    def test_basic_exit_plan_mode(self):
        """Test basic exit plan mode functionality."""
        result = exit_plan_mode_v2_tool()
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check required fields
        self.assertIn("plan", data)
        self.assertIn("isAgent", data)
        
        # Check values
        self.assertIsInstance(data["plan"], str)
        self.assertGreater(len(data["plan"]), 0)
        self.assertIsInstance(data["isAgent"], bool)
        self.assertFalse(data["isAgent"])  # Simplified: not in agent context
        
        # Check optional fields that should be present in our implementation
        self.assertIn("hasTaskTool", data)
        self.assertIn("planWasEdited", data)
        self.assertIn("awaitingLeaderApproval", data)
        
        # Check metadata
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        self.assertIn("success", metadata)
        self.assertIn("simplifiedImplementation", metadata)
        self.assertTrue(metadata["success"])
        self.assertTrue(metadata["simplifiedImplementation"])
    
    def test_with_allowed_prompts(self):
        """Test exit plan mode with allowed prompts."""
        allowed_prompts = [
            {"tool": "Bash", "prompt": "run unit tests"},
            {"tool": "FileEdit", "prompt": "update configuration files"}
        ]
        
        result = exit_plan_mode_v2_tool(allowedPrompts=allowed_prompts)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertTrue(data["_metadata"]["success"])
        
        # Check that allowedPrompts are in metadata
        metadata = data["_metadata"]
        self.assertIn("allowedPrompts", metadata)
        self.assertEqual(metadata["allowedPrompts"], allowed_prompts)
    
    def test_with_plan_content(self):
        """Test exit plan mode with explicit plan content."""
        test_plan = "# Custom Plan\n\n## Objective\nTest the ExitPlanModeV2Tool\n\n## Steps\n1. Test basic functionality\n2. Test with parameters\n3. Validate output"
        
        result = exit_plan_mode_v2_tool(plan=test_plan)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["plan"], test_plan)
    
    def test_with_plan_file_path(self):
        """Test exit plan mode with plan file path."""
        # Create a temporary plan file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# File-Based Plan\n\nLoaded from file.\n\n## Content\nThis is test content.")
            temp_file = f.name
        
        try:
            result = exit_plan_mode_v2_tool(planFilePath=temp_file)
            data = json.loads(result)
            
            self.assertNotIn("error", data)
            self.assertIn("plan", data)
            self.assertIn("filePath", data)
            self.assertEqual(data["filePath"], temp_file)
            self.assertIn("File-Based Plan", data["plan"])
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_with_plan_file_path_and_content(self):
        """Test when both plan and planFilePath are provided (plan should take precedence)."""
        explicit_plan = "# Explicit Plan\n\nThis should be used."
        
        # Create a temporary file with different content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# File Plan\n\nThis should NOT be used.")
            temp_file = f.name
        
        try:
            result = exit_plan_mode_v2_tool(plan=explicit_plan, planFilePath=temp_file)
            data = json.loads(result)
            
            self.assertNotIn("error", data)
            self.assertEqual(data["plan"], explicit_plan)
            self.assertIn("filePath", data)
            self.assertEqual(data["filePath"], temp_file)
            self.assertNotIn("File Plan", data["plan"])
        finally:
            # Clean up temp file
            os.unlink(temp_file)
    
    def test_with_nonexistent_plan_file(self):
        """Test with non-existent plan file path (should generate default plan)."""
        non_existent_file = "/tmp/nonexistent_plan_file_12345.md"
        
        result = exit_plan_mode_v2_tool(planFilePath=non_existent_file)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertIn("plan", data)
        self.assertIn("filePath", data)
        self.assertEqual(data["filePath"], non_existent_file)
        self.assertGreater(len(data["plan"]), 0)
        # Should contain the error or default plan text
        self.assertIsInstance(data["plan"], str)
    
    def test_claude_code_compatibility(self):
        """Test that output matches Claude Code's ExitPlanModeV2Tool format."""
        result = exit_plan_mode_v2_tool()
        data = json.loads(result)
        
        # Required fields from Claude Code ExitPlanModeV2Tool output schema
        required_fields = ["plan", "isAgent"]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing Claude Code field: {field}")
        
        # Type checking
        self.assertIsInstance(data["plan"], str)
        self.assertIsInstance(data["isAgent"], bool)
        
        # Check optional fields that may be present
        optional_fields = ["filePath", "hasTaskTool", "planWasEdited", "awaitingLeaderApproval", "requestId"]
        
        # At least some optional fields should be present in our implementation
        present_optional = [field for field in optional_fields if field in data]
        self.assertGreater(len(present_optional), 0, "No optional fields present")
    
    def test_allowed_prompts_json_string(self):
        """Test that allowedPrompts can be provided as JSON string."""
        allowed_prompts_json = '[{"tool": "Bash", "prompt": "install dependencies"}]'
        
        result = exit_plan_mode_v2_tool(allowedPrompts=allowed_prompts_json)
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        metadata = data["_metadata"]
        self.assertIn("allowedPrompts", metadata)
        
        # Should be parsed as list
        allowed_prompts = metadata["allowedPrompts"]
        self.assertIsInstance(allowed_prompts, list)
        self.assertEqual(len(allowed_prompts), 1)
        self.assertEqual(allowed_prompts[0]["tool"], "Bash")
        self.assertEqual(allowed_prompts[0]["prompt"], "install dependencies")
    
    def test_error_handling(self):
        """Test error handling (should return error in JSON)."""
        # This test would check that errors are properly caught and returned
        # Our current implementation catches all exceptions and returns error JSON
        # So we can test by ensuring no uncaught exceptions
        
        # Test with invalid allowedPrompts (should still work due to error handling)
        result = exit_plan_mode_v2_tool(allowedPrompts="invalid json string")
        data = json.loads(result)
        
        # Should not have error field (invalid JSON is handled gracefully)
        self.assertNotIn("error", data)
        
        # Test with other edge cases
        result2 = exit_plan_mode_v2_tool(planFilePath="/root/nonexistent/file.md")
        data2 = json.loads(result2)
        
        # Should not have error (permission errors are caught)
        self.assertNotIn("error", data2)
    
    def test_simplified_implementation_note(self):
        """Test that simplified implementation metadata is included."""
        result = exit_plan_mode_v2_tool()
        data = json.loads(result)
        
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        
        self.assertIn("simplifiedImplementation", metadata)
        self.assertTrue(metadata["simplifiedImplementation"])
        self.assertIn("note", metadata)
        self.assertIsInstance(metadata["note"], str)
        self.assertGreater(len(metadata["note"]), 0)


if __name__ == "__main__":
    unittest.main()