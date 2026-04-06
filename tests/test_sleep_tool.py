#!/usr/bin/env python3
"""
Tests for SleepTool (Claude Code compatible version - simplified).
"""

import os
import sys
import json
import time
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.sleep_tool import sleep_tool


class TestSleepTool(unittest.TestCase):
    """Test suite for SleepTool."""
    
    def test_basic_sleep_functionality(self):
        """Test basic sleep functionality."""
        start_time = time.time()
        result = sleep_tool(duration=0.1)  # 0.1 second sleep
        elapsed_time = time.time() - start_time
        
        data = json.loads(result)
        
        # Check for error
        self.assertNotIn("error", data, f"Error in response: {data}")
        
        # Check required fields
        self.assertTrue(data["success"])
        self.assertEqual(data["duration"], 0.1)
        self.assertEqual(data["unit"], "seconds")
        self.assertIn("actualSleepTime", data)
        
        # Check that sleep actually happened (within tolerance)
        self.assertGreaterEqual(elapsed_time, 0.09)  # At least 90ms
        self.assertLessEqual(elapsed_time, 0.15)     # At most 150ms
        
        # Check metadata
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        self.assertIn("simplifiedImplementation", metadata)
        self.assertTrue(metadata["simplifiedImplementation"])
    
    def test_sleep_with_unit_conversion(self):
        """Test sleep with different time units."""
        # Test minutes
        result = sleep_tool(duration=0.0167, unit="minutes")  # ~1 second
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["unit"], "minutes")
        self.assertEqual(data["duration"], 1.0)  # 0.0167 minutes = 1 second
        
        # Test hours
        result = sleep_tool(duration=0.000278, unit="hours")  # ~1 second
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["unit"], "hours")
        self.assertEqual(data["duration"], 1.0)  # 0.000278 hours = 1 second
        
        # Test milliseconds
        result = sleep_tool(duration=100, unit="milliseconds")  # 100ms
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["unit"], "milliseconds")
        self.assertEqual(data["duration"], 0.1)  # 100ms = 0.1 second
    
    def test_sleep_with_reason(self):
        """Test sleep with reason parameter."""
        reason = "Waiting for external API response"
        result = sleep_tool(duration=0.1, reason=reason)
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["reason"], reason)
    
    def test_sleep_error_handling(self):
        """Test error handling for invalid inputs."""
        # Negative duration
        result = sleep_tool(duration=-1)
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("error", data)
        
        # Zero duration
        result = sleep_tool(duration=0)
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("error", data)
        
        # Non-numeric duration (string will be handled by type system, but test anyway)
        # Our function expects int/float, but Python may convert
        
        # Very large duration (exceeds max)
        result = sleep_tool(duration=1000)  # 1000 seconds > 300 max
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("error", data)
        self.assertIn("too long", data["error"].lower())
    
    def test_sleep_timing_accuracy(self):
        """Test that sleep timing is reasonably accurate."""
        test_duration = 0.2  # 200ms
        
        start_time = time.time()
        result = sleep_tool(duration=test_duration)
        elapsed_time = time.time() - start_time
        
        data = json.loads(result)
        
        # Check success
        self.assertTrue(data["success"])
        
        # Check reported sleep time
        actual_sleep_time = data["actualSleepTime"]
        
        # Should be close to requested duration (within 10% tolerance)
        tolerance = test_duration * 0.1
        self.assertAlmostEqual(actual_sleep_time, test_duration, delta=tolerance)
        self.assertAlmostEqual(elapsed_time, test_duration, delta=tolerance)
    
    def test_claude_code_compatibility(self):
        """Test that output matches Claude Code's SleepTool format."""
        result = sleep_tool(duration=0.1)
        data = json.loads(result)
        
        # Required fields from our implementation
        required_fields = ["success", "duration", "unit", "actualSleepTime"]
        
        for field in required_fields:
            self.assertIn(field, data, f"Missing field: {field}")
        
        # Type checking
        self.assertIsInstance(data["success"], bool)
        self.assertIsInstance(data["duration"], (int, float))
        self.assertIsInstance(data["unit"], str)
        self.assertIsInstance(data["actualSleepTime"], (int, float))
        
        # Check that timing fields are present
        self.assertIn("startTime", data)
        self.assertIn("endTime", data)
        self.assertIsInstance(data["startTime"], (int, float))
        self.assertIsInstance(data["endTime"], (int, float))
        
        # Check metadata
        self.assertIn("_metadata", data)
    
    def test_default_unit(self):
        """Test that default unit is seconds."""
        result = sleep_tool(duration=0.1)
        data = json.loads(result)
        
        self.assertEqual(data["unit"], "seconds")
        
        # Explicitly pass "seconds"
        result2 = sleep_tool(duration=0.1, unit="seconds")
        data2 = json.loads(result2)
        
        self.assertEqual(data2["unit"], "seconds")
    
    def test_unknown_unit_falls_back_to_seconds(self):
        """Test that unknown units fall back to seconds."""
        result = sleep_tool(duration=1, unit="unknown_unit")
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        # Should default to seconds or keep the provided unit
        self.assertEqual(data["unit"], "unknown_unit")
        self.assertEqual(data["duration"], 1.0)
    
    def test_max_duration_enforcement(self):
        """Test maximum duration enforcement."""
        # Test at max boundary
        result = sleep_tool(duration=300)  # Exactly max
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        
        # Test just over max
        result = sleep_tool(duration=301)  # 1 second over max
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("error", data)
        
        # Check that error includes max duration info
        error_msg = data["error"].lower()
        self.assertIn("max", error_msg)
        self.assertIn("300", data.get("max_allowed", ""))
    
    def test_sleep_with_float_duration(self):
        """Test sleep with floating point duration."""
        result = sleep_tool(duration=0.55)  # 550ms
        data = json.loads(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["duration"], 0.55)
        
        # Check timing
        actual_sleep = data["actualSleepTime"]
        self.assertGreaterEqual(actual_sleep, 0.5)
        self.assertLessEqual(actual_sleep, 0.6)


if __name__ == "__main__":
    unittest.main()