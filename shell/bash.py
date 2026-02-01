from base import function_ai, parameters_func, property_param

import os
import subprocess
import sys

__BASH_PROPERTY_ONE__ = property_param(
    name="command",
    description="The bash command to execute.",
    t="string",
    required=True
)

__BASH_PROPERTY_TWO__ = property_param(
    name="working_dir",
    description="The working directory where the command will be executed.",
    t="string"
)

__BASH_PROPERTY_THREE__ = property_param(
    name="timeout",
    description="Timeout in seconds for command execution.",
    t="integer"
)

__BASH_PROPERTY_4__ = property_param(
    name="capture_output",
    description="Whether to capture and return the command output.",
    t="boolean"
)

__BASH_PROPERTY_5__ = property_param(
    name="env_vars",
    description="Additional environment variables as a dictionary.",
    t="object"
)

__BASH_PROPERTY_6__ = property_param(
    name="shell",
    description="Whether to run the command through the shell.",
    t="boolean"
)

__BASH_PROPERTY_7__ = property_param(
    name="args",
    description="Additional arguments for the command.",
    t="array"
)

__BASH_PROPERTY_8__ = property_param(
    name="input_data",
    description="Input data to send to the command's stdin.",
    t="string"
)

__BASH_EXECUTE_FUNCTION__ = function_ai(name="execute_command",
                                         description="Execute a bash command and return the output.",
                                         parameters=parameters_func([__BASH_PROPERTY_ONE__, __BASH_PROPERTY_TWO__, __BASH_PROPERTY_THREE__, __BASH_PROPERTY_4__, __BASH_PROPERTY_5__, __BASH_PROPERTY_6__, __BASH_PROPERTY_8__]))

__BASH_CHECK_COMMAND_FUNCTION__ = function_ai(name="check_command_exists",
                                               description="Check if a command exists in the system.",
                                               parameters=parameters_func([__BASH_PROPERTY_ONE__]))

__BASH_EXECUTE_MULTIPLE_FUNCTION__ = function_ai(name="execute_multiple_commands",
                                                 description="Execute multiple bash commands sequentially.",
                                                 parameters=parameters_func([__BASH_PROPERTY_ONE__, __BASH_PROPERTY_TWO__, __BASH_PROPERTY_THREE__, __BASH_PROPERTY_4__, __BASH_PROPERTY_6__]))

__BASH_GET_PROCESS_INFO_FUNCTION__ = function_ai(name="get_process_info",
                                                  description="Get information about running processes.",
                                                  parameters=parameters_func([__BASH_PROPERTY_ONE__]))

import os
import subprocess
import shutil

