#!/usr/bin/env python3
"""
Unit tests for WebSearchTool.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the network directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from network.web_search_tool import web_search_tool, WebSearchConfig


class TestWebSearchTool(unittest.TestCase):
    """Test cases for WebSearchTool"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment
        self.original_env = os.environ.copy()
        
        # Set environment variables for testing
        os.environ["WEB_SEARCH_INTERACTIVE"] = "false"  # Disable interactive output for tests
        os.environ["WEB_SEARCH_USE_SIMULATION"] = "true"  # Use simulation for tests
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_web_search_basic(self):
        """Test basic web search"""
        result = web_search_tool(query="python")
        data = json.loads(result)
        
        self.assertIn("tool_use_id", data)
        self.assertIn("content", data)
        self.assertIsInstance(data["content"], list)
        
        # Should have some results
        self.assertGreater(len(data["content"]), 0)
        
        # Each result should have title and url
        for result_item in data["content"]:
            self.assertIn("title", result_item)
            self.assertIn("url", result_item)
            self.assertIsInstance(result_item["title"], str)
            self.assertIsInstance(result_item["url"], str)
    
    def test_web_search_with_allowed_domains(self):
        """Test web search with allowed domains filtering"""
        allowed_domains = json.dumps(["python.org", "wikipedia.org"])
        
        result = web_search_tool(query="python", allowed_domains=allowed_domains)
        data = json.loads(result)
        
        self.assertIn("content", data)
        
        # Check that results contain allowed domains (in simulation, might not match exactly)
        # At least verify no crash
        
    def test_web_search_with_blocked_domains(self):
        """Test web search with blocked domains filtering"""
        blocked_domains = json.dumps(["example.com"])
        
        result = web_search_tool(query="python", blocked_domains=blocked_domains)
        data = json.loads(result)
        
        self.assertIn("content", data)
        # Can't verify filtering in simulation, but ensure no crash
    
    def test_web_search_with_both_domain_filters(self):
        """Test web search with both allowed and blocked domains"""
        allowed_domains = json.dumps(["python.org", "wikipedia.org"])
        blocked_domains = json.dumps(["example.com"])
        
        result = web_search_tool(
            query="python", 
            allowed_domains=allowed_domains,
            blocked_domains=blocked_domains
        )
        data = json.loads(result)
        
        self.assertIn("content", data)
    
    def test_web_search_invalid_query_empty(self):
        """Test web search with empty query"""
        result = web_search_tool(query="")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Query must be a non-empty string", data.get("error", ""))
    
    def test_web_search_invalid_query_too_short(self):
        """Test web search with query too short"""
        result = web_search_tool(query="a")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Query must be at least 2 characters", data.get("error", ""))
    
    def test_web_search_invalid_query_type(self):
        """Test web search with non-string query"""
        # Note: base module converts to string, but test with None
        result = web_search_tool(query=None)
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Query must be a non-empty string", data.get("error", ""))
    
    def test_web_search_disabled_tool(self):
        """Test when tool is disabled by configuration"""
        os.environ["WEB_SEARCH_ENABLED"] = "false"
        
        result = web_search_tool(query="python")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("WebSearchTool is disabled", data.get("error", ""))
        
        # Clean up env var
        del os.environ["WEB_SEARCH_ENABLED"]
    
    def test_web_search_config_overrides(self):
        """Test configuration overrides from environment variables"""
        # Test various config options
        test_configs = [
            ("WEB_SEARCH_ENABLED", "false", False),
            ("WEB_SEARCH_INTERACTIVE", "false", False),
            ("WEB_SEARCH_MAX_RESULTS", "5", 5),
            ("WEB_SEARCH_USE_SIMULATION", "false", False),
            ("WEB_SEARCH_SIMULATION_DELAY_MS", "500", 500),
        ]
        
        for env_var, value, expected_value in test_configs:
            os.environ[env_var] = value
            config = WebSearchConfig.from_env()
            
            config_key = env_var
            self.assertEqual(config.get(config_key), expected_value)
            
            # Clean up
            del os.environ[env_var]
    
    def test_web_search_domain_config(self):
        """Test domain configuration from environment variables"""
        # Test allowed domains
        os.environ["WEB_SEARCH_ALLOWED_DOMAINS"] = '["python.org", "github.com"]'
        config = WebSearchConfig.from_env()
        
        self.assertEqual(config.get("WEB_SEARCH_ALLOWED_DOMAINS"), ["python.org", "github.com"])
        del os.environ["WEB_SEARCH_ALLOWED_DOMAINS"]
        
        # Test blocked domains
        os.environ["WEB_SEARCH_BLOCKED_DOMAINS"] = '["example.com", "test.com"]'
        config = WebSearchConfig.from_env()
        
        self.assertEqual(config.get("WEB_SEARCH_BLOCKED_DOMAINS"), ["example.com", "test.com"])
        del os.environ["WEB_SEARCH_BLOCKED_DOMAINS"]
        
        # Test invalid JSON (should use default)
        os.environ["WEB_SEARCH_ALLOWED_DOMAINS"] = "not a json array"
        config = WebSearchConfig.from_env()
        
        # Should fall back to default (empty list)
        self.assertEqual(config.get("WEB_SEARCH_ALLOWED_DOMAINS"), [])
        del os.environ["WEB_SEARCH_ALLOWED_DOMAINS"]
    
    def test_web_search_response_structure(self):
        """Test that response matches Claude Code expected structure"""
        result = web_search_tool(query="test")
        data = json.loads(result)
        
        # Required fields by Claude Code WebSearchTool
        required_fields = ["tool_use_id", "content"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Field types
        self.assertIsInstance(data["tool_use_id"], str)
        self.assertIsInstance(data["content"], list)
        
        # Content items should have title and url
        if data["content"]:
            for item in data["content"]:
                self.assertIn("title", item)
                self.assertIn("url", item)
                self.assertIsInstance(item["title"], str)
                self.assertIsInstance(item["url"], str)
    
    def test_web_search_simulation_delay(self):
        """Test simulation delay (shouldn't crash)"""
        os.environ["WEB_SEARCH_SIMULATION_DELAY_MS"] = "50"
        
        import time
        start_time = time.time()
        
        result = web_search_tool(query="python")
        data = json.loads(result)
        
        elapsed = time.time() - start_time
        
        # Should have taken at least some time (though delay is small)
        self.assertGreater(elapsed, 0.01)
        self.assertIn("content", data)
        
        del os.environ["WEB_SEARCH_SIMULATION_DELAY_MS"]
    
    def test_web_search_max_results(self):
        """Test max results limit"""
        os.environ["WEB_SEARCH_MAX_RESULTS"] = "3"
        
        result = web_search_tool(query="python")
        data = json.loads(result)
        
        # Should have at most 3 results
        self.assertLessEqual(len(data.get("content", [])), 3)
        
        del os.environ["WEB_SEARCH_MAX_RESULTS"]
    
    def test_web_search_domain_extraction(self):
        """Test domain extraction from URLs"""
        from network.web_search_tool import _extract_domain
        
        test_cases = [
            ("https://www.example.com/path", "example.com"),
            ("http://example.com", "example.com"),
            ("https://subdomain.example.com/page", "subdomain.example.com"),
            ("not a url", ""),
            ("", ""),
        ]
        
        for url, expected in test_cases:
            self.assertEqual(_extract_domain(url), expected)
    
    def test_web_search_simulation_results(self):
        """Test simulation results generation"""
        from network.web_search_tool import _simulate_search_results
        
        # Test with known query
        results = _simulate_search_results("python", 3)
        self.assertLessEqual(len(results), 3)
        
        for result in results:
            self.assertIn("title", result)
            self.assertIn("url", result)
        
        # Test with unknown query (should return default results)
        results = _simulate_search_results("some unknown query", 2)
        self.assertLessEqual(len(results), 2)
    
    def test_web_search_comma_separated_domains(self):
        """Test domain parsing from comma-separated strings"""
        # Test allowed_domains as comma-separated string (not JSON)
        result = web_search_tool(
            query="python",
            allowed_domains="python.org, github.com, wikipedia.org"
        )
        data = json.loads(result)
        
        # Should not crash
        self.assertIn("content", data)
        
        # Test blocked_domains as comma-separated string
        result = web_search_tool(
            query="python",
            blocked_domains="example.com, test.com"
        )
        data = json.loads(result)
        
        self.assertIn("content", data)
    
    def test_web_search_interactive_mode(self):
        """Test interactive mode (mostly just ensure it doesn't crash)"""
        os.environ["WEB_SEARCH_INTERACTIVE"] = "true"
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            result = web_search_tool(query="python")
            data = json.loads(result)
            
            # Should still succeed
            self.assertIn("content", data)
            
            # Should have printed something in interactive mode
            self.assertTrue(mock_print.called)
        
        del os.environ["WEB_SEARCH_INTERACTIVE"]
    
    def test_web_search_exception_handling(self):
        """Test exception handling in tool"""
        # Mock time.sleep to raise exception
        with patch('time.sleep', side_effect=Exception("Mocked sleep error")):
            result = web_search_tool(query="python")
            data = json.loads(result)
            
            self.assertFalse(data.get("success", True))
            self.assertIn("Web search failed", data.get("error", ""))
    
    def test_web_search_real_api_disabled(self):
        """Test with simulation disabled (should still use simulation as fallback)"""
        os.environ["WEB_SEARCH_USE_SIMULATION"] = "false"
        
        # Even with simulation disabled, our implementation falls back to simulation
        result = web_search_tool(query="python")
        data = json.loads(result)
        
        self.assertIn("content", data)
        self.assertGreater(len(data["content"]), 0)
        
        del os.environ["WEB_SEARCH_USE_SIMULATION"]


if __name__ == "__main__":
    unittest.main()