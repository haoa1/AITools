#!/usr/bin/env python3
"""
Fixed tests for PowerShellTool (Claude Code compatible version).
Clean version without duplicate function definitions.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shell.power_shell_tool import (
    power_shell, 
    _get_powershell_path, 
    _is_powershell_available,
    _build_powershell_command,
    _get_return_code_interpretation,
    _is_no_output_expected,
    _is_image_output
)


class TestPowerShellToolHelpers(unittest.TestCase):
    """Test helper functions for PowerShellTool."""
    
    def test_get_return_code_interpretation(self):
        """Test return code interpretation."""
        # Success
        self.assertEqual(_get_return_code_interpretation(0, "test"), "Success")
        
        # Known PowerShell error codes
        self.assertEqual(_get_return_code_interpretation(1, "test"), "General error")
        self.assertEqual(_get_return_code_interpretation(2, "test"), "Parse error in PowerShell script")
        self.assertEqual(_get_return_code_interpretation(3, "test"), "Pipeline stopped")
        self.assertEqual(_get_return_code_interpretation(4, "test"), "Script terminated by Ctrl+C or Stop-Processing")
        self.assertEqual(_get_return_code_interpretation(5, "test"), "Unhandled exception")
        self.assertEqual(_get_return_code_interpretation(-1, "test"), "Command timeout or interrupted")
    
    def test_is_no_output_expected(self):
        """Test detection of commands expected to produce no output."""
        # Cmdlets that typically don't produce output
        self.assertTrue(_is_no_output_expected("Set-Variable -Name test -Value 1"))
        self.assertTrue(_is_no_output_expected("New-Item -Path . -Name test.txt"))
        self.assertTrue(_is_no_output_expected("Remove-Item test.txt"))
        self.assertTrue(_is_no_output_expected("Rename-Item old.txt new.txt"))
        self.assertTrue(_is_no_output_expected("Move-Item source.txt dest.txt"))
        
        # Variable assignment
        self.assertTrue(_is_no_output_expected("$var = 'test'"))
        self.assertTrue(_is_no_output_expected("$result = Get-Process"))
        
        # Output redirection to null
        self.assertTrue(_is_no_output_expected("Get-Process | Out-Null"))
        self.assertTrue(_is_no_output_expected("Write-Host 'test' > $null"))
        
        # Commands that should produce output
        self.assertFalse(_is_no_output_expected("Get-Process"))
        self.assertFalse(_is_no_output_expected("Get-ChildItem"))
        self.assertFalse(_is_no_output_expected("Write-Host 'Hello'"))
        
        # Mixed
        self.assertTrue(_is_no_output_expected("Get-Process | Select-Object Name | Out-Null"))
    
    def test_is_image_output(self):
        """Test image detection in output."""
        # Empty data
        self.assertFalse(_is_image_output(b''))
        
        # Text data
        self.assertFalse(_is_image_output(b'Hello World'))
        self.assertFalse(_is_image_output(b'{"json": "data"}'))
        
        # PNG header (simulated)
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        self.assertTrue(_is_image_output(png_header))
    
    @patch('shutil.which')
    def test_get_powershell_path_found(self, mock_which):
        """Test finding PowerShell path when available."""
        mock_which.side_effect = lambda cmd: {
            'pwsh': '/usr/bin/pwsh',
            'powershell': None
        }.get(cmd)
        
        path = _get_powershell_path()
        self.assertEqual(path, '/usr/bin/pwsh')
    
    @patch('shutil.which')
    def test_get_powershell_path_not_found(self, mock_which):
        """Test not finding PowerShell path."""
        mock_which.return_value = None
        
        path = _get_powershell_path()
        self.assertIsNone(path)
    
    @patch('shell.power_shell_tool._get_powershell_path')
    @patch('subprocess.run')
    def test_is_powershell_available_available(self, mock_run, mock_get_path):
        """Test PowerShell availability check when available."""
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "7.3.4\n"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        available, version_info, error = _is_powershell_available()
        
        self.assertTrue(available)
        self.assertIn("PowerShell 7.3.4 at /usr/bin/pwsh", version_info)
        self.assertIsNone(error)
    
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_is_powershell_available_not_found(self, mock_get_path):
        """Test PowerShell availability check when not found."""
        mock_get_path.return_value = None
        
        available, version_info, error = _is_powershell_available()
        
        self.assertFalse(available)
        self.assertIsNone(version_info)
        self.assertIn("PowerShell not found", error)
    
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_build_powershell_command_simple(self, mock_get_path):
        """Test building simple PowerShell command."""
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        cmd = _build_powershell_command("Get-Process", None, None, None)
        
        self.assertEqual(len(cmd), 3)
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_build_powershell_command_simple(self, mock_get_path):
        """Test building simple PowerShell command."""
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        cmd = _build_powershell_command("Get-Process", None, None)
        
        self.assertEqual(len(cmd), 3)
        self.assertEqual(cmd[0], '/usr/bin/pwsh')
        self.assertEqual(cmd[1], '-Command')
        self.assertEqual(cmd[2], "Get-Process")
    
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_build_powershell_command_with_execution_policy(self, mock_get_path):
        """Test building PowerShell command with execution policy."""
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        cmd = _build_powershell_command("Get-Process", "Bypass", None)
        
        self.assertEqual(len(cmd), 5)
        self.assertEqual(cmd[0], '/usr/bin/pwsh')
        self.assertEqual(cmd[1], '-ExecutionPolicy')
        self.assertEqual(cmd[2], 'Bypass')
        self.assertEqual(cmd[3], '-Command')
        self.assertEqual(cmd[4], "Get-Process")
    
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_build_powershell_command_invalid_policy(self, mock_get_path):
        """Test building PowerShell command with invalid execution policy."""
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        cmd = _build_powershell_command("Get-Process", "InvalidPolicy", None)
        
        # Should ignore invalid policies (not add -ExecutionPolicy)
        self.assertEqual(len(cmd), 3)  # No -ExecutionPolicy added
        self.assertEqual(cmd[0], '/usr/bin/pwsh')
        self.assertEqual(cmd[1], '-Command')
        self.assertEqual(cmd[2], "Get-Process")


class TestPowerShellToolMain(unittest.TestCase):
    """Test main power_shell function."""
    
    def setUp(self):
        # Save original environment
        self.original_cwd = os.getcwd()
        
        # Create temp directory for tests
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        # Restore original directory
        os.chdir(self.original_cwd)
        
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _parse_result(self, result_str):
        """Parse JSON result from power_shell function."""
        return json.loads(result_str)
    
    def test_empty_command(self):
        """Test with empty command."""
        result = power_shell("")
    def test_empty_command(self):
        """Test with empty command."""
        result = power_shell("")
        data = self._parse_result(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        self.assertIn("non-empty string", data["error"])
    
    @patch('shell.power_shell_tool._is_powershell_available')
    @patch('shell.power_shell_tool._get_powershell_path')
    @patch('subprocess.run')
    def test_simple_command_success(self, mock_run, mock_get_path, mock_available):
        """Test successful execution of simple command."""
        # Mock PowerShell available
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        # Mock subprocess result
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Process1\nProcess2\nProcess3\n"
        mock_process.stderr = b""
        mock_run.return_value = mock_process
        
        result = power_shell("Get-Process")
        data = self._parse_result(result)
        
        # Check that success is in metadata, not at top level
        metadata = data["_metadata"]
        self.assertTrue(metadata.get("success", False))
        
        self.assertEqual(data["interrupted"], False)
        self.assertEqual(data["returnCodeInterpretation"], "Success")
        self.assertEqual(data["stdout"], "Process1\nProcess2\nProcess3\n")
        self.assertEqual(data["stderr"], "")
        self.assertNotIn("_warning", data)
        
        # Check metadata
        self.assertEqual(metadata.get("returnCode"), 0)
        self.assertEqual(metadata.get("powerShellAvailable"), True)
        self.assertEqual(metadata.get("powerShellVersion"), "PowerShell 7.3.4 at /usr/bin/pwsh")
        self.assertEqual(metadata.get("executionPolicy"), None)
    
    @patch('shell.power_shell_tool._is_powershell_available')
    @patch('shell.power_shell_tool._get_powershell_path')
    @patch('subprocess.run')
    def test_command_with_timeout_success(self, mock_run, mock_get_path, mock_available):
        """Test command with timeout that completes successfully."""
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Completed"
        mock_process.stderr = b""
        mock_run.return_value = mock_process
        
        # Call power_shell with timeout
        result = power_shell("Get-Process", timeout=5000)
        data = self._parse_result(result)
        
        self.assertNotIn("error", data)
        self.assertEqual(data["interrupted"], False)
        self.assertIn("Completed", data["stdout"])
        
        metadata = data["_metadata"]
        self.assertEqual(metadata.get("timeoutMs"), 5000)
    
    @patch('shell.power_shell_tool._is_powershell_available')
    @patch('shell.power_shell_tool._get_powershell_path')
    @patch('subprocess.run')
    def test_command_with_timeout_expired(self, mock_run, mock_get_path, mock_available):
        """Test command that times out."""
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        # Simulate timeout
        mock_run.side_effect = TimeoutError("Command timed out")
        
        # Call power_shell with timeout
        result = power_shell("Get-Process", timeout=1000)
        data = self._parse_result(result)
        
        # Should have timeout response
        self.assertEqual(data["interrupted"], True)
        self.assertIn("timed out", data["stderr"])
        self.assertIn("timed out", data["returnCodeInterpretation"])
        
        metadata = data["_metadata"]
        # Call power_shell with timeout
        result = power_shell("Get-Process", timeout=1000)
        data = self._parse_result(result)
        
        # Should have timeout response
        self.assertEqual(data["interrupted"], True)
        self.assertIn("timed out", data["stderr"])
        self.assertIn("timed out", data["returnCodeInterpretation"])
        
        # Check metadata
        metadata = data["_metadata"]
        self.assertEqual(metadata.get("returnCode"), -1)
        self.assertFalse(metadata.get("success"))
        self.assertEqual(metadata.get("error"), "TimeoutExpired")
        mock_run.return_value = mock_process
        
        result = power_shell("Get-Process", executionPolicy="Bypass")
        data = self._parse_result(result)
        
        self.assertNotIn("error", data)
        
        metadata = data["_metadata"]
        self.assertEqual(metadata.get("executionPolicy"), "Bypass")
    
    @patch('shell.power_shell_tool._is_powershell_available')
    @patch('shell.power_shell_tool._get_powershell_path')
    @patch('subprocess.run')
    def test_command_with_background_request(self, mock_run, mock_get_path, mock_available):
        """Test command with background execution request."""
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = b"Running in background"
        mock_process.stderr = b""
        mock_run.return_value = mock_process
        
        result = power_shell("Get-Process", run_in_background=True)
        data = self._parse_result(result)
        
        self.assertIn("Background execution", data["_warning"])
        
        metadata = data["_metadata"]
        self.assertTrue(metadata.get("runInBackground"))
        self.assertTrue(metadata.get("success", False))  # success should be True when returncode=0
        
        # Check command does NOT include -ExecutionPolicy Bypass (not specified)
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd_str = ' '.join(call_args[0][0])
        # Should not include -ExecutionPolicy since we didn't specify it
        self.assertNotIn("-ExecutionPolicy", cmd_str)
    
    @patch('shell.power_shell_tool._is_powershell_available')
    @patch('shell.power_shell_tool._get_powershell_path')
    def test_negative_timeout(self, mock_get_path, mock_available):
        """Test with negative timeout value."""
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        mock_get_path.return_value = '/usr/bin/pwsh'
        
        result = power_shell("Get-Process", timeout=-1000)
        data = self._parse_result(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        self.assertIn("must be positive", data["error"])
    
    @patch('shell.power_shell_tool._is_powershell_available')
    def test_nonexistent_working_directory(self, mock_available):
        """Test with non-existent working directory."""
        mock_available.return_value = (True, "PowerShell 7.3.4 at /usr/bin/pwsh", None)
        
        # Change to non-existent directory
        non_existent_dir = os.path.join(self.temp_dir, "nonexistent")
        
        # Temporarily change directory
        original_dir = os.getcwd()
        try:
            # Actually we can't change to non-existent dir, so we'll patch os.getcwd
            with patch('os.getcwd', return_value=non_existent_dir):
                result = power_shell("Get-Process")
                data = self._parse_result(result)
                
                self.assertIn("error", data)
                self.assertFalse(data.get("success", True))
                self.assertIn("does not exist", data["error"])
        finally:
            os.chdir(original_dir)


class TestPowerShellToolIntegration(unittest.TestCase):
    """Integration tests for PowerShellTool module."""
    
    def test_module_exports(self):
        """Test module exports."""
        from shell.power_shell_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("power_shell", TOOL_CALL_MAP)
    
    def test_function_ai_decorator_presence(self):
        """Test that function_ai decorator is properly applied."""
        from shell.power_shell_tool import __POWERSHELL_TOOL_FUNCTION__
        
        # Check that the decorator was applied
        self.assertIsNotNone(__POWERSHELL_TOOL_FUNCTION__)
        self.assertIn("function", __POWERSHELL_TOOL_FUNCTION__)
        self.assertIn("name", __POWERSHELL_TOOL_FUNCTION__["function"])
        self.assertEqual(__POWERSHELL_TOOL_FUNCTION__["function"]["name"], "power_shell")
    
    def test_default_parameters(self):
        """Test function parameter defaults."""
        import inspect
        from shell.power_shell_tool import power_shell
        
        sig = inspect.signature(power_shell)
        params = sig.parameters
        
        self.assertIn('timeout', params)
        self.assertEqual(params['timeout'].default, None)
        
        self.assertIn('description', params)
        self.assertEqual(params['description'].default, None)
        
        self.assertIn('run_in_background', params)
        self.assertEqual(params['run_in_background'].default, False)
        
        self.assertIn('dangerouslyDisableSandbox', params)
        self.assertEqual(params['dangerouslyDisableSandbox'].default, False)
        
        self.assertIn('executionPolicy', params)
        self.assertEqual(params['executionPolicy'].default, None)
        
        self.assertIn('encoding', params)
        self.assertEqual(params['encoding'].default, None)


if __name__ == '__main__':
    unittest.main()