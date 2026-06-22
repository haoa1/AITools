"""
Shell operations module for AITools.

This module provides shell command execution and system information,
including both bash (Unix) and PowerShell (cross-platform) support.
"""

__version__ = "1.1.0"
__author__ = "AITools Team"
__description__ = "Shell command execution and system operations (bash + powershell)"

from .bash import (
    bash,
)

from .power_shell_tool import (
    power_shell,
    tools as powershell_tools,
    TOOL_CALL_MAP as powershell_tool_map,
)

__all__ = [
    'bash',
    'power_shell',
    'powershell_tools',
    'powershell_tool_map',
]