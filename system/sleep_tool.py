#!/usr/bin/env python3
"""
SleepTool implementation for AITools (Claude Code compatible version - simplified).
Provides sleep/wait functionality aligned with Claude Code's SleepTool.
Based on analysis of Claude Code source: restored-src/src/tools/SleepTool/
Simplified version focusing on basic sleep/wait functionality.
"""

import time
import json
from base import function_ai, parameters_func, property_param

# Property definitions for SleepTool
__DURATION_PROPERTY__ = property_param(
    name="duration",
    description="Duration to sleep in seconds",
    t="integer",
    required=True,
)

__UNIT_PROPERTY__ = property_param(
    name="unit",
    description="Time unit (default: 'seconds', other values may include 'minutes', 'hours')",
    t="string",
    required=False,
)

__REASON_PROPERTY__ = property_param(
    name="reason",
    description="Reason for sleeping (optional)",
    t="string",
    required=False,
)

# Function metadata
__SLEEP_TOOL_FUNCTION__ = function_ai(
    name="sleep_tool",
    description="Wait for a specified duration. Compatible with Claude Code's SleepTool (simplified version).",
    parameters=parameters_func([
        __DURATION_PROPERTY__,
        __UNIT_PROPERTY__,
        __REASON_PROPERTY__,
    ]),
)

tools = [__SLEEP_TOOL_FUNCTION__]


def sleep_tool(duration: int, unit: str = "seconds", reason: str = None) -> str:
    """
    Wait for a specified duration.
    
    Claude Code compatible version based on SleepTool analysis:
    - duration: Duration to sleep (required, in seconds by default)
    - unit: Time unit (optional, default 'seconds')
    - reason: Reason for sleeping (optional)
    
    Returns JSON matching Claude Code's SleepTool output schema (simplified).
    Simplified implementation: uses time.sleep() for the specified duration.
    
    Core functionality in Claude Code:
    1. Allows AI to wait/sleep for specified time
    2. Can be interrupted by user
    3. Useful when waiting for processes or when nothing to do
    4. Preferred over Bash(sleep) to avoid holding shell process
    
    Simplified implementation:
    1. Uses time.sleep() for the duration
    2. Returns success status and timing information
    3. No interrupt handling (simplified)
    4. Supports basic time units conversion
    """
    try:
        # Validate inputs
        if not isinstance(duration, (int, float)) or duration <= 0:
            return json.dumps({
                "error": "Duration must be a positive number",
                "success": False
            }, indent=2)
        
        # Convert duration based on unit
        unit_lower = unit.lower() if unit else "seconds"
        actual_duration = float(duration)
        
        if unit_lower == "minutes":
            actual_duration *= 60
        elif unit_lower == "hours":
            actual_duration *= 3600
        elif unit_lower == "milliseconds":
            actual_duration /= 1000
        elif unit_lower != "seconds":
            # Default to seconds for unknown units
            pass
        
        # Limit maximum sleep time for safety (simplified: 5 minutes max)
        max_duration = 300  # 5 minutes in seconds
        if actual_duration > max_duration:
            return json.dumps({
                "error": f"Duration too long (max {max_duration} seconds)",
                "success": False,
                "requested_duration": actual_duration,
                "max_allowed": max_duration
            }, indent=2)
        
        # Record start time
        start_time = time.time()
        
        # Sleep for the specified duration
        time.sleep(actual_duration)
        
        # Calculate actual sleep time
        end_time = time.time()
        actual_sleep_time = end_time - start_time
        
        # Build Claude Code compatible response
        response = {
            "success": True,
            "duration": actual_duration,
            "unit": unit_lower,
            "actualSleepTime": actual_sleep_time,
            "startTime": start_time,
            "endTime": end_time,
            "reason": reason,
            "_metadata": {
                "simplifiedImplementation": True,
                "note": "Sleep executed. No interrupt handling in this simplified version.",
                "maxDurationEnforced": f"{max_duration} seconds"
            }
        }
        
        # Remove None values for cleaner output
        response = {k: v for k, v in response.items() if v is not None}
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Sleep failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "sleep_tool": sleep_tool
}


if __name__ == "__main__":
    # Test the sleep_tool function
    print("Testing SleepTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Basic sleep (short duration)
    print("1. Basic sleep (1 second):")
    start = time.time()
    result = sleep_tool(duration=1)
    elapsed = time.time() - start
    
    data = json.loads(result)
    print(f"   Success: {data.get('success')}")
    print(f"   Duration: {data.get('duration')}")
    print(f"   Unit: {data.get('unit')}")
    print(f"   Actual sleep time: {data.get('actualSleepTime'):.2f}s")
    print(f"   Measured elapsed: {elapsed:.2f}s")
    print(f"   Has metadata: {'_metadata' in data}")
    
    # Test 2: Check Claude Code compatibility
    print("\n2. Claude Code compatibility check:")
    expected_fields = ["success", "duration", "unit", "actualSleepTime"]
    
    missing_fields = [field for field in expected_fields if field not in data]
    
    if missing_fields:
        print(f"   Missing required fields: {missing_fields}")
    else:
        print("   All required fields present ✓")
    
    # Test 3: Test with unit parameter
    print("\n3. Test with minutes unit (0.05 minutes = 3 seconds):")
    start = time.time()
    result3 = sleep_tool(duration=0.05, unit="minutes")
    elapsed3 = time.time() - start
    
    data3 = json.loads(result3)
    print(f"   Success: {data3.get('success')}")
    print(f"   Duration in minutes: {data3.get('duration')}")
    print(f"   Unit: {data3.get('unit')}")
    print(f"   Actual sleep time: {data3.get('actualSleepTime'):.2f}s")
    print(f"   Should be ~3s: {2.5 < elapsed3 < 3.5}")
    
    # Test 4: Test with reason
    print("\n4. Test with reason:")
    result4 = sleep_tool(duration=0.5, reason="Waiting for process completion")
    data4 = json.loads(result4)
    print(f"   Success: {data4.get('success')}")
    print(f"   Reason: {data4.get('reason')}")
    
    # Test 5: Test error handling
    print("\n5. Test error handling (negative duration):")
    result5 = sleep_tool(duration=-1)
    data5 = json.loads(result5)
    print(f"   Success: {data5.get('success', 'field not found')}")
    print(f"   Has error: {'error' in data5}")
    
    # Test 6: Test max duration enforcement
    print("\n6. Test max duration enforcement (request 400 seconds > 300 max):")
    result6 = sleep_tool(duration=400)
    data6 = json.loads(result6)
    print(f"   Success: {data6.get('success', 'field not found')}")
    print(f"   Has error: {'error' in data6}")
    if 'error' in data6:
        print(f"   Error message includes 'too long': {'too long' in data6['error'].lower()}")
    
    print("\n" + "=" * 60)
    print("SleepTool test completed.")