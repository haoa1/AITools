#!/usr/bin/env python3
"""
Basic tests for DownloadTool (Claude Code compatible version).
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.download_tool import download_file, _parse_json_string, _get_filename_from_url


class TestDownloadToolHelpers(unittest.TestCase):
    """Test helper functions for DownloadTool."""
    
    def test_parse_json_string_valid(self):
        """Test parsing valid JSON string."""
        result = _parse_json_string('{"key": "value"}', {})
        self.assertEqual(result, {"key": "value"})
    
    def test_parse_json_string_empty(self):
        """Test parsing empty string."""
        result = _parse_json_string("", {"default": "val"})
        self.assertEqual(result, {"default": "val"})
    
    def test_parse_json_string_invalid(self):
        """Test parsing invalid JSON string."""
        result = _parse_json_string('not json', {"default": "val"})
        self.assertEqual(result, "not json")
    
    def test_get_filename_from_url_with_filename(self):
        """Test extracting filename from URL with filename."""
        url = "http://example.com/file.txt"
        result = _get_filename_from_url(url)
        self.assertEqual(result, "file.txt")
    
    def test_get_filename_from_url_no_filename(self):
        """Test extracting filename from URL without filename."""
        url = "http://example.com/"
        result = _get_filename_from_url(url)
        self.assertIn("download_", result)
        self.assertIn(".bin", result)
    
    def test_get_filename_from_url_with_query(self):
        """Test extracting filename from URL with query parameters."""
        url = "http://example.com/file.txt?param=value"
        result = _get_filename_from_url(url)
        self.assertEqual(result, "file.txt")


class TestDownloadToolMain(unittest.TestCase):
    """Test main download_file function."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_url = "http://example.com/file.txt"
        self.test_save_path = "/tmp/test_download.txt"
        self.test_headers = '{"Content-Type": "application/octet-stream"}'
    
    def _parse_result(self, result_str):
        """Parse JSON result from download_file function."""
        return json.loads(result_str)
    
    @patch('network.download_tool.requests.get')
    @patch('network.download_tool.os.path.getsize')
    @patch('network.download_tool.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file_success(self, mock_file, mock_makedirs, mock_getsize, mock_get):
        """Test successful file download."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '1024'
        }
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value = mock_response
        
        # Mock file size
        mock_getsize.return_value = 1024
        
        result = download_file(
            url=self.test_url,
            save_path=self.test_save_path,
            headers=self.test_headers,
            timeout=30
        )
        
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "download_file")
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["save_path"], os.path.abspath(self.test_save_path))
        self.assertEqual(data["file_size_bytes"], 1024)
        self.assertEqual(data["expected_size_bytes"], 1024)
        self.assertTrue(data["download_success"])
        self.assertTrue(data["size_match"])
        self.assertEqual(data["status_code"], 200)
        self.assertEqual(data["content_type"], "text/plain")
        
        mock_get.assert_called_once()
        mock_file.assert_called()
    
    @patch('network.download_tool.requests.get')
    def test_download_file_timeout(self, mock_get):
        """Test file download timeout."""
        from requests.exceptions import Timeout
        mock_get.side_effect = Timeout("Request timed out")
        
        result = download_file(url=self.test_url, save_path=self.test_save_path, timeout=5)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("timed out", data["error"])
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["save_path"], self.test_save_path)
        self.assertEqual(data["timeout_seconds"], 5)
    
    @patch('network.download_tool.requests.get')
    def test_download_file_http_error(self, mock_get):
        """Test file download with HTTP error."""
        from requests.exceptions import HTTPError
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason = "Not Found"
        
        # Create HTTPError with response attribute
        http_error = HTTPError("404 Not Found")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        result = download_file(url=self.test_url, save_path=self.test_save_path)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("HTTP error", data["error"])
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["save_path"], self.test_save_path)
        self.assertEqual(data["status_code"], 404)
    
    @patch('network.download_tool.requests.get')
    def test_download_file_connection_error(self, mock_get):
        """Test file download connection error."""
        from requests.exceptions import ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        result = download_file(url=self.test_url, save_path=self.test_save_path)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Failed to connect", data["error"])
        self.assertEqual(data["url"], self.test_url)
    
    @patch('network.download_tool.requests.get')
    def test_download_file_ssl_error(self, mock_get):
        """Test file download SSL error."""
        from requests.exceptions import SSLError
        mock_get.side_effect = SSLError("SSL error")
        
        result = download_file(url=self.test_url, save_path=self.test_save_path, verify_ssl=True)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("SSL certificate", data["error"])
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["verify_ssl"], True)
    
    @patch('network.download_tool.requests.get')
    @patch('network.download_tool.os.path.getsize')
    @patch('network.download_tool.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file_size_mismatch(self, mock_file, mock_makedirs, mock_getsize, mock_get):
        """Test file download with size mismatch."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '2048'  # Expected 2048 bytes
        }
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'chunk1']
        mock_get.return_value = mock_response
        
        # Mock file size - different from expected
        mock_getsize.return_value = 1024  # Actual 1024 bytes
        
        result = download_file(url=self.test_url, save_path=self.test_save_path)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "download_file")
        self.assertEqual(data["file_size_bytes"], 1024)
        self.assertEqual(data["expected_size_bytes"], 2048)
        self.assertFalse(data["size_match"])
        self.assertIn("warning", data)
        self.assertIn("Expected 2048 bytes", data["warning"])
        self.assertEqual(data["size_difference_bytes"], -1024)
    
    def test_download_file_no_save_path(self):
        """Test file download without save_path (should generate filename)."""
        with patch('network.download_tool.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Type': 'text/plain'}
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.return_value = [b'chunk1']
            mock_get.return_value = mock_response
            
            with patch('network.download_tool.os.path.getsize') as mock_getsize:
                mock_getsize.return_value = 100
                
                with patch('builtins.open', new_callable=mock_open):
                    with patch('network.download_tool.os.makedirs'):
                        result = download_file(url=self.test_url)
                        data = self._parse_result(result)
                        
                        self.assertTrue(data["success"])
                        self.assertEqual(data["url"], self.test_url)
                        # Should have generated a save_path
                        self.assertIsNotNone(data["save_path"])
                        self.assertIn("file.txt", data["save_path"])


class TestDownloadToolIntegration(unittest.TestCase):
    """Integration tests for DownloadTool module."""
    
    def test_module_exports(self):
        """Test module exports."""
        from network.download_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 1)
        
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("download_file", TOOL_CALL_MAP)
    
    def test_function_ai_decorator(self):
        """Test that function_ai decorator is properly applied."""
        from network.download_tool import __DOWNLOAD_FILE_FUNCTION__
        
        self.assertIsNotNone(__DOWNLOAD_FILE_FUNCTION__)
        self.assertIn("function", __DOWNLOAD_FILE_FUNCTION__)
        self.assertIn("name", __DOWNLOAD_FILE_FUNCTION__["function"])
        self.assertEqual(__DOWNLOAD_FILE_FUNCTION__["function"]["name"], "download_file")
    
    def test_default_parameters(self):
        """Test function parameter defaults."""
        import inspect
        from network.download_tool import download_file
        
        sig = inspect.signature(download_file)
        params = sig.parameters
        
        self.assertEqual(params['timeout'].default, 30)
        self.assertEqual(params['verify_ssl'].default, True)
        self.assertEqual(params['follow_redirects'].default, True)
        self.assertEqual(params['stream'].default, True)
        self.assertEqual(params['save_path'].default, None)
        self.assertEqual(params['headers'].default, None)


if __name__ == "__main__":
    unittest.main()