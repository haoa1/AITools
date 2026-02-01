from base import function_ai, parameters_func, property_param

import requests
import json
import os
import sys
import time
import socket
import urllib.parse
from typing import Dict, List, Optional, Any
import subprocess

__NETWORK_PROPERTY_ONE__ = property_param(
    name="url",
    description="The URL to send the request to.",
    t="string",
    required=True
)

__NETWORK_PROPERTY_TWO__ = property_param(
    name="headers",
    description="HTTP headers as a JSON string.",
    t="string"
)

__NETWORK_PROPERTY_THREE__ = property_param(
    name="params",
    description="URL query parameters as a JSON string.",
    t="string"
)

__NETWORK_PROPERTY_4__ = property_param(
    name="data",
    description="Request body data as a JSON string or raw string.",
    t="string"
)

__NETWORK_PROPERTY_5__ = property_param(
    name="json_data",
    description="JSON data to send in request body.",
    t="string"
)

__NETWORK_PROPERTY_6__ = property_param(
    name="timeout",
    description="Request timeout in seconds.",
    t="integer"
)

__NETWORK_PROPERTY_7__ = property_param(
    name="method",
    description="HTTP method (GET, POST, PUT, DELETE, etc.).",
    t="string"
)

__NETWORK_PROPERTY_8__ = property_param(
    name="save_path",
    description="Path to save downloaded file.",
    t="string"
)

__NETWORK_PROPERTY_9__ = property_param(
    name="host",
    description="Hostname or IP address to connect to.",
    t="string"
)

__NETWORK_PROPERTY_10__ = property_param(
    name="port",
    description="Port number to connect to.",
    t="integer"
)

__NETWORK_PROPERTY_11__ = property_param(
    name="verify_ssl",
    description="Verify SSL certificate (default: True).",
    t="boolean"
)

__NETWORK_PROPERTY_12__ = property_param(
    name="follow_redirects",
    description="Follow HTTP redirects (default: True).",
    t="boolean"
)

__NETWORK_PROPERTY_13__ = property_param(
    name="auth_user",
    description="Username for HTTP authentication.",
    t="string"
)

__NETWORK_PROPERTY_14__ = property_param(
    name="auth_pass",
    description="Password for HTTP authentication.",
    t="string"
)

__NETWORK_PROPERTY_15__ = property_param(
    name="proxy",
    description="Proxy server URL (e.g., http://proxy.example.com:8080).",
    t="string"
)

__NETWORK_PROPERTY_16__ = property_param(
    name="stream",
    description="Stream response content (for large files).",
    t="boolean"
)

__NETWORK_HTTP_REQUEST_FUNCTION__ = function_ai(name="http_request",
                                               description="Send an HTTP request with configurable method, headers, and data.",
                                               parameters=parameters_func([__NETWORK_PROPERTY_ONE__, __NETWORK_PROPERTY_TWO__, __NETWORK_PROPERTY_THREE__, __NETWORK_PROPERTY_4__, __NETWORK_PROPERTY_5__, __NETWORK_PROPERTY_6__, __NETWORK_PROPERTY_7__, __NETWORK_PROPERTY_11__, __NETWORK_PROPERTY_12__, __NETWORK_PROPERTY_13__, __NETWORK_PROPERTY_14__, __NETWORK_PROPERTY_15__]))

__NETWORK_GET_FUNCTION__ = function_ai(name="http_get",
                                      description="Send an HTTP GET request.",
                                      parameters=parameters_func([__NETWORK_PROPERTY_ONE__, __NETWORK_PROPERTY_TWO__, __NETWORK_PROPERTY_THREE__, __NETWORK_PROPERTY_6__, __NETWORK_PROPERTY_11__, __NETWORK_PROPERTY_12__, __NETWORK_PROPERTY_13__, __NETWORK_PROPERTY_14__, __NETWORK_PROPERTY_15__]))

