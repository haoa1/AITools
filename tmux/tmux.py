from base import function_ai, parameters_func, property_param

import os
import subprocess
import sys
import re
import time
import json
from typing import List, Dict, Optional

__TMUX_PROPERTY_ONE__ = property_param(
    name="session_name",
    description="The name of the tmux session.",
    t="string",
    required=True
)

__TMUX_PROPERTY_TWO__ = property_param(
    name="command",
    description="The command to run in the tmux session or pane.",
    t="string"
)

__TMUX_PROPERTY_THREE__ = property_param(
    name="window_name",
    description="The name of the tmux window.",
    t="string"
)

__TMUX_PROPERTY_4__ = property_param(
    name="pane_index",
    description="The index of the pane (0-based).",
    t="integer"
)

__TMUX_PROPERTY_5__ = property_param(
    name="window_index",
    description="The index of the window (0-based).",
    t="integer"
)

__TMUX_PROPERTY_6__ = property_param(
    name="kill",
    description="Kill the session/window/pane instead of detaching.",
    t="boolean"
)

__TMUX_PROPERTY_7__ = property_param(
    name="detach",
    description="Detach from the session after creation.",
    t="boolean"
)

__TMUX_PROPERTY_8__ = property_param(
    name="shell",
    description="Shell command to use in new session/window.",
    t="string"
)

__TMUX_PROPERTY_9__ = property_param(
    name="working_dir",
    description="Working directory for the new session/window.",
    t="string"
)

__TMUX_PROPERTY_10__ = property_param(
    name="width",
    description="Width of the pane in columns.",
    t="integer"
)

__TMUX_PROPERTY_11__ = property_param(
    name="height",
    description="Height of the pane in rows.",
    t="integer"
)

__TMUX_PROPERTY_12__ = property_param(
    name="split_direction",
    description="Direction to split pane (horizontal or vertical).",
    t="string"
)

__TMUX_PROPERTY_13__ = property_param(
    name="target_session",
    description="Target session name for various operations.",
    t="string"
)

__TMUX_PROPERTY_14__ = property_param(
    name="new_name",
    description="New name for renaming operations.",
    t="string"
)

__TMUX_PROPERTY_15__ = property_param(
    name="force",
    description="Force the operation (e.g., kill session without confirmation).",
    t="boolean"
)

__TMUX_PROPERTY_16__ = property_param(
    name="capture_output",
    description="Capture command output instead of running interactively.",
    t="boolean"
)

__TMUX_CREATE_SESSION_FUNCTION__ = function_ai(name="tmux_create_session",
                                               description="Create a new tmux session.",
                                               parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_TWO__, __TMUX_PROPERTY_7__, __TMUX_PROPERTY_8__, __TMUX_PROPERTY_9__]))

__TMUX_LIST_SESSIONS_FUNCTION__ = function_ai(name="tmux_list_sessions",
                                              description="List all tmux sessions.",
                                              parameters=parameters_func([]))

__TMUX_ATTACH_SESSION_FUNCTION__ = function_ai(name="tmux_attach_session",
                                               description="Attach to a tmux session.",
                                               parameters=parameters_func([__TMUX_PROPERTY_ONE__]))

__TMUX_DETACH_SESSION_FUNCTION__ = function_ai(name="tmux_detach_session",
                                               description="Detach from the current tmux session.",
                                               parameters=parameters_func([__TMUX_PROPERTY_13__]))

__TMUX_KILL_SESSION_FUNCTION__ = function_ai(name="tmux_kill_session",
                                             description="Kill a tmux session.",
                                             parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_15__]))

__TMUX_RENAME_SESSION_FUNCTION__ = function_ai(name="tmux_rename_session",
                                               description="Rename a tmux session.",
                                               parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_14__]))

__TMUX_NEW_WINDOW_FUNCTION__ = function_ai(name="tmux_new_window",
                                           description="Create a new window in a tmux session.",
                                           parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_THREE__, __TMUX_PROPERTY_TWO__, __TMUX_PROPERTY_9__]))

__TMUX_KILL_WINDOW_FUNCTION__ = function_ai(name="tmux_kill_window",
                                            description="Kill a window in a tmux session.",
                                            parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_5__, __TMUX_PROPERTY_THREE__]))

