#!/usr/bin/env python3
"""
AgentTool implementation for AITools (Claude Code compatible version - simplified).
Provides agent mode functionality aligned with Claude Code's AgentTool.
Based on analysis of Claude Code source: restored-src/src/tools/AgentTool/AgentTool.tsx
Simplified version focusing on core synchronous execution.
"""

import os
import json
import uuid
import time
from base import function_ai, parameters_func, property_param

# Property definitions for AgentTool
__DESCRIPTION_PROPERTY__ = property_param(
    name="description",
    description="A short (3-5 word) description of the task",
    t="string",
    required=True,
)

__PROMPT_PROPERTY__ = property_param(
    name="prompt",
    description="The task for the agent to perform",
    t="string",
    required=True,
)

__SUBAGENT_TYPE_PROPERTY__ = property_param(
    name="subagent_type",
    description="The type of specialized agent to use for this task",
    t="string",
    required=False,
)

__MODEL_PROPERTY__ = property_param(
    name="model",
    description="Optional model override for this agent. Takes precedence over the agent definition's model frontmatter. If omitted, uses the agent definition's model, or inherits from the parent.",
    t="string",
    required=False,
)

__RUN_IN_BACKGROUND_PROPERTY__ = property_param(
    name="run_in_background",
    description="Set to true to run this agent in the background. You will be notified when it completes.",
    t="boolean",
    required=False,
)

__NAME_PROPERTY__ = property_param(
    name="name",
    description="Name for the spawned agent. Makes it addressable via SendMessage({to: name}) while running.",
    t="string",
    required=False,
)

__TEAM_NAME_PROPERTY__ = property_param(
    name="team_name",
    description="Team name for spawning. Uses current team context if omitted.",
    t="string",
    required=False,
)

__MODE_PROPERTY__ = property_param(
    name="mode",
    description="Permission mode for spawned teammate (e.g., 'plan' to require plan approval).",
    t="string",
    required=False,
)

__ISOLATION_PROPERTY__ = property_param(
    name="isolation",
    description='Isolation mode. "worktree" creates a temporary git worktree so the agent works on an isolated copy of the repo.',
    t="string",
    required=False,
)

__CWD_PROPERTY__ = property_param(
    name="cwd",
    description="Absolute path to run the agent in. Overrides the working directory for all filesystem and shell operations within this agent. Mutually exclusive with isolation: 'worktree'.",
    t="string",
    required=False,
)

# Function metadata
__AGENT_TOOL_FUNCTION__ = function_ai(
    name="agent_tool",
    description="Execute a task using agent mode. Compatible with Claude Code's AgentTool (simplified version).",
    parameters=parameters_func([
        __DESCRIPTION_PROPERTY__,
        __PROMPT_PROPERTY__,
        __SUBAGENT_TYPE_PROPERTY__,
        __MODEL_PROPERTY__,
        __RUN_IN_BACKGROUND_PROPERTY__,
        __NAME_PROPERTY__,
        __TEAM_NAME_PROPERTY__,
        __MODE_PROPERTY__,
        __ISOLATION_PROPERTY__,
        __CWD_PROPERTY__,
    ]),
)

tools = [__AGENT_TOOL_FUNCTION__]


