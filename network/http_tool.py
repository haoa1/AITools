#!/usr/bin/env python3
"""
HttpTool implementation for AITools (Claude Code compatible version).
Provides HTTP request functionality (GET, POST, generic request).
Based on network.py with simplified implementation and proper tool structure.
"""

import json
import requests
from typing import Any
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__HTTP_URL_PROPERTY__ = property_param(
    name="url",
    description="The URL to send the request to.",
    t="string",
    required=True,
)

__HTTP_HEADERS_PROPERTY__ = property_param(
    name="headers",
    description="HTTP headers as a JSON string.",
    t="string",
    required=False,
)

__HTTP_PARAMS_PROPERTY__ = property_param(
    name="params",
    description="URL query parameters as a JSON string.",
    t="string",
    required=False,
)

__HTTP_DATA_PROPERTY__ = property_param(
    name="data",
    description="Request body data as a JSON string or raw string.",
    t="string",
    required=False,
)

__HTTP_JSON_DATA_PROPERTY__ = property_param(
    name="json_data",
    description="JSON data to send in request body.",
    t="string",
    required=False,
)

__HTTP_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Request timeout in seconds (default: 30).",
    t="number",
    required=False,
)

__HTTP_METHOD_PROPERTY__ = property_param(
    name="method",
    description="HTTP method (GET, POST, PUT, DELETE, etc., default: GET).",
    t="string",
    required=False,
)

__HTTP_VERIFY_SSL_PROPERTY__ = property_param(
    name="verify_ssl",
    description="Verify SSL certificate (default: true).",
    t="boolean",
    required=False,
)

__HTTP_FOLLOW_REDIRECTS_PROPERTY__ = property_param(
    name="follow_redirects",
    description="Follow HTTP redirects (default: true).",
    t="boolean",
    required=False,
)

__HTTP_AUTH_USER_PROPERTY__ = property_param(
    name="auth_user",
    description="Username for HTTP authentication.",
    t="string",
    required=False,
)

__HTTP_AUTH_PASS_PROPERTY__ = property_param(
    name="auth_pass",
    description="Password for HTTP authentication.",
    t="string",
    required=False,
)

