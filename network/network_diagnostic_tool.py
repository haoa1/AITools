#!/usr/bin/env python3
"""
NetworkDiagnosticTool implementation for AITools (Claude Code compatible version).
Provides various network diagnostic functions: connectivity check, DNS lookup, 
WHOIS lookup, SSL certificate check.
Based on network.py with simplified implementation and proper tool structure.
"""

import json
import socket
import ssl
import subprocess
import time
import urllib.parse
from datetime import datetime
from typing import Any, List, Set
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS (for individual functions)
# ============================================================================

__HOST_PROPERTY__ = property_param(
    name="host",
    description="Hostname or IP address.",
    t="string",
    required=True,
)

__PORT_PROPERTY__ = property_param(
    name="port",
    description="Port number to connect to (default: 80).",
    t="number",
    required=False,
)

__TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Connection timeout in seconds (default: 10).",
    t="number",
    required=False,
)

__URL_PROPERTY__ = property_param(
    name="url",
    description="URL to check.",
    t="string",
    required=True,
)

# ============================================================================
# TOOL FUNCTION DEFINITIONS
# ============================================================================

__CHECK_CONNECTIVITY_FUNCTION__ = function_ai(
    name="check_connectivity",
    description="Check network connectivity to a host and port.",
    parameters=parameters_func([
        __HOST_PROPERTY__,
        __PORT_PROPERTY__,
        __TIMEOUT_PROPERTY__,
    ]),
)

__DNS_LOOKUP_FUNCTION__ = function_ai(
    name="dns_lookup",
    description="Perform DNS lookup for a hostname.",
    parameters=parameters_func([
        __HOST_PROPERTY__,
    ]),
)

__WHOIS_LOOKUP_FUNCTION__ = function_ai(
    name="whois_lookup",
    description="Perform WHOIS lookup for a domain.",
    parameters=parameters_func([
        __HOST_PROPERTY__,
    ]),
)