__TMUX_RENAME_WINDOW_FUNCTION__ = function_ai(name="tmux_rename_window",
                                              description="Rename a window in a tmux session.",
                                              parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_5__, __TMUX_PROPERTY_THREE__, __TMUX_PROPERTY_14__]))

__TMUX_SPLIT_WINDOW_FUNCTION__ = function_ai(name="tmux_split_window",
                                             description="Split a pane in a tmux session.",
                                             parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_TWO__, __TMUX_PROPERTY_12__, __TMUX_PROPERTY_9__, __TMUX_PROPERTY_10__, __TMUX_PROPERTY_11__]))

__TMUX_KILL_PANE_FUNCTION__ = function_ai(name="tmux_kill_pane",
                                          description="Kill a pane in a tmux session.",
                                          parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_4__, __TMUX_PROPERTY_5__]))

__TMUX_SEND_KEYS_FUNCTION__ = function_ai(name="tmux_send_keys",
                                          description="Send keys/commands to a tmux pane.",
                                          parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_TWO__, __TMUX_PROPERTY_4__, __TMUX_PROPERTY_5__, __TMUX_PROPERTY_16__]))

__TMUX_CAPTURE_PANE_FUNCTION__ = function_ai(name="tmux_capture_pane",
                                             description="Capture the output of a tmux pane.",
                                             parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_4__, __TMUX_PROPERTY_5__]))

__TMUX_LIST_WINDOWS_FUNCTION__ = function_ai(name="tmux_list_windows",
                                             description="List windows in a tmux session.",
                                             parameters=parameters_func([__TMUX_PROPERTY_ONE__]))

__TMUX_LIST_PANES_FUNCTION__ = function_ai(name="tmux_list_panes",
                                           description="List panes in a tmux session.",
                                           parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_5__]))

__TMUX_SWITCH_CLIENT_FUNCTION__ = function_ai(name="tmux_switch_client",
                                              description="Switch client to a different session.",
                                              parameters=parameters_func([__TMUX_PROPERTY_ONE__]))

__TMUX_SESSION_INFO_FUNCTION__ = function_ai(name="tmux_session_info",
                                             description="Get detailed information about a tmux session.",
                                             parameters=parameters_func([__TMUX_PROPERTY_ONE__]))

__TMUX_RUN_COMMAND_FUNCTION__ = function_ai(name="tmux_run_command",
                                            description="Run a command in a tmux session and capture output.",
                                            parameters=parameters_func([__TMUX_PROPERTY_ONE__, __TMUX_PROPERTY_TWO__, __TMUX_PROPERTY_4__, __TMUX_PROPERTY_5__, __TMUX_PROPERTY_16__]))

tools = [
    __TMUX_CREATE_SESSION_FUNCTION__,
    __TMUX_LIST_SESSIONS_FUNCTION__,
    __TMUX_ATTACH_SESSION_FUNCTION__,
    __TMUX_DETACH_SESSION_FUNCTION__,
    __TMUX_KILL_SESSION_FUNCTION__,
    __TMUX_RENAME_SESSION_FUNCTION__,
    __TMUX_NEW_WINDOW_FUNCTION__,
    __TMUX_KILL_WINDOW_FUNCTION__,
    __TMUX_RENAME_WINDOW_FUNCTION__,
    __TMUX_SPLIT_WINDOW_FUNCTION__,
    __TMUX_KILL_PANE_FUNCTION__,
    __TMUX_SEND_KEYS_FUNCTION__,
    __TMUX_CAPTURE_PANE_FUNCTION__,
    __TMUX_LIST_WINDOWS_FUNCTION__,
    __TMUX_LIST_PANES_FUNCTION__,
    __TMUX_SWITCH_CLIENT_FUNCTION__,
    __TMUX_SESSION_INFO_FUNCTION__,
    __TMUX_RUN_COMMAND_FUNCTION__
]

