from .interaction import tools, TOOL_CALL_MAP
from .enhanced_interaction import tools as enhanced_tools, TOOL_CALL_MAP as enhanced_tool_call_map

# Combine tools
all_tools = tools + enhanced_tools

# Combine tool call maps
all_tool_call_map = TOOL_CALL_MAP.copy()
all_tool_call_map.update(enhanced_tool_call_map)

__all__ = ['tools', 'TOOL_CALL_MAP', 'enhanced_tools', 'enhanced_tool_call_map', 'all_tools', 'all_tool_call_map']