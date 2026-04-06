"""
Network operations module for AITools.
Provides tools for HTTP requests, web fetching, and network diagnostics.
"""

from .network import tools as network_tools, TOOL_CALL_MAP as network_map
from .web_fetch_tool import tools as web_fetch_tools, TOOL_CALL_MAP as web_fetch_map
from .list_mcp_resources_tool import tools as mcp_resources_tools, TOOL_CALL_MAP as mcp_resources_map
from .read_mcp_resource_tool import tools as read_mcp_resource_tools, TOOL_CALL_MAP as read_mcp_resource_map

# Combine tools and TOOL_CALL_MAPs
tools = web_fetch_tools
TOOL_CALL_MAP = {**web_fetch_map}


__all__ = ['tools', 'TOOL_CALL_MAP']
