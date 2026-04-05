#!/usr/bin/env python3
"""
Tests for NetworkDiagnosticTool (Claude Code compatible version).
"""

import os
import sys
import json
import socket
import ssl
import subprocess
import unittest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network.network_diagnostic_tool import (
    check_connectivity, 
    dns_lookup, 
    whois_lookup, 
    check_ssl_certificate,
    _extract_domain_from_host,
    _format_json_response
)


class TestNetworkDiagnosticToolHelpers(unittest.TestCase):
    """Test helper functions for NetworkDiagnosticTool."""
    
    def test_extract_domain_from_host_with_www(self):
        """Test extracting domain from hostname with www prefix."""
        result = _extract_domain_from_host("www.example.com")
        self.assertEqual(result, "example.com")
    
    def test_extract_domain_from_host_without_www(self):
        """Test extracting domain from hostname without www prefix."""
        result = _extract_domain_from_host("example.com")
        self.assertEqual(result, "example.com")
    
    def test_extract_domain_from_host_empty(self):
        """Test extracting domain from empty hostname."""
        result = _extract_domain_from_host("")
        self.assertEqual(result, "")
    
    def test_format_json_response_success(self):
        """Test formatting JSON response."""
        data = {"test": "data", "number": 123}
        result = _format_json_response(data)
        
        parsed = json.loads(result)
        self.assertEqual(parsed, data)
    
    def test_format_json_response_error(self):
        """Test formatting JSON response with non-serializable data.
        
        Note: This test might fail if the function handles errors gracefully.
        """
        # Create data with circular reference (non-serializable)
        class Circular:
            def __init__(self):
                self.self = self
        
        data = {"circular": Circular()}
        result = _format_json_response(data)
        
        # Should return error JSON
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("Failed to format", parsed["error"])


class TestCheckConnectivityFunction(unittest.TestCase):
    """Test check_connectivity function."""
    
    def _parse_result(self, result_str):
        """Helper to parse JSON result string."""
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON: {result_str}")
    
    def test_invalid_host_empty(self):
        """Test connectivity check with empty host."""
        result = check_connectivity("")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Host must be a non-empty string", data["error"])
    
    def test_invalid_port_too_low(self):
        """Test connectivity check with port too low."""
        result = check_connectivity("example.com", port=0)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Port must be between 1 and 65535", data["error"])
    
    def test_invalid_port_too_high(self):
        """Test connectivity check with port too high."""
        result = check_connectivity("example.com", port=65536)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Port must be between 1 and 65535", data["error"])
    
    def test_invalid_timeout(self):
        """Test connectivity check with invalid timeout."""
        result = check_connectivity("example.com", timeout=0)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Timeout must be positive", data["error"])
    
    @patch('network.network_diagnostic_tool.socket.socket')
    def test_successful_connection(self, mock_socket_class):
        """Test successful connectivity check."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 0
        mock_socket_class.return_value = mock_socket
        
        result = check_connectivity("example.com", port=80, timeout=5)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "check_connectivity")
        self.assertEqual(data["host"], "example.com")
        self.assertEqual(data["port"], 80)
        self.assertTrue(data["connectivity"])
        self.assertIsNone(data.get("error_code"))
        self.assertIsNone(data.get("error_message"))
        self.assertIn("connection_time_ms", data)
        
        metadata = data.get("_metadata", {})
        self.assertEqual(metadata.get("timeout_seconds"), 5)
        self.assertEqual(metadata.get("protocol"), "TCP")
        self.assertIn("test_timestamp", metadata)
        
        mock_socket.connect_ex.assert_called_once_with(("example.com", 80))
        mock_socket.close.assert_called_once()
    
    @patch('network.network_diagnostic_tool.socket.socket')
    def test_failed_connection(self, mock_socket_class):
        """Test failed connectivity check."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.return_value = 61  # Connection refused
        mock_socket_class.return_value = mock_socket
        
        result = check_connectivity("example.com", port=8080, timeout=5)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])  # Operation succeeded
        self.assertFalse(data["connectivity"])  # But connection failed
        self.assertEqual(data["error_code"], 61)
        self.assertIn("Connection failed with error code", data["error_message"])
    
    @patch('network.network_diagnostic_tool.socket.socket')
    def test_socket_gaierror(self, mock_socket_class):
        """Test connectivity check with hostname resolution failure."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.gaierror("Name or service not known")
        mock_socket_class.return_value = mock_socket
        
        result = check_connectivity("invalid.host", port=80, timeout=5)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Hostname resolution failed", data["error"])
    
    @patch('network.network_diagnostic_tool.socket.socket')
    def test_socket_timeout(self, mock_socket_class):
        """Test connectivity check with socket timeout."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.timeout()
        mock_socket_class.return_value = mock_socket
        
        result = check_connectivity("slow.host", port=80, timeout=2)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("timed out", data["error"])
    
    @patch('network.network_diagnostic_tool.socket.socket')
    def test_socket_generic_error(self, mock_socket_class):
        """Test connectivity check with generic socket error."""
        mock_socket = MagicMock()
        mock_socket.connect_ex.side_effect = socket.error("Generic socket error")
        mock_socket_class.return_value = mock_socket
        
        result = check_connectivity("error.host", port=80, timeout=5)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Socket error", data["error"])