def execute_command(command: str, working_dir: str = None, timeout: int = 30, 
                    capture_output: bool = True, env_vars: dict = None, 
                    shell: bool = True, input_data: str = None) -> str:
    '''
    Execute a bash command and return the output.
    
    :param command: The bash command to execute
    :type command: str
    :param working_dir: Working directory for command execution
    :type working_dir: str
    :param timeout: Timeout in seconds
    :type timeout: int
    :param capture_output: Whether to capture command output
    :type capture_output: bool
    :param env_vars: Additional environment variables
    :type env_vars: dict
    :param shell: Whether to run through shell
    :type shell: bool
    :param input_data: Input data for command's stdin
    :type input_data: str
    :return: Command output or error message
    :rtype: str
    '''
    try:
        
        # Convert parameters to correct types if needed
        # Ensure capture_output is boolean
        if isinstance(capture_output, str):
            if capture_output.lower() in ('true', '1', 'yes'):
                capture_output = True
            elif capture_output.lower() in ('false', '0', 'no'):
                capture_output = False
            else:
                return f"Error: capture_output must be a boolean, got: {capture_output}"
        
        # Ensure shell is boolean
        if isinstance(shell, str):
            if shell.lower() in ('true', '1', 'yes'):
                shell = True
            elif shell.lower() in ('false', '0', 'no'):
                shell = False
            else:
                return f"Error: shell must be a boolean, got: {shell}"
        
        # Convert timeout to number if needed
        if timeout is not None and not isinstance(timeout, (int, float)):
            try:
                timeout = float(timeout)
            except (ValueError, TypeError):
                try:
                    timeout = int(timeout)
                except (ValueError, TypeError):
                    return f"Error: timeout must be a number, got: {timeout}"
        
        # Update environment variables
        env = os.environ.copy()
        if env_vars:
            # Ensure env_vars is a dict
            if isinstance(env_vars, dict):
                env.update(env_vars)
            else:
                return f"Error: env_vars must be a dictionary, got: {type(env_vars)}"
        
        # Set working directory
        cwd = working_dir if working_dir else os.getcwd()
        
        # Expand user directory if needed
        cwd = os.path.expanduser(cwd)
        
        # Check if working directory exists
        if not os.path.exists(cwd):
            try:
                os.makedirs(cwd, exist_ok=True)
            except Exception as e:
                return f"Error: Working directory does not exist and cannot be created: {cwd}. Error: {str(e)}"
        
        # Prepare command execution
        kwargs = {
            'cwd': cwd,
            'env': env,
            'timeout': timeout,
            'shell': shell
        }
        
        # Check if bash is available for brace expansion
        if shell and '{' in command and '}' in command:
            # Try to find bash explicitly
            bash_path = shutil.which('bash')
            if bash_path:
                # Use bash explicitly for brace expansion
                command = f'bash -c "{command}"'
                # Don't set executable, we've already wrapped the command
            else:
                print(f"[DEBUG] Bash not found in PATH")
        
        if capture_output:
            print(f"[DEBUG] Capture output is True, setting up stdout/stderr capture")
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.PIPE
            kwargs['text'] = True
        
        if input_data:
            kwargs['stdin'] = subprocess.PIPE
            kwargs['input'] = input_data
        
        # Execute command
        process = subprocess.run(command, **kwargs)
        
        # Prepare result
        result = {
            'return_code': process.returncode,
            'success': process.returncode == 0
        }
        
        if capture_output:
            result['stdout'] = process.stdout if process.stdout else ""
            result['stderr'] = process.stderr if process.stderr else ""
            
            if process.returncode == 0:
                output = result['stdout']
                if result['stderr']:
                    output += f"\nWarning (stderr): {result['stderr']}"
            else:
                output = f"Command failed with return code {process.returncode}\n"
                if result['stderr']:
                    output += f"Error: {result['stderr']}"
                elif result['stdout']:
                    output += f"Output: {result['stdout']}"
        else:
            output = f"Command executed with return code {process.returncode}"
        
        # Check if directories were created
        if "mkdir" in command.lower():
            # Extract directory paths from command
            import re
            # Simple pattern to find directory names after mkdir -p
            pattern = r'mkdir\s+-p\s+(.+)'
            match = re.search(pattern, command)
            if match:
                dirs_spec = match.group(1)
                # Check for brace expansion
                if '{' in dirs_spec and '}' in dirs_spec:
                    import glob
                    # Expand the pattern
                    expanded_dirs = glob.glob(dirs_spec.replace('{', '*').replace('}', '*').replace(',', '*'))
                    for dir_path in expanded_dirs:
                        abs_path = os.path.join(cwd, dir_path) if not os.path.isabs(dir_path) else dir_path
                        if os.path.exists(abs_path):
                            print(f"[DEBUG] ✓ Directory exists: {abs_path}")
                        else:
                            print(f"[DEBUG] ✗ Directory does NOT exist: {abs_path}")
        
        return output
    
    except subprocess.TimeoutExpired as e:
        return f"Error: Command timed out after {timeout} seconds: {str(e)}"
    except FileNotFoundError as e:
        return f"Error: Command not found or cannot be executed: {str(e)}"
    except PermissionError as e:
        return f"Error: Permission denied when executing command: {str(e)}"
    except ValueError as e:
        return f"Error: Invalid arguments for command execution: {str(e)}"
    except subprocess.SubprocessError as e:
        return f"Error: Subprocess error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when executing command: {str(e)}"