def _run_tmux_command(args: List[str], capture_output: bool = True, timeout: int = 30) -> str:
    """Internal helper function to run tmux commands."""
    try:
        # Check if tmux is available
        try:
            subprocess.run(['tmux', '-V'], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Error: tmux is not installed or not in PATH"
        
        # Run tmux command
        cmd = ['tmux'] + args
        process = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        if process.returncode != 0:
            error_msg = process.stderr.strip() if process.stderr else "Unknown error"
            return f"Error executing tmux command: {error_msg}"
        
        if capture_output:
            return process.stdout.strip()
        else:
            return "Command executed successfully"
    
    except subprocess.TimeoutExpired:
        return f"Error: tmux command timed out after {timeout} seconds"
    except PermissionError as e:
        return f"Error: Permission error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error executing tmux command: {str(e)}"

def _get_session_list() -> List[Dict[str, str]]:
    """Get list of tmux sessions."""
    try:
        output = _run_tmux_command(['list-sessions', '-F', '#{session_name}||#{session_attached}||#{session_windows}||#{session_width}x#{session_height}'])
        if output.startswith("Error:"):
            return []
        
        sessions = []
        for line in output.split('\n'):
            if line.strip():
                parts = line.split('||')
                if len(parts) >= 4:
                    sessions.append({
                        'name': parts[0],
                        'attached': parts[1] == '1',
                        'windows': parts[2],
                        'dimensions': parts[3]
                    })
        return sessions
    except Exception:
        return []

def tmux_create_session(session_name: str, command: str = None, detach: bool = True, 
                        shell: str = None, working_dir: str = None) -> str:
    '''
    Create a new tmux session.
    
    :param session_name: Name of the new session
    :type session_name: str
    :param command: Command to run in the new session
    :type command: str
    :param detach: Create session detached (not attached to current terminal)
    :type detach: bool
    :param shell: Shell to use (default: $SHELL)
    :type shell: str
    :param working_dir: Working directory for the new session
    :type working_dir: str
    :return: Creation status message
    :rtype: str
    '''
    try:
        # Check if session already exists
        sessions = _get_session_list()
        for session in sessions:
            if session['name'] == session_name:
                return f"Error: Session '{session_name}' already exists"
        
        # Build command arguments
        args = ['new-session', '-d', '-s', session_name]
        
        if not detach:
            args.remove('-d')
        
        if shell:
            args.extend(['-e', f'SHELL={shell}'])
        
        if working_dir:
            # Expand user home directory
            working_dir = os.path.expanduser(working_dir)
            if os.path.exists(working_dir) and os.path.isdir(working_dir):
                args.extend(['-c', working_dir])
            else:
                return f"Error: Working directory does not exist: {working_dir}"
        
        # Run initial tmux command
        result = _run_tmux_command(args)
        if result.startswith("Error:"):
            return result
        
        # If command is provided, send it to the session
        if command:
            # Wait a bit for session to be ready
            time.sleep(0.5)
            cmd_result = tmux_send_keys(session_name, command, 0, 0, True)
            
            if cmd_result.startswith("Error:"):
                return f"Session created but command failed: {cmd_result}"
            
            return f"Session '{session_name}' created successfully with command: {command}"
        
        return f"Session '{session_name}' created successfully"
    
    except Exception as e:
        return f"Error creating tmux session: {str(e)}"

def tmux_list_sessions() -> str:
    '''
    List all tmux sessions.
    
    :return: List of tmux sessions with details
    :rtype: str
    '''
    try:
        sessions = _get_session_list()
        
        if not sessions:
            return "No tmux sessions found"
        
        # Format output
        result = ["TMUX Sessions:"]
        result.append("-" * 80)
        result.append(f"{'Name':<20} {'Attached':<10} {'Windows':<10} {'Dimensions':<15} {'Status':<15}")
        result.append("-" * 80)
        
        for session in sessions:
            name = session['name'][:18]
            attached = "Yes" if session['attached'] else "No"
            windows = session['windows']
            dimensions = session['dimensions'][:13]
            status = "Active" if session['attached'] else "Detached"
            
            result.append(f"{name:<20} {attached:<10} {windows:<10} {dimensions:<15} {status:<15}")
        
        result.append(f"\nTotal: {len(session)} session(s)")
        
        # Get more detailed info using tmux command
        detailed_output = _run_tmux_command(['list-sessions'])
        if not detailed_output.startswith("Error:"):
            result.append("\nDetailed session list:")
            result.append(detailed_output)
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error listing tmux sessions: {str(e)}"

def tmux_attach_session(session_name: str) -> str:
    '''
    Attach to a tmux session.
    
    :param session_name: Name of the session to attach to
    :type session_name: str
    :return: Attachment instructions
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Check if already attached
        for session in sessions:
            if session['name'] == session_name and session['attached']:
                return f"Session '{session_name}' is already attached. Use 'tmux switch-client -t {session_name}' to switch to it."
        
        # Provide attachment command
        return f"To attach to session '{session_name}', run:\n\n  tmux attach-session -t {session_name}\n\nOr use the detach command first if another client is attached."
    
    except Exception as e:
        return f"Error preparing to attach to session: {str(e)}"

def tmux_detach_session(target_session: str = None) -> str:
    '''
    Detach from a tmux session.
    
    :param target_session: Specific session to detach from (default: current)
    :type target_session: str
    :return: Detachment instructions or result
    :rtype: str
    '''
    try:
        if target_session:
            # Detach specific session
            return _run_tmux_command(['detach-client', '-s', target_session])
        else:
            # Detach current session
            return _run_tmux_command(['detach-client'])
    
    except Exception as e:
        return f"Error detaching from tmux session: {str(e)}"

def tmux_kill_session(session_name: str, force: bool = False) -> str:
    '''
    Kill a tmux session.
    
    :param session_name: Name of the session to kill
    :type session_name: str
    :param force: Force kill without confirmation
    :type force: bool
    :return: Kill status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build command
        args = ['kill-session', '-t', session_name]
        
        result = _run_tmux_command(args)
        
        if result.startswith("Error:"):
            if force and "still attached" in result.lower():
                # Force kill attached session
                result = _run_tmux_command(['kill-session', '-t', session_name, '-a'])
            
        if result.startswith("Error:"):
            return result
        
        return f"Session '{session_name}' killed successfully"
    
    except Exception as e:
        return f"Error killing tmux session: {str(e)}"

def tmux_rename_session(session_name: str, new_name: str) -> str:
    '''
    Rename a tmux session.
    
    :param session_name: Current session name
    :type session_name: str
    :param new_name: New session name
    :type new_name: str
    :return: Rename status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Check if new name already exists
        for session in sessions:
            if session['name'] == new_name:
                return f"Error: Session '{new_name}' already exists"
        
        # Rename session
        result = _run_tmux_command(['rename-session', '-t', session_name, new_name])
        
        if result.startswith("Error:"):
            return result
        
        return f"Session '{session_name}' renamed to '{new_name}'"
    
    except Exception as e:
        return f"Error renaming tmux session: {str(e)}"

def tmux_new_window(session_name: str, window_name: str = None, command: str = None, 
                    working_dir: str = None) -> str:
    '''
    Create a new window in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param window_name: Name for the new window
    :type window_name: str
    :param command: Command to run in the new window
    :type command: str
    :param working_dir: Working directory for the new window
    :type working_dir: str
    :return: Creation status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build command
        args = ['new-window', '-t', session_name, '-d']
        
        if window_name:
            args.extend(['-n', window_name])
        
        if working_dir:
            working_dir = os.path.expanduser(working_dir)
            if os.path.exists(working_dir) and os.path.isdir(working_dir):
                args.extend(['-c', working_dir])
            else:
                return f"Error: Working directory does not exist: {working_dir}"
        
        result = _run_tmux_command(args)
        
        if result.startswith("Error:"):
            return result
        
        # Get window index
        window_list = _run_tmux_command(['list-windows', '-t', session_name, '-F', '#{window_index}'])
        if not window_list.startswith("Error:"):
            windows = window_list.strip().split('\n')
            if windows:
                new_window_index = windows[-1]
                
                # Send command if provided
                if command:
                    send_result = tmux_send_keys(session_name, command, 0, int(new_window_index), True)
                    if send_result.startswith("Error:"):
                        return f"Window created but command failed: {send_result}"
                
                return f"New window created in session '{session_name}' (index: {new_window_index})"
        
        return f"New window created in session '{session_name}'"
    
    except Exception as e:
        return f"Error creating new window: {str(e)}"

def tmux_kill_window(session_name: str, window_index: int = None, window_name: str = None) -> str:
    '''
    Kill a window in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param window_index: Index of window to kill
    :type window_index: int
    :param window_name: Name of window to kill
    :type window_name: str
    :return: Kill status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build command
        args = ['kill-window', '-t', f'{session_name}:']
        
        if window_index is not None:
            args[-1] += str(window_index)
        elif window_name:
            args[-1] += window_name
        else:
            # Kill current window
            args = ['kill-window', '-t', session_name]
        
        result = _run_tmux_command(args)
        
        if result.startswith("Error:"):
            return result
        
        return f"Window killed in session '{session_name}'"
    
    except Exception as e:
        return f"Error killing window: {str(e)}"

def tmux_rename_window(session_name: str, window_index: int = None, window_name: str = None, 
                       new_name: str = None) -> str:
    '''
    Rename a window in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param window_index: Index of window to rename
    :type window_index: int
    :param window_name: Name of window to rename
    :type window_name: str
    :param new_name: New name for the window
    :type new_name: str
    :return: Rename status message
    :rtype: str
    '''
    try:
        if not new_name:
            return "Error: New name is required"
        
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build command
        target = f'{session_name}:'
        
        if window_index is not None:
            target += str(window_index)
        elif window_name:
            target += window_name
        else:
            # Rename current window
            target = session_name
        
        result = _run_tmux_command(['rename-window', '-t', target, new_name])
        
        if result.startswith("Error:"):
            return result
        
        return f"Window renamed to '{new_name}' in session '{session_name}'"
    
    except Exception as e:
        return f"Error renaming window: {str(e)}"

def tmux_split_window(session_name: str, command: str = None, split_direction: str = "vertical", 
                      working_dir: str = None, width: int = None, height: int = None) -> str:
    '''
    Split a pane in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param command: Command to run in the new pane
    :type command: str
    :param split_direction: Direction to split (horizontal or vertical)
    :type split_direction: str
    :param working_dir: Working directory for the new pane
    :type working_dir: str
    :param width: Width of new pane in columns
    :type width: int
    :param height: Height of new pane in rows
    :type height: int
    :return: Split status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build command
        args = ['split-window', '-t', session_name]
        
        if split_direction.lower() == "horizontal":
            args.append('-h')  # Horizontal split (side by side)
        else:
            args.append('-v')  # Vertical split (top and bottom) - default
        
        if working_dir:
            working_dir = os.path.expanduser(working_dir)
            if os.path.exists(working_dir) and os.path.isdir(working_dir):
                args.extend(['-c', working_dir])
            else:
                return f"Error: Working directory does not exist: {working_dir}"
        
        if width:
            args.extend(['-l', str(width)])
        
        if height:
            args.extend(['-p', str(height)])
        
        result = _run_tmux_command(args)
        
        if result.startswith("Error:"):
            return result
        
        # Send command if provided
        if command:
            # Get list of panes to find the new one
            time.sleep(0.5)
            # Send to current pane (which should be the new one)
            send_result = tmux_send_keys(session_name, command, None, None, True)
            if send_result.startswith("Error:"):
                return f"Pane split but command failed: {send_result}"
        
        return f"Pane split successfully in session '{session_name}' ({split_direction} split)"
    
    except Exception as e:
        return f"Error splitting pane: {str(e)}"

def tmux_kill_pane(session_name: str, pane_index: int = None, window_index: int = None) -> str:
    '''
    Kill a pane in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param pane_index: Index of pane to kill
    :type pane_index: int
    :param window_index: Index of window containing the pane
    :type window_index: int
    :return: Kill status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build target
        target = session_name
        if window_index is not None:
            target += f':{window_index}'
            if pane_index is not None:
                target += f'.{pane_index}'
        
        result = _run_tmux_command(['kill-pane', '-t', target])
        
        if result.startswith("Error:"):
            return result
        
        return f"Pane killed in session '{session_name}'"
    
    except Exception as e:
        return f"Error killing pane: {str(e)}"

def tmux_send_keys(session_name: str, command: str, pane_index: int = None, 
                   window_index: int = None, capture_output: bool = False) -> str:
    '''
    Send keys/commands to a tmux pane.
    
    :param session_name: Name of the session
    :type session_name: str
    :param command: Command/keys to send
    :type command: str
    :param pane_index: Index of target pane
    :type pane_index: int
    :param window_index: Index of target window
    :type window_index: int
    :param capture_output: Capture command output
    :type capture_output: bool
    :return: Command execution result
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build target
        target = session_name
        if window_index is not None:
            target += f':{window_index}'
            if pane_index is not None:
                target += f'.{pane_index}'
        
        if capture_output:
            # Run command and capture output
            # First, send the command
            send_args = ['send-keys', '-t', target, command, 'C-m']
            send_result = _run_tmux_command(send_args, capture_output=False)
            
            if send_result.startswith("Error:"):
                return send_result
            
            # Wait for command to complete
            time.sleep(1)
            
            # Capture pane content
            capture_args = ['capture-pane', '-t', target, '-p']
            output = _run_tmux_command(capture_args)
            
            if output.startswith("Error:"):
                return output
            
            # Extract the last command output (simplified approach)
            lines = output.split('\n')
            # Try to find the command in the output and get what comes after
            for i, line in enumerate(lines):
                if command in line:
                    # Return lines after the command
                    if i + 1 < len(lines):
                        return '\n'.join(lines[i+1:]).strip()
            
            return output[-1000:] if len(output) > 1000 else output  # Return last 1000 chars
        
        else:
            # Just send the keys
            args = ['send-keys', '-t', target, command, 'C-m']
            return _run_tmux_command(args, capture_output=False)
    
    except Exception as e:
        return f"Error sending keys to tmux pane: {str(e)}"

def tmux_capture_pane(session_name: str, pane_index: int = None, window_index: int = None) -> str:
    '''
    Capture the output of a tmux pane.
    
    :param session_name: Name of the session
    :type session_name: str
    :param pane_index: Index of pane to capture
    :type pane_index: int
    :param window_index: Index of window containing the pane
    :type window_index: int
    :return: Pane content
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build target
        target = session_name
        if window_index is not None:
            target += f':{window_index}'
            if pane_index is not None:
                target += f'.{pane_index}'
        
        args = ['capture-pane', '-t', target, '-p']
        output = _run_tmux_command(args)
        
        if output.startswith("Error:"):
            return output
        
        if not output:
            return "Pane is empty"
        
        # Limit output length
        if len(output) > 5000:
            output = output[:5000] + "\n... (truncated, output too long)"
        
        return output
    
    except Exception as e:
        return f"Error capturing pane content: {str(e)}"

def tmux_list_windows(session_name: str) -> str:
    '''
    List windows in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :return: List of windows with details
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Get window list
        args = ['list-windows', '-t', session_name, '-F', '#{window_index}||#{window_name}||#{window_active}||#{window_panes}']
        output = _run_tmux_command(args)
        
        if output.startswith("Error:"):
            return output
        
        windows = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('||')
                if len(parts) >= 4:
                    windows.append({
                        'index': parts[0],
                        'name': parts[1],
                        'active': parts[2] == '1',
                        'panes': parts[3]
                    })
        
        if not windows:
            return f"No windows found in session '{session_name}'"
        
        # Format output
        result = [f"Windows in session '{session_name}':"]
        result.append("-" * 70)
        result.append(f"{'Index':<6} {'Name':<20} {'Active':<8} {'Panes':<8} {'Status':<15}")
        result.append("-" * 70)
        
        for window in windows:
            index = window['index']
            name = window['name'][:18]
            active = "Yes" if window['active'] else "No"
            panes = window['panes']
            status = "Active" if window['active'] else "Inactive"
            
            result.append(f"{index:<6} {name:<20} {active:<8} {panes:<8} {status:<15}")
        
        result.append(f"\nTotal: {len(windows)} window(s)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error listing windows: {str(e)}"

def tmux_list_panes(session_name: str, window_index: int = None) -> str:
    '''
    List panes in a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :param window_index: Index of window to list panes from (default: all windows)
    :type window_index: int
    :return: List of panes with details
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        # Build target
        target = session_name
        if window_index is not None:
            target += f':{window_index}'
        
        # Get pane list
        args = ['list-panes', '-t', target, '-F', '#{pane_index}||#{window_index}||#{pane_active}||#{pane_current_command}||#{pane_width}x#{pane_height}']
        output = _run_tmux_command(args)
        
        if output.startswith("Error:"):
            return output
        
        panes = []
        for line in output.strip().split('\n'):
            if line:
                parts = line.split('||')
                if len(parts) >= 5:
                    panes.append({
                        'pane_index': parts[0],
                        'window_index': parts[1],
                        'active': parts[2] == '1',
                        'command': parts[3],
                        'dimensions': parts[4]
                    })
        
        if not panes:
            return f"No panes found in session '{session_name}'"
        
        # Format output
        result = [f"Panes in session '{session_name}':"]
        result.append("-" * 90)
        result.append(f"{'Pane':<6} {'Window':<8} {'Active':<8} {'Command':<20} {'Dimensions':<12} {'Status':<15}")
        result.append("-" * 90)
        
        for pane in panes:
            pane_idx = pane['pane_index']
            window_idx = pane['window_index']
            active = "Yes" if pane['active'] else "No"
            command = pane['command'][:18] if pane['command'] else "bash"
            dimensions = pane['dimensions'][:10]
            status = "Active" if pane['active'] else "Inactive"
            
            result.append(f"{pane_idx:<6} {window_idx:<8} {active:<8} {command:<20} {dimensions:<12} {status:<15}")
        
        result.append(f"\nTotal: {len(panes)} pane(s)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error listing panes: {str(e)}"

def tmux_switch_client(session_name: str) -> str:
    '''
    Switch client to a different session.
    
    :param session_name: Name of the session to switch to
    :type session_name: str
    :return: Switch status message
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_exists = any(session['name'] == session_name for session in sessions)
        
        if not session_exists:
            return f"Error: Session '{session_name}' does not exist"
        
        result = _run_tmux_command(['switch-client', '-t', session_name])
        
        if result.startswith("Error:"):
            return result
        
        return f"Switched to session '{session_name}'"
    
    except Exception as e:
        return f"Error switching client: {str(e)}"

def tmux_session_info(session_name: str) -> str:
    '''
    Get detailed information about a tmux session.
    
    :param session_name: Name of the session
    :type session_name: str
    :return: Detailed session information
    :rtype: str
    '''
    try:
        # Check if session exists
        sessions = _get_session_list()
        session_info = None
        for session in sessions:
            if session['name'] == session_name:
                session_info = session
                break
        
        if not session_info:
            return f"Error: Session '{session_name}' does not exist"
        
        # Get detailed session info
        details = _run_tmux_command(['display-message', '-p', '-t', session_name, 
                                     '#{session_name}||#{session_created}||#{session_attached}||#{session_windows}||#{session_width}x#{session_height}'])
        
        # Format output
        result = [f"TMUX Session Information:"]
        result.append("=" * 60)
        result.append(f"Name: {session_info['name']}")
        result.append(f"Status: {'Attached' if session_info['attached'] else 'Detached'}")
        result.append(f"Windows: {session_info['windows']}")
        result.append(f"Dimensions: {session_info['dimensions']}")
        
        if not details.startswith("Error:"):
            parts = details.split('||')
            if len(parts) >= 5:
                created_timestamp = parts[1]
                try:
                    # Convert timestamp to readable date
                    import datetime
                    created_dt = datetime.datetime.fromtimestamp(int(created_timestamp))
                    result.append(f"Created: {created_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    result.append(f"Created timestamp: {created_timestamp}")
        
        # List windows
        windows_result = tmux_list_windows(session_name)
        if not windows_result.startswith("Error:"):
            result.append("\n" + windows_result)
        
        # List panes
        panes_result = tmux_list_panes(session_name)
        if not panes_result.startswith("Error:"):
            result.append("\n" + panes_result)
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error getting session info: {str(e)}"

def tmux_run_command(session_name: str, command: str, pane_index: int = None, 
                     window_index: int = None, capture_output: bool = True) -> str:
    '''
    Run a command in a tmux session and capture output.
    
    :param session_name: Name of the session
    :type session_name: str
    :param command: Command to run
    :type command: str
    :param pane_index: Index of target pane
    :type pane_index: int
    :param window_index: Index of target window
    :type window_index: int
    :param capture_output: Capture command output
    :type capture_output: bool
    :return: Command execution result
    :rtype: str
    '''
    return tmux_send_keys(session_name, command, pane_index, window_index, capture_output)

TOOL_CALL_MAP = {
    "tmux_create_session": tmux_create_session,
    "tmux_list_sessions": tmux_list_sessions,
    "tmux_attach_session": tmux_attach_session,
    "tmux_detach_session": tmux_detach_session,
    "tmux_kill_session": tmux_kill_session,
    "tmux_rename_session": tmux_rename_session,
    "tmux_new_window": tmux_new_window,
    "tmux_kill_window": tmux_kill_window,
    "tmux_rename_window": tmux_rename_window,
    "tmux_split_window": tmux_split_window,
    "tmux_kill_pane": tmux_kill_pane,
    "tmux_send_keys": tmux_send_keys,
    "tmux_capture_pane": tmux_capture_pane,
    "tmux_list_windows": tmux_list_windows,
    "tmux_list_panes": tmux_list_panes,
    "tmux_switch_client": tmux_switch_client,
    "tmux_session_info": tmux_session_info,
    "tmux_run_command": tmux_run_command,
}