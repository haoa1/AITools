from base import function_ai, parameters_func, property_param

import os
import sys
import json
import time
import readline  # For better input handling on Unix-like systems
from typing import List, Dict, Optional, Any
import tempfile
import subprocess

__INTERACTION_PROPERTY_ONE__ = property_param(
    name="message",
    description="The message to display to the user.",
    t="string",
    required=True
)

__INTERACTION_PROPERTY_TWO__ = property_param(
    name="prompt",
    description="Prompt text to display when asking for input.",
    t="string"
)

__INTERACTION_PROPERTY_THREE__ = property_param(
    name="default_value",
    description="Default value to use if user provides no input.",
    t="string"
)

__INTERACTION_PROPERTY_4__ = property_param(
    name="choices",
    description="List of choices for user selection as JSON string.",
    t="string"
)

__INTERACTION_PROPERTY_5__ = property_param(
    name="timeout",
    description="Timeout in seconds for waiting for user input (0 for no timeout).",
    t="integer"
)

__INTERACTION_PROPERTY_6__ = property_param(
    name="file_path",
    description="Path to file for file-based interactions.",
    t="string"
)

__INTERACTION_PROPERTY_7__ = property_param(
    name="content",
    description="Content to write or display.",
    t="string"
)

__INTERACTION_PROPERTY_8__ = property_param(
    name="title",
    description="Title for dialog or display.",
    t="string"
)

__INTERACTION_PROPERTY_9__ = property_param(
    name="level",
    description="Message level (info, warning, error, success).",
    t="string"
)

__INTERACTION_PROPERTY_10__ = property_param(
    name="confirm_text",
    description="Text for confirmation dialog.",
    t="string"
)

__INTERACTION_PROPERTY_11__ = property_param(
    name="wait",
    description="Wait for user to press Enter after displaying message.",
    t="boolean"
)

__INTERACTION_PROPERTY_12__ = property_param(
    name="format",
    description="Format for displaying data (json, yaml, table, plain).",
    t="string"
)

__INTERACTION_PROPERTY_13__ = property_param(
    name="data",
    description="Data to display in various formats.",
    t="string"
)

__INTERACTION_DISPLAY_MESSAGE_FUNCTION__ = function_ai(name="display_message",
                                                      description="Display a message to the user with optional formatting and level.",
                                                      parameters=parameters_func([__INTERACTION_PROPERTY_ONE__, __INTERACTION_PROPERTY_8__, __INTERACTION_PROPERTY_9__, __INTERACTION_PROPERTY_11__, __INTERACTION_PROPERTY_12__]))

__INTERACTION_GET_INPUT_FUNCTION__ = function_ai(name="get_user_input",
                                                description="Get input from the user with a prompt.",
                                                parameters=parameters_func([__INTERACTION_PROPERTY_TWO__, __INTERACTION_PROPERTY_THREE__, __INTERACTION_PROPERTY_5__]))

__INTERACTION_SELECT_CHOICE_FUNCTION__ = function_ai(name="select_from_choices",
                                                    description="Present a list of choices for the user to select from.",
                                                    parameters=parameters_func([__INTERACTION_PROPERTY_ONE__, __INTERACTION_PROPERTY_4__, __INTERACTION_PROPERTY_THREE__, __INTERACTION_PROPERTY_5__]))

__INTERACTION_CONFIRM_ACTION_FUNCTION__ = function_ai(name="confirm_action",
                                                     description="Ask the user to confirm an action.",
                                                     parameters=parameters_func([__INTERACTION_PROPERTY_10__, __INTERACTION_PROPERTY_THREE__, __INTERACTION_PROPERTY_5__]))

__INTERACTION_DISPLAY_DATA_FUNCTION__ = function_ai(name="display_data",
                                                   description="Display data in various formats (JSON, table, etc.).",
                                                   parameters=parameters_func([__INTERACTION_PROPERTY_13__, __INTERACTION_PROPERTY_8__, __INTERACTION_PROPERTY_12__, __INTERACTION_PROPERTY_11__]))

