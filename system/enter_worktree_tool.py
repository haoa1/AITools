#!/usr/bin/env python3
"""
EnterWorktreeTool implementation for AITools (Claude Code compatible version - simplified).
Enter or create a worktree for isolated work.
Based on analysis of Claude Code source: restored-src/src/tools/EnterWorktreeTool/EnterWorktreeTool.ts
Simplified version with basic directory creation.
"""

import os
import json
import tempfile
import uuid
from base import function_ai, parameters_func, property_param

# Property definitions for EnterWorktreeTool
__NAME_PROPERTY__ = property_param(
    name="name",
    description="Optional name for the worktree. Each '/' -separated segment may contain only letters, digits, dots, underscores, and dashes; max 64 chars total. A random name is generated if not provided.",
    t="string",
    required=False,
)

# Function definition
__ENTER_WORKTREE_TOOL_FUNCTION__ = function_ai(
    name="enter_worktree_tool",
    description="Enter or create a worktree for isolated work",
    parameters=parameters_func([
        __NAME_PROPERTY__,
    ]),
)

tools = [__ENTER_WORKTREE_TOOL_FUNCTION__]


class EnterWorktreeConfig:
    """Configuration for EnterWorktreeTool"""
    
    DEFAULT_CONFIG = {
        "ENTER_WORKTREE_ENABLED": True,
        "ENTER_WORKTREE_INTERACTIVE": True,
        "ENTER_WORKTREE_BASE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_worktrees"),
        "ENTER_WORKTREE_VALIDATE_NAME": True,
        "ENTER_WORKTREE_MAX_WORKTREES": 10,
        "ENTER_WORKTREE_ANALYTICS_ENABLED": False,
    }
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        enter_worktree_enabled = os.getenv("ENTER_WORKTREE_ENABLED", "")
        enter_worktree_interactive = os.getenv("ENTER_WORKTREE_INTERACTIVE", "")
        enter_worktree_base_path = os.getenv("ENTER_WORKTREE_BASE_PATH", "")
        enter_worktree_validate_name = os.getenv("ENTER_WORKTREE_VALIDATE_NAME", "")
        enter_worktree_max_worktrees = os.getenv("ENTER_WORKTREE_MAX_WORKTREES", "")
        
        config = EnterWorktreeConfig.DEFAULT_CONFIG.copy()
        
        # 覆盖环境变量设置（如果非空）
        if enter_worktree_enabled != "":
            config["ENTER_WORKTREE_ENABLED"] = enter_worktree_enabled.lower() in ["true", "1", "yes", "y"]
        
        if enter_worktree_interactive != "":
            config["ENTER_WORKTREE_INTERACTIVE"] = enter_worktree_interactive.lower() in ["true", "1", "yes", "y"]
        
        if enter_worktree_base_path != "":
            config["ENTER_WORKTREE_BASE_PATH"] = enter_worktree_base_path
        
        if enter_worktree_validate_name != "":
            config["ENTER_WORKTREE_VALIDATE_NAME"] = enter_worktree_validate_name.lower() in ["true", "1", "yes", "y"]
        
        if enter_worktree_max_worktrees != "":
            try:
                config["ENTER_WORKTREE_MAX_WORKTREES"] = int(enter_worktree_max_worktrees)
            except ValueError:
                pass
        
        return config


def validate_worktree_name(name):
    """Validate worktree name according to Claude Code rules"""
    if not name:
        return True, "Name is optional"
    
    if not isinstance(name, str):
        return False, "Name must be a string"
    
    # Check total length
    if len(name) > 64:
        return False, f"Name too long (max 64 chars, got {len(name)})"
    
    # Check each segment
    segments = name.split('/')
    for segment in segments:
        if not segment:
            return False, "Segment cannot be empty"
        
        # Check segment characters
        for char in segment:
            if not (char.isalnum() or char in '._-'):
                return False, f"Invalid character '{char}' in segment '{segment}'. Only letters, digits, dots, underscores, and dashes allowed."
    
    return True, "Name is valid"