class TestDnsLookupFunction(unittest.TestCase):
    """Test dns_lookup function."""
    
    def _parse_result(self, result_str):
        """Helper to parse JSON result string."""
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON: {result_str}")
    
    def test_invalid_hostname_empty(self):
        """Test DNS lookup with empty hostname."""
        result = dns_lookup("")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Hostname must be a non-empty string", data["error"])
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_successful_dns_lookup(self, mock_getaddrinfo):
        """Test successful DNS lookup."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.35', 0)),
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2606:2800:220:1:248:1893:25c8:1946', 0, 0, 0)),
        ]
        
        result = dns_lookup("example.com")
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "dns_lookup")
        self.assertEqual(data["hostname"], "example.com")
        
        # Check IP addresses - all in one list
        self.assertIn("ip_addresses", data)
        ip_addresses = data["ip_addresses"]
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertIn("93.184.216.34", ip_addresses)
        self.assertIn("93.184.216.35", ip_addresses)
        self.assertIn("2606:2800:220:1:248:1893:25c8:1946", ip_addresses)
        
        metadata = data.get("_metadata", {})
        self.assertIn("lookup_timestamp", metadata)
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_dns_lookup_ipv4_only(self, mock_getaddrinfo):
        """Test DNS lookup with IPv4 addresses only."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.1', 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.0.2.2', 0)),
        ]
        
        result = dns_lookup("ipv4-only.example.com")
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertIn("ip_addresses", data)
        ip_addresses = data["ip_addresses"]
        self.assertEqual(len(ip_addresses), 2)
        self.assertIn("192.0.2.1", ip_addresses)
        self.assertIn("192.0.2.2", ip_addresses)
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_dns_lookup_ipv6_only(self, mock_getaddrinfo):
        """Test DNS lookup with IPv6 addresses only."""
        mock_getaddrinfo.return_value = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2001:db8::1', 0, 0, 0)),
        ]
        
        result = dns_lookup("ipv6-only.example.com")
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertIn("ip_addresses", data)
        ip_addresses = data["ip_addresses"]
        self.assertEqual(len(ip_addresses), 1)
        self.assertIn("2001:db8::1", ip_addresses)
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_dns_lookup_no_addresses(self, mock_getaddrinfo):
        """Test DNS lookup with no addresses returned."""
        mock_getaddrinfo.return_value = []
        
        result = dns_lookup("no-address.example.com")
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])  # Operation succeeded
        self.assertIn("ip_addresses", data)
        self.assertEqual(len(data["ip_addresses"]), 0)
        # Note: actual implementation doesn't have "status" field
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_dns_lookup_resolution_failure(self, mock_getaddrinfo):
        """Test DNS lookup with resolution failure."""
        mock_getaddrinfo.side_effect = socket.gaierror("Name or service not known")
        
        result = dns_lookup("invalid.hostname")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("DNS resolution failed", data["error"])
    
    @patch('network.network_diagnostic_tool.socket.getaddrinfo')
    def test_dns_lookup_socket_error(self, mock_getaddrinfo):
        """Test DNS lookup with socket error."""
        mock_getaddrinfo.side_effect = socket.error("Generic socket error")
        
        result = dns_lookup("error.hostname")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Unexpected error:", data["error"])
        self.assertIn("Generic socket error", data["error"])