__INTERACTION_OPEN_EDITOR_FUNCTION__ = function_ai(name="open_text_editor",
                                                  description="Open a text editor for user input with optional initial content.",
                                                  parameters=parameters_func([__INTERACTION_PROPERTY_7__, __INTERACTION_PROPERTY_8__, __INTERACTION_PROPERTY_6__]))

__INTERACTION_PROGRESS_BAR_FUNCTION__ = function_ai(name="show_progress",
                                                   description="Show a progress bar for long-running operations.",
                                                   parameters=parameters_func([__INTERACTION_PROPERTY_ONE__, __INTERACTION_PROPERTY_7__]))

__INTERACTION_LOG_MESSAGE_FUNCTION__ = function_ai(name="log_message",
                                                  description="Log a message to a file with timestamp.",
                                                  parameters=parameters_func([__INTERACTION_PROPERTY_ONE__, __INTERACTION_PROPERTY_6__, __INTERACTION_PROPERTY_9__]))

tools = [
    __INTERACTION_DISPLAY_MESSAGE_FUNCTION__,
    __INTERACTION_GET_INPUT_FUNCTION__,
    __INTERACTION_SELECT_CHOICE_FUNCTION__,
    __INTERACTION_CONFIRM_ACTION_FUNCTION__,
    __INTERACTION_DISPLAY_DATA_FUNCTION__,
    __INTERACTION_OPEN_EDITOR_FUNCTION__,
    __INTERACTION_PROGRESS_BAR_FUNCTION__,
    __INTERACTION_LOG_MESSAGE_FUNCTION__,
]

def _parse_choices(choices_str: str) -> List[str]:
    """Parse choices from JSON string or comma-separated string."""
    if not choices_str:
        return []
    
    try:
        choices = json.loads(choices_str)
        if isinstance(choices, list):
            return choices
        else:
            return [str(choices)]
    except json.JSONDecodeError:
        # Try comma-separated
        return [choice.strip() for choice in choices_str.split(',') if choice.strip()]

def _format_message(message: str, title: str = None, level: str = "info") -> str:
    """Format message with title and level indicators."""
    level_colors = {
        "info": "\033[94m",      # Blue
        "success": "\033[92m",   # Green
        "warning": "\033[93m",   # Yellow
        "error": "\033[91m",     # Red
    }
    
    level_symbols = {
        "info": "[INFO]",
        "success": "[SUCCESS]",
        "warning": "[WARNING]",
        "error": "[ERROR]",
    }
    
    color = level_colors.get(level, "\033[94m")
    symbol = level_symbols.get(level, "[INFO]")
    reset = "\033[0m"
    
    lines = []
    
    if title:
        lines.append(f"\n{color}{'=' * 60}{reset}")
        lines.append(f"{color}{title.center(60)}{reset}")
        lines.append(f"{color}{'=' * 60}{reset}")
    
    lines.append(f"{color}{symbol}{reset} {message}")
    
    return "\n".join(lines)

def display_message(message: str, title: str = None, level: str = "info", 
                    wait: bool = False, format: str = "plain") -> str:
    '''
    Display a message to the user with optional formatting and level.
    
    :param message: Message to display
    :type message: str
    :param title: Title for the message display
    :type title: str
    :param level: Message level (info, warning, error, success)
    :type level: str
    :param wait: Wait for user to press Enter after displaying
    :type wait: bool
    :param format: Format for display (json, yaml, table, plain)
    :type format: str
    :return: Confirmation that message was displayed
    :rtype: str
    '''
    try:
        # Format message based on format type
        if format == "json":
            try:
                parsed = json.loads(message)
                formatted_message = json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                formatted_message = message
        elif format == "table":
            # Simple table formatting for list of dictionaries
            try:
                data = json.loads(message)
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    headers = list(data[0].keys())
                    rows = [[str(item.get(h, '')) for h in headers] for item in data]
                    
                    # Calculate column widths
                    col_widths = [len(h) for h in headers]
                    for row in rows:
                        for i, cell in enumerate(row):
                            col_widths[i] = max(col_widths[i], len(cell))
                    
                    # Build table
                    table_lines = []
                    # Header
                    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
                    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
                    table_lines.append(header_line)
                    table_lines.append(separator)
                    
                    # Rows
                    for row in rows:
                        row_line = " | ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))
                        table_lines.append(row_line)
                    
                    formatted_message = "\n".join(table_lines)
                else:
                    formatted_message = message
            except:
                formatted_message = message
        else:
            formatted_message = message
        
        # Add formatting
        final_message = _format_message(formatted_message, title, level)
        
        # Print to console
        print(final_message)
        
        if wait:
            input("\nPress Enter to continue...")
        
        return f"Message displayed successfully (level: {level})"
        
    except Exception as e:
        return f"Error displaying message: {str(e)}"

