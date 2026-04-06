#!/usr/bin/env python3
"""
PowerShellTool implementation for AITools (Claude Code compatible version).
Provides PowerShell command execution functionality for cross-platform support.
Based on BashTool pattern with PowerShell-specific adaptations.
"""

import os
import json
import subprocess
import shutil
import time
import platform
from typing import Optional, Dict, Any, Tuple

# AITools decorators
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__PS_COMMAND_PROPERTY__ = property_param(
    name="command",
    description="The PowerShell command or script to execute.",
    t="string",
    required=True,
)

__PS_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description=f"Optional timeout in milliseconds (max 300000).",
    t="number",
    required=False,
)

__PS_DESCRIPTION_PROPERTY__ = property_param(
    name="description",
    description="""Clear, concise description of what this PowerShell command does in active voice.

For simple commands (Get-ChildItem, Get-Service, etc.), keep it brief:
- Get-ChildItem → "List files and directories"
- Get-Service → "List Windows services"
- Get-Process → "List running processes"

For more complex commands or scripts, add context:
- Get-WmiObject -Class Win32_ComputerSystem → "Get computer system information"
- Get-EventLog -LogName Application -Newest 10 → "Get latest 10 application event log entries"
- Get-ChildItem -Recurse -Filter *.log | Select-String -Pattern "Error" → "Search for 'Error' in all log files recursively" """,
    t="string",
    required=False,
)

__PS_RUN_IN_BACKGROUND_PROPERTY__ = property_param(
    name="run_in_background",
    description="Set to true to run this command in the background. Use Read to read the output later.",
    t="boolean",
    required=False,
)

__PS_DANGEROUSLY_DISABLE_SANDBOX_PROPERTY__ = property_param(
    name="dangerouslyDisableSandbox",
    description="Set to true to disable sandbox restrictions (not implemented in this version).",
    t="boolean",
    required=False,
)

__PS_EXECUTION_POLICY_PROPERTY__ = property_param(
    name="executionPolicy",
    description="PowerShell execution policy to use (default: 'Bypass' for this session).",
    t="string",
    required=False,
)