class TestWhoisLookupFunction(unittest.TestCase):
    """Test whois_lookup function."""
    
    def _parse_result(self, result_str):
        """Helper to parse JSON result string."""
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON: {result_str}")
    
    def test_invalid_domain_empty(self):
        """Test WHOIS lookup with empty domain."""
        result = whois_lookup("")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Domain must be a non-empty string", data["error"])
    
    @patch('network.network_diagnostic_tool.subprocess.run')
    def test_whois_command_not_available(self, mock_run):
        """Test WHOIS lookup when whois command is not available."""
        mock_run.side_effect = FileNotFoundError("whois: command not found")
        
        result = whois_lookup("example.com")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("whois command not available", data["error"])
    
    @patch('network.network_diagnostic_tool.subprocess.run')
    def test_successful_whois_lookup(self, mock_run):
        """Test successful WHOIS lookup."""
        # Mock whois availability check
        mock_process_check = MagicMock()
        mock_process_check.returncode = 0
        
        # Mock actual whois lookup
        mock_process_whois = MagicMock()
        mock_process_whois.returncode = 0
        mock_process_whois.stdout = """Domain Name: EXAMPLE.COM
Registry Domain ID: 2336799_DOMAIN_COM-VRSN
Registrar WHOIS Server: whois.iana.org
Registrar URL: http://example.com
Updated Date: 2023-08-14T07:01:31Z
Creation Date: 1995-08-14T04:00:00Z
Registry Expiry Date: 2024-08-13T04:00:00Z
Registrar: Example Registrar
Registrar IANA ID: 1234
Registrar Abuse Contact Email: abuse@example.com
"""
        
        mock_run.side_effect = [mock_process_check, mock_process_whois]
        
        result = whois_lookup("example.com")
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "whois_lookup")
        self.assertEqual(data["domain"], "example.com")
        self.assertTrue(data.get("whois_available", False))
        
        self.assertIn("output_preview", data)
        self.assertIn("Domain Name: EXAMPLE.COM", data["output_preview"])
        self.assertIn("raw_output_length", data)
        self.assertIn("parsed_fields", data)
        
        metadata = data.get("_metadata", {})
        self.assertTrue(metadata.get("whois_command_available", False))
        self.assertIn("lookup_timestamp", metadata)
    
    @patch('network.network_diagnostic_tool.subprocess.run')
    def test_whois_lookup_with_www_prefix(self, mock_run):
        """Test WHOIS lookup with www prefix."""
        mock_process_check = MagicMock()
        mock_process_check.returncode = 0
        
        mock_process_whois = MagicMock()
        mock_process_whois.returncode = 0
        mock_process_whois.stdout = "Domain information"
        
        mock_run.side_effect = [mock_process_check, mock_process_whois]
        
        result = whois_lookup("www.example.com")
        data = self._parse_result(result)
        
        self.assertEqual(data["domain"], "example.com")
    
    @patch('network.network_diagnostic_tool.subprocess.run')
    def test_whois_lookup_error(self, mock_run):
        """Test WHOIS lookup with command error."""
        mock_process_check = MagicMock()
        mock_process_check.returncode = 0
        
        mock_process_whois = MagicMock()
        mock_process_whois.returncode = 1
        mock_process_whois.stderr = "WHOIS query failed"
        
        mock_run.side_effect = [mock_process_check, mock_process_whois]
        
        result = whois_lookup("example.com")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("WHOIS lookup failed", data["error"])
        self.assertIn("WHOIS query failed", data["error"])
    
    @patch('network.network_diagnostic_tool.subprocess.run')
    def test_whois_lookup_timeout(self, mock_run):
        """Test WHOIS lookup with timeout."""
        mock_process_check = MagicMock()
        mock_process_check.returncode = 0
        
        mock_run.side_effect = [mock_process_check, subprocess.TimeoutExpired(cmd=["whois"], timeout=30)]
        
        result = whois_lookup("example.com")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("timed out", data["error"])