def get_user_input(prompt: str = "Enter value: ", default_value: str = None, 
                   timeout: int = 0) -> str:
    '''
    Get input from the user with a prompt.
    
    :param prompt: Prompt text to display
    :type prompt: str
    :param default_value: Default value if user provides no input
    :type default_value: str
    :param timeout: Timeout in seconds (0 for no timeout)
    :type timeout: int
    :return: User input or default value
    :rtype: str
    '''
    try:
        # Build prompt with default value
        full_prompt = prompt
        if default_value is not None:
            full_prompt = f"{prompt} [{default_value}]: "
        else:
            full_prompt = f"{prompt}: "
        
        print(full_prompt, end='', flush=True)
        
        # Handle timeout
        if timeout > 0:
            import select
            import sys
            
            # Wait for input with timeout
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                user_input = sys.stdin.readline().strip()
            else:
                print(f"\nTimeout after {timeout} seconds, using default value.")
                user_input = ""
        else:
            # No timeout
            user_input = input().strip()
        
        # Use default if no input
        if not user_input and default_value is not None:
            user_input = default_value
        
        return user_input
        
    except KeyboardInterrupt:
        return "\nInput interrupted by user"
    except Exception as e:
        return f"Error getting user input: {str(e)}"

def select_from_choices(message: str, choices: str, default_value: str = None, 
                        timeout: int = 0) -> str:
    '''
    Present a list of choices for the user to select from.
    
    :param message: Message explaining the choices
    :type message: str
    :param choices: List of choices as JSON string or comma-separated string
    :type choices: str
    :param default_value: Default choice index or value
    :type default_value: str
    :param timeout: Timeout in seconds (0 for no timeout)
    :type timeout: int
    :return: Selected choice or error message
    :rtype: str
    '''
    try:
        choice_list = _parse_choices(choices)
        
        if not choice_list:
            return "Error: No choices provided"
        
        # Display message and choices
        print(_format_message(message, None, "info"))
        print("\nAvailable choices:")
        
        for i, choice in enumerate(choice_list, 1):
            print(f"  {i}. {choice}")
        
        # Determine default index
        default_index = None
        if default_value:
            try:
                # Try as index
                default_index = int(default_value)
                if 1 <= default_index <= len(choice_list):
                    print(f"\nDefault choice: {default_index} ({choice_list[default_index-1]})")
            except ValueError:
                # Try as value
                if default_value in choice_list:
                    default_index = choice_list.index(default_value) + 1
                    print(f"\nDefault choice: {default_index} ({default_value})")
        
        # Get user selection
        prompt = f"\nEnter choice number (1-{len(choice_list)})"
        if default_index:
            prompt += f" [default: {default_index}]"
        prompt += ": "
        
        selected = get_user_input(prompt, str(default_index) if default_index else None, timeout)
        
        if not selected:
            return "Error: No selection made"
        
        # Parse selection
        try:
            selected_index = int(selected)
            if 1 <= selected_index <= len(choice_list):
                selected_choice = choice_list[selected_index - 1]
                return f"Selected: {selected_choice}"
            else:
                return f"Error: Invalid choice number {selected_index}. Must be between 1 and {len(choice_list)}"
        except ValueError:
            # Maybe user entered the choice directly
            if selected in choice_list:
                return f"Selected: {selected}"
            else:
                return f"Error: '{selected}' is not a valid choice"
                
    except KeyboardInterrupt:
        return "Selection interrupted by user"
    except Exception as e:
        return f"Error presenting choices: {str(e)}"