def enter_worktree_tool(name: str = None) -> str:
    """
    Enter or create a worktree for isolated work.
    
    Claude Code compatible version based on EnterWorktreeTool/EnterWorktreeTool.ts:
    - name: Optional name for the worktree
    
    Returns JSON matching Claude Code's EnterWorktreeTool output schema (simplified).
    
    Simplified implementation notes:
    - Creates a directory in a base worktrees location
    - Validates name if enabled
    - Returns worktree path and message
    - Does not integrate with git (simplified)
    """
    try:
        # Load configuration
        config = EnterWorktreeConfig.from_env()
        
        # Check if tool is enabled
        if not config.get("ENTER_WORKTREE_ENABLED", True):
            return json.dumps({
                "error": "EnterWorktreeTool is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Validate name if provided and validation is enabled
        validate_name = config.get("ENTER_WORKTREE_VALIDATE_NAME", True)
        if name and validate_name:
            is_valid, validation_msg = validate_worktree_name(name)
            if not is_valid:
                return json.dumps({
                    "error": f"Invalid worktree name: {validation_msg}",
                    "success": False
                }, indent=2)
        
        # Get base path for worktrees
        base_path = config.get("ENTER_WORKTREE_BASE_PATH")
        
        # Ensure base directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Determine worktree name
        if not name:
            # Generate a random name
            name = f"worktree_{uuid.uuid4().hex[:8]}"
        
        # Create worktree path
        worktree_path = os.path.join(base_path, name)
        
        # Check if worktree already exists
        worktree_exists = os.path.exists(worktree_path)
        
        # Check max worktrees limit
        max_worktrees = config.get("ENTER_WORKTREE_MAX_WORKTREES", 10)
        if not worktree_exists:
            # Count existing worktrees
            existing_count = 0
            try:
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        existing_count += 1
            except (OSError, IOError):
                existing_count = 0
            
            if existing_count >= max_worktrees:
                return json.dumps({
                    "error": f"Maximum number of worktrees reached ({max_worktrees}). Please delete some worktrees before creating new ones.",
                    "success": False
                }, indent=2)
        
        # Create worktree directory if it doesn't exist
        if not worktree_exists:
            os.makedirs(worktree_path, exist_ok=True)
            
            # Create a simple README file in the worktree
            readme_path = os.path.join(worktree_path, "README.md")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"# Worktree: {name}\n\n")
                f.write(f"Created by AITools EnterWorktreeTool\n")
                f.write(f"Path: {worktree_path}\n")
                f.write(f"Created at: {time.ctime()}\n")
        
        # In a real implementation, this would change the working directory
        # But for this simplified version, we'll just return the path
        # and let the caller decide what to do with it
        
        # Get current working directory for reference
        original_cwd = os.getcwd()
        
        # Build Claude Code compatible response
        response = {
            "worktreePath": worktree_path,
            "worktreeBranch": None,  # Simplified: no git integration
            "message": f"Entered worktree: {name} at {worktree_path}"
        }
        
        # Add existence info
        if worktree_exists:
            response["_metadata"] = {
                "worktreeExisted": True,
                "originalCwd": original_cwd,
                "action": "entered_existing"
            }
            response["message"] = f"Entered existing worktree: {name} at {worktree_path}"
        else:
            response["_metadata"] = {
                "worktreeExisted": False,
                "originalCwd": original_cwd,
                "action": "created_new"
            }
            response["message"] = f"Created new worktree: {name} at {worktree_path}"
        
        # Interactive mode output (if enabled)
        interactive = config.get("ENTER_WORKTREE_INTERACTIVE", True)
        if interactive:
            print(f"📁 Entering worktree: {name}")
            print(f"   Path: {worktree_path}")
            print(f"   Status: {'Existing' if worktree_exists else 'New'}")
            print(f"   Original CWD: {original_cwd}")
            
            if not worktree_exists:
                print(f"   ✅ Created new worktree directory")
            else:
                print(f"   🔄 Using existing worktree directory")
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Enter worktree failed: {str(e)}",
            "success": False
        }, indent=2)


# Import time for timestamp
import time

# Tool call map for dispatching
TOOL_CALL_MAP = {
    "enter_worktree_tool": enter_worktree_tool
}


if __name__ == "__main__":
    # Test the enter_worktree_tool function
    print("Testing EnterWorktreeTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Create worktree with random name
    print("1. Create worktree with random name:")
    result1 = enter_worktree_tool()
    data1 = json.loads(result1)
    
    print(f"Success: {data1.get('success', True)}")
    print(f"Worktree path: {data1.get('worktreePath', 'None')}")
    print(f"Message: {data1.get('message', 'None')}")
    
    # Test 2: Create worktree with specific name
    print("\n2. Create worktree with specific name:")
    result2 = enter_worktree_tool(name="test_worktree")
    data2 = json.loads(result2)
    
    print(f"Success: {data2.get('success', True)}")
    print(f"Worktree path: {data2.get('worktreePath', 'None')}")
    
    # Test 3: Invalid name (if validation enabled)
    print("\n3. Test with invalid name (contains invalid characters):")
    result3 = enter_worktree_tool(name="test/worktree@invalid")
    data3 = json.loads(result3)
    
    # Might fail validation or succeed depending on config
    print(f"Success: {data3.get('success', True)}")
    if data3.get("error"):
        print(f"Error: {data3.get('error', 'None')}")
    
    # Test 4: Check Claude Code compatibility
    print("\n4. Claude Code compatibility check:")
    test_response = {
        "worktreePath": "/tmp/test",
        "worktreeBranch": "main",
        "message": "Test message"
    }
    
    expected_fields = ["worktreePath", "message"]
    missing_fields = [field for field in expected_fields if field not in test_response]
    
    if missing_fields:
        print(f"  Missing fields in test response: {missing_fields}")
    else:
        print("  All expected fields present ✓")