__NETWORK_POST_FUNCTION__ = function_ai(name="http_post",
                                       description="Send an HTTP POST request.",
                                       parameters=parameters_func([__NETWORK_PROPERTY_ONE__, __NETWORK_PROPERTY_TWO__, __NETWORK_PROPERTY_THREE__, __NETWORK_PROPERTY_4__, __NETWORK_PROPERTY_5__, __NETWORK_PROPERTY_6__, __NETWORK_PROPERTY_11__, __NETWORK_PROPERTY_12__, __NETWORK_PROPERTY_13__, __NETWORK_PROPERTY_14__, __NETWORK_PROPERTY_15__]))

__NETWORK_DOWNLOAD_FILE_FUNCTION__ = function_ai(name="download_file",
                                                description="Download a file from a URL.",
                                                parameters=parameters_func([__NETWORK_PROPERTY_ONE__, __NETWORK_PROPERTY_8__, __NETWORK_PROPERTY_TWO__, __NETWORK_PROPERTY_6__, __NETWORK_PROPERTY_11__, __NETWORK_PROPERTY_12__, __NETWORK_PROPERTY_13__, __NETWORK_PROPERTY_14__, __NETWORK_PROPERTY_15__, __NETWORK_PROPERTY_16__]))

__NETWORK_CHECK_CONNECTIVITY_FUNCTION__ = function_ai(name="check_connectivity",
                                                     description="Check network connectivity to a host and port.",
                                                     parameters=parameters_func([__NETWORK_PROPERTY_9__, __NETWORK_PROPERTY_10__, __NETWORK_PROPERTY_6__]))

__NETWORK_DNS_LOOKUP_FUNCTION__ = function_ai(name="dns_lookup",
                                             description="Perform DNS lookup for a hostname.",
                                             parameters=parameters_func([__NETWORK_PROPERTY_9__]))

__NETWORK_PING_FUNCTION__ = function_ai(name="ping_host",
                                       description="Ping a host to check connectivity.",
                                       parameters=parameters_func([__NETWORK_PROPERTY_9__, __NETWORK_PROPERTY_6__]))

__NETWORK_WHOIS_FUNCTION__ = function_ai(name="whois_lookup",
                                        description="Perform WHOIS lookup for a domain.",
                                        parameters=parameters_func([__NETWORK_PROPERTY_9__]))

__NETWORK_SSL_CHECK_FUNCTION__ = function_ai(name="check_ssl_certificate",
                                            description="Check SSL certificate information for a URL.",
                                            parameters=parameters_func([__NETWORK_PROPERTY_ONE__, __NETWORK_PROPERTY_6__]))

tools = [
    __NETWORK_HTTP_REQUEST_FUNCTION__,
    __NETWORK_GET_FUNCTION__,
    __NETWORK_POST_FUNCTION__,
    __NETWORK_DOWNLOAD_FILE_FUNCTION__,
    __NETWORK_CHECK_CONNECTIVITY_FUNCTION__,
    __NETWORK_DNS_LOOKUP_FUNCTION__,
    __NETWORK_PING_FUNCTION__,
    __NETWORK_WHOIS_FUNCTION__,
    __NETWORK_SSL_CHECK_FUNCTION__,
]

def _parse_json_string(json_str: str, default: Any = None) -> Any:
    """Parse a JSON string, return default if parsing fails."""
    if not json_str:
        return default
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If it's not valid JSON, return as string
        return json_str

def _format_response(response: requests.Response) -> str:
    """Format HTTP response for display."""
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

def http_request(url: str, headers: str = None, params: str = None, data: str = None, 
                 json_data: str = None, timeout: int = 30, method: str = "GET",
                 verify_ssl: bool = True, follow_redirects: bool = True,
                 auth_user: str = None, auth_pass: str = None, proxy: str = None) -> str:
    '''
    Send an HTTP request with configurable method, headers, and data.
    
    :param url: URL to send request to
    :type url: str
    :param headers: HTTP headers as JSON string
    :type headers: str
    :param params: URL query parameters as JSON string
    :type params: str
    :param data: Request body data as JSON string or raw string
    :type data: str
    :param json_data: JSON data to send in request body
    :type json_data: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
    :type method: str
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param follow_redirects: Follow HTTP redirects
    :type follow_redirects: bool
    :param auth_user: Username for HTTP authentication
    :type auth_user: str
    :param auth_pass: Password for HTTP authentication
    :type auth_pass: str
    :param proxy: Proxy server URL
    :type proxy: str
    :return: HTTP response details or error message
    :rtype: str
    '''
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
        
        return _format_response(response)
        
    except requests.exceptions.Timeout:
        return f"Error: Request to {url} timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Failed to connect to {url}"
    except requests.exceptions.SSLError:
        return f"Error: SSL certificate verification failed for {url}. Try verify_ssl=False"
    except requests.exceptions.TooManyRedirects:
        return f"Error: Too many redirects for {url}"
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error: {str(e)}"