__PS_ENCODING_PROPERTY__ = property_param(
    name="encoding",
    description="Output encoding to use (default: 'UTF8').",
    t="string",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__POWERSHELL_TOOL_FUNCTION__ = function_ai(
    name="power_shell",
    description="Execute a PowerShell command or script (cross-platform support).",
    parameters=parameters_func([
        __PS_COMMAND_PROPERTY__,
        __PS_TIMEOUT_PROPERTY__,
        __PS_DESCRIPTION_PROPERTY__,
        __PS_RUN_IN_BACKGROUND_PROPERTY__,
        __PS_DANGEROUSLY_DISABLE_SANDBOX_PROPERTY__,
        __PS_EXECUTION_POLICY_PROPERTY__,
        __PS_ENCODING_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_powershell_path() -> Optional[str]:
    """
    Find PowerShell executable path.
    Returns path to pwsh (PowerShell Core) or powershell (Windows PowerShell).
    """
    # Try PowerShell Core first (cross-platform)
    pwsh_path = shutil.which('pwsh')
    if pwsh_path:
        return pwsh_path
    
    # Try Windows PowerShell (Windows only)
    powershell_path = shutil.which('powershell')
    if powershell_path:
        return powershell_path
    
    # On Windows, try common paths
    if platform.system() == 'Windows':
        common_paths = [
            r'C:\Program Files\PowerShell\7\pwsh.exe',
            r'C:\Program Files\PowerShell\6\pwsh.exe',
            r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    
    return None

def _is_powershell_available() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if PowerShell is available and return version info.
    Returns (is_available, version_info, error_message)
    """
    ps_path = _get_powershell_path()
    if not ps_path:
        return False, None, "PowerShell not found. Install PowerShell Core (pwsh) or Windows PowerShell."
    
    try:
        # Try to get version info
        result = subprocess.run(
            [ps_path, '-Command', '$PSVersionTable.PSVersion.ToString()'],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False
        )
        
        if result.returncode == 0 and result.stdout.strip():
            version = result.stdout.strip()
            version_info = f"PowerShell {version} at {ps_path}"
        else:
            version_info = f"PowerShell at {ps_path}"
        
        return True, version_info, None
        
    except Exception as e:
        return False, None, f"PowerShell check failed: {e}"

def _build_powershell_command(
    command: str, 
    execution_policy: Optional[str] = None,
    encoding: Optional[str] = None
) -> list:
    """
    Build PowerShell command arguments list.
    """
    ps_path = _get_powershell_path()
    if not ps_path:
        raise RuntimeError("PowerShell not found")
    
    args = [ps_path]
    
    # Add execution policy if specified
    if execution_policy:
        if execution_policy.lower() in ['bypass', 'unrestricted', 'remotesigned', 'allsigned', 'restricted']:
            args.extend(['-ExecutionPolicy', execution_policy])
    
    # Add encoding if specified
    if encoding:
        if encoding.lower() in ['utf8', 'utf16', 'ascii', 'unicode', 'bigendianunicode']:
            args.extend(['-OutputFormat', 'Text', '-EncodedCommand'])
            # PowerShell expects Base64 encoded command when using -EncodedCommand
            import base64
            encoded_bytes = base64.b64encode(command.encode('utf-16-le'))
            args.append(encoded_bytes.decode('ascii'))
            return args
    
    # Default: use -Command parameter
    args.extend(['-Command', command])
    return args

def _get_return_code_interpretation(returncode: int, command: str) -> str:
    """
    Provide human-readable interpretation of PowerShell return codes.
    """
    if returncode == 0:
        return "Success"
    elif returncode == 1:
        return "General error"
    elif returncode == 2:
        return "Parse error in PowerShell script"
    elif returncode == 3:
        return "Pipeline stopped"
    elif returncode == 4:
        return "Script terminated by Ctrl+C or Stop-Processing"
    elif returncode == 5:
        return "Unhandled exception"
    elif returncode == -1:
        return "Command timeout or interrupted"
    else:
        # Check for common Windows error codes
        error_codes = {
            2: "File not found",
            3: "Path not found",
            5: "Access denied",
            267: "Directory not empty",
            183: "File already exists",
        }
        
        if returncode in error_codes:
            return error_codes[returncode]
        
        return f"Exit code {returncode}"

def _is_image_output(data: bytes) -> bool:
    """
    Check if output appears to be image data.
    Simplified version from BashTool.
    """
    if not data:
        return False
    
    # Check for common image magic bytes
    image_signatures = [
        b'\xff\xd8\xff',  # JPEG
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'GIF87a',  # GIF
        b'GIF89a',  # GIF
        b'BM',  # BMP
        b'RIFF',  # WEBP
    ]
    
    for signature in image_signatures:
        if data.startswith(signature):
            return True
    
    return False

def _is_no_output_expected(command: str) -> bool:
    """
    Determine if command is expected to produce no output.
    PowerShell-specific heuristics.
    """
    cmd_lower = command.lower()
    
    # PowerShell cmdlets that typically don't produce console output
    # Note: Write-Host, Write-Output produce output, so not included
    no_output_cmdlets = [
        'set-', 'new-', 'remove-', 'rename-', 'move-', 'copy-',
        'add-', 'clear-', 'disable-', 'enable-', 'export-', 'import-',
        'initialize-', 'limit-', 'lock-', 'mount-', 'pop-', 'push-',
        'register-', 'reset-', 'restart-', 'resume-', 'save-', 'select-',
        'start-', 'stop-', 'suspend-', 'unlock-', 'unregister-', 'update-',
    ]
    
    # Check for cmdlets
    for cmdlet in no_output_cmdlets:
        if cmd_lower.startswith(cmdlet):
            return True
    
    # Check for common operations
    no_output_patterns = [
        '= ',  # Variable assignment
        '$',   # Variable reference without output
        '| out-null',
        '> $null',
        '>> $null',
    ]
    
    for pattern in no_output_patterns:
        if pattern in cmd_lower:
            return True
    
    return False
    
    for pattern in no_output_patterns:
        if pattern in cmd_lower:
            return True
    
    return False

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def power_shell(
    command: str,
    timeout: Optional[int] = None,
    description: Optional[str] = None,
    run_in_background: bool = False,
    dangerouslyDisableSandbox: bool = False,
    executionPolicy: Optional[str] = None,
    encoding: Optional[str] = None
) -> str:
    """
    Execute a PowerShell command or script and return structured output.
    
    Args:
        command: PowerShell command or script to execute
        timeout: Timeout in milliseconds (optional)
        description: Command description (optional)
        run_in_background: Run in background (simplified support)
        dangerouslyDisableSandbox: Disable sandbox (not implemented)
        executionPolicy: PowerShell execution policy (default: 'Bypass' for session)
        encoding: Output encoding (default: 'UTF8')
    
    Returns:
        JSON matching Claude Code tool output schema with PowerShell-specific adaptations.
    """
    try:
        # Validate inputs
        if not command or not isinstance(command, str):
            return json.dumps({
                "error": "Command must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Check PowerShell availability
        ps_available, ps_version, ps_error = _is_powershell_available()
        if not ps_available:
            return json.dumps({
                "error": f"PowerShell not available: {ps_error}",
                "success": False,
                "_metadata": {
                    "command": command,
                    "description": description,
                    "powerShellAvailable": False,
                    "error": ps_error
                }
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
        background_warning = None
        if run_in_background:
            background_warning = "Background execution requested but not fully implemented in this version"
        
        # Check for sandbox disable request
        sandbox_warning = None
        if dangerouslyDisableSandbox:
            sandbox_warning = "Sandbox disabled (sandbox not implemented in this version)"
        
        # Use current working directory
        cwd = os.getcwd()
        
        # Check if working directory exists
        if not os.path.exists(cwd):
            return json.dumps({
                "error": f"Working directory does not exist: {cwd}",
                "success": False
            }, indent=2)
        
        # Build PowerShell command
        try:
            ps_args = _build_powershell_command(command, executionPolicy, encoding)
        except Exception as e:
            return json.dumps({
                "error": f"Failed to build PowerShell command: {e}",
                "success": False
            }, indent=2)
        
        # Prepare environment
        env = os.environ.copy()
        
        # Add PowerShell-specific environment variables
        if platform.system() == 'Windows':
            # Ensure UTF-8 output on Windows
            if not encoding:
                env['PYTHONIOENCODING'] = 'utf-8'
        
        # Prepare subprocess arguments
        kwargs = {
            'args': ps_args,
            'cwd': cwd,
            'env': env,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'text': False,  # Get bytes for image detection
        }
        
        if timeout_seconds:
            kwargs['timeout'] = timeout_seconds
        
        # Track start time
        start_time = time.time()
        interrupted = False
        
        try:
            # Execute command
            process = subprocess.run(**kwargs)
            execution_time = time.time() - start_time
            
            # Get outputs as bytes
            stdout_bytes = process.stdout if process.stdout else b''
            stderr_bytes = process.stderr if process.stderr else b''
            
            # Check if output appears to be image data
            is_image = _is_image_output(stdout_bytes)
            
            # Decode outputs
            try:
                # Try UTF-8 first
                stdout = stdout_bytes.decode('utf-8', errors='replace')
                stderr = stderr_bytes.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                # Fall back to system encoding
                stdout = stdout_bytes.decode('latin-1', errors='replace')
                stderr = stderr_bytes.decode('latin-1', errors='replace')
            
            # Get return code interpretation
            return_code_interpretation = _get_return_code_interpretation(process.returncode, command)
            
            # Check if command is expected to produce no output
            no_output_expected = _is_no_output_expected(command)
            
            # Build response
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
            
            # Add metadata
            response["_metadata"] = {
                "success": process.returncode == 0,
                "returnCode": process.returncode,
                "executionTime": execution_time,
                "command": command,
                "description": description,
                "timeoutMs": timeout,
                "runInBackground": run_in_background,
                "executionPolicy": executionPolicy,
                "encoding": encoding,
                "powerShellAvailable": True,
                "powerShellVersion": ps_version,
                "platform": platform.system(),
                "workingDirectory": cwd,
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
                    "executionPolicy": executionPolicy,
                    "encoding": encoding,
                    "error": "TimeoutExpired",
                    "powerShellAvailable": True,
                    "powerShellVersion": ps_version,
                }
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": f"PowerShell execution failed: {str(e)}",
                "success": False,
                "_metadata": {
                    "command": command,
                    "description": description,
                    "executionPolicy": executionPolicy,
                    "encoding": encoding,
                    "powerShellAvailable": True,
                    "powerShellVersion": ps_version,
                    "error": str(e)
                }
            }, indent=2)
            
    except Exception as e:
        # Catch-all for unexpected errors
        return json.dumps({
            "error": f"Unexpected error in PowerShellTool: {str(e)}",
            "success": False,
            "_metadata": {
                "command": command if 'command' in locals() else None,
                "description": description if 'description' in locals() else None,
            }
        }, indent=2)

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__POWERSHELL_TOOL_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "power_shell": power_shell
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'power_shell', '__POWERSHELL_TOOL_FUNCTION__']