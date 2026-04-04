"""
Network operations module for AITools.
Provides tools for HTTP requests, web fetching, and network diagnostics.
"""

from .network import tools as network_tools, TOOL_CALL_MAP as network_map
from .web_fetch import tools as web_fetch_tools, TOOL_CALL_MAP as web_fetch_map

# Combine tools and TOOL_CALL_MAPs
tools = network_tools + web_fetch_tools
TOOL_CALL_MAP = {**network_map, **web_fetch_map}

__all__ = ['tools', 'TOOL_CALL_MAP']