__HTTP_PROXY_PROPERTY__ = property_param(
    name="proxy",
    description="Proxy server URL (e.g., http://proxy.example.com:8080).",
    t="string",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITIONS
# ============================================================================

__HTTP_REQUEST_FUNCTION__ = function_ai(
    name="http_request",
    description="Send an HTTP request with configurable method, headers, and data.",
    parameters=parameters_func([
        __HTTP_URL_PROPERTY__,
        __HTTP_HEADERS_PROPERTY__,
        __HTTP_PARAMS_PROPERTY__,
        __HTTP_DATA_PROPERTY__,
        __HTTP_JSON_DATA_PROPERTY__,
        __HTTP_TIMEOUT_PROPERTY__,
        __HTTP_METHOD_PROPERTY__,
        __HTTP_VERIFY_SSL_PROPERTY__,
        __HTTP_FOLLOW_REDIRECTS_PROPERTY__,
        __HTTP_AUTH_USER_PROPERTY__,
        __HTTP_AUTH_PASS_PROPERTY__,
        __HTTP_PROXY_PROPERTY__,
    ]),
)

__HTTP_GET_FUNCTION__ = function_ai(
    name="http_get",
    description="Send an HTTP GET request.",
    parameters=parameters_func([
        __HTTP_URL_PROPERTY__,
        __HTTP_HEADERS_PROPERTY__,
        __HTTP_PARAMS_PROPERTY__,
        __HTTP_TIMEOUT_PROPERTY__,
        __HTTP_VERIFY_SSL_PROPERTY__,
        __HTTP_FOLLOW_REDIRECTS_PROPERTY__,
        __HTTP_AUTH_USER_PROPERTY__,
        __HTTP_AUTH_PASS_PROPERTY__,
        __HTTP_PROXY_PROPERTY__,
    ]),
)

__HTTP_POST_FUNCTION__ = function_ai(
    name="http_post",
    description="Send an HTTP POST request.",
    parameters=parameters_func([
        __HTTP_URL_PROPERTY__,
        __HTTP_HEADERS_PROPERTY__,
        __HTTP_PARAMS_PROPERTY__,
        __HTTP_DATA_PROPERTY__,
        __HTTP_JSON_DATA_PROPERTY__,
        __HTTP_TIMEOUT_PROPERTY__,
        __HTTP_VERIFY_SSL_PROPERTY__,
        __HTTP_FOLLOW_REDIRECTS_PROPERTY__,
        __HTTP_AUTH_USER_PROPERTY__,
        __HTTP_AUTH_PASS_PROPERTY__,
        __HTTP_PROXY_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_json_string(json_str: str, default: Any = None) -> Any:
    """
    Parse a JSON string, return default if parsing fails.
    """
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If it's not valid JSON, return as string
        return json_str

def _format_response(response: requests.Response) -> str:
    """
    Format HTTP response for display.
    """
    try:
        result = []
        result.append(f"Status Code: {response.status_code} {response.reason}")
        result.append(f"URL: {response.url}")
        result.append(f"Response Time: {response.elapsed.total_seconds():.3f}s")
        
        # Headers
        result.append("\nResponse Headers:")
        for key, value in response.headers.items():
            result.append(f"  {key}: {value}")
        
        # Try to parse response content
        content_type = response.headers.get('Content-Type', '')
        content = response.text
        
        # Truncate very large responses
        if len(content) > 10000:
            content = content[:10000] + f"\n... (truncated, total {len(content)} chars)"
        
        if 'application/json' in content_type:
            try:
                json_content = json.loads(content)
                formatted_json = json.dumps(json_content, indent=2, ensure_ascii=False)
                result.append(f"\nResponse Body (JSON):\n{formatted_json}")
            except:
                result.append(f"\nResponse Body:\n{content}")
        else:
            result.append(f"\nResponse Body:\n{content}")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error formatting response: {str(e)}"

def _format_json_response(response_data: dict) -> str:
    """
    Format response as JSON for Claude Code compatibility.
    """
    try:
        return json.dumps(response_data, indent=2)
    except:
        return json.dumps({"error": "Failed to format response as JSON"}, indent=2)

# ============================================================================
# MAIN TOOL FUNCTIONS
# ============================================================================

def http_request(
    url: str,
    headers: str = None,
    params: str = None,
    data: str = None,
    json_data: str = None,
    timeout: int = 30,
    method: str = "GET",
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    auth_user: str = None,
    auth_pass: str = None,
    proxy: str = None
) -> str:
    """
    Send an HTTP request with configurable method, headers, and data.
    
    Args:
        url: URL to send request to
        headers: HTTP headers as JSON string
        params: URL query parameters as JSON string
        data: Request body data as JSON string or raw string
        json_data: JSON data to send in request body
        timeout: Request timeout in seconds (default: 30)
        method: HTTP method (default: GET)
        verify_ssl: Verify SSL certificate (default: true)
        follow_redirects: Follow HTTP redirects (default: true)
        auth_user: Username for HTTP authentication
        auth_pass: Password for HTTP authentication
        proxy: Proxy server URL
    
    Returns:
        JSON string with HTTP response details matching Claude Code tool format.
    """
    try:
        # Parse parameters
        headers_dict = _parse_json_string(headers, {})
        params_dict = _parse_json_string(params, {})
        data_dict = _parse_json_string(data, None)
        json_dict = _parse_json_string(json_data, None)
        
        # Prepare authentication
        auth = None
        if auth_user and auth_pass:
            auth = (auth_user, auth_pass)
        
        # Prepare proxies
        proxies = None
        if proxy:
            proxies = {
                'http': proxy,
                'https': proxy
            }
        
        # Send request
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers_dict,
            params=params_dict,
            data=data_dict if data_dict and not json_dict else None,
            json=json_dict,
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=follow_redirects,
            auth=auth,
            proxies=proxies
        )
        
        # Format response in Claude Code compatible JSON
        response_data = {
            "success": True,
            "operation": "http_request",
            "method": method.upper(),
            "url": url,
            "status_code": response.status_code,
            "reason": response.reason,
            "response_time": round(response.elapsed.total_seconds(), 3),
            "response_url": response.url,
            "headers": dict(response.headers),
            "content": response.text[:5000],  # Limit content size
            "content_truncated": len(response.text) > 5000,
            "content_type": response.headers.get('Content-Type', ''),
            "content_length": len(response.text),
            "_metadata": {
                "verify_ssl": verify_ssl,
                "follow_redirects": follow_redirects,
                "has_auth": auth is not None,
                "has_proxy": proxy is not None,
                "timeout_seconds": timeout
            }
        }
        
        return _format_json_response(response_data)
        
    except requests.exceptions.Timeout:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"Request to {url} timed out after {timeout} seconds",
            "url": url,
            "method": method.upper(),
            "timeout_seconds": timeout
        })
    except requests.exceptions.SSLError:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"SSL certificate verification failed for {url}. Try verify_ssl=False",
            "url": url,
            "method": method.upper(),
            "verify_ssl": verify_ssl
        })
    except requests.exceptions.ConnectionError:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"Failed to connect to {url}",
            "url": url,
            "method": method.upper()
        })
    except requests.exceptions.TooManyRedirects:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"Too many redirects for {url}",
            "url": url,
            "method": method.upper(),
            "follow_redirects": follow_redirects
        })
    except requests.exceptions.RequestException as e:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"Request failed: {str(e)}",
            "url": url,
            "method": method.upper()
        })
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "http_request",
            "error": f"Unexpected error: {str(e)}",
            "url": url,
            "method": method.upper()
        })