class TestCheckSslCertificateFunction(unittest.TestCase):
    """Test check_ssl_certificate function."""
    
    def _parse_result(self, result_str):
        """Helper to parse JSON result string."""
        try:
            return json.loads(result_str)
        except json.JSONDecodeError:
            self.fail(f"Failed to parse JSON: {result_str}")
    
    def test_invalid_url_empty(self):
        """Test SSL certificate check with empty URL."""
        result = check_ssl_certificate("")
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("URL must be a non-empty string", data["error"])
    
    def test_invalid_timeout(self):
        """Test SSL certificate check with invalid timeout."""
        result = check_ssl_certificate("https://example.com", timeout=0)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Timeout must be positive", data["error"])
    
    @patch('network.network_diagnostic_tool.ssl.create_default_context')
    @patch('network.network_diagnostic_tool.socket.create_connection')
    def test_successful_ssl_check(self, mock_create_connection, mock_create_context):
        """Test successful SSL certificate check."""
        # Mock socket
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        # Mock SSL context and socket
        mock_context = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket
        
        # Mock certificate
        mock_cert = {
            'subject': ((('commonName', 'example.com'),),),
            'issuer': ((('organizationName', 'Example CA'),),),
            'notBefore': '20230101000000Z',
            'notAfter': '20241231235959Z',
            'serialNumber': '1234567890',
            'version': 3
        }
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_create_context.return_value = mock_context
        
        result = check_ssl_certificate("https://example.com", timeout=10)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["operation"], "check_ssl_certificate")
        self.assertEqual(data["url"], "https://example.com")
        self.assertEqual(data["hostname"], "example.com")
        self.assertEqual(data["port"], 443)
        self.assertTrue(data["ssl_enabled"])
        self.assertFalse(data.get("certificate_expired", True))
        
        cert_info = data.get("certificate_info", {})
        self.assertEqual(cert_info.get("common_name"), "example.com")
        self.assertEqual(cert_info.get("issuer"), "Example CA")
        self.assertIn("valid_from", cert_info)
        self.assertIn("valid_to", cert_info)
        self.assertEqual(cert_info.get("serial_number"), "1234567890")
        
        metadata = data.get("_metadata", {})
        self.assertEqual(metadata.get("timeout_seconds"), 10)
        self.assertIn("check_timestamp", metadata)
        
        mock_create_connection.assert_called_once_with(("example.com", 443), timeout=10)
        mock_context.wrap_socket.assert_called_once()
    
    @patch('network.network_diagnostic_tool.ssl.create_default_context')
    @patch('network.network_diagnostic_tool.socket.create_connection')
    def test_ssl_check_http_url(self, mock_create_connection, mock_create_context):
        """Test SSL certificate check with HTTP URL (should attempt HTTPS)."""
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_context = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket
        mock_ssl_socket.getpeercert.return_value = {'subject': ((('commonName', 'example.com'),),)}
        mock_create_context.return_value = mock_context
        
        result = check_ssl_certificate("http://example.com", timeout=10)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])
        self.assertEqual(data["url"], "http://example.com")
        self.assertEqual(data["hostname"], "example.com")
        self.assertEqual(data["port"], 443)  # Should use HTTPS port
    
    @patch('network.network_diagnostic_tool.socket.create_connection')
    def test_ssl_check_connection_failed(self, mock_create_connection):
        """Test SSL certificate check with connection failure."""
        mock_create_connection.side_effect = ConnectionRefusedError("Connection refused")
        
        result = check_ssl_certificate("https://unreachable.example.com", timeout=5)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("Connection refused", data["error"])
    
    @patch('network.network_diagnostic_tool.ssl.create_default_context')
    @patch('network.network_diagnostic_tool.socket.create_connection')
    def test_ssl_check_ssl_error(self, mock_create_connection, mock_create_context):
        """Test SSL certificate check with SSL error."""
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_context = MagicMock()
        mock_context.wrap_socket.side_effect = ssl.SSLError("SSL handshake failed")
        mock_create_context.return_value = mock_context
        
        result = check_ssl_certificate("https://invalid-ssl.example.com", timeout=10)
        data = self._parse_result(result)
        
        self.assertFalse(data["success"])
        self.assertIn("SSL error", data["error"])
    
    @patch('network.network_diagnostic_tool.ssl.create_default_context')
    @patch('network.network_diagnostic_tool.socket.create_connection')
    def test_ssl_check_certificate_expired(self, mock_create_connection, mock_create_context):
        """Test SSL certificate check with expired certificate."""
        mock_socket = MagicMock()
        mock_create_connection.return_value = mock_socket
        
        mock_context = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket
        
        # Mock expired certificate (past date)
        mock_cert = {
            'subject': ((('commonName', 'expired.example.com'),),),
            'issuer': ((('organizationName', 'Expired CA'),),),
            'notBefore': '20220101000000Z',
            'notAfter': '20221231235959Z',  # Expired in 2022
            'serialNumber': '9876543210',
            'version': 3
        }
        mock_ssl_socket.getpeercert.return_value = mock_cert
        mock_create_context.return_value = mock_context
        
        result = check_ssl_certificate("https://expired.example.com", timeout=10)
        data = self._parse_result(result)
        
        self.assertTrue(data["success"])  # Operation succeeded
        self.assertTrue(data.get("certificate_expired", False))  # But certificate is expired
        self.assertIn("expired", data.get("certificate_status", ""))


if __name__ == '__main__':
    unittest.main()