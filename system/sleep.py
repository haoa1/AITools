from base import function_ai, parameters_func, property_param
import time

__SLEEP_PROPERTY_ONE__ = property_param(
    name="seconds",
    description="Number of seconds to sleep.",
    t="number",
    required=True,
)

__SLEEP_PROPERTY_TWO__ = property_param(
    name="milliseconds",
    description="Number of milliseconds to sleep (alternative to seconds).",
    t="number",
)

__SLEEP_PROPERTY_THREE__ = property_param(
    name="minutes",
    description="Number of minutes to sleep (alternative to seconds).",
    t="number",
)

__SLEEP_FUNCTION__ = function_ai(
    name="sleep",
    description="Pause execution for a specified duration. Useful for waiting between operations or implementing delays.",
    parameters=parameters_func(
        [
            __SLEEP_PROPERTY_ONE__,
            __SLEEP_PROPERTY_TWO__,
            __SLEEP_PROPERTY_THREE__,
        ]
    ),
)

tools = [__SLEEP_FUNCTION__]


def sleep(seconds: float = None, milliseconds: float = None, minutes: float = None) -> str:
    """
    Pause execution for a specified duration.
    
    Args:
        seconds: Number of seconds to sleep
        milliseconds: Number of milliseconds to sleep
        minutes: Number of minutes to sleep
    
    Returns:
        Confirmation message with actual sleep duration
    """
    # Calculate total sleep time in seconds
    total_seconds = 0
    
    if seconds is not None:
        if seconds < 0:
            return "Error: Sleep duration cannot be negative"
        total_seconds += seconds
    
    if milliseconds is not None:
        if milliseconds < 0:
            return "Error: Sleep duration cannot be negative"
        total_seconds += milliseconds / 1000.0
    
    if minutes is not None:
        if minutes < 0:
            return "Error: Sleep duration cannot be negative"
        total_seconds += minutes * 60.0
    
    # Check if any duration was provided
    if total_seconds == 0:
        return "Error: No sleep duration specified. Provide seconds, milliseconds, or minutes"
    
    # Check for excessively long sleep (more than 1 hour)
    if total_seconds > 3600:
        return f"Error: Sleep duration too long ({total_seconds:.1f} seconds > 1 hour). Maximum allowed is 1 hour."
    
    # Check for very short sleep (less than 0.001 seconds)
    if total_seconds < 0.001:
        return f"Error: Sleep duration too short ({total_seconds:.6f} seconds < 1ms). Minimum allowed is 1 millisecond."
    
    # Perform sleep
    try:
        time.sleep(total_seconds)
        
        # Format duration for output
        if total_seconds < 1:
            duration_str = f"{total_seconds * 1000:.1f} milliseconds"
        elif total_seconds < 60:
            duration_str = f"{total_seconds:.2f} seconds"
        else:
            minutes = total_seconds / 60.0
            if minutes < 60:
                duration_str = f"{minutes:.2f} minutes"
            else:
                hours = minutes / 60.0
                duration_str = f"{hours:.2f} hours"
        
        return f"Successfully slept for {duration_str} ({total_seconds:.3f} seconds)"
    
    except KeyboardInterrupt:
        return "Sleep interrupted by user"
    except Exception as e:
        return f"Error during sleep: {str(e)}"


TOOL_CALL_MAP = {
    "sleep": sleep,
}