"""
User interaction module for AITools.
Provides tools for asking questions, getting feedback, generating briefs, REPL interactions, and other user interactions.
"""

from .ask_user_question_tool import tools as ask_user_question_tools, TOOL_CALL_MAP as ask_user_question_map
from .brief_tool import tools as brief_tools, TOOL_CALL_MAP as brief_map
from .send_message_tool import tools as send_message_tools, TOOL_CALL_MAP as send_message_map
from .repl_tool import tools as repl_tools, TOOL_CALL_MAP as repl_map

# Combine tools and TOOL_CALL_MAPs 
tools = ask_user_question_tools + brief_tools + repl_tools
TOOL_CALL_MAP = {**ask_user_question_map, **brief_map, **repl_map}

__all__ = ['tools', 'TOOL_CALL_MAP']
