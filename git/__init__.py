"""
Git module for AITools framework.

This module exposes git operations as tools for the AI assistant.
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "Git version control operations for AI assistant"

# Import from git.py
from .git import tools, TOOL_CALL_MAP

# List of exported functions
__all__ = [
    'tools',
    'TOOL_CALL_MAP',
]