#!/usr/bin/env python3
"""
SyntheticOutputTool implementation for AITools (Claude Code compatible version - simplified).
Returns structured output in requested format.
Based on analysis of Claude Code source: restored-src/src/tools/SyntheticOutputTool/SyntheticOutputTool.ts
Simplified version with basic JSON validation.
"""

import os
import json
from base import function_ai, parameters_func, property_param

# SyntheticOutputTool has dynamic schema, so we accept any object
# In base module, we need to define parameters, but can use a generic object
# We'll use a string parameter that contains JSON

__STRUCTURED_OUTPUT_PROPERTY__ = property_param(
    name="structured_output",
    description="Structured output to return (JSON string)",
    t="string",
    required=True,
)

# Function definition
__SYNTHETIC_OUTPUT_TOOL_FUNCTION__ = function_ai(
    name="synthetic_output_tool",
    description="Return structured output in the requested format",
    parameters=parameters_func([
        __STRUCTURED_OUTPUT_PROPERTY__,
    ]),
)

tools = [__SYNTHETIC_OUTPUT_TOOL_FUNCTION__]


class SyntheticOutputConfig:
    """Configuration for SyntheticOutputTool"""
    
    DEFAULT_CONFIG = {
        "SYNTHETIC_OUTPUT_ENABLED": True,
        "SYNTHETIC_OUTPUT_INTERACTIVE": True,
        "SYNTHETIC_OUTPUT_VALIDATE_JSON": True,
        "SYNTHETIC_OUTPUT_MAX_SIZE_KB": 100,  # 100KB max output size
        "SYNTHETIC_OUTPUT_ANALYTICS_ENABLED": False,
    }
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        synthetic_output_enabled = os.getenv("SYNTHETIC_OUTPUT_ENABLED", "")
        synthetic_output_interactive = os.getenv("SYNTHETIC_OUTPUT_INTERACTIVE", "")
        synthetic_output_validate_json = os.getenv("SYNTHETIC_OUTPUT_VALIDATE_JSON", "")
        synthetic_output_max_size_kb = os.getenv("SYNTHETIC_OUTPUT_MAX_SIZE_KB", "")
        
        config = SyntheticOutputConfig.DEFAULT_CONFIG.copy()
        
        # 覆盖环境变量设置（如果非空）
        if synthetic_output_enabled != "":
            config["SYNTHETIC_OUTPUT_ENABLED"] = synthetic_output_enabled.lower() in ["true", "1", "yes", "y"]
        
        if synthetic_output_interactive != "":
            config["SYNTHETIC_OUTPUT_INTERACTIVE"] = synthetic_output_interactive.lower() in ["true", "1", "yes", "y"]
        
        if synthetic_output_validate_json != "":
            config["SYNTHETIC_OUTPUT_VALIDATE_JSON"] = synthetic_output_validate_json.lower() in ["true", "1", "yes", "y"]
        
        if synthetic_output_max_size_kb != "":
            try:
                config["SYNTHETIC_OUTPUT_MAX_SIZE_KB"] = int(synthetic_output_max_size_kb)
            except ValueError:
                pass
        
        return config


def synthetic_output_tool(structured_output: str) -> str:
    """
    Return structured output in the requested format.
    
    Claude Code compatible version based on SyntheticOutputTool/SyntheticOutputTool.ts:
    - structured_output: JSON string containing the structured output
    
    Returns the structured output as a JSON string (validated).
    
    Simplified implementation notes:
    - Validates JSON structure if enabled
    - Returns the validated JSON as a string
    - Used for returning final response in structured format
    """
    try:
        # Load configuration
        config = SyntheticOutputConfig.from_env()
        
        # Check if tool is enabled
        if not config.get("SYNTHETIC_OUTPUT_ENABLED", True):
            return json.dumps({
                "error": "SyntheticOutputTool is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Validate input
        if not structured_output or not isinstance(structured_output, str):
            return json.dumps({
                "error": "Structured output must be a non-empty JSON string",
                "success": False
            }, indent=2)
        
        # Check size limit
        max_size_kb = config.get("SYNTHETIC_OUTPUT_MAX_SIZE_KB", 100)
        if len(structured_output) > max_size_kb * 1024:
            return json.dumps({
                "error": f"Structured output too large (max {max_size_kb}KB)",
                "success": False
            }, indent=2)
        
        # Validate JSON if enabled
        validate_json = config.get("SYNTHETIC_OUTPUT_VALIDATE_JSON", True)
        parsed_data = None
        if validate_json:
            try:
                parsed_data = json.loads(structured_output)
                # Re-serialize to ensure valid JSON
                structured_output = json.dumps(parsed_data, separators=(',', ':'))
            except json.JSONDecodeError as e:
                return json.dumps({
                    "error": f"Invalid JSON in structured output: {str(e)}",
                    "success": False
                }, indent=2)
            except Exception as e:
                # Catch any other exception during JSON parsing
                return json.dumps({
                    "error": f"Error parsing JSON: {str(e)}",
                    "success": False
                }, indent=2)
        
        # Interactive mode output (if enabled)
        interactive = config.get("SYNTHETIC_OUTPUT_INTERACTIVE", True)
        if interactive:
            print("📋 Returning structured output")
            
            # Determine output type for display
            output_type = "raw string"
            if parsed_data is not None:
                output_type = type(parsed_data).__name__
            else:
                # Try to parse just for display (if validation is disabled)
                try:
                    parsed_display = json.loads(structured_output)
                    output_type = type(parsed_display).__name__
                except:
                    # Can't parse, remains "raw string"
                    pass
            
            print(f"   Output type: {output_type}")
            
            # Show preview
            if len(structured_output) > 200:
                preview = structured_output[:200] + "..."
                print(f"   Preview: {preview}")
            else:
                print(f"   Content: {structured_output}")
        
        # Return the structured output string
        # Claude Code expects the output to be a string (the structured output)
        return structured_output
        
    except Exception as e:
        return json.dumps({
            "error": f"Synthetic output failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "synthetic_output_tool": synthetic_output_tool
}


if __name__ == "__main__":
    # Test the synthetic_output_tool function
    print("Testing SyntheticOutputTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Valid JSON
    print("1. Valid JSON output:")
    test_json = json.dumps({"result": "success", "data": [1, 2, 3]})
    result1 = synthetic_output_tool(test_json)
    
    try:
        parsed = json.loads(result1)
        print(f"Success: Valid JSON returned")
        print(f"Content: {result1[:100]}...")
    except:
        print(f"Raw output: {result1[:100]}...")
    
    # Test 2: Invalid JSON
    print("\n2. Invalid JSON output:")
    result2 = synthetic_output_tool("{ invalid json")
    data2 = json.loads(result2)
    
    print(f"Success: {data2.get('success', True)}")
    print(f"Error: {data2.get('error', 'None')}")
    
    # Test 3: Empty output
    print("\n3. Empty output:")
    result3 = synthetic_output_tool("")
    data3 = json.loads(result3)
    
    print(f"Success: {data3.get('success', True)}")
    print(f"Error: {data3.get('error', 'None')}")
    
    # Test 4: Check Claude Code compatibility
    print("\n4. Claude Code compatibility check:")
    # The tool should return the structured output directly (not wrapped)
    test_output = '{"test": "value"}'
    result4 = synthetic_output_tool(test_output)
    
    try:
        parsed = json.loads(result4)
        print("  Returns valid JSON directly ✓")
    except:
        print("  Does not return valid JSON")