def check_command_exists(command: str) -> str:
    '''
    Check if a command exists in the system.
    
    :param command: The command to check
    :type command: str
    :return: Command availability status
    :rtype: str
    '''
    try:
        # Check if command is in PATH
        result = subprocess.run(
            ['which', command] if sys.platform != 'win32' else ['where', command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return f"Command '{command}' exists at: {result.stdout.strip()}"
        else:
            # Try alternative method
            try:
                subprocess.run(
                    [command, '--version'] if '--' in command else [command, '-h'],
                    capture_output=True,
                    timeout=3
                )
                return f"Command '{command}' exists (checked via --version/-h)"
            except:
                return f"Command '{command}' not found in PATH"
    
    except subprocess.TimeoutExpired:
        return f"Timeout checking command '{command}'"
    except Exception as e:
        return f"Error checking command '{command}': {str(e)}"

def execute_multiple_commands(commands: str, working_dir: str = None, 
                              timeout: int = 60, capture_output: bool = True, 
                              shell: bool = True) -> str:
    '''
    Execute multiple bash commands sequentially.
    
    :param commands: Multiple commands separated by semicolons or newlines
    :type commands: str
    :param working_dir: Working directory for command execution
    :type working_dir: str
    :param timeout: Timeout in seconds for each command
    :type timeout: int
    :param capture_output: Whether to capture command output
    :type capture_output: bool
    :param shell: Whether to run through shell
    :type shell: bool
    :return: Combined output of all commands
    :rtype: str
    '''
    try:
        # Convert parameters to correct types if needed (e.g., from JSON string to int)
        if isinstance(timeout, str):
            try:
                # Try to convert string to float first (supports decimal values)
                timeout = float(timeout)
            except ValueError:
                # If that fails, try int
                try:
                    timeout = int(timeout)
                except ValueError:
                    return f"Error: timeout must be a number, got: {timeout}"
        
        # Split commands by semicolons or newlines
        command_list = []
        if ';' in commands:
            command_list = [cmd.strip() for cmd in commands.split(';') if cmd.strip()]
        else:
            command_list = [cmd.strip() for cmd in commands.split('\n') if cmd.strip()]
        
        if not command_list:
            return "Error: No commands provided"
        
        results = []
        for i, cmd in enumerate(command_list, 1):
            results.append(f"Command {i}: {cmd}")
            
            try:
                output = execute_command(
                    command=cmd,
                    working_dir=working_dir,
                    timeout=timeout,
                    capture_output=capture_output,
                    shell=shell
                )
                results.append(f"Output:\n{output}")
            except Exception as e:
                results.append(f"Error executing command {i}: {str(e)}")
            
            results.append("-" * 50)
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Error executing multiple commands: {str(e)}"

def get_process_info(process_filter: str = "") -> str:
    '''
    Get information about running processes.
    
    :param process_filter: Filter processes by name or pattern
    :type process_filter: str
    :return: Process information
    :rtype: str
    '''
    try:
        if sys.platform == "win32":
            # Windows
            if process_filter:
                command = f'tasklist | findstr /i "{process_filter}"'
            else:
                command = 'tasklist'
        else:
            # Unix/Linux/Mac
            if process_filter:
                command = f'ps aux | grep -i "{process_filter}" | grep -v grep'
            else:
                command = 'ps aux'
        
        return execute_command(
            command=command,
            capture_output=True,
            shell=True,
            timeout=10
        )
    
    except Exception as e:
        return f"Error getting process information: {str(e)}"

def get_system_info(**kwargs) -> str:
    '''
    Get basic system information.
    
    :return: System information
    :rtype: str
    '''
    try:
        if sys.platform == "win32":
            commands = [
                "systeminfo | findstr /B /C:\"OS Name\" /C:\"OS Version\" /C:\"System Type\"",
                "wmic cpu get name",
                "wmic memorychip get capacity",
                "hostname"
            ]
        else:
            commands = [
                "uname -a",
                "cat /etc/os-release | grep -E '^(NAME|VERSION)='",
                "lscpu | grep 'Model name'",
                "free -h",
                "hostname"
            ]
        
        results = ["System Information:", "=" * 50]
        
        for cmd in commands:
            results.append(f"$ {cmd}")
            output = execute_command(cmd, capture_output=True, shell=True, timeout=5)
            results.append(output)
            results.append("-" * 30)
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Error getting system information: {str(e)}"

# 添加系统信息函数到工具列表
__BASH_SYSTEM_INFO_FUNCTION__ = function_ai(name="get_system_info",
                                           description="Get basic system information.",
                                           parameters=parameters_func([]))

tools = [
    __BASH_EXECUTE_FUNCTION__,
    __BASH_CHECK_COMMAND_FUNCTION__,
    __BASH_EXECUTE_MULTIPLE_FUNCTION__,
    __BASH_GET_PROCESS_INFO_FUNCTION__,
    __BASH_SYSTEM_INFO_FUNCTION__,
]

TOOL_CALL_MAP = {
    "execute_command": execute_command,
    "check_command_exists": check_command_exists,
    "execute_multiple_commands": execute_multiple_commands,
    "get_process_info": get_process_info,
    "get_system_info": get_system_info,
}