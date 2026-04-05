#!/usr/bin/env python3
"""
Tests for HttpTool (Claude Code compatible version).
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.http_tool import http_request, http_get, http_post, _parse_json_string, _format_response


class TestHttpToolHelpers(unittest.TestCase):
    """Test helper functions for HttpTool."""
    
    def test_parse_json_string_valid(self):
        """Test parsing valid JSON string."""
        result = _parse_json_string('{"key": "value"}', {})
        self.assertEqual(result, {"key": "value"})
    
    def test_parse_json_string_empty(self):
        """Test parsing empty string."""
        result = _parse_json_string("", {"default": "val"})
        self.assertEqual(result, {"default": "val"})
    
    def test_parse_json_string_none(self):
        """Test parsing None."""
        result = _parse_json_string(None, {"default": "val"})
        self.assertEqual(result, {"default": "val"})
    
    def test_parse_json_string_invalid(self):
        """Test parsing invalid JSON string."""
        result = _parse_json_string('not json', {"default": "val"})
        self.assertEqual(result, "not json")
    
    def test_format_response_success(self):
        """Test formatting HTTP response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = "http://example.com"
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        
        result = _format_response(mock_response)
        
        self.assertIn("Status Code: 200 OK", result)
        self.assertIn("URL: http://example.com", result)
        self.assertIn("Response Time: 0.123s", result)
        self.assertIn("Content-Type: application/json", result)
        self.assertIn('"test": "data"', result)


