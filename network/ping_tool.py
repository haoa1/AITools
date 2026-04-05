#!/usr/bin/env python3
"""
PingTool implementation for AITools (Claude Code compatible version).
Provides network ping functionality to check host connectivity.
Based on network.py with simplified implementation and proper tool structure.
"""

import json
import socket
import subprocess
import time
from typing import Any
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__PING_HOST_PROPERTY__ = property_param(
    name="host",
    description="Hostname or IP address to ping.",
    t="string",
    required=True,
)

__PING_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Ping timeout in seconds (default: 10).",
    t="number",
    required=False,
)

__PING_COUNT_PROPERTY__ = property_param(
    name="count",
    description="Number of ping packets to send (default: 3).",
    t="number",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__PING_HOST_FUNCTION__ = function_ai(
    name="ping_host",
    description="Ping a host to check connectivity.",
    parameters=parameters_func([
        __PING_HOST_PROPERTY__,
        __PING_TIMEOUT_PROPERTY__,
        __PING_COUNT_PROPERTY__,
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

def _parse_ping_output(output: str) -> dict:
    """
    Parse ping command output to extract statistics.
    """
    result = {
        "packets_transmitted": 0,
        "packets_received": 0,
        "packet_loss_percent": 100.0,
        "min_rtt_ms": 0.0,
        "avg_rtt_ms": 0.0,
        "max_rtt_ms": 0.0,
        "raw_output": output[:1000]  # Limit raw output size
    }
    
    lines = output.split('\n')
    
    # Parse statistics line
    for line in lines:
        line = line.strip()
        
        # Packet statistics: "3 packets transmitted, 3 received, 0% packet loss"
        if 'packets transmitted' in line:
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if 'packets transmitted' in part:
                    result["packets_transmitted"] = int(part.split()[0])
                elif 'received' in part:
                    result["packets_received"] = int(part.split()[0])
                elif 'packet loss' in part:
                    try:
                        loss_percent = float(part.split('%')[0])
                        result["packet_loss_percent"] = loss_percent
                    except:
                        pass
        
        # RTT statistics: "rtt min/avg/max/mdev = 10.123/20.456/30.789/5.123 ms"
        elif 'min/avg/max' in line or 'rtt min/avg/max' in line:
            try:
                # Extract the numbers part
                if '=' in line:
                    numbers_part = line.split('=')[1].strip()
                else:
                    numbers_part = line
                
                # Parse the four numbers (min/avg/max/mdev)
                numbers = numbers_part.split()[0].split('/')
                if len(numbers) >= 3:
                    result["min_rtt_ms"] = float(numbers[0])
                    result["avg_rtt_ms"] = float(numbers[1])
                    result["max_rtt_ms"] = float(numbers[2])
            except:
                pass
    
    return result

def _check_ping_availability() -> tuple:
    """
    Check if ping command is available on the system.
    """
    try:
        # Test ping command availability by pinging localhost
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '1', '127.0.0.1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True, ""
    except FileNotFoundError:
        return False, "ping command not found on this system"
    except subprocess.CalledProcessError:
        return False, "ping command returned an error"
    except Exception as e:
        return False, f"Error checking ping availability: {str(e)}"

def _ping_with_socket(host: str, timeout: int) -> dict:
    """
    Fallback ping implementation using sockets when system ping is not available.
    """
    try:
        start_time = time.time()
        
        # Try to resolve hostname first
        try:
            ip_address = socket.gethostbyname(host)
        except socket.gaierror:
            return {
                "success": False,
                "error": f"Could not resolve hostname: {host}",
                "connectivity": False
            }
        
        # Try to connect to port 80 (HTTP) to check connectivity
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            result = sock.connect_ex((ip_address, 80))
            elapsed = time.time() - start_time
            connectivity = (result == 0)
            
            return {
                "success": True,
                "connectivity": connectivity,
                "ip_address": ip_address,
                "response_time_ms": round(elapsed * 1000, 2),
                "method": "socket_connect"
            }
        finally:
            sock.close()
            
    except socket.timeout:
        return {
            "success": False,
            "error": f"Connection to {host} timed out",
            "connectivity": False,
            "method": "socket_connect"
        }
    except socket.error as e:
        return {
            "success": False,
            "error": f"Socket error: {str(e)}",
            "connectivity": False,
            "method": "socket_connect"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "connectivity": False,
            "method": "socket_connect"
        }

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def ping_host(
    host: str,
    timeout: int = 10,
    count: int = 3
) -> str:
    """
    Ping a host to check connectivity.
    
    Args:
        host: Hostname or IP address to ping
        timeout: Ping timeout in seconds (default: 10)
        count: Number of ping packets to send (default: 3)
    
    Returns:
        JSON string with ping results matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not host or not isinstance(host, str):
            return _format_json_response({
                "success": False,
                "operation": "ping_host",
                "error": "Host must be a non-empty string",
                "host": host
            })
        
        if timeout <= 0:
            return _format_json_response({
                "success": False,
                "operation": "ping_host",
                "error": f"Timeout must be positive, got: {timeout}",
                "host": host,
                "timeout_seconds": timeout
            })
        
        if count <= 0:
            return _format_json_response({
                "success": False,
                "operation": "ping_host",
                "error": f"Count must be positive, got: {count}",
                "host": host,
                "count": count
            })
        
        # Check if system ping is available
        ping_available, ping_error = _check_ping_availability()
        
        if ping_available:
            # Use system ping command
            try:
                # Execute ping command
                cmd = ['ping', '-c', str(count), '-W', str(timeout), host]
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout + 5
                )
                
                if process.returncode == 0:
                    # Parse successful ping output
                    ping_stats = _parse_ping_output(process.stdout)
                    
                    response_data = {
                        "success": True,
                        "operation": "ping_host",
                        "host": host,
                        "connectivity": True,
                        "method": "system_ping",
                        "packets_transmitted": ping_stats["packets_transmitted"],
                        "packets_received": ping_stats["packets_received"],
                        "packet_loss_percent": ping_stats["packet_loss_percent"],
                        "min_rtt_ms": ping_stats["min_rtt_ms"],
                        "avg_rtt_ms": ping_stats["avg_rtt_ms"],
                        "max_rtt_ms": ping_stats["max_rtt_ms"],
                        "raw_output": ping_stats["raw_output"],
                        "_metadata": {
                            "timeout_seconds": timeout,
                            "ping_count": count,
                            "system_ping_available": True
                        }
                    }
                    
                    return _format_json_response(response_data)
                else:
                    # Ping failed
                    error_output = process.stderr.strip() if process.stderr else "Unknown error"
                    
                    response_data = {
                        "success": True,  # Still successful operation, just no connectivity
                        "operation": "ping_host",
                        "host": host,
                        "connectivity": False,
                        "method": "system_ping",
                        "error_message": error_output,
                        "_metadata": {
                            "timeout_seconds": timeout,
                            "ping_count": count,
                            "system_ping_available": True,
                            "exit_code": process.returncode
                        }
                    }
                    
                    return _format_json_response(response_data)
                    
            except subprocess.TimeoutExpired:
                return _format_json_response({
                    "success": False,
                    "operation": "ping_host",
                    "error": f"Ping to {host} timed out after {timeout} seconds",
                    "host": host,
                    "timeout_seconds": timeout,
                    "method": "system_ping"
                })
            except Exception as e:
                return _format_json_response({
                    "success": False,
                    "operation": "ping_host",
                    "error": f"Ping command failed: {str(e)}",
                    "host": host,
                    "method": "system_ping"
                })
        else:
            # Fallback to socket-based ping
            socket_result = _ping_with_socket(host, timeout)
            
            if socket_result.get("success", False):
                response_data = {
                    "success": True,
                    "operation": "ping_host",
                    "host": host,
                    "connectivity": socket_result["connectivity"],
                    "method": "socket_connect",
                    "ip_address": socket_result.get("ip_address"),
                    "response_time_ms": socket_result.get("response_time_ms", 0),
                    "system_ping_error": ping_error,
                    "_metadata": {
                        "timeout_seconds": timeout,
                        "ping_count": count,
                        "system_ping_available": False,
                        "fallback_method_used": True
                    }
                }
                
                if not socket_result["connectivity"] and "error" in socket_result:
                    response_data["error_message"] = socket_result["error"]
                
                return _format_json_response(response_data)
            else:
                return _format_json_response({
                    "success": False,
                    "operation": "ping_host",
                    "error": socket_result.get("error", "Unknown socket error"),
                    "host": host,
                    "connectivity": False,
                    "method": "socket_connect",
                    "system_ping_error": ping_error,
                    "_metadata": {
                        "system_ping_available": False,
                        "fallback_method_used": True
                    }
                })
                
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "ping_host",
            "error": f"Unexpected error: {str(e)}",
            "host": host,
            "timeout_seconds": timeout,
            "count": count
        })

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__PING_HOST_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "ping_host": ping_host,
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'ping_host']