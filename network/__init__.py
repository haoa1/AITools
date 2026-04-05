from .network import tools as network_tools, TOOL_CALL_MAP as network_map
try:
    from web_search import tools as web_search_tools, TOOL_CALL_MAP as web_search_map
    has_web_search = True
except ImportError:
    # web_search模块可能不存在或导入失败
    web_search_tools = []
    web_search_map = {}
    has_web_search = False
    print("警告：无法导入web_search模块，跳过web_search工具", file=__import__('sys').stderr)

from .web_fetch_tool import tools as web_fetch_tools, TOOL_CALL_MAP as web_fetch_map
from .list_mcp_resources_tool import tools as mcp_resources_tools, TOOL_CALL_MAP as mcp_resources_map
from .read_mcp_resource_tool import tools as read_mcp_resource_tools, TOOL_CALL_MAP as read_mcp_resource_map

# Combine tools and TOOL_CALL_MAPs
tools = network_tools + web_fetch_tools + mcp_resources_tools + read_mcp_resource_tools
TOOL_CALL_MAP = {**network_map, **web_fetch_map, **mcp_resources_map, **read_mcp_resource_map}

# 如果web_search存在，添加它
if has_web_search:
    tools = tools + web_search_tools
    TOOL_CALL_MAP = {**TOOL_CALL_MAP, **web_search_map}

__all__ = ['tools', 'TOOL_CALL_MAP']