def http_get(url: str, headers: str = None, params: str = None, timeout: int = 30,
             verify_ssl: bool = True, follow_redirects: bool = True,
             auth_user: str = None, auth_pass: str = None, proxy: str = None) -> str:
    '''
    Send an HTTP GET request.
    
    :param url: URL to send GET request to
    :type url: str
    :param headers: HTTP headers as JSON string
    :type headers: str
    :param params: URL query parameters as JSON string
    :type params: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param follow_redirects: Follow HTTP redirects
    :type follow_redirects: bool
    :param auth_user: Username for HTTP authentication
    :type auth_user: str
    :param auth_pass: Password for HTTP authentication
    :type auth_pass: str
    :param proxy: Proxy server URL
    :type proxy: str
    :return: HTTP response details or error message
    :rtype: str
    '''
    return http_request(url, headers, params, None, None, timeout, "GET", 
                       verify_ssl, follow_redirects, auth_user, auth_pass, proxy)

def http_post(url: str, headers: str = None, params: str = None, data: str = None, 
              json_data: str = None, timeout: int = 30, verify_ssl: bool = True, 
              follow_redirects: bool = True, auth_user: str = None, auth_pass: str = None, 
              proxy: str = None) -> str:
    '''
    Send an HTTP POST request.
    
    :param url: URL to send POST request to
    :type url: str
    :param headers: HTTP headers as JSON string
    :type headers: str
    :param params: URL query parameters as JSON string
    :type params: str
    :param data: Request body data as JSON string or raw string
    :type data: str
    :param json_data: JSON data to send in request body
    :type json_data: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param follow_redirects: Follow HTTP redirects
    :type follow_redirects: bool
    :param auth_user: Username for HTTP authentication
    :type auth_user: str
    :param auth_pass: Password for HTTP authentication
    :type auth_pass: str
    :param proxy: Proxy server URL
    :type proxy: str
    :return: HTTP response details or error message
    :rtype: str
    '''
    return http_request(url, headers, params, data, json_data, timeout, "POST",
                       verify_ssl, follow_redirects, auth_user, auth_pass, proxy)

def download_file(url: str, save_path: str = None, headers: str = None, timeout: int = 30,
                  verify_ssl: bool = True, follow_redirects: bool = True,
                  auth_user: str = None, auth_pass: str = None, proxy: str = None,
                  stream: bool = True) -> str:
    '''
    Download a file from a URL.
    
    :param url: URL to download file from
    :type url: str
    :param save_path: Path to save downloaded file (default: filename from URL or response)
    :type save_path: str
    :param headers: HTTP headers as JSON string
    :type headers: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :param verify_ssl: Verify SSL certificate
    :type verify_ssl: bool
    :param follow_redirects: Follow HTTP redirects
    :type follow_redirects: bool
    :param auth_user: Username for HTTP authentication
    :type auth_user: str
    :param auth_pass: Password for HTTP authentication
    :type auth_pass: str
    :param proxy: Proxy server URL
    :type proxy: str
    :param stream: Stream response content (for large files)
    :type stream: bool
    :return: Download status message
    :rtype: str
    '''
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
            # Extract filename from URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = f"download_{int(time.time())}.bin"
            save_path = filename
        
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
        
        # Download with progress
        downloaded = 0
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
        
        # Verify download
        actual_size = os.path.getsize(save_path)
        
        result = []
        result.append(f"Successfully downloaded file from {url}")
        result.append(f"Saved to: {save_path}")
        result.append(f"File size: {actual_size} bytes")
        result.append(f"Status Code: {response.status_code}")
        
        if total_size > 0 and actual_size != total_size:
            result.append(f"Warning: Expected {total_size} bytes, got {actual_size} bytes")
        
        return "\n".join(result)
        
    except requests.exceptions.Timeout:
        return f"Error: Download from {url} timed out after {timeout} seconds"
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP error downloading file: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed: {str(e)}"
    except IOError as e:
        return f"Error: File I/O error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error: {str(e)}"

