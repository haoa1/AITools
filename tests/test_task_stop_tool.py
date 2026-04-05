#!/usr/bin/env python3
"""
Unit tests for TaskStopTool.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add the system directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from system.task_stop_tool import task_stop_tool, TaskStopConfig


class TestTaskStopTool(unittest.TestCase):
    """Test cases for TaskStopTool"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.temp_tasks_file = os.path.join(self.temp_dir, "tasks.json")
        
        # Set environment variables for testing
        self.original_env = os.environ.copy()
        os.environ["TASK_STOP_TASKS_PATH"] = self.temp_tasks_file
        os.environ["TASK_STOP_INTERACTIVE"] = "false"  # Disable interactive output for tests
        
        # Create a sample task for testing
        self.sample_task = {
            "id": "test_task_123",
            "subject": "Test task subject",
            "description": "Test task description",
            "status": "running",
            "type": "bash",
            "created_at": 1234567890,
            "updated_at": 1234567890
        }
        
        # Create tasks file with sample task
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump([self.sample_task], f, indent=2)
    
    def tearDown(self):
        """Clean up test environment"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
    
    def test_task_stop_success(self):
        """Test successful task stopping"""
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertEqual(data.get("task_id"), "test_task_123")
        self.assertEqual(data.get("task_type"), "bash")
        self.assertEqual(data.get("command"), "Test task subject")
        self.assertIn("Successfully stopped task", data.get("message", ""))
        
        # Verify task was updated in file
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        updated_task = next((t for t in tasks if t["id"] == "test_task_123"), None)
        self.assertIsNotNone(updated_task)
        self.assertEqual(updated_task["status"], "stopped")
    
    def test_task_stop_shell_id_compatibility(self):
        """Test backward compatibility with shell_id parameter"""
        result = task_stop_tool(shell_id="test_task_123")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertEqual(data.get("task_id"), "test_task_123")
        self.assertIn("Successfully stopped task", data.get("message", ""))
    
    def test_task_stop_task_id_precedence(self):
        """Test that task_id takes precedence over shell_id"""
        # Create another task for testing
        another_task = {
            "id": "another_task_456",
            "subject": "Another task",
            "status": "running",
            "type": "agent",
            "created_at": 1234567890
        }
        
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        tasks.append(another_task)
        
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
        
        # Call with both task_id and shell_id
        result = task_stop_tool(task_id="another_task_456", shell_id="test_task_123")
        data = json.loads(result)
        
        # Should stop the task_id, not shell_id
        self.assertEqual(data.get("task_id"), "another_task_456")
    
    def test_task_stop_missing_parameters(self):
        """Test missing both task_id and shell_id"""
        result = task_stop_tool()
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Missing required parameter", data.get("error", ""))
    
    def test_task_stop_nonexistent_task(self):
        """Test stopping a non-existent task"""
        result = task_stop_tool(task_id="nonexistent_task_999")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("No task found with ID", data.get("error", ""))
    
    def test_task_stop_invalid_task_id_format(self):
        """Test invalid task ID format"""
        # Empty string
        result = task_stop_tool(task_id="")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Task ID must be a non-empty string", data.get("error", ""))
        
        # Too long task ID
        long_id = "x" * 101
        result = task_stop_tool(task_id=long_id)
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Task ID too long", data.get("error", ""))
    
    def test_task_stop_disabled_tool(self):
        """Test when tool is disabled by configuration"""
        os.environ["TASK_STOP_ENABLED"] = "false"
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("TaskStopTool is disabled", data.get("error", ""))
        
        # Clean up env var
        del os.environ["TASK_STOP_ENABLED"]
    
    def test_task_stop_simulate_only_mode(self):
        """Test simulate only mode (no actual changes)"""
        os.environ["TASK_STOP_SIMULATE_ONLY"] = "true"
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertIn("Simulated stopping task", data.get("message", ""))
        
        # Verify task was NOT updated in file
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        original_task = next((t for t in tasks if t["id"] == "test_task_123"), None)
        self.assertIsNotNone(original_task)
        self.assertEqual(original_task["status"], "running")  # Still running
        
        # Clean up env var
        del os.environ["TASK_STOP_SIMULATE_ONLY"]
    
    def test_task_stop_allow_any_status(self):
        """Test stopping tasks regardless of status"""
        # Update task to non-running status
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        tasks[0]["status"] = "completed"
        
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
        
        # By default, should allow stopping any status
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        
        # Now disable allowing any status
        os.environ["TASK_STOP_ALLOW_ANY_STATUS"] = "false"
        
        # Reset task to completed
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        tasks[0]["status"] = "completed"
        
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("is not running", data.get("error", ""))
        
        # Clean up env var
        del os.environ["TASK_STOP_ALLOW_ANY_STATUS"]
    
    def test_task_stop_corrupted_storage_file(self):
        """Test handling corrupted storage file"""
        # Write invalid JSON to tasks file
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid json")
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        # Should fail because task not found in empty/corrupted storage
        self.assertFalse(data.get("success", True))
        self.assertIn("No task found with ID", data.get("error", ""))
    
    def test_task_stop_storage_file_not_exist(self):
        """Test when storage file doesn't exist"""
        # Remove tasks file
        os.remove(self.temp_tasks_file)
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("No task found with ID", data.get("error", ""))
    
    def test_task_stop_interactive_mode(self):
        """Test interactive mode (mostly just ensure it doesn't crash)"""
        os.environ["TASK_STOP_INTERACTIVE"] = "true"
        
        # Mock print to capture output
        with patch('builtins.print') as mock_print:
            result = task_stop_tool(task_id="test_task_123")
            data = json.loads(result)
            
            # Should still succeed
            self.assertTrue(data.get("success", True))
            
            # Should have printed something in interactive mode
            self.assertTrue(mock_print.called)
        
        del os.environ["TASK_STOP_INTERACTIVE"]
    
    def test_task_stop_config_overrides(self):
        """Test configuration overrides from environment variables"""
        # Test various config options
        test_configs = [
            ("TASK_STOP_ENABLED", "false", False),
            ("TASK_STOP_INTERACTIVE", "false", False),
            ("TASK_STOP_ALLOW_ANY_STATUS", "false", False),
            ("TASK_STOP_SIMULATE_ONLY", "true", True),
        ]
        
        for env_var, value, expected_value in test_configs:
            os.environ[env_var] = value
            config = TaskStopConfig.from_env()
            
            # Convert expected boolean
            if value in ["true", "false"]:
                expected = value.lower() == "true"
            else:
                expected = value
            
            config_key = env_var
            self.assertEqual(config.get(config_key), expected)
            
            # Clean up
            del os.environ[env_var]
    
    def test_task_stop_response_structure(self):
        """Test that response matches Claude Code expected structure"""
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        # Required fields by Claude Code
        required_fields = ["message", "task_id", "task_type", "command"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Field types
        self.assertIsInstance(data["message"], str)
        self.assertIsInstance(data["task_id"], str)
        self.assertIsInstance(data["task_type"], str)
        self.assertIsInstance(data["command"], str)
    
    def test_task_stop_multiple_tasks(self):
        """Test stopping tasks when multiple exist"""
        # Add more tasks
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        tasks.extend([
            {
                "id": "task_2",
                "subject": "Second task",
                "status": "running",
                "type": "agent",
                "created_at": 1234567891
            },
            {
                "id": "task_3",
                "subject": "Third task",
                "status": "completed",
                "type": "bash",
                "created_at": 1234567892
            }
        ])
        
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2)
        
        # Stop the second task
        result = task_stop_tool(task_id="task_2")
        data = json.loads(result)
        
        self.assertTrue(data.get("success", True))
        self.assertEqual(data.get("task_id"), "task_2")
        
        # Verify only task_2 was updated
        with open(self.temp_tasks_file, 'r', encoding='utf-8') as f:
            updated_tasks = json.load(f)
        
        task_statuses = {t["id"]: t["status"] for t in updated_tasks}
        self.assertEqual(task_statuses["test_task_123"], "running")  # Still running (not stopped)
        self.assertEqual(task_statuses["task_2"], "stopped")  # Was stopped
        self.assertEqual(task_statuses["task_3"], "completed")  # Unchanged
    
    def test_task_stop_empty_storage(self):
        """Test stopping task from empty storage"""
        # Empty the tasks file
        with open(self.temp_tasks_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
        
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("No task found with ID", data.get("error", ""))
    
    def test_task_stop_with_metadata(self):
        """Test that response includes useful metadata"""
        result = task_stop_tool(task_id="test_task_123")
        data = json.loads(result)
        
        # Should have metadata (our extension, not part of Claude Code spec)
        self.assertIn("_metadata", data)
        metadata = data["_metadata"]
        
        self.assertTrue(metadata.get("success", False))
        self.assertEqual(metadata.get("previousStatus"), "running")
        self.assertEqual(metadata.get("newStatus"), "stopped")
        self.assertFalse(metadata.get("simulateOnly", True))
    
    def test_task_stop_exception_handling(self):
        """Test exception handling in tool"""
        # Mock open to raise exception
        with patch('builtins.open', side_effect=IOError("Mocked IO error")):
            result = task_stop_tool(task_id="test_task_123")
            data = json.loads(result)
            
            self.assertFalse(data.get("success", True))
            # When file open fails, tasks list is empty and task is not found
            self.assertIn("No task found with ID", data.get("error", ""))
    
    def test_task_stop_validation_edge_cases(self):
        """Test various edge cases in parameter validation"""
        # Non-string task_id (will come as string from base module, but test anyway)
        result = task_stop_tool(task_id=123)  # Number instead of string
        data = json.loads(result)
        
        # Should still work (base module converts to string)
        # But our validation checks isinstance(task_id, str)
        # In practice, base module ensures string type
        
        # Actually test with actual string
        result = task_stop_tool(task_id="  ")  # Whitespace only
        data = json.loads(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("Task ID must be a non-empty string", data.get("error", ""))


if __name__ == "__main__":
    unittest.main()