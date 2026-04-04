"""
System monitoring and control module for AITools.
Provides tools for monitoring system resources, controlling execution, and configuration management.
"""

from .monitor import tools as monitor_tools, TOOL_CALL_MAP as monitor_map
from .sleep import tools as sleep_tools, TOOL_CALL_MAP as sleep_map
from .config import tools as config_tools, TOOL_CALL_MAP as config_map

# Combine tools and TOOL_CALL_MAPs
tools = monitor_tools + sleep_tools + config_tools
TOOL_CALL_MAP = {**monitor_map, **sleep_map, **config_map}

__all__ = ['tools', 'TOOL_CALL_MAP']