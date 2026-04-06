#!/usr/bin/env python3
"""
SkillTool implementation for AITools (Claude Code compatible version - simplified).
Provides skill execution functionality aligned with Claude Code's SkillTool.
Based on analysis of Claude Code source: restored-src/src/tools/SkillTool/SkillTool.ts
Simplified version focusing on inline skill information retrieval.
"""

import os
import json
import yaml
import re
from base import function_ai, parameters_func, property_param
from typing import List, Dict, Optional, Tuple

# Import existing skill functions - use absolute import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill.skill import (
    _get_skills_base_path,
    _parse_markdown_sections,
    get_skill_by_name,
    load_skill_by_name,
    ai_get_available_skills,
    ai_load_skill
)

# Property definitions for SkillTool
__SKILL_PROPERTY__ = property_param(
    name="skill",
    description='The skill name. E.g., "commit", "review-pr", or "pdf"',
    t="string",
    required=True,
)

__ARGS_PROPERTY__ = property_param(
    name="args",
    description="Optional arguments for the skill",
    t="string",
    required=False,
)

# Function metadata
__SKILL_TOOL_FUNCTION__ = function_ai(
    name="skill_tool",
    description="Execute a skill or retrieve skill information. Compatible with Claude Code's SkillTool (simplified version).",
    parameters=parameters_func([
        __SKILL_PROPERTY__,
        __ARGS_PROPERTY__,
    ]),
)

tools = [__SKILL_TOOL_FUNCTION__]


def _extract_frontmatter_and_content(content: str) -> Tuple[Optional[Dict], str]:
    """
    Extract YAML frontmatter from skill content.
    Returns (frontmatter_dict, content_without_frontmatter)
    """
    # Check for YAML frontmatter pattern: ---\n...\n---
    frontmatter_match = re.match(r'^---\s*\n(.*?\n)---\s*\n', content, re.DOTALL)
    
    if frontmatter_match:
        frontmatter_text = frontmatter_match.group(1)
        content_without_frontmatter = content[frontmatter_match.end():]
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, content_without_frontmatter
        except yaml.YAMLError:
            # If YAML parsing fails, return no frontmatter
            return None, content
    else:
        return None, content


def _extract_allowed_tools_from_frontmatter(frontmatter: Optional[Dict]) -> Optional[List[str]]:
    """
    Extract allowed tools from skill frontmatter.
    Claude Code skills may have 'tools' or 'allowed_tools' in frontmatter.
    """
    if not frontmatter:
        return None
    
    # Check for tools in various possible fields
    tools = frontmatter.get('tools')
    if tools:
        if isinstance(tools, str):
            return [tools]
        elif isinstance(tools, list):
            return tools
    
    allowed_tools = frontmatter.get('allowed_tools')
    if allowed_tools:
        if isinstance(allowed_tools, str):
            return [allowed_tools]
        elif isinstance(allowed_tools, list):
            return allowed_tools
    
    return None


def _extract_model_from_frontmatter(frontmatter: Optional[Dict]) -> Optional[str]:
    """
    Extract model override from skill frontmatter.
    """
    if not frontmatter:
        return None
    
    # Check for model in various possible fields
    model = frontmatter.get('model')
    if model and isinstance(model, str):
        return model
    
    # Also check for model in other common fields
    for field in ['model_override', 'llm_model', 'claude_model']:
        model = frontmatter.get(field)
        if model and isinstance(model, str):
            return model
    
    return None


