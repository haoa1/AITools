#!/usr/bin/env python3
"""
BashTool implementation for AITools (Claude Code compatible version).
Provides bash command execution functionality aligned with Claude Code's BashTool.
Based on analysis of Claude Code source: restored-src/src/tools/BashTool/BashTool.tsx
"""

import os
import json
import subprocess
import shutil
import time
from base import function_ai, parameters_func, property_param

# Property definitions for BashTool
__COMMAND_PROPERTY__ = property_param(
    name="command",
    description="The command to execute.",
    t="string",
    required=True,
)

__TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description=f"Optional timeout in milliseconds (max 300000).",
    t="number",
    required=False,
)

__DESCRIPTION_PROPERTY__ = property_param(
    name="description",
    description="""Clear, concise description of what this command does in active voice. Never use words like "complex" or "risk" in the description - just describe what it does.

For simple commands (git, npm, standard CLI tools), keep it brief (5-10 words):
- ls → "List files in current directory"
- git status → "Show working tree status"
- npm install → "Install package dependencies"

For commands that are harder to parse at a glance (piped commands, obscure flags, etc.), add enough context to clarify what it does:
- find . -name "*.tmp" -exec rm {} \\; → "Find and delete all .tmp files recursively"
- git reset --hard origin/main → "Discard all local changes and match remote main"
- curl -s url | jq '.data[]' → "Fetch JSON from URL and extract data array elements" """,
    t="string",
    required=False,
)

__RUN_IN_BACKGROUND_PROPERTY__ = property_param(
    name="run_in_background",
    description="Set to true to run this command in the background. Use Read to read the output later.",
    t="boolean",
    required=False,
)

__DANGEROUSLY_DISABLE_SANDBOX_PROPERTY__ = property_param(
    name="dangerouslyDisableSandbox",
    description="Set this to true to dangerously override sandbox mode and run commands without sandboxing.",
    t="boolean",
    required=False,
)

# Function metadata
__BASH_TOOL_FUNCTION__ = function_ai(
    name="bash_tool",
    description="Execute a bash command and return structured output. Compatible with Claude Code's BashTool.",
    parameters=parameters_func([
        __COMMAND_PROPERTY__,
        __TIMEOUT_PROPERTY__,
        __DESCRIPTION_PROPERTY__,
        __RUN_IN_BACKGROUND_PROPERTY__,
        __DANGEROUSLY_DISABLE_SANDBOX_PROPERTY__,
    ]),
)

tools = [__BASH_TOOL_FUNCTION__]


def is_image_output(data: bytes) -> bool:
    """
    Check if output data appears to be image data.
    Simplified version - checks for common image magic bytes.
    """
    if len(data) < 4:
        return False
    
    # Check for common image formats
    magic_bytes = data[:4]
    
    # PNG: \x89PNG
    if magic_bytes.startswith(b'\x89PNG'):
        return True
    # JPEG: \xff\xd8\xff
    if magic_bytes.startswith(b'\xff\xd8\xff'):
        return True
    # GIF: GIF8
    if magic_bytes.startswith(b'GIF8'):
        return True
    # BMP: BM
    if magic_bytes.startswith(b'BM'):
        return True
    
    return False


def get_return_code_interpretation(return_code: int, command: str) -> str:
    """
    Generate semantic interpretation for non-error exit codes.
    """
    if return_code == 0:
        return "Command completed successfully"
    
    # Common Unix exit codes
    if return_code == 1:
        return "General error"
    elif return_code == 2:
        return "Misuse of shell builtins"
    elif return_code == 126:
        return "Command invoked cannot execute"
    elif return_code == 127:
        return "Command not found"
    elif return_code == 128:
        return "Invalid exit argument"
    elif return_code > 128:
        signal = return_code - 128
        signals = {
            1: "SIGHUP (Hangup)",
            2: "SIGINT (Interrupt)",
            3: "SIGQUIT (Quit)",
            9: "SIGKILL (Kill)",
            15: "SIGTERM (Termination)",
        }
        signal_name = signals.get(signal, f"Signal {signal}")
        return f"Command terminated by {signal_name}"
    
    return f"Command exited with code {return_code}"


