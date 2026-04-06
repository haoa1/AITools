#!/usr/bin/env python3
"""
ExitPlanModeV2Tool implementation for AITools (Claude Code compatible version - simplified).
Provides plan mode exit functionality aligned with Claude Code's ExitPlanModeV2Tool.
Based on analysis of Claude Code source: restored-src/src/tools/ExitPlanModeTool/ExitPlanModeV2Tool.ts
Simplified version focusing on basic plan mode exit confirmation.
"""

import os
import json
import uuid
from base import function_ai, parameters_func, property_param

# Property definitions for ExitPlanModeV2Tool
__ALLOWED_PROMPTS_PROPERTY__ = property_param(
    name="allowedPrompts",
    description="Prompt-based permissions needed to implement the plan. These describe categories of actions rather than specific commands.",
    t="array",
    required=False,
)

__PLAN_PROPERTY__ = property_param(
    name="plan",
    description="The plan content (injected by normalizeToolInput from disk)",
    t="string",
    required=False,
)

__PLAN_FILE_PATH_PROPERTY__ = property_param(
    name="planFilePath",
    description="The plan file path (injected by normalizeToolInput)",
    t="string",
    required=False,
)

# Function metadata
__EXIT_PLAN_MODE_V2_TOOL_FUNCTION__ = function_ai(
    name="exit_plan_mode_v2_tool",
    description="Prompt the user to exit plan mode and start coding. Compatible with Claude Code's ExitPlanModeV2Tool (simplified version).",
    parameters=parameters_func([
        __ALLOWED_PROMPTS_PROPERTY__,
        __PLAN_PROPERTY__,
        __PLAN_FILE_PATH_PROPERTY__,
    ]),
)

tools = [__EXIT_PLAN_MODE_V2_TOOL_FUNCTION__]


def exit_plan_mode_v2_tool(allowedPrompts: list = None, plan: str = None, planFilePath: str = None) -> str:
    """
    Prompt the user to exit plan mode and start coding.
    
    Claude Code compatible version based on ExitPlanModeV2Tool.ts:
    - allowedPrompts: Prompt-based permissions needed to implement the plan (optional)
    - plan: The plan content (optional, for simplified implementation)
    - planFilePath: The plan file path (optional)
    
    Returns JSON matching Claude Code's ExitPlanModeV2Tool output schema (simplified).
    Simplified implementation: simulates plan mode exit without actual mode management.
    
    Core functionality in Claude Code:
    1. For teammates requiring leader approval: sends approval request
    2. For non-teammates: requires user confirmation to exit plan mode
    3. Updates tool permission context mode from 'plan' to previous mode
    
    Simplified implementation:
    1. Returns basic success response with plan information
    2. Simulates plan mode exit (no actual mode management)
    3. Returns Claude Code compatible output structure
    """
    try:
        # Parse allowedPrompts if provided as JSON string
        parsed_allowed_prompts = None
        if allowedPrompts:
            if isinstance(allowedPrompts, str):
                try:
                    parsed_allowed_prompts = json.loads(allowedPrompts)
                except:
                    parsed_allowed_prompts = allowedPrompts
            else:
                parsed_allowed_prompts = allowedPrompts
        
        # Get plan content from file if planFilePath provided but plan is None
        resolved_plan = plan
        resolved_file_path = planFilePath
        
        if planFilePath and not plan:
            try:
                if os.path.exists(planFilePath):
                    with open(planFilePath, 'r', encoding='utf-8') as f:
                        resolved_plan = f.read()
                else:
                    # Simulate a default plan if file doesn't exist
                    resolved_plan = "# Plan\n\nPlan details not found in file.\n\n## Implementation Steps\n1. Analyze requirements\n2. Design solution\n3. Implement code\n4. Test and verify"
            except Exception as e:
                resolved_plan = f"# Plan\n\nError reading plan file: {str(e)}"
        
        # If no plan provided, create a simulated plan
        if not resolved_plan:
            resolved_plan = "# Plan\n\n## Overview\nThis is a simulated plan for ExitPlanModeV2Tool demonstration.\n\n## Implementation Steps\n1. Analyze requirements and constraints\n2. Design architecture and components\n3. Write implementation code\n4. Test and validate results\n5. Document and deploy"
        
        # Generate a request ID if needed (for approval scenario)
        request_id = str(uuid.uuid4())[:8]
        
        # Simulate different scenarios based on simplified logic
        # In real implementation, this would check if in teammate mode, etc.
        
        # Simplified: Always assume successful exit (no teammate/leader approval)
        is_agent = False  # Simplified: not in agent context
        has_task_tool = True  # Simplified: assume Agent tool is available
        plan_was_edited = False  # Simplified: no plan editing tracking
        awaiting_leader_approval = False  # Simplified: no teammate mode
        
        # Build Claude Code compatible response
        response = {
            "plan": resolved_plan,
            "isAgent": is_agent,
            "hasTaskTool": has_task_tool,
            "planWasEdited": plan_was_edited,
            "awaitingLeaderApproval": awaiting_leader_approval,
            "_metadata": {
                "success": True,
                "simplifiedImplementation": True,
                "note": "Plan mode exit simulated. No actual mode management in this simplified version.",
                "allowedPrompts": parsed_allowed_prompts
            }
        }
        
        # Add file path if provided
        if resolved_file_path:
            response["filePath"] = resolved_file_path
        
        # Add request ID if awaiting approval (not in this simplified case)
        if awaiting_leader_approval:
            response["requestId"] = request_id
        
        # Remove None values for cleaner output
        response = {k: v for k, v in response.items() if v is not None}
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Exit plan mode failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "exit_plan_mode_v2_tool": exit_plan_mode_v2_tool
}


