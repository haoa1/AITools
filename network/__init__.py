from .network import tools as network_tools, TOOL_CALL_MAP as network_map
from .web_search import tools as web_search_tools, TOOL_CALL_MAP as web_search_map

# Combine tools and TOOL_CALL_MAPs
tools = network_tools + web_search_tools
TOOL_CALL_MAP = {**network_map, **web_search_map}

__all__ = ['tools', 'TOOL_CALL_MAP']