def skill_tool(skill: str, args: str = None) -> str:
    """
    Execute a skill or retrieve skill information.
    
    Claude Code compatible version based on SkillTool/SkillTool.ts:
    - skill: The skill name (required)
    - args: Optional arguments for the skill (simplified: appended to content)
    
    Returns JSON matching Claude Code's SkillTool output schema (simplified).
    Only supports inline mode (status: 'inline'), not forked execution.
    
    Simplified implementation:
    1. Loads skill content using existing AITools skill system
    2. Extracts frontmatter information (tools, model override)
    3. Returns skill information in Claude Code compatible format
    4. If args provided, appends them to the content
    """
    try:
        # Validate inputs
        if not skill or not isinstance(skill, str):
            return json.dumps({
                "error": "Skill name must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Get skill info using existing AITools function
        try:
            skill_info_str = get_skill_by_name(skill_name=skill)
            # get_skill_by_name returns a string representation of a dict
            import ast
            skill_info = ast.literal_eval(skill_info_str)
            
            # Check if it's an error
            if isinstance(skill_info, dict) and "error" in skill_info:
                return json.dumps({
                    "error": f"Skill '{skill}' not found: {skill_info.get('error')}",
                    "success": False
                }, indent=2)
                
        except Exception as e:
            return json.dumps({
                "error": f"Failed to get skill info for '{skill}': {str(e)}",
                "success": False
            }, indent=2)
        
        # Get skill content
        try:
            skill_content = load_skill_by_name(skill_name=skill, max_sections=None)
            # load_skill_by_name returns content as string
        except Exception as e:
            return json.dumps({
                "error": f"Failed to load skill content for '{skill}': {str(e)}",
                "success": False
            }, indent=2)
        
        # Parse frontmatter from skill content
        frontmatter, content_without_frontmatter = _extract_frontmatter_and_content(skill_content)
        
        # Extract allowed tools from frontmatter
        allowed_tools = _extract_allowed_tools_from_frontmatter(frontmatter)
        
        # Extract model override from frontmatter
        model_override = _extract_model_from_frontmatter(frontmatter)
        
        # Handle args if provided
        final_content = skill_content
        if args:
            final_content = f"{skill_content}\n\n## Arguments Provided:\n{args}"
        
        # Build Claude Code compatible response (inline mode)
        response = {
            "success": True,
            "commandName": skill,
            "status": "inline",
            "content": final_content,
            "allowedTools": allowed_tools,
            "model": model_override,
            "_metadata": {
                "simplifiedImplementation": True,
                "executionMode": "inline_only",
                "note": "Forked execution not implemented in this simplified version"
            }
        }
        
        # Add args if provided
        if args:
            response["args"] = args
        
        # Add frontmatter if found
        if frontmatter:
            response["frontmatter"] = frontmatter
        
        # Remove None values for cleaner output
        response = {k: v for k, v in response.items() if v is not None}
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Skill execution failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "skill_tool": skill_tool
}


if __name__ == "__main__":
    # Test the skill_tool function
    print("Testing SkillTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Create a test skill directory and file
    print("1. Creating test skill...")
    skills_dir = _get_skills_base_path()
    test_skill_dir = os.path.join(skills_dir, "test_skill")
    os.makedirs(test_skill_dir, exist_ok=True)
    
    test_skill_content = """---
name: test_skill
description: A test skill for SkillTool testing
tools: [file_read, file_write]
model: claude-3-5-sonnet
---
# Test Skill

This is a test skill for SkillTool implementation testing.

## Usage

This skill demonstrates the SkillTool functionality.
"""
    
    test_skill_file = os.path.join(test_skill_dir, "SKILL.md")
    with open(test_skill_file, "w") as f:
        f.write(test_skill_content)
    
    print(f"   Created test skill at: {test_skill_file}")
    
    # Test with the test skill
    print(f"\n2. Testing skill_tool with test skill:")
    result = skill_tool(skill="test_skill")
    data = json.loads(result)
    
    print(f"   Success: {data.get('success')}")
    print(f"   Command name: {data.get('commandName')}")
    print(f"   Status: {data.get('status')}")
    print(f"   Has content: {'content' in data}")
    print(f"   Content length: {len(data.get('content', ''))}")
    print(f"   Allowed tools: {data.get('allowedTools')}")
    print(f"   Model: {data.get('model')}")
    
    # Test 3: Check Claude Code compatibility
    print("\n3. Claude Code compatibility check:")
    # Required fields for Claude Code SkillTool output
    required_fields = ["success", "commandName", "status"]
    
    # For inline mode, content is also required
    if data.get("status") == "inline":
        required_fields.append("content")
    
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"   Missing required fields: {missing_fields}")
    else:
        print("   All required fields present ✓")
    
    # Optional fields (nice to have)
    optional_fields = ["allowedTools", "model", "args", "frontmatter"]
    present_optional = [field for field in optional_fields if field in data]
    if present_optional:
        print(f"   Optional fields present: {present_optional}")
    
    # Test 4: Test with args
    print("\n4. Test with arguments:")
    result4 = skill_tool(skill="test_skill", args="--test argument")
    data4 = json.loads(result4)
    print(f"   Success: {data4.get('success')}")
    print(f"   Args: {data4.get('args')}")
    print(f"   Content includes args: {'Arguments Provided' in data4.get('content', '')}")
    
    # Test 5: Test with non-existent skill
    print("\n5. Test with non-existent skill:")
    result5 = skill_tool(skill="non_existent_skill_12345")
    data5 = json.loads(result5)
    print(f"   Success: {data5.get('success', 'field not found')}")
    print(f"   Has error: {'error' in data5}")
    
    print("\n" + "=" * 60)
    print("SkillTool test completed.")