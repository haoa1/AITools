"""
Cross-platform input helper using prompt_toolkit.
Falls back to plain input() if prompt_toolkit is not available.
"""

import sys

try:
    from prompt_toolkit import PromptSession

    _session = PromptSession()

    def get_input(prompt: str = "") -> str:
        """Get input using prompt_toolkit (cross-platform, with history support)."""
        try:
            return _session.prompt(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""

except ImportError:

    def get_input(prompt: str = "") -> str:
        """Fallback to plain input() when prompt_toolkit is not installed."""
        try:
            return input(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""