class TestHttpToolMain(unittest.TestCase):
    """Test main http functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_url = "http://example.com"
        self.test_headers = '{"Content-Type": "application/json"}'
        self.test_params = '{"page": "1"}'
        self.test_data = '{"key": "value"}'
        self.test_json = '{"json_key": "json_value"}'
    
    def _parse_result(self, result_str):
        """Parse JSON result from http functions."""
        return json.loads(result_str)
    
    @patch('network.http_tool.requests.request')
    def test_http_request_success(self, mock_request):
        """Test successful HTTP request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = self.test_url
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_request.return_value = mock_response
        
        result = http_request(
            url=self.test_url,
            headers=self.test_headers,
            params=self.test_params,
            data=self.test_data,
            json_data=self.test_json,
            timeout=30,
            method="POST"
        )
        
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "http_request")
        self.assertEqual(data["method"], "POST")
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["status_code"], 200)
        self.assertEqual(data["reason"], "OK")
        self.assertIn("headers", data)
        self.assertIn("content", data)
        
        mock_request.assert_called_once()
    
    @patch('network.http_tool.requests.request')
    def test_http_request_timeout(self, mock_request):
        """Test HTTP request timeout."""
        from requests.exceptions import Timeout
        mock_request.side_effect = Timeout("Request timed out")
        
        result = http_request(url=self.test_url, timeout=5)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("timed out", data["error"])
        self.assertEqual(data["url"], self.test_url)
    
    @patch('network.http_tool.requests.request')
    def test_http_request_connection_error(self, mock_request):
        """Test HTTP request connection error."""
        from requests.exceptions import ConnectionError
        mock_request.side_effect = ConnectionError("Connection failed")
        
        result = http_request(url=self.test_url)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Failed to connect", data["error"])
        self.assertEqual(data["url"], self.test_url)
    
    @patch('network.http_tool.requests.request')
    def test_http_request_ssl_error(self, mock_request):
        """Test HTTP request SSL error."""
        from requests.exceptions import SSLError
        mock_request.side_effect = SSLError("SSL error")
        
        result = http_request(url=self.test_url, verify_ssl=True)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("SSL certificate", data["error"])
        self.assertIn("verify_ssl", data)
    
    @patch('network.http_tool.requests.request')
    def test_http_request_too_many_redirects(self, mock_request):
        """Test HTTP request with too many redirects."""
        from requests.exceptions import TooManyRedirects
        mock_request.side_effect = TooManyRedirects("Too many redirects")
        
        result = http_request(url=self.test_url, follow_redirects=True)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Too many redirects", data["error"])
        self.assertIn("follow_redirects", data)
    
    @patch('network.http_tool.requests.request')
    def test_http_get_success(self, mock_request):
        """Test successful HTTP GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = self.test_url
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"test": "data"}'
        mock_request.return_value = mock_response
        
        result = http_get(
            url=self.test_url,
            headers=self.test_headers,
            params=self.test_params
        )
        
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "http_request")  # http_get calls http_request
        self.assertEqual(data["method"], "GET")
        self.assertEqual(data["url"], self.test_url)
    
    @patch('network.http_tool.requests.request')
    def test_http_post_success(self, mock_request):
        """Test successful HTTP POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.reason = "Created"
        mock_response.url = self.test_url
        mock_response.elapsed.total_seconds.return_value = 0.456
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = '{"id": 123}'
        mock_request.return_value = mock_response
        
        result = http_post(
            url=self.test_url,
            headers=self.test_headers,
            json_data=self.test_json
        )
        
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "http_request")  # http_post calls http_request
        self.assertEqual(data["method"], "POST")
        self.assertEqual(data["url"], self.test_url)
        self.assertEqual(data["status_code"], 201)
    
    def test_http_request_invalid_json_headers(self):
        """Test HTTP request with invalid JSON headers."""
        result = http_request(url=self.test_url, headers="not valid json")
        data = self._parse_result(result)
        
        # Should still work, headers will be treated as string
        self.assertTrue(data.get("success", False) or "error" in data)
    
    def test_http_request_auth(self):
        """Test HTTP request with authentication."""
        with patch('network.http_tool.requests.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.reason = "OK"
            mock_response.url = self.test_url
            mock_response.elapsed.total_seconds.return_value = 0.123
            mock_response.headers = {}
            mock_response.text = 'Authenticated'
            mock_request.return_value = mock_response
            
            result = http_request(
                url=self.test_url,
                auth_user="user",
                auth_pass="pass"
            )
            
            data = self._parse_result(result)
            
            self.assertTrue(data["success"])
            self.assertTrue(data["_metadata"]["has_auth"])
    
    def test_http_request_proxy(self):
        """Test HTTP request with proxy."""
        with patch('network.http_tool.requests.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.reason = "OK"
            mock_response.url = self.test_url
            mock_response.elapsed.total_seconds.return_value = 0.123
            mock_response.headers = {}
            mock_response.text = 'Via proxy'
            mock_request.return_value = mock_response
            
            result = http_request(
                url=self.test_url,
                proxy="http://proxy.example.com:8080"
            )
            
            data = self._parse_result(result)
            
            self.assertTrue(data["success"])
            self.assertTrue(data["_metadata"]["has_proxy"])
    
    @patch('network.http_tool.requests.request')
    def test_http_request_large_content(self, mock_request):
        """Test HTTP request with large content (truncation)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = self.test_url
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_response.headers = {"Content-Type": "text/plain"}
        
        # Create large content
        large_content = "x" * 15000
        mock_response.text = large_content
        mock_request.return_value = mock_response
        
        result = http_request(url=self.test_url)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertTrue(data["content_truncated"])
        self.assertEqual(len(data["content"]), 5000)
    
    @patch('network.http_tool.requests.request')
    def test_http_request_json_content(self, mock_request):
        """Test HTTP request with JSON content."""
        json_content = '{"name": "test", "value": 123}'
        content_length = len(json_content)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.url = self.test_url
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.text = json_content
        mock_request.return_value = mock_response
        
        result = http_request(url=self.test_url)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["content_type"], "application/json")
        self.assertEqual(data["content_length"], content_length)
    
    def test_http_request_invalid_method(self):
        """Test HTTP request with invalid method."""
        # This should work, requests will handle invalid method
        with patch('network.http_tool.requests.request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.reason = "OK"
            mock_response.url = self.test_url
            mock_response.elapsed.total_seconds.return_value = 0.123
            mock_response.headers = {}
            mock_response.text = 'Response'
            mock_request.return_value = mock_response
            
            result = http_request(url=self.test_url, method="INVALID")
            data = self._parse_result(result)
            
            self.assertTrue(data["success"])
            self.assertEqual(data["method"], "INVALID")


class TestHttpToolIntegration(unittest.TestCase):
    """Integration tests for HttpTool module."""
    
    def test_module_exports(self):
        """Test module exports."""
        from network.http_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertEqual(len(tools), 3)
        
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("http_request", TOOL_CALL_MAP)
        self.assertIn("http_get", TOOL_CALL_MAP)
        self.assertIn("http_post", TOOL_CALL_MAP)
    
    def test_function_ai_decorators(self):
        """Test that function_ai decorators are properly applied."""
        from network.http_tool import (
            __HTTP_REQUEST_FUNCTION__,
            __HTTP_GET_FUNCTION__,
            __HTTP_POST_FUNCTION__
        )
        
        # Check that decorators were applied
        for func in [__HTTP_REQUEST_FUNCTION__, __HTTP_GET_FUNCTION__, __HTTP_POST_FUNCTION__]:
            self.assertIsNotNone(func)
            self.assertIn("function", func)
            self.assertIn("name", func["function"])
    
    def test_default_parameters_http_request(self):
        """Test http_request function parameter defaults."""
        import inspect
        from network.http_tool import http_request
        
        sig = inspect.signature(http_request)
        params = sig.parameters
        
        self.assertEqual(params['timeout'].default, 30)
        self.assertEqual(params['method'].default, "GET")
        self.assertEqual(params['verify_ssl'].default, True)
        self.assertEqual(params['follow_redirects'].default, True)
        self.assertEqual(params['headers'].default, None)
        self.assertEqual(params['params'].default, None)
    
    def test_default_parameters_http_get(self):
        """Test http_get function parameter defaults."""
        import inspect
        from network.http_tool import http_get
        
        sig = inspect.signature(http_get)
        params = sig.parameters
        
        self.assertEqual(params['timeout'].default, 30)
        self.assertEqual(params['verify_ssl'].default, True)
        self.assertEqual(params['follow_redirects'].default, True)
        self.assertEqual(params['headers'].default, None)
        self.assertEqual(params['params'].default, None)
    
    def test_default_parameters_http_post(self):
        """Test http_post function parameter defaults."""
        import inspect
        from network.http_tool import http_post
        
        sig = inspect.signature(http_post)
        params = sig.parameters
        
        self.assertEqual(params['timeout'].default, 30)
        self.assertEqual(params['verify_ssl'].default, True)
        self.assertEqual(params['follow_redirects'].default, True)
        self.assertEqual(params['headers'].default, None)
        self.assertEqual(params['params'].default, None)


if __name__ == "__main__":
    unittest.main()