def confirm_action(confirm_text: str = "Are you sure?", default_value: str = "no", 
                   timeout: int = 0) -> str:
    '''
    Ask the user to confirm an action.
    
    :param confirm_text: Text for confirmation dialog
    :type confirm_text: str
    :param default_value: Default response (yes/no)
    :type default_value: str
    :param timeout: Timeout in seconds (0 for no timeout)
    :type timeout: int
    :return: Confirmation result (yes/no) or error
    :rtype: str
    '''
    try:
        default = default_value.lower() if default_value else "no"
        if default not in ["yes", "no", "y", "n"]:
            default = "no"
        
        # Build prompt
        prompt = f"{confirm_text} (yes/no)"
        if default in ["yes", "y"]:
            prompt += " [Y/n]: "
            default_display = "yes"
        else:
            prompt += " [y/N]: "
            default_display = "no"
        
        response = get_user_input(prompt, default_display, timeout).lower()
        
        if response in ["yes", "y"]:
            return "Confirmed: yes"
        elif response in ["no", "n"]:
            return "Confirmed: no"
        else:
            return f"Error: Invalid response '{response}'. Please answer yes or no."
            
    except KeyboardInterrupt:
        return "Confirmation interrupted by user"
    except Exception as e:
        return f"Error getting confirmation: {str(e)}"

def display_data(data: str, title: str = None, format: str = "json", 
                 wait: bool = False) -> str:
    '''
    Display data in various formats (JSON, table, etc.).
    
    :param data: Data to display (JSON string for structured data)
    :type data: str
    :param title: Title for the display
    :type title: str
    :param format: Format for display (json, yaml, table, plain)
    :type format: str
    :param wait: Wait for user to press Enter after displaying
    :type wait: bool
    :return: Confirmation that data was displayed
    :rtype: str
    '''
    try:
        # Try to parse as JSON if needed
        parsed_data = None
        if format in ["json", "table", "yaml"]:
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                # Not JSON, use as plain text
                format = "plain"
        
        # Format based on format type
        if format == "json" and parsed_data:
            formatted = json.dumps(parsed_data, indent=2, ensure_ascii=False)
        elif format == "table" and parsed_data:
            # Already handled in display_message
            return display_message(data, title, "info", wait, "table")
        elif format == "yaml" and parsed_data:
            try:
                import yaml
                formatted = yaml.dump(parsed_data, default_flow_style=False)
            except ImportError:
                formatted = "YAML format requires PyYAML package. Installing with: pip install pyyaml\n\n" + json.dumps(parsed_data, indent=2)
        else:
            formatted = data
        
        return display_message(formatted, title, "info", wait, "plain")
        
    except Exception as e:
        return f"Error displaying data: {str(e)}"

