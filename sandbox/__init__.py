"""
Sandbox module for AITools.

Provides a single `sandbox` tool with sub-commands for creating and managing
isolated Garuda testing environments.

Architecture:
  - garuda REPL runs as subprocess.PIPE (for precise I/O control)
  - Bash workspace runs in tmux window 0 (for sandbox exec)
  - Async notifications via Garuda event system (optional dependency)
  - Temporary workspace at /tmp/garuda-sandbox-{name}/

Exports:
  tools: list of AI tool definitions (single sandbox tool)
  TOOL_CALL_MAP: {"sandbox": sandbox_handler}
"""

from .sandbox import sandbox_handler, __tools__, __tool_call_map__

tools = __tools__
TOOL_CALL_MAP = __tool_call_map__