__SSL_CHECK_FUNCTION__ = function_ai(
    name="check_ssl_certificate",
    description="Check SSL certificate information for a URL.",
    parameters=parameters_func([
        __URL_PROPERTY__,
        __TIMEOUT_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_json_response(response_data: dict) -> str:
    """
    Format response as JSON for Claude Code compatibility.
    """
    try:
        return json.dumps(response_data, indent=2)
    except:
        return json.dumps({"error": "Failed to format response as JSON"}, indent=2)

def _extract_domain_from_host(host: str) -> str:
    """
    Extract domain from hostname (remove www. prefix if present).
    """
    if host.startswith('www.'):
        return host[4:]
    return host

# ============================================================================
# MAIN TOOL FUNCTIONS
# ============================================================================

def check_connectivity(
    host: str,
    port: int = 80,
    timeout: int = 10
) -> str:
    """
    Check network connectivity to a host and port.
    
    Args:
        host: Hostname or IP address to connect to
        port: Port number to connect to (default: 80)
        timeout: Connection timeout in seconds (default: 10)
    
    Returns:
        JSON string with connectivity results matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not host or not isinstance(host, str):
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": "Host must be a non-empty string",
                "host": host,
                "port": port
            })
        
        if port <= 0 or port > 65535:
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": f"Port must be between 1 and 65535, got: {port}",
                "host": host,
                "port": port
            })
        
        if timeout <= 0:
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": f"Timeout must be positive, got: {timeout}",
                "host": host,
                "port": port,
                "timeout_seconds": timeout
            })
        
        # Perform connectivity check
        start_time = time.time()
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((host, port))
            elapsed = time.time() - start_time
            
            sock.close()
            
            connectivity = (result == 0)
            
            response_data = {
                "success": True,
                "operation": "check_connectivity",
                "host": host,
                "port": port,
                "connectivity": connectivity,
                "connection_time_ms": round(elapsed * 1000, 2),
                "error_code": result if not connectivity else None,
                "error_message": f"Connection failed with error code: {result}" if not connectivity else None,
                "_metadata": {
                    "timeout_seconds": timeout,
                    "protocol": "TCP",
                    "test_timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
            
            return _format_json_response(response_data)
            
        except socket.gaierror as e:
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": f"Hostname resolution failed for {host}: {str(e)}",
                "host": host,
                "port": port,
                "connectivity": False,
                "_metadata": {
                    "error_type": "dns_resolution_failed"
                }
            })
        except socket.timeout:
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": f"Connection to {host}:{port} timed out after {timeout} seconds",
                "host": host,
                "port": port,
                "connectivity": False,
                "_metadata": {
                    "error_type": "connection_timeout",
                    "timeout_seconds": timeout
                }
            })
        except socket.error as e:
            return _format_json_response({
                "success": False,
                "operation": "check_connectivity",
                "error": f"Socket error: {str(e)}",
                "host": host,
                "port": port,
                "connectivity": False,
                "_metadata": {
                    "error_type": "socket_error"
                }
            })
            
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "check_connectivity",
            "error": f"Unexpected error: {str(e)}",
            "host": host,
            "port": port,
            "timeout_seconds": timeout
        })

def dns_lookup(
    hostname: str
) -> str:
    """
    Perform DNS lookup for a hostname.
    
    Args:
        hostname: Hostname to look up
    
    Returns:
        JSON string with DNS lookup results matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not hostname or not isinstance(hostname, str):
            return _format_json_response({
                "success": False,
                "operation": "dns_lookup",
                "error": "Hostname must be a non-empty string",
                "hostname": hostname
            })
        
        # Perform DNS lookup
        try:
            # Get IP addresses
            addresses = socket.getaddrinfo(hostname, None)
            ips: Set[str] = set()
            
            for addr in addresses:
                ip = addr[4][0]
                if ip:
                    ips.add(ip)
            
            # Get canonical name
            canonical_name = socket.getfqdn(hostname)
            
            # Prepare response data
            response_data = {
                "success": True,
                "operation": "dns_lookup",
                "hostname": hostname,
                "ip_addresses": list(sorted(ips)) if ips else [],
                "canonical_name": canonical_name if canonical_name != hostname else None,
                "reverse_dns": {},
                "_metadata": {
                    "address_family": "all",
                    "lookup_timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }
            
            # Try reverse DNS for first IP
            if ips:
                first_ip = sorted(ips)[0]
                try:
                    reverse_dns = socket.gethostbyaddr(first_ip)[0]
                    response_data["reverse_dns"][first_ip] = reverse_dns
                except:
                    pass
            
            return _format_json_response(response_data)
            
        except socket.gaierror as e:
            return _format_json_response({
                "success": False,
                "operation": "dns_lookup",
                "error": f"DNS resolution failed for {hostname}: {str(e)}",
                "hostname": hostname,
                "ip_addresses": [],
                "_metadata": {
                    "error_type": "dns_resolution_failed"
                }
            })
            
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "dns_lookup",
            "error": f"Unexpected error: {str(e)}",
            "hostname": hostname
        })

def whois_lookup(
    domain: str
) -> str:
    """
    Perform WHOIS lookup for a domain.
    
    Args:
        domain: Domain name to look up
    
    Returns:
        JSON string with WHOIS information matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not domain or not isinstance(domain, str):
            return _format_json_response({
                "success": False,
                "operation": "whois_lookup",
                "error": "Domain must be a non-empty string",
                "domain": domain
            })
        
        # Clean domain name
        clean_domain = domain.strip().lower()
        clean_domain = _extract_domain_from_host(clean_domain)
        
        # Check if whois command is available
        try:
            # Test whois command
            subprocess.run(
                ['whois', 'example.com'],
                capture_output=True,
                timeout=5
            )
            whois_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            whois_available = False
        
        if not whois_available:
            return _format_json_response({
                "success": False,
                "operation": "whois_lookup",
                "error": "whois command not available on this system",
                "domain": clean_domain,
                "_metadata": {
                    "whois_command_available": False
                }
            })
        
        # Execute whois lookup
        try:
            cmd = ['whois', clean_domain]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                output = process.stdout.strip()
                
                # Parse common WHOIS fields
                whois_data = {
                    "raw_output": output[:5000],  # Limit output size
                    "truncated": len(output) > 5000,
                    "parsed_fields": {}
                }
                
                # Try to extract common fields
                lines = output.split('\n')
                for line in lines:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        # Common WHOIS fields to extract
                        common_fields = [
                            'domain name', 'registrar', 'creation date',
                            'expiry date', 'updated date', 'name server',
                            'registrant', 'admin', 'tech', 'status'
                        ]
                        
                        for field in common_fields:
                            if field in key:
                                if field not in whois_data["parsed_fields"]:
                                    whois_data["parsed_fields"][field] = []
                                whois_data["parsed_fields"][field].append(value)
                
                response_data = {
                    "success": True,
                    "operation": "whois_lookup",
                    "domain": clean_domain,
                    "whois_available": True,
                    "raw_output_length": len(output),
                    "parsed_fields": whois_data["parsed_fields"],
                    "output_preview": whois_data["raw_output"],
                    "_metadata": {
                        "whois_command_available": True,
                        "lookup_timestamp": datetime.utcnow().isoformat() + "Z",
                        "exit_code": process.returncode
                    }
                }
                
                return _format_json_response(response_data)
            else:
                error_msg = process.stderr.strip() if process.stderr else "Unknown error"
                return _format_json_response({
                    "success": False,
                    "operation": "whois_lookup",
                    "error": f"WHOIS lookup failed: {error_msg}",
                    "domain": clean_domain,
                    "_metadata": {
                        "whois_command_available": True,
                        "exit_code": process.returncode
                    }
                })
                
        except subprocess.TimeoutExpired:
            return _format_json_response({
                "success": False,
                "operation": "whois_lookup",
                "error": f"WHOIS lookup for {clean_domain} timed out",
                "domain": clean_domain,
                "_metadata": {
                    "whois_command_available": True,
                    "timeout_seconds": 30
                }
            })
            
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "whois_lookup",
            "error": f"Unexpected error: {str(e)}",
            "domain": domain
        })

def check_ssl_certificate(
    url: str,
    timeout: int = 10
) -> str:
    """
    Check SSL certificate information for a URL.
    
    Args:
        url: URL to check SSL certificate for
        timeout: Connection timeout in seconds (default: 10)
    
    Returns:
        JSON string with SSL certificate information matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not url or not isinstance(url, str):
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": "URL must be a non-empty string",
                "url": url
            })
        
        if timeout <= 0:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"Timeout must be positive, got: {timeout}",
                "url": url,
                "timeout_seconds": timeout
            })
        
        # Parse URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme:
            parsed = urllib.parse.urlparse(f"https://{url}")
        
        hostname = parsed.hostname
        if not hostname:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"Could not extract hostname from URL: {url}",
                "url": url
            })
        
        port = parsed.port or 443
        
        # Check SSL certificate
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse certificate information
                    cert_info = {
                        "subject": {},
                        "issuer": {},
                        "validity": {},
                        "status": "unknown",
                        "details": {}
                    }
                    
                    # Subject
                    subject = dict(x[0] for x in cert.get('subject', []))
                    cert_info["subject"] = subject
                    
                    # Issuer
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    cert_info["issuer"] = issuer
                    
                    # Validity dates
                    not_before = cert.get('notBefore', 'Unknown')
                    not_after = cert.get('notAfter', 'Unknown')
                    
                    cert_info["validity"] = {
                        "not_before": not_before,
                        "not_after": not_after
                    }
                    
                    # Check validity
                    try:
                        now = datetime.utcnow()
                        format_str = '%b %d %H:%M:%S %Y GMT'
                        valid_from = datetime.strptime(not_before, format_str)
                        valid_to = datetime.strptime(not_after, format_str)
                        
                        if now < valid_from:
                            days_until = (valid_from - now).days
                            cert_info["status"] = "not_yet_valid"
                            cert_info["days_until_valid"] = days_until
                        elif now > valid_to:
                            days_expired = (now - valid_to).days
                            cert_info["status"] = "expired"
                            cert_info["days_expired"] = days_expired
                        else:
                            days_remaining = (valid_to - now).days
                            cert_info["status"] = "valid"
                            cert_info["days_remaining"] = days_remaining
                    except:
                        cert_info["status"] = "date_parse_error"
                    
                    # Additional details
                    cert_info["details"] = {
                        "version": cert.get('version', 'Unknown'),
                        "serial_number": cert.get('serialNumber', 'Unknown'),
                        "signature_algorithm": cert.get('signatureAlgorithm', {}).get('algorithm', 'Unknown'),
                        "extensions": list(cert.get('subjectAltName', [])),
                        "has_subject_alt_name": 'subjectAltName' in cert
                    }
                    
                    response_data = {
                        "success": True,
                        "operation": "check_ssl_certificate",
                        "url": url,
                        "hostname": hostname,
                        "port": port,
                        "certificate_info": cert_info,
                        "connectivity": True,
                        "_metadata": {
                            "timeout_seconds": timeout,
                            "check_timestamp": datetime.utcnow().isoformat() + "Z",
                            "protocol": "TLS"
                        }
                    }
                    
                    return _format_json_response(response_data)
                    
        except ssl.SSLError as e:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"SSL Error for {url}: {str(e)}",
                "url": url,
                "hostname": hostname,
                "connectivity": False,
                "_metadata": {
                    "error_type": "ssl_error"
                }
            })
        except socket.timeout:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"Connection to {url} timed out after {timeout} seconds",
                "url": url,
                "hostname": hostname,
                "connectivity": False,
                "_metadata": {
                    "error_type": "connection_timeout",
                    "timeout_seconds": timeout
                }
            })
        except socket.gaierror as e:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"Could not resolve hostname {hostname}: {str(e)}",
                "url": url,
                "hostname": hostname,
                "connectivity": False,
                "_metadata": {
                    "error_type": "dns_resolution_failed"
                }
            })
        except ConnectionRefusedError:
            return _format_json_response({
                "success": False,
                "operation": "check_ssl_certificate",
                "error": f"Connection refused to {hostname}:{port}",
                "url": url,
                "hostname": hostname,
                "port": port,
                "connectivity": False,
                "_metadata": {
                    "error_type": "connection_refused"
                }
            })
            
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "check_ssl_certificate",
            "error": f"Unexpected error: {str(e)}",
            "url": url,
            "timeout_seconds": timeout
        })

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [
    __CHECK_CONNECTIVITY_FUNCTION__,
    __DNS_LOOKUP_FUNCTION__,
    __WHOIS_LOOKUP_FUNCTION__,
    __SSL_CHECK_FUNCTION__,
]

# Tool call map
TOOL_CALL_MAP = {
    "check_connectivity": check_connectivity,
    "dns_lookup": dns_lookup,
    "whois_lookup": whois_lookup,
    "check_ssl_certificate": check_ssl_certificate,
}

__all__ = [
    'tools', 'TOOL_CALL_MAP',
    'check_connectivity', 'dns_lookup', 'whois_lookup', 'check_ssl_certificate'
]