def check_connectivity(host: str, port: int = 80, timeout: int = 10) -> str:
    '''
    Check network connectivity to a host and port.
    
    :param host: Hostname or IP address to connect to
    :type host: str
    :param port: Port number to connect to
    :type port: int
    :param timeout: Connection timeout in seconds
    :type timeout: int
    :return: Connectivity status message
    :rtype: str
    '''
    try:
        start_time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        result = sock.connect_ex((host, port))
        elapsed = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            return f"Successfully connected to {host}:{port} in {elapsed:.3f} seconds"
        else:
            return f"Failed to connect to {host}:{port} (error code: {result})"
            
    except socket.gaierror as e:
        return f"Error: Hostname resolution failed for {host}: {str(e)}"
    except socket.timeout:
        return f"Error: Connection to {host}:{port} timed out after {timeout} seconds"
    except socket.error as e:
        return f"Error: Socket error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error: {str(e)}"

def dns_lookup(hostname: str) -> str:
    '''
    Perform DNS lookup for a hostname.
    
    :param hostname: Hostname to look up
    :type hostname: str
    :return: DNS lookup results
    :rtype: str
    '''
    try:
        result = []
        
        # Get IP addresses
        try:
            addresses = socket.getaddrinfo(hostname, None)
            ips = set()
            for addr in addresses:
                ip = addr[4][0]
                ips.add(ip)
            
            result.append(f"DNS Lookup for: {hostname}")
            result.append(f"IP Addresses: {', '.join(sorted(ips))}")
        except socket.gaierror as e:
            result.append(f"Error resolving {hostname}: {str(e)}")
        
        # Get canonical name
        try:
            canonical_name = socket.getfqdn(hostname)
            if canonical_name != hostname:
                result.append(f"Canonical Name: {canonical_name}")
        except:
            pass
        
        # Try reverse DNS for first IP
        if 'IP Addresses' in result[1]:
            try:
                first_ip = list(ips)[0] if ips else None
                if first_ip:
                    reverse_dns = socket.gethostbyaddr(first_ip)[0]
                    result.append(f"Reverse DNS for {first_ip}: {reverse_dns}")
            except:
                pass
        
        return "\n".join(result) if result else f"No DNS information found for {hostname}"
        
    except Exception as e:
        return f"Error performing DNS lookup: {str(e)}"

