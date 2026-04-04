"""
Shell operations module for AITools.

This module provides shell command execution and system information.
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "Shell command execution and system operations"

from .bash import (
    bash,
)

__all__ = [
    'bash',
]