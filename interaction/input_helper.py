"""
Cross-platform input helper using prompt_toolkit.
Falls back to plain input() if prompt_toolkit is not available
or if running in a non-interactive environment (e.g. subprocess, pipe).
"""

import sys
import os

# Delayed session initialization - don't create PromptSession at module level,
# because on Windows it crashes with NoConsoleScreenBufferError when
# there's no real console (e.g. subprocess, pipe, or non-interactive shell).
_session = None


def _get_session():
    """Lazy-init prompt_toolkit session, return None if unavailable."""
    global _session
    if _session is not None:
        return _session
    try:
        from prompt_toolkit import PromptSession
        _session = PromptSession()
        return _session
    except Exception:
        _session = False  # sentinel: don't retry
        return None


def get_input(prompt: str = "") -> str:
    """Get input using prompt_toolkit if available, else plain input()."""
    session = _get_session()
    if session:
        try:
            return session.prompt(prompt)
        except (EOFError, KeyboardInterrupt):
            return ""
        except Exception:
            # prompt_toolkit runtime error (e.g. console detached) → fallback
            pass

    # Fallback to plain input()
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        return ""
