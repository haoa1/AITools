"""
User interaction module for AITools.
Provides tools for asking questions, getting feedback, generating briefs, and other user interactions.
"""

from .ask_user_question import tools as ask_user_question_tools, TOOL_CALL_MAP as ask_user_question_map
from .brief import tools as brief_tools, TOOL_CALL_MAP as brief_map

# Combine tools and TOOL_CALL_MAPs
tools = ask_user_question_tools + brief_tools
TOOL_CALL_MAP = {**ask_user_question_map, **brief_map}

__all__ = ['tools', 'TOOL_CALL_MAP']