def agent_tool(description: str, prompt: str, subagent_type: str = None,
               model: str = None, run_in_background: bool = False,
               name: str = None, team_name: str = None, mode: str = None,
               isolation: str = None, cwd: str = None) -> str:
    """
    Execute a task using agent mode.
    
    Claude Code compatible version based on AgentTool/AgentTool.tsx:
    - description: Short description of the task (3-5 words)
    - prompt: The task for the agent to perform
    - subagent_type: Type of specialized agent (simplified: not implemented)
    - model: Model override (simplified: not implemented)
    - run_in_background: Run in background (simplified: warning only)
    - name: Agent name (simplified: used for identification)
    - team_name: Team name (simplified: not implemented)
    - mode: Permission mode (simplified: not implemented)
    - isolation: Isolation mode (simplified: not implemented)
    - cwd: Working directory (simplified: not implemented)
    
    Returns JSON matching Claude Code's AgentTool output schema (simplified).
    Only supports synchronous execution (status: 'completed').
    """
    try:
        # Validate inputs
        if not description or not isinstance(description, str):
            return json.dumps({
                "error": "Description must be a non-empty string",
                "success": False
            }, indent=2)
        
        if not prompt or not isinstance(prompt, str):
            return json.dumps({
                "error": "Prompt must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Check for background execution request
        background_warning = None
        if run_in_background:
            background_warning = "Background execution requested but not fully implemented in this simplified version"
        
        # Check for unsupported features
        unsupported_features = []
        if subagent_type:
            unsupported_features.append(f"subagent_type: '{subagent_type}'")
        if model:
            unsupported_features.append(f"model: '{model}'")
        if team_name:
            unsupported_features.append(f"team_name: '{team_name}'")
        if mode:
            unsupported_features.append(f"mode: '{mode}'")
        if isolation:
            unsupported_features.append(f"isolation: '{isolation}'")
        if cwd:
            unsupported_features.append(f"cwd: '{cwd}'")
        
        # Generate agent ID
        agent_id = str(uuid.uuid4())[:8]
        
        # Use provided name or generate one
        agent_name = name or f"agent_{agent_id}"
        
        # Track start time for duration calculation
        start_time = time.time()
        
        # In this simplified implementation, we'll simulate agent execution
        # by analyzing the prompt and generating a simulated response
        # In a real implementation, this would actually execute the task
        
        # Simulate some processing time
        time.sleep(0.1)  # Small delay to simulate processing
        
        # Generate simulated content based on prompt
        # This is a placeholder - real implementation would execute the task
        simulated_content = [
            {
                "type": "text",
                "text": f"Executed task: {description}\n\nPrompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n\n"
            }
        ]
        
        # Add note about simplified implementation
        simulated_content[0]["text"] += "\nNote: This is a simplified AgentTool implementation. In the full Claude Code version, the agent would actually execute the task using available tools."
        
        # Add warnings for unsupported features
        if unsupported_features:
            warning_text = f"\n\nSimplified implementation notes:\n- The following features are not fully implemented: {', '.join(unsupported_features)}"
            simulated_content[0]["text"] += warning_text
        
        if background_warning:
            simulated_content[0]["text"] += f"\n- {background_warning}"
        
        # Calculate execution metrics
        total_duration_ms = int((time.time() - start_time) * 1000)
        
        # Simulated metrics (in real implementation, these would be actual counts)
        total_tool_use_count = 0  # Simplified: no tool usage tracked
        total_tokens = len(prompt) + len(simulated_content[0]["text"])  # Rough estimate
        
        # Build Claude Code compatible response (synchronous completion)
        response = {
            "status": "completed",
            "agentId": agent_id,
            "agentType": subagent_type or "general",
            "content": simulated_content,
            "totalToolUseCount": total_tool_use_count,
            "totalDurationMs": total_duration_ms,
            "totalTokens": total_tokens,
            "usage": {
                "input_tokens": len(prompt),
                "output_tokens": len(simulated_content[0]["text"]),
                "cache_creation_input_tokens": None,
                "cache_read_input_tokens": None,
                "server_tool_use": None,
                "service_tier": None,
                "cache_creation": None
            },
            "prompt": prompt,
            "description": description
        }
        
        # Add optional fields if provided
        if name:
            response["name"] = name
        
        # Add metadata (not part of Claude Code spec but useful)
        response["_metadata"] = {
            "success": True,
            "agentName": agent_name,
            "simplifiedImplementation": True,
            "timestamp": time.time(),
            "unsupportedFeatures": unsupported_features if unsupported_features else None
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Agent execution failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "agent_tool": agent_tool
}


if __name__ == "__main__":
    # Test the agent_tool function
    print("Testing AgentTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Simple agent task
    print("1. Simple agent task:")
    result = agent_tool(
        description="Test agent task",
        prompt="Please analyze the current directory and list all Python files",
        name="test_agent"
    )
    data = json.loads(result)
    
    print(f"Status: {data.get('status')}")
    print(f"Agent ID: {data.get('agentId')}")
    print(f"Agent Type: {data.get('agentType')}")
    print(f"Has content: {'content' in data}")
    print(f"Total tool use count: {data.get('totalToolUseCount')}")
    print(f"Total duration (ms): {data.get('totalDurationMs')}")
    print(f"Total tokens: {data.get('totalTokens')}")
    
    # Test 2: Check Claude Code compatibility
    print("\n2. Claude Code compatibility check:")
    expected_fields = ["status", "agentId", "content", "totalToolUseCount", 
                      "totalDurationMs", "totalTokens", "usage", "prompt"]
    missing_fields = [field for field in expected_fields if field not in data]
    
    if missing_fields:
        print(f"  Missing fields: {missing_fields}")
    else:
        print("  All expected fields present ✓")
    
    # Test 3: Test with unsupported features
    print("\n3. Test with unsupported features:")
    result3 = agent_tool(
        description="Test with features",
        prompt="Test task",
        subagent_type="specialized",
        model="opus",
        run_in_background=True,
        isolation="worktree"
    )
    data3 = json.loads(result3)
    print(f"Status: {data3.get('status')}")
    
    print("\n" + "=" * 60)
    print("AgentTool test completed.")