def open_text_editor(content: str = None, title: str = None, 
                     file_path: str = None) -> str:
    '''
    Open a text editor for user input with optional initial content.
    
    :param content: Initial content for the editor
    :type content: str
    :param title: Title/suggested filename
    :type title: str
    :param file_path: Specific file path to edit (optional)
    :type file_path: str
    :return: Edited content or error message
    :rtype: str
    '''
    try:
        # Determine editor
        editor = os.environ.get('EDITOR', 'vi')
        
        # Create temp file if no file path provided
        if file_path:
            temp_file = file_path
            if not os.path.exists(temp_file):
                with open(temp_file, 'w') as f:
                    f.write(content or '')
        else:
            # Create temp file with title as hint
            prefix = "edit_"
            if title:
                # Sanitize title for filename
                import re
                safe_title = re.sub(r'[^\w\-_]', '_', title)[:30]
                prefix = f"edit_{safe_title}_"
            
            with tempfile.NamedTemporaryFile(mode='w', prefix=prefix, suffix='.txt', delete=False) as f:
                temp_file = f.name
                if content:
                    f.write(content)
        
        # Open editor
        try:
            subprocess.run([editor, temp_file], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error opening editor: {str(e)}"
        except FileNotFoundError:
            # Try alternative editors
            for alt_editor in ['nano', 'vim', 'vi', 'emacs']:
                try:
                    subprocess.run([alt_editor, temp_file], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                return "Error: No text editor found. Please set EDITOR environment variable."
        
        # Read edited content
        with open(temp_file, 'r') as f:
            edited_content = f.read()
        
        # Clean up temp file if we created it
        if not file_path:
            os.unlink(temp_file)
        
        return f"Editor closed. Content:\n\n{edited_content}"
        
    except PermissionError as e:
        return f"Error: Permission denied: {str(e)}"
    except Exception as e:
        return f"Error opening text editor: {str(e)}"

def show_progress(message: str, total: str = None) -> str:
    '''
    Show a progress bar for long-running operations.
    
    :param message: Message to display with progress
    :type message: str
    :param total: Total steps or percentage as string (e.g., "50" or "50%")
    :type total: str
    :return: Progress display status
    :rtype: str
    '''
    try:
        # Parse total
        is_percentage = False
        progress_value = 0
        
        if total:
            if total.endswith('%'):
                is_percentage = True
                progress_value = float(total.rstrip('%'))
            else:
                try:
                    progress_value = float(total)
                except ValueError:
                    progress_value = 0
        
        # Simple progress display
        if is_percentage and progress_value >= 0:
            bar_length = 40
            filled = int(bar_length * progress_value / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r{message}: [{bar}] {progress_value:.1f}%", end='', flush=True)
            
            if progress_value >= 100:
                print()  # New line when complete
        else:
            # Simple message with spinner
            import itertools
            import sys
            import threading
            import time as time_module
            
            spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
            stop_spinner = False
            
            def spin():
                while not stop_spinner:
                    sys.stdout.write(f'\r{message} {next(spinner)}')
                    sys.stdout.flush()
                    time_module.sleep(0.1)
            
            spinner_thread = threading.Thread(target=spin)
            spinner_thread.start()
            
            # Return immediately - caller should call again to update or stop
            # For now, just sleep a bit to show spinner
            time_module.sleep(1)
            stop_spinner = True
            spinner_thread.join()
            print(f'\r{message} ✓', ' ' * 20)
        
        return f"Progress displayed: {message}"
        
    except Exception as e:
        return f"Error showing progress: {str(e)}"

def log_message(message: str, file_path: str = None, level: str = "info") -> str:
    '''
    Log a message to a file with timestamp.
    
    :param message: Message to log
    :type message: str
    :param file_path: Path to log file (default: ./interaction.log)
    :type file_path: str
    :param level: Log level (info, warning, error, success)
    :type level: str
    :return: Logging status message
    :rtype: str
    '''
    try:
        if not file_path:
            file_path = "interaction.log"
        
        # Ensure directory exists
        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Format log entry
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level.upper()}] {message}\n"
        
        # Write to log file
        with open(file_path, 'a') as f:
            f.write(log_entry)
        
        return f"Message logged to {file_path}"
        
    except PermissionError as e:
        return f"Error: Permission denied writing to log file: {str(e)}"
    except Exception as e:
        return f"Error logging message: {str(e)}"

TOOL_CALL_MAP = {
    "display_message": display_message,
    "get_user_input": get_user_input,
    "select_from_choices": select_from_choices,
    "confirm_action": confirm_action,
    "display_data": display_data,
    "open_text_editor": open_text_editor,
    "show_progress": show_progress,
    "log_message": log_message,
}