if __name__ == "__main__":
    # Test the exit_plan_mode_v2_tool function
    print("Testing ExitPlanModeV2Tool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Basic exit plan mode
    print("1. Basic exit plan mode:")
    result = exit_plan_mode_v2_tool()
    data = json.loads(result)
    
    print(f"   Has plan: {'plan' in data}")
    print(f"   Plan length: {len(data.get('plan', ''))}")
    print(f"   isAgent: {data.get('isAgent')}")
    print(f"   hasTaskTool: {data.get('hasTaskTool')}")
    print(f"   planWasEdited: {data.get('planWasEdited')}")
    print(f"   awaitingLeaderApproval: {data.get('awaitingLeaderApproval')}")
    
    # Test 2: Check Claude Code compatibility
    print("\n2. Claude Code compatibility check:")
    expected_fields = ["plan", "isAgent"]
    
    missing_fields = [field for field in expected_fields if field not in data]
    
    if missing_fields:
        print(f"   Missing required fields: {missing_fields}")
    else:
        print("   All required fields present ✓")
    
    # Test 3: Test with allowedPrompts
    print("\n3. Test with allowedPrompts:")
    allowed_prompts = [
        {"tool": "Bash", "prompt": "run tests"},
        {"tool": "FileEdit", "prompt": "update configuration files"}
    ]
    result3 = exit_plan_mode_v2_tool(allowedPrompts=allowed_prompts)
    data3 = json.loads(result3)
    print(f"   Success: {'error' not in data3}")
    print(f"   Metadata includes allowedPrompts: {'allowedPrompts' in data3.get('_metadata', {})}")
    
    # Test 4: Test with plan content
    print("\n4. Test with plan content:")
    test_plan = "# Test Plan\n\n## Goal\nTest the ExitPlanModeV2Tool implementation.\n\n## Steps\n1. Write test code\n2. Run tests\n3. Verify results"
    result4 = exit_plan_mode_v2_tool(plan=test_plan)
    data4 = json.loads(result4)
    print(f"   Plan matches input: {data4.get('plan', '').startswith('# Test Plan')}")
    
    # Test 5: Test with plan file path
    print("\n5. Test with plan file path:")
    # Create a temporary plan file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("# Plan from File\n\nThis plan was loaded from a file.\n\n## Details\nFile-based plan content.")
        temp_file = f.name
    
    result5 = exit_plan_mode_v2_tool(planFilePath=temp_file)
    data5 = json.loads(result5)
    print(f"   Has filePath: {'filePath' in data5}")
    print(f"   Plan from file: {'Plan from File' in data5.get('plan', '')}")
    
    # Clean up temp file
    os.unlink(temp_file)
    
    print("\n" + "=" * 60)
    print("ExitPlanModeV2Tool test completed.")