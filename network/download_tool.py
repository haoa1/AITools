#!/usr/bin/env python3
"""
DownloadTool implementation for AITools (Claude Code compatible version).
Provides file download functionality from URLs.
Based on network.py with simplified implementation and proper tool structure.
"""

import os
import json
import time
import urllib.parse
import requests
from typing import Any
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__DOWNLOAD_URL_PROPERTY__ = property_param(
    name="url",
    description="The URL to download file from.",
    t="string",
    required=True,
)

__DOWNLOAD_SAVE_PATH_PROPERTY__ = property_param(
    name="save_path",
    description="Path to save downloaded file (default: filename from URL).",
    t="string",
    required=False,
)

__DOWNLOAD_HEADERS_PROPERTY__ = property_param(
    name="headers",
    description="HTTP headers as a JSON string.",
    t="string",
    required=False,
)

__DOWNLOAD_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Request timeout in seconds (default: 30).",
    t="number",
    required=False,
)

__DOWNLOAD_VERIFY_SSL_PROPERTY__ = property_param(
    name="verify_ssl",
    description="Verify SSL certificate (default: true).",
    t="boolean",
    required=False,
)

__DOWNLOAD_FOLLOW_REDIRECTS_PROPERTY__ = property_param(
    name="follow_redirects",
    description="Follow HTTP redirects (default: true).",
    t="boolean",
    required=False,
)

__DOWNLOAD_AUTH_USER_PROPERTY__ = property_param(
    name="auth_user",
    description="Username for HTTP authentication.",
    t="string",
    required=False,
)

__DOWNLOAD_AUTH_PASS_PROPERTY__ = property_param(
    name="auth_pass",
    description="Password for HTTP authentication.",
    t="string",
    required=False,
)

__DOWNLOAD_PROXY_PROPERTY__ = property_param(
    name="proxy",
    description="Proxy server URL (e.g., http://proxy.example.com:8080).",
    t="string",
    required=False,
)

__DOWNLOAD_STREAM_PROPERTY__ = property_param(
    name="stream",
    description="Stream response content for large files (default: true).",
    t="boolean",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__DOWNLOAD_FILE_FUNCTION__ = function_ai(
    name="download_file",
    description="Download a file from a URL.",
    parameters=parameters_func([
        __DOWNLOAD_URL_PROPERTY__,
        __DOWNLOAD_SAVE_PATH_PROPERTY__,
        __DOWNLOAD_HEADERS_PROPERTY__,
        __DOWNLOAD_TIMEOUT_PROPERTY__,
        __DOWNLOAD_VERIFY_SSL_PROPERTY__,
        __DOWNLOAD_FOLLOW_REDIRECTS_PROPERTY__,
        __DOWNLOAD_AUTH_USER_PROPERTY__,
        __DOWNLOAD_AUTH_PASS_PROPERTY__,
        __DOWNLOAD_PROXY_PROPERTY__,
        __DOWNLOAD_STREAM_PROPERTY__,
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

def _format_json_response(response_data: dict) -> str:
    """
    Format response as JSON for Claude Code compatibility.
    """
    try:
        return json.dumps(response_data, indent=2)
    except:
        return json.dumps({"error": "Failed to format response as JSON"}, indent=2)

def _get_filename_from_url(url: str) -> str:
    """
    Extract filename from URL.
    """
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)
    if not filename:
        # If no filename in path, use timestamp
        filename = f"download_{int(time.time())}.bin"
    
    # Remove query parameters from filename
    if '?' in filename:
        filename = filename.split('?')[0]
    
    return filename

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def download_file(
    url: str,
    save_path: str = None,
    headers: str = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    follow_redirects: bool = True,
    auth_user: str = None,
    auth_pass: str = None,
    proxy: str = None,
    stream: bool = True
) -> str:
    """
    Download a file from a URL.
    
    Args:
        url: URL to download file from
        save_path: Path to save downloaded file (default: filename from URL)
        headers: HTTP headers as JSON string
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Verify SSL certificate (default: true)
        follow_redirects: Follow HTTP redirects (default: true)
        auth_user: Username for HTTP authentication
        auth_pass: Password for HTTP authentication
        proxy: Proxy server URL
        stream: Stream response content for large files (default: true)
    
    Returns:
        JSON string with download status and details matching Claude Code tool format.
    """
    try:
        # Parse headers
        headers_dict = _parse_json_string(headers, {})
        
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
        
        # Determine save path
        if not save_path:
            save_path = _get_filename_from_url(url)
        
        # Ensure directory exists
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        
        # Download file
        response = requests.get(
            url,
            headers=headers_dict,
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=follow_redirects,
            auth=auth,
            proxies=proxies,
            stream=stream
        )
        response.raise_for_status()
        
        # Get file size from headers
        total_size = int(response.headers.get('Content-Length', 0))
        
        # Download with progress tracking
        downloaded = 0
        start_time = time.time()
        
        with open(save_path, 'wb') as f:
            if stream:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            else:
                content = response.content
                f.write(content)
                downloaded = len(content)
        
        elapsed_time = time.time() - start_time
        
        # Verify download
        actual_size = os.path.getsize(save_path)
        
        # Calculate download speed
        speed_kbps = 0
        if elapsed_time > 0:
            speed_kbps = (actual_size / 1024) / elapsed_time
        
        # Build response data
        response_data = {
            "success": True,
            "operation": "download_file",
            "url": url,
            "save_path": os.path.abspath(save_path),
            "file_size_bytes": actual_size,
            "expected_size_bytes": total_size if total_size > 0 else None,
            "download_success": True,
            "size_match": total_size == 0 or actual_size == total_size,
            "download_speed_kbps": round(speed_kbps, 2),
            "download_time_seconds": round(elapsed_time, 3),
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', ''),
            "headers": dict(response.headers),
            "_metadata": {
                "verify_ssl": verify_ssl,
                "follow_redirects": follow_redirects,
                "has_auth": auth is not None,
                "has_proxy": proxy is not None,
                "stream_enabled": stream,
                "timeout_seconds": timeout
            }
        }
        
        # Add warnings if size mismatch
        if total_size > 0 and actual_size != total_size:
            response_data["warning"] = f"Expected {total_size} bytes, got {actual_size} bytes"
            response_data["size_difference_bytes"] = actual_size - total_size
        
        return _format_json_response(response_data)
        
    except requests.exceptions.Timeout:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"Download from {url} timed out after {timeout} seconds",
            "url": url,
            "save_path": save_path,
            "timeout_seconds": timeout
        })
    except requests.exceptions.HTTPError as e:
        status_code = None
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"HTTP error downloading file: {str(e)}",
            "url": url,
            "save_path": save_path,
            "status_code": status_code
        })
    except requests.exceptions.SSLError:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"SSL certificate verification failed for {url}. Try verify_ssl=False",
            "url": url,
            "save_path": save_path,
            "verify_ssl": verify_ssl
        })
    except requests.exceptions.ConnectionError:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"Failed to connect to {url}",
            "url": url,
            "save_path": save_path
        })
    except IOError as e:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"File I/O error: {str(e)}",
            "url": url,
            "save_path": save_path
        })
    except requests.exceptions.RequestException as e:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"Request failed: {str(e)}",
            "url": url,
            "save_path": save_path
        })
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "download_file",
            "error": f"Unexpected error: {str(e)}",
            "url": url,
            "save_path": save_path
        })

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__DOWNLOAD_FILE_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "download_file": download_file,
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'download_file']