def bash_tool(command: str, timeout: int = None, description: str = None,
              run_in_background: bool = False, dangerouslyDisableSandbox: bool = False) -> str:
    """
    Execute a bash command and return structured output.
    
    Claude Code compatible version based on BashTool/BashTool.tsx:
    - command: The command to execute
    - timeout: Timeout in milliseconds (optional)
    - description: Command description (optional)
    - run_in_background: Run in background (simplified support)
    - dangerouslyDisableSandbox: Disable sandbox (not implemented)
    
    Returns JSON matching Claude Code's BashTool output schema.
    """
    try:
        # Validate inputs
        if not command or not isinstance(command, str):
            return json.dumps({
                "error": "Command must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Convert timeout from milliseconds to seconds for subprocess
        timeout_seconds = None
        if timeout is not None:
            if not isinstance(timeout, (int, float)):
                try:
                    timeout = float(timeout)
                except (ValueError, TypeError):
                    return json.dumps({
                        "error": f"Timeout must be a number, got: {timeout}",
                        "success": False
                    }, indent=2)
            
            if timeout <= 0:
                return json.dumps({
                    "error": f"Timeout must be positive, got: {timeout}",
                    "success": False
                }, indent=2)
            
            # Convert milliseconds to seconds
            timeout_seconds = timeout / 1000.0
        
        # Check for background execution request
        # Simplified implementation - for now, we don't support true background execution
        # but we can handle long-running commands with appropriate timeout
        background_warning = None
        if run_in_background:
            background_warning = "Background execution requested but not fully implemented in this version"
        
        # Check for sandbox disable request
        sandbox_warning = None
        if dangerouslyDisableSandbox:
            sandbox_warning = "Sandbox disabled (sandbox not implemented in this version)"
        
        # Execute command using subprocess
        # Use current working directory
        cwd = os.getcwd()
        
        # Check if working directory exists
        if not os.path.exists(cwd):
            return json.dumps({
                "error": f"Working directory does not exist: {cwd}",
                "success": False
            }, indent=2)
        
        # Prepare command execution
        kwargs = {
            'cwd': cwd,
            'env': os.environ.copy(),
            'shell': True,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': False,  # Get bytes for image detection
        }
        
        if timeout_seconds:
            kwargs['timeout'] = timeout_seconds
        
        # Check for bash availability for brace expansion
        if '{' in command and '}' in command:
            bash_path = shutil.which('bash')
            if bash_path:
                command = f'bash -c "{command}"'
        
        # Track start time
        start_time = time.time()
        interrupted = False
        
        try:
            # Execute command
            process = subprocess.run(command, **kwargs)
            execution_time = time.time() - start_time
            
            # Get outputs as bytes for image detection
            stdout_bytes = process.stdout if process.stdout else b''
            stderr_bytes = process.stderr if process.stderr else b''
            
            # Check if output appears to be image data
            is_image = is_image_output(stdout_bytes)
            
            # Convert to strings if not image
            if is_image:
                stdout = "[BINARY IMAGE DATA - base64 encoded]"
                # For simplicity, we'll encode small images in base64
                if len(stdout_bytes) < 10000:  # 10KB limit for inline
                    import base64
                    stdout = f"data:image;base64,{base64.b64encode(stdout_bytes).decode('utf-8')}"
                else:
                    stdout = f"[IMAGE DATA: {len(stdout_bytes)} bytes - too large for inline]"
            else:
                stdout = stdout_bytes.decode('utf-8', errors='replace')
            
            stderr = stderr_bytes.decode('utf-8', errors='replace')
            
            # Get return code interpretation
            return_code_interpretation = get_return_code_interpretation(process.returncode, command)
            
            # Check if command is expected to produce no output
            # Simple heuristic based on common commands
            no_output_expected = False
            silent_commands = ['mv', 'cp', 'rm', 'mkdir', 'rmdir', 'chmod', 'chown', 
                              'chgrp', 'touch', 'ln', 'cd', 'export', 'unset']
            cmd_lower = command.lower()
            for silent_cmd in silent_commands:
                if cmd_lower.startswith(silent_cmd):
                    no_output_expected = True
                    break
            
            # Build Claude Code compatible response
            response = {
                "stdout": stdout,
                "stderr": stderr,
                "interrupted": interrupted,
                "isImage": is_image if is_image else None,
                "dangerouslyDisableSandbox": dangerouslyDisableSandbox if dangerouslyDisableSandbox else None,
                "returnCodeInterpretation": return_code_interpretation,
                "noOutputExpected": no_output_expected if no_output_expected else None,
            }
            
            # Add optional fields if they have values
            if background_warning:
                response["_warning"] = background_warning
            
            if sandbox_warning:
                response["_warning_sandbox"] = sandbox_warning
            
            # Add metadata (not part of Claude Code spec but useful)
            response["_metadata"] = {
                "success": process.returncode == 0,
                "returnCode": process.returncode,
                "executionTime": execution_time,
                "command": command,
                "description": description,
                "timeoutMs": timeout,
                "runInBackground": run_in_background,
            }
            
            return json.dumps(response, indent=2)
            
        except subprocess.TimeoutExpired:
            interrupted = True
            execution_time = time.time() - start_time
            
            return json.dumps({
                "stdout": "",
                "stderr": f"Command timed out after {timeout_seconds} seconds",
                "interrupted": interrupted,
                "returnCodeInterpretation": f"Command timed out after {timeout_seconds} seconds",
                "_metadata": {
                    "success": False,
                    "returnCode": -1,
                    "executionTime": execution_time,
                    "command": command,
                    "description": description,
                    "timeoutMs": timeout,
                    "runInBackground": run_in_background,
                    "error": "TimeoutExpired"
                }
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"Command execution failed: {str(e)}",
                "success": False,
                "_metadata": {
                    "command": command,
                    "description": description,
                }
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "bash_tool": bash_tool
}


if __name__ == "__main__":
    # Test the bash_tool function
    import tempfile
    
    print("Testing BashTool (Claude Code compatible)...")
    print("-" * 60)
    
    # Test 1: Simple command
    print("1. Simple command (ls):")
    result = bash_tool("ls -la", description="List files in current directory")
    data = json.loads(result)
    
    print(f"Success: {'error' not in data and ('_metadata' in data and data['_metadata'].get('success') == True)}")
    print(f"Has stdout: {'stdout' in data}")
    print(f"Has stderr: {'stderr' in data}")
    print(f"interrupted: {data.get('interrupted')}")
    
    # Test 2: Command with timeout
    print("\n2. Command with timeout (should complete):")
    result2 = bash_tool("echo 'test'", timeout=5000, description="Echo test with timeout")
    data2 = json.loads(result2)
    print(f"Has timeout metadata: {'timeoutMs' in data2.get('_metadata', {})}")
    
    # Test 3: Check Claude Code compatibility
    print("\n3. Claude Code compatibility check:")
    expected_fields = ["stdout", "stderr", "interrupted"]
    missing_fields = [field for field in expected_fields if field not in data]
    
    if missing_fields:
        print(f"  Missing fields: {missing_fields}")
    else:
        print("  All expected fields present ✓")
        
    # Test 4: Error case
    print("\n4. Error case (non-existent command):")
    result4 = bash_tool("nonexistentcommand12345", description="Non-existent command")
    data4 = json.loads(result4)
    print(f"Has error or non-zero return: {'error' in data4 or data4.get('_metadata', {}).get('success') == False}")
    
    print("\n" + "=" * 60)
    print("BashTool test completed.")