def http_get(
    url: str,
    headers: str = None,
    params: str = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    auth_user: str = None,
    auth_pass: str = None,
    proxy: str = None
) -> str:
    """
    Send an HTTP GET request.
    
    Args:
        url: URL to send GET request to
        headers: HTTP headers as JSON string
        params: URL query parameters as JSON string
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Verify SSL certificate (default: true)
        follow_redirects: Follow HTTP redirects (default: true)
        auth_user: Username for HTTP authentication
        auth_pass: Password for HTTP authentication
        proxy: Proxy server URL
    
    Returns:
        JSON string with HTTP GET response details.
    """
    return http_request(
        url=url,
        headers=headers,
        params=params,
        data=None,
        json_data=None,
        timeout=timeout,
        method="GET",
        verify_ssl=verify_ssl,
        follow_redirects=follow_redirects,
        auth_user=auth_user,
        auth_pass=auth_pass,
        proxy=proxy
    )

def http_post(
    url: str,
    headers: str = None,
    params: str = None,
    data: str = None,
    json_data: str = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    auth_user: str = None,
    auth_pass: str = None,
    proxy: str = None
) -> str:
    """
    Send an HTTP POST request.
    
    Args:
        url: URL to send POST request to
        headers: HTTP headers as JSON string
        params: URL query parameters as JSON string
        data: Request body data as JSON string or raw string
        json_data: JSON data to send in request body
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Verify SSL certificate (default: true)
        follow_redirects: Follow HTTP redirects (default: true)
        auth_user: Username for HTTP authentication
        auth_pass: Password for HTTP authentication
        proxy: Proxy server URL
    
    Returns:
        JSON string with HTTP POST response details.
    """
    return http_request(
        url=url,
        headers=headers,
        params=params,
        data=data,
        json_data=json_data,
        timeout=timeout,
        method="POST",
        verify_ssl=verify_ssl,
        follow_redirects=follow_redirects,
        auth_user=auth_user,
        auth_pass=auth_pass,
        proxy=proxy
    )

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__HTTP_REQUEST_FUNCTION__, __HTTP_GET_FUNCTION__, __HTTP_POST_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "http_request": http_request,
    "http_get": http_get,
    "http_post": http_post,
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'http_request', 'http_get', 'http_post']