#!/usr/bin/env python3
"""
Tests for AgentTool (Claude Code compatible version - simplified).
"""

import os
import sys
import json
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.agent_tool import agent_tool


class TestAgentTool(unittest.TestCase):
    """Test suite for AgentTool."""
    
    def test_basic_agent_execution(self):
        """Test executing a basic agent task."""
        result = agent_tool(
            description="Test task",
            prompt="This is a test prompt for the agent",
            name="test_agent"
        )
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check Claude Code compatibility fields
        self.assertIn("status", data)
        self.assertIn("agentId", data)
        self.assertIn("content", data)
        self.assertIn("totalToolUseCount", data)
        self.assertIn("totalDurationMs", data)
        self.assertIn("totalTokens", data)
        self.assertIn("usage", data)
        self.assertIn("prompt", data)
        
        # Check values
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["prompt"], "This is a test prompt for the agent")
        self.assertEqual(data["description"], "Test task")
        
        # Check content structure
        content = data["content"]
        self.assertIsInstance(content, list)
        self.assertGreater(len(content), 0)
        self.assertIn("type", content[0])
        self.assertIn("text", content[0])
        self.assertEqual(content[0]["type"], "text")
    
    def test_required_parameters(self):
        """Test that description and prompt are required."""
        # Test missing description
        result = agent_tool(description="", prompt="Test prompt")
        data = json.loads(result)
        self.assertTrue("error" in data or not data.get("success", True))
        
        # Test missing prompt  
        result = agent_tool(description="Test task", prompt="")
        data = json.loads(result)
        self.assertTrue("error" in data or not data.get("success", True))
    
    def test_optional_parameters(self):
        """Test optional parameters."""
        result = agent_tool(
            description="Test with options",
            prompt="Test prompt",
            subagent_type="specialized",
            model="opus",
            run_in_background=False,
            name="custom_name",
            team_name="test_team",
            mode="plan",
            isolation="worktree",
            cwd="/tmp"
        )
        data = json.loads(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["status"], "completed")
        
        # Check optional fields are included or handled
        self.assertEqual(data.get("name"), "custom_name")
        self.assertEqual(data.get("agentType"), "specialized")
    
    def test_background_execution_warning(self):
        """Test background execution parameter (warning in simplified implementation)."""
        result = agent_tool(
            description="Background test",
            prompt="Test prompt",
            run_in_background=True
        )
        data = json.loads(result)
        
        # Should complete successfully with warning in metadata or content
        self.assertEqual(data.get("status"), "completed")
        
        # Check that background execution doesn't cause error
        self.assertNotIn("error", data)
    
    def test_usage_structure(self):
        """Test that usage structure matches Claude Code format."""
        result = agent_tool(
            description="Test usage",
            prompt="Test prompt for usage tracking"
        )
        data = json.loads(result)
        
        self.assertIn("usage", data)
        usage = data["usage"]
        
        # Check required usage fields
        self.assertIn("input_tokens", usage)
        self.assertIn("output_tokens", usage)
        self.assertIn("cache_creation_input_tokens", usage)
        self.assertIn("cache_read_input_tokens", usage)
        self.assertIn("server_tool_use", usage)
        self.assertIn("service_tier", usage)
        self.assertIn("cache_creation", usage)
        
        # Type checking
        self.assertIsInstance(usage["input_tokens"], int)
        self.assertIsInstance(usage["output_tokens"], int)
    
    def test_content_structure(self):
        """Test that content follows Claude Code format."""
        result = agent_tool(
            description="Content test",
            prompt="Test prompt for content"
        )
        data = json.loads(result)
        
        content = data["content"]
        self.assertIsInstance(content, list)
        
        if content:
            first_item = content[0]
            self.assertEqual(first_item["type"], "text")
            self.assertIsInstance(first_item["text"], str)
            self.assertGreater(len(first_item["text"]), 0)
    
    def test_agent_id_generation(self):
        """Test that agent IDs are generated."""
        result1 = agent_tool(
            description="Test 1",
            prompt="Prompt 1"
        )
        result2 = agent_tool(
            description="Test 2", 
            prompt="Prompt 2"
        )
        
        data1 = json.loads(result1)
        data2 = json.loads(result2)
        
        # Agent IDs should be different
        self.assertNotEqual(data1["agentId"], data2["agentId"])
        self.assertIsInstance(data1["agentId"], str)
        self.assertGreater(len(data1["agentId"]), 0)
    
    def test_claude_code_compatibility(self):
        """Test that output matches Claude Code's AgentTool format."""
        result = agent_tool(
            description="Compatibility test",
            prompt="Test prompt for compatibility check"
        )
        data = json.loads(result)
        
        # Main fields from Claude Code's AgentTool output (sync completion)
        expected_fields = [
            "status", "agentId", "content", "totalToolUseCount",
            "totalDurationMs", "totalTokens", "usage", "prompt", "description"
        ]
        
        for field in expected_fields:
            self.assertIn(field, data, f"Missing Claude Code field: {field}")
        
        # Status should be 'completed' for sync execution
        self.assertEqual(data["status"], "completed")
        
        # Type checking
        self.assertIsInstance(data["agentId"], str)
        self.assertIsInstance(data["content"], list)
        self.assertIsInstance(data["totalToolUseCount"], int)
        self.assertIsInstance(data["totalDurationMs"], int)
        self.assertIsInstance(data["totalTokens"], int)
        self.assertIsInstance(data["usage"], dict)
        self.assertIsInstance(data["prompt"], str)
        self.assertIsInstance(data["description"], str)
    
    def test_metadata_inclusion(self):
        """Test that metadata is included (AITools extension)."""
        result = agent_tool(
            description="Metadata test",
            prompt="Test prompt"
        )
        data = json.loads(result)
        
        # _metadata is an AITools extension, not part of Claude Code spec
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        
        # Check metadata fields
        self.assertIn("success", metadata)
        self.assertIn("agentName", metadata)
        self.assertIn("simplifiedImplementation", metadata)
        self.assertIn("timestamp", metadata)
        
        self.assertTrue(metadata["success"])
        self.assertTrue(metadata["simplifiedImplementation"])
    
    def test_execution_metrics(self):
        """Test that execution metrics are reasonable."""
        result = agent_tool(
            description="Metrics test",
            prompt="A" * 100  # Longer prompt for token count
        )
        data = json.loads(result)
        
        # Check that duration is positive
        self.assertGreater(data["totalDurationMs"], 0)
        
        # Check that token counts are reasonable
        self.assertGreater(data["totalTokens"], 0)
        self.assertGreater(data["usage"]["input_tokens"], 0)
        self.assertGreater(data["usage"]["output_tokens"], 0)
        
        # Input tokens should be at least prompt length
        self.assertGreaterEqual(data["usage"]["input_tokens"], 100)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # This test would check for proper error responses
        # Current implementation doesn't raise exceptions for invalid types
        # but returns error JSON
        pass


if __name__ == "__main__":
    unittest.main()