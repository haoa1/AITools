#!/usr/bin/env python3
"""
SystemInfoTool implementation for AITools (Claude Code compatible version).
Provides system information collection: CPU, memory, disk, system, network.
Simplified implementation focusing on cross-platform compatibility.
"""

import os
import sys
import json
import platform
import socket
import time
import subprocess
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__SYSINFO_DETAIL_PROPERTY__ = property_param(
    name="detail_level",
    description="Level of detail: 'basic' (default), 'detailed', 'full'.",
    t="string",
    required=False,
)

__SYSINFO_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Timeout in seconds for gathering system information (default: 10).",
    t="number",
    required=False,
)

__SYSINFO_INCLUDE_PROPERTY__ = property_param(
    name="include",
    description="Specific information to include: 'cpu', 'memory', 'disk', 'system', 'network', 'all' (default).",
    t="string",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__SYSINFO_FUNCTION__ = function_ai(
    name="get_system_info",
    description="Get comprehensive system information including CPU, memory, disk, system, and network details.",
    parameters=parameters_func([
        __SYSINFO_DETAIL_PROPERTY__,
        __SYSINFO_TIMEOUT_PROPERTY__,
        __SYSINFO_INCLUDE_PROPERTY__,
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

def _get_cpu_info() -> Dict[str, Any]:
    """
    Get CPU information.
    """
    cpu_info = {
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cores_physical": os.cpu_count() or 1,
        "cores_logical": os.cpu_count() or 1,
    }
    
    # Try to get more detailed CPU info
    try:
        if platform.system() == "Linux":
            # Read CPU info from /proc/cpuinfo on Linux
            with open('/proc/cpuinfo', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip().startswith('model name'):
                        cpu_info["model"] = line.split(':')[1].strip()
                        break
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                cpu_info["model"] = result.stdout.strip()
    except:
        pass
    
    # Try to get CPU usage (simplified)
    try:
        if platform.system() == "Linux":
            # Read CPU stats from /proc/stat
            with open('/proc/stat', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('cpu '):
                        parts = line.split()
                        total = sum(int(x) for x in parts[1:])
                        idle = int(parts[4]) + int(parts[5])  # idle + iowait
                        if total > 0:
                            cpu_info["usage_percent"] = round(100 * (total - idle) / total, 1)
                        break
    except:
        pass
    
    return cpu_info

def _get_memory_info() -> Dict[str, Any]:
    """
    Get memory information.
    """
    memory_info = {}
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        memory_info = {
            "total_bytes": mem.total,
            "available_bytes": mem.available,
            "used_bytes": mem.used,
            "usage_percent": mem.percent,
            "free_bytes": mem.free,
        }
    except ImportError:
        # Fallback without psutil
        try:
            if platform.system() == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    mem_data = {}
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            mem_data[key.strip()] = value.strip()
                    
                    # Convert to bytes (values are in kB)
                    if 'MemTotal' in mem_data:
                        total_kb = int(mem_data['MemTotal'].split()[0])
                        memory_info["total_bytes"] = total_kb * 1024
                    
                    if 'MemAvailable' in mem_data:
                        avail_kb = int(mem_data['MemAvailable'].split()[0])
                        memory_info["available_bytes"] = avail_kb * 1024
                        memory_info["used_bytes"] = memory_info["total_bytes"] - memory_info["available_bytes"]
                        memory_info["usage_percent"] = round(100 * memory_info["used_bytes"] / memory_info["total_bytes"], 1)
                    
                    if 'MemFree' in mem_data:
                        free_kb = int(mem_data['MemFree'].split()[0])
                        memory_info["free_bytes"] = free_kb * 1024
            
            elif platform.system() == "Darwin":  # macOS
                # Use vm_stat command
                result = subprocess.run(['vm_stat'], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse vm_stat output (simplified)
                    lines = result.stdout.split('\n')
                    page_size = 4096  # Default page size on macOS
                    
                    for line in lines:
                        if 'Pages free' in line:
                            try:
                                free_pages = int(line.split(':')[1].strip().rstrip('.'))
                                memory_info["free_bytes"] = free_pages * page_size
                            except:
                                pass
        except:
            pass
    
    # Ensure all fields exist
    for key in ["total_bytes", "available_bytes", "used_bytes", "usage_percent", "free_bytes"]:
        if key not in memory_info:
            memory_info[key] = 0
    
    return memory_info

def _get_disk_info() -> Dict[str, Any]:
    """
    Get disk information.
    """
    disk_info = {}
    
    try:
        import psutil
        partitions = psutil.disk_partitions()
        disk_usage = []
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_usage.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_bytes": usage.total,
                    "used_bytes": usage.used,
                    "free_bytes": usage.free,
                    "usage_percent": usage.percent,
                })
            except:
                continue
        
        disk_info["partitions"] = disk_usage
        
        # Get overall disk usage for current directory
        try:
            current_usage = psutil.disk_usage('.')
            disk_info["current"] = {
                "total_bytes": current_usage.total,
                "used_bytes": current_usage.used,
                "free_bytes": current_usage.free,
                "usage_percent": current_usage.percent,
            }
        except:
            pass
            
    except ImportError:
        # Fallback without psutil
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['df', '-B1', '--output=source,target,fstype,size,used,avail,pcent'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        disk_usage = []
                        for line in lines[1:]:  # Skip header
                            parts = line.strip().split()
                            if len(parts) >= 7:
                                try:
                                    disk_usage.append({
                                        "device": parts[0],
                                        "mountpoint": parts[1],
                                        "fstype": parts[2],
                                        "total_bytes": int(parts[3]),
                                        "used_bytes": int(parts[4]),
                                        "free_bytes": int(parts[5]),
                                        "usage_percent": float(parts[6].rstrip('%')),
                                    })
                                except:
                                    continue
                        
                        disk_info["partitions"] = disk_usage
            
            # Get current directory usage
            try:
                if hasattr(shutil, 'disk_usage'):
                    usage = shutil.disk_usage('.')
                    disk_info["current"] = {
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "usage_percent": round(100 * usage.used / usage.total, 1) if usage.total > 0 else 0,
                    }
            except:
                pass
                
        except:
            pass
    
    return disk_info

def _get_system_info() -> Dict[str, Any]:
    """
    Get general system information.
    """
    system_info = {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    # Get system uptime if available
    try:
        if platform.system() == "Linux":
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                system_info["uptime_seconds"] = uptime_seconds
                system_info["uptime_days"] = round(uptime_seconds / 86400, 2)
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(['sysctl', '-n', 'kern.boottime'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Parse boottime (format: { sec = 1234567890, usec = 123456 })
                import re
                match = re.search(r'sec\s*=\s*(\d+)', result.stdout)
                if match:
                    boottime = int(match.group(1))
                    uptime_seconds = time.time() - boottime
                    system_info["uptime_seconds"] = uptime_seconds
                    system_info["uptime_days"] = round(uptime_seconds / 86400, 2)
    except:
        pass
    
    # Get current user
    try:
        import getpass
        system_info["user"] = getpass.getuser()
    except:
        pass
    
    return system_info

def _get_network_info() -> Dict[str, Any]:
    """
    Get network information.
    """
    network_info = {}
    
    try:
        import psutil
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        interfaces = {}
        for interface_name, addresses in net_if_addrs.items():
            interface_data = {
                "addresses": [],
                "status": "down",
            }
            
            # Get interface status
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                interface_data["status"] = "up" if stats.isup else "down"
                interface_data["speed_mbps"] = stats.speed
                interface_data["mtu"] = stats.mtu
            
            # Get addresses
            for addr in addresses:
                addr_data = {
                    "family": "IPv4" if addr.family == socket.AF_INET else 
                             "IPv6" if addr.family == socket.AF_INET6 else 
                             "MAC" if addr.family == psutil.AF_LINK else "unknown",
                    "address": addr.address,
                    "netmask": addr.netmask if hasattr(addr, 'netmask') else None,
                    "broadcast": addr.broadcast if hasattr(addr, 'broadcast') else None,
                }
                interface_data["addresses"].append(addr_data)
            
            interfaces[interface_name] = interface_data
        
        network_info["interfaces"] = interfaces
        
        # Get default gateway
        try:
            import netifaces
            gateways = netifaces.gateways()
            network_info["gateways"] = gateways
        except:
            pass
            
    except ImportError:
        # Fallback without psutil
        try:
            # Get hostname and IP
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            
            network_info["hostname"] = hostname
            network_info["ip_address"] = ip_address
            
            # Try to get more info using system commands
            if platform.system() == "Linux":
                result = subprocess.run(['ip', 'addr', 'show'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    network_info["raw_ip_output"] = result.stdout[:1000]  # Limit size
        except:
            pass
    
    return network_info

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def get_system_info(
    detail_level: str = "basic",
    timeout: int = 10,
    include: str = "all"
) -> str:
    """
    Get comprehensive system information.
    
    Args:
        detail_level: Level of detail - 'basic', 'detailed', 'full'
        timeout: Timeout in seconds for gathering information
        include: Information to include - 'cpu', 'memory', 'disk', 'system', 'network', 'all'
    
    Returns:
        JSON string with system information matching Claude Code tool format.
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        if detail_level not in ["basic", "detailed", "full"]:
            return _format_json_response({
                "success": False,
                "operation": "get_system_info",
                "error": f"Invalid detail_level: {detail_level}. Must be 'basic', 'detailed', or 'full'.",
                "detail_level": detail_level
            })
        
        if timeout <= 0:
            return _format_json_response({
                "success": False,
                "operation": "get_system_info",
                "error": f"Timeout must be positive, got: {timeout}",
                "timeout_seconds": timeout
            })
        
        include_options = ["cpu", "memory", "disk", "system", "network", "all"]
        if include not in include_options:
            return _format_json_response({
                "success": False,
                "operation": "get_system_info",
                "error": f"Invalid include: {include}. Must be one of: {', '.join(include_options)}",
                "include": include
            })
        
        # Prepare response data
        response_data = {
            "success": True,
            "operation": "get_system_info",
            "detail_level": detail_level,
            "include": include,
            "_metadata": {
                "collection_time_seconds": 0,
                "timeout_seconds": timeout,
                "platform": platform.system(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        # Gather requested information
        info_sections = {}
        
        # Determine which sections to include
        sections_to_gather = []
        if include == "all":
            sections_to_gather = ["system", "cpu", "memory", "disk", "network"]
        else:
            sections_to_gather = [include]
        
        # Gather each section
        for section in sections_to_gather:
            try:
                if section == "cpu":
                    info_sections["cpu"] = _get_cpu_info()
                elif section == "memory":
                    info_sections["memory"] = _get_memory_info()
                elif section == "disk":
                    info_sections["disk"] = _get_disk_info()
                elif section == "system":
                    info_sections["system"] = _get_system_info()
                elif section == "network":
                    info_sections["network"] = _get_network_info()
                
                # Check timeout
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"System info collection timed out after {timeout} seconds")
                    
            except Exception as e:
                info_sections[section] = {
                    "error": f"Failed to gather {section} information: {str(e)}"
                }
        
        # Add gathered information to response
        response_data.update(info_sections)
        
        # Calculate collection time
        collection_time = time.time() - start_time
        response_data["_metadata"]["collection_time_seconds"] = round(collection_time, 2)
        
        # Apply detail level filtering
        if detail_level == "basic":
            # Keep only essential information
            for section in info_sections:
                if isinstance(info_sections[section], dict):
                    # Simplify each section
                    simplified = {}
                    if section == "cpu":
                        simplified = {
                            "cores": info_sections[section].get("cores_physical", 0),
                            "usage_percent": info_sections[section].get("usage_percent", 0)
                        }
                    elif section == "memory":
                        simplified = {
                            "total_gb": round(info_sections[section].get("total_bytes", 0) / (1024**3), 1),
                            "usage_percent": info_sections[section].get("usage_percent", 0)
                        }
                    elif section == "disk":
                        if "current" in info_sections[section]:
                            simplified = {
                                "total_gb": round(info_sections[section]["current"].get("total_bytes", 0) / (1024**3), 1),
                                "usage_percent": info_sections[section]["current"].get("usage_percent", 0)
                            }
                    elif section == "system":
                        simplified = {
                            "system": info_sections[section].get("system", "unknown"),
                            "node": info_sections[section].get("node", "unknown"),
                            "uptime_days": info_sections[section].get("uptime_days", 0)
                        }
                    elif section == "network":
                        simplified = {
                            "hostname": info_sections[section].get("hostname", "unknown"),
                            "ip_address": info_sections[section].get("ip_address", "unknown")
                        }
                    
                    if simplified:
                        response_data[section] = simplified
        
        return _format_json_response(response_data)
        
    except TimeoutError as e:
        return _format_json_response({
            "success": False,
            "operation": "get_system_info",
            "error": str(e),
            "detail_level": detail_level,
            "include": include,
            "timeout_seconds": timeout
        })
    except Exception as e:
        return _format_json_response({
            "success": False,
            "operation": "get_system_info",
            "error": f"Unexpected error: {str(e)}",
            "detail_level": detail_level,
            "include": include
        })

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__SYSINFO_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "get_system_info": get_system_info,
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'get_system_info']