def ping_host(host: str, timeout: int = 10) -> str:
    '''
    Ping a host to check connectivity.
    
    :param host: Hostname or IP address to ping
    :type host: str
    :param timeout: Ping timeout in seconds
    :type timeout: int
    :return: Ping results
    :rtype: str
    '''
    try:
        # Check if ping command is available
        try:
            subprocess.run(['ping', '-c', '1', '-W', '1', '127.0.0.1'], 
                          capture_output=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Error: ping command not available on this system"
        
        # Execute ping
        cmd = ['ping', '-c', '3', '-W', str(timeout), host]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        
        if process.returncode == 0:
            # Parse ping output
            output = process.stdout
            lines = output.split('\n')
            
            result = []
            result.append(f"Ping results for {host}:")
            
            # Extract summary line
            for line in lines:
                if 'packets transmitted' in line:
                    result.append(f"  {line.strip()}")
                elif 'min/avg/max' in line:
                    result.append(f"  {line.strip()}")
            
            if len(result) == 1:  # Only header line
                result.append("  Ping successful but could not parse output")
                result.append(f"  Raw output: {output[:200]}...")
            
            return "\n".join(result)
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            return f"Ping to {host} failed: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return f"Error: Ping to {host} timed out after {timeout} seconds"
    except Exception as e:
        return f"Error: Unexpected error pinging host: {str(e)}"

def whois_lookup(domain: str) -> str:
    '''
    Perform WHOIS lookup for a domain.
    
    :param domain: Domain name to look up
    :type domain: str
    :return: WHOIS information
    :rtype: str
    '''
    try:
        # Check if whois command is available
        try:
            subprocess.run(['whois', 'example.com'], capture_output=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Error: whois command not available on this system"
        
        # Execute whois
        cmd = ['whois', domain]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if process.returncode == 0:
            output = process.stdout.strip()
            if output:
                # Limit output length
                if len(output) > 5000:
                    output = output[:5000] + "\n... (truncated, output too long)"
                return f"WHOIS information for {domain}:\n\n{output}"
            else:
                return f"No WHOIS information found for {domain}"
        else:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            return f"WHOIS lookup failed for {domain}: {error_msg}"
            
    except subprocess.TimeoutExpired:
        return f"Error: WHOIS lookup for {domain} timed out"
    except Exception as e:
        return f"Error: Unexpected error performing WHOIS lookup: {str(e)}"

def check_ssl_certificate(url: str, timeout: int = 10) -> str:
    '''
    Check SSL certificate information for a URL.
    
    :param url: URL to check SSL certificate for
    :type url: str
    :param timeout: Request timeout in seconds
    :type timeout: int
    :return: SSL certificate information
    :rtype: str
    '''
    try:
        import ssl
        from urllib.parse import urlparse
        
        # Parse URL
        parsed = urlparse(url)
        if not parsed.scheme:
            parsed = urlparse(f"https://{url}")
        
        hostname = parsed.hostname
        port = parsed.port or 443
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Get certificate info
                result = []
                result.append(f"SSL Certificate Information for {hostname}:")
                result.append("=" * 60)
                
                # Subject
                subject = dict(x[0] for x in cert.get('subject', []))
                result.append("Subject:")
                for key, value in subject.items():
                    result.append(f"  {key}: {value}")
                
                # Issuer
                issuer = dict(x[0] for x in cert.get('issuer', []))
                result.append("\nIssuer:")
                for key, value in issuer.items():
                    result.append(f"  {key}: {value}")
                
                # Validity
                not_before = cert.get('notBefore', 'Unknown')
                not_after = cert.get('notAfter', 'Unknown')
                result.append(f"\nValid From: {not_before}")
                result.append(f"Valid Until: {not_after}")
                
                # Check if certificate is valid
                from datetime import datetime
                try:
                    now = datetime.utcnow()
                    format_str = '%b %d %H:%M:%S %Y GMT'
                    valid_from = datetime.strptime(not_before, format_str)
                    valid_to = datetime.strptime(not_after, format_str)
                    
                    if now < valid_from:
                        result.append(f"Status: Certificate not yet valid (starts in {(valid_from - now).days} days)")
                    elif now > valid_to:
                        result.append(f"Status: Certificate EXPIRED {(now - valid_to).days} days ago!")
                    else:
                        days_left = (valid_to - now).days
                        result.append(f"Status: Certificate is valid ({days_left} days remaining)")
                except:
                    result.append("Status: Could not parse certificate dates")
                
                # Certificate version and serial
                result.append(f"\nVersion: {cert.get('version', 'Unknown')}")
                result.append(f"Serial Number: {cert.get('serialNumber', 'Unknown')}")
                
                return "\n".join(result)
                
    except ssl.SSLError as e:
        return f"SSL Error for {url}: {str(e)}"
    except socket.timeout:
        return f"Error: Connection to {url} timed out after {timeout} seconds"
    except socket.gaierror as e:
        return f"Error: Could not resolve hostname {url}: {str(e)}"
    except ConnectionRefusedError:
        return f"Error: Connection refused to {url}"
    except Exception as e:
        return f"Error checking SSL certificate: {str(e)}"

TOOL_CALL_MAP = {
    "http_request": http_request,
    "http_get": http_get,
    "http_post": http_post,
    "download_file": download_file,
    "check_connectivity": check_connectivity,
    "dns_lookup": dns_lookup,
    "ping_host": ping_host,
    "whois_lookup": whois_lookup,
    "check_ssl_certificate": check_ssl_certificate,
}