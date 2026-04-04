from base import function_ai, parameters_func, property_param
import os
import json
import tempfile
from typing import Any, Optional

__SETTING_PROPERTY__ = property_param(
    name="setting",
    description="The setting key to get or set (e.g., 'theme', 'model', 'timeout', 'default_path').",
    t="string",
    required=True,
)

__VALUE_PROPERTY__ = property_param(
    name="value",
    description="The new value for the setting. Omit to get current value. Can be string, number, or boolean.",
    t="string",
)

__CONFIG_FUNCTION__ = function_ai(
    name="config",
    description="Get or set configuration values. Similar to Claude Code's ConfigTool, this manages application settings with persistence. Configuration is saved to a JSON file.",
    parameters=parameters_func(
        [__SETTING_PROPERTY__, __VALUE_PROPERTY__]
    ),
)

tools = [__CONFIG_FUNCTION__]

# Configuration file path
_CONFIG_FILE = os.path.join(tempfile.gettempdir(), "aitools_config.json")

def _load_config() -> dict:
    """Load configuration from file."""
    if not os.path.exists(_CONFIG_FILE):
        return {}
    
    try:
        with open(_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_config(config: dict) -> bool:
    """Save configuration to file."""
    try:
        with open(_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False

def _parse_value(value_str: str) -> Any:
    """Parse string value to appropriate type (bool, int, float, or string)."""
    if not value_str:
        return value_str
    
    # Try to parse as boolean
    if value_str.lower() in ('true', 'false'):
        return value_str.lower() == 'true'
    
    # Try to parse as integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try to parse as float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Return as string
    return value_str

def _format_value(value: Any) -> str:
    """Format value for display."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value)

def config(setting: str, value: Optional[str] = None) -> str:
    """
    Get or set configuration values.
    
    Args:
        setting: The setting key to get or set
        value: The new value (omit to get current value)
    
    Returns:
        Formatted string with operation result
    """
    if not setting:
        return "Error: Setting key cannot be empty"
    
    # Load current configuration
    current_config = _load_config()
    
    # GET operation
    if value is None or value == "":
        if setting in current_config:
            current_value = current_config[setting]
            formatted_value = _format_value(current_value)
            return f"Setting '{setting}' = {formatted_value}"
        else:
            return f"Setting '{setting}' is not set (default or unconfigured)"
    
    # SET operation
    try:
        # Parse the value
        parsed_value = _parse_value(value)
        
        # Store previous value for message
        previous_value = current_config.get(setting)
        
        # Update configuration
        current_config[setting] = parsed_value
        
        # Save to file
        if _save_config(current_config):
            previous_str = _format_value(previous_value) if previous_value is not None else "unset"
            new_str = _format_value(parsed_value)
            return f"Setting '{setting}' updated: {previous_str} → {new_str}"
        else:
            return f"Error: Failed to save configuration to {_CONFIG_FILE}"
    
    except Exception as e:
        return f"Error: Failed to set configuration: {str(e)}"

TOOL_CALL_MAP = {
    "config": config,
}