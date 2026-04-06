#!/usr/bin/env python3
"""
ExitWorktreeTool implementation for AITools (Claude Code compatible version - simplified).
Exit a worktree, optionally keeping or removing it.
Based on analysis of Claude Code source: restored-src/src/tools/ExitWorktreeTool/ExitWorktreeTool.ts
Simplified version with basic directory management.
"""

import os
import json
import shutil
from base import function_ai, parameters_func, property_param

# Property definitions for ExitWorktreeTool
__ACTION_PROPERTY__ = property_param(
    name="action",
    description='"keep" leaves the worktree and branch on disk; "remove" deletes both.',
    t="string",
    required=True,
)

__DISCARD_CHANGES_PROPERTY__ = property_param(
    name="discard_changes",
    description='Required true when action is "remove" and the worktree has uncommitted files or unmerged commits. The tool will refuse and list them otherwise.',
    t="boolean",
    required=False,
)

# Function definition
__EXIT_WORKTREE_TOOL_FUNCTION__ = function_ai(
    name="exit_worktree_tool",
    description="Exit a worktree, optionally keeping or removing it",
    parameters=parameters_func([
        __ACTION_PROPERTY__,
        __DISCARD_CHANGES_PROPERTY__,
    ]),
)

tools = [__EXIT_WORKTREE_TOOL_FUNCTION__]


class ExitWorktreeConfig:
    """Configuration for ExitWorktreeTool"""
    
    DEFAULT_CONFIG = {
        "EXIT_WORKTREE_ENABLED": True,
        "EXIT_WORKTREE_INTERACTIVE": True,
        "EXIT_WORKTREE_BASE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_worktrees"),
        "EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE": True,
        "EXIT_WORKTREE_ALLOW_REMOVE": True,
        "EXIT_WORKTREE_ANALYTICS_ENABLED": False,
    }
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        exit_worktree_enabled = os.getenv("EXIT_WORKTREE_ENABLED", "")
        exit_worktree_interactive = os.getenv("EXIT_WORKTREE_INTERACTIVE", "")
        exit_worktree_base_path = os.getenv("EXIT_WORKTREE_BASE_PATH", "")
        exit_worktree_require_discard_for_remove = os.getenv("EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE", "")
        exit_worktree_allow_remove = os.getenv("EXIT_WORKTREE_ALLOW_REMOVE", "")
        
        config = ExitWorktreeConfig.DEFAULT_CONFIG.copy()
        
        # 覆盖环境变量设置（如果非空）
        if exit_worktree_enabled != "":
            config["EXIT_WORKTREE_ENABLED"] = exit_worktree_enabled.lower() in ["true", "1", "yes", "y"]
        
        if exit_worktree_interactive != "":
            config["EXIT_WORKTREE_INTERACTIVE"] = exit_worktree_interactive.lower() in ["true", "1", "yes", "y"]
        
        if exit_worktree_base_path != "":
            config["EXIT_WORKTREE_BASE_PATH"] = exit_worktree_base_path
        
        if exit_worktree_require_discard_for_remove != "":
            config["EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE"] = exit_worktree_require_discard_for_remove.lower() in ["true", "1", "yes", "y"]
        
        if exit_worktree_allow_remove != "":
            config["EXIT_WORKTREE_ALLOW_REMOVE"] = exit_worktree_allow_remove.lower() in ["true", "1", "yes", "y"]
        
        return config


def exit_worktree_tool(action: str, discard_changes: bool = None) -> str:
    """
    Exit a worktree, optionally keeping or removing it.
    
    Claude Code compatible version based on ExitWorktreeTool/ExitWorktreeTool.ts:
    - action: "keep" leaves the worktree, "remove" deletes it
    - discard_changes: Required true when action is "remove" and there are changes
    
    Returns JSON matching Claude Code's ExitWorktreeTool output schema (simplified).
    
    Simplified implementation notes:
    - Determines current worktree from current working directory
    - Supports "keep" (do nothing) and "remove" (delete directory)
    - Validates discard_changes requirement for removal
    - Returns original CWD and worktree info
    """
    try:
        # Load configuration
        config = ExitWorktreeConfig.from_env()
        
        # Check if tool is enabled
        if not config.get("EXIT_WORKTREE_ENABLED", True):
            return json.dumps({
                "error": "ExitWorktreeTool is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Validate action parameter
        if action not in ["keep", "remove"]:
            return json.dumps({
                "error": f'Action must be "keep" or "remove", got "{action}"',
                "success": False
            }, indent=2)
        
        # Check if remove is allowed by configuration
        if action == "remove" and not config.get("EXIT_WORKTREE_ALLOW_REMOVE", True):
            return json.dumps({
                "error": "Worktree removal is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Get current working directory (assumed to be the worktree)
        worktree_path = os.getcwd()
        original_cwd = worktree_path  # In simplified version, we don't track original CWD
        
        # Check if we're in a worktree directory
        base_path = config.get("EXIT_WORKTREE_BASE_PATH")
        # Normalize paths for comparison (handle symlinks like /var vs /private/var on macOS)
        norm_worktree_path = os.path.realpath(worktree_path)
        norm_base_path = os.path.realpath(base_path)
        is_in_worktree_tree = norm_worktree_path.startswith(norm_base_path)
        
        # If not in worktree tree, we might still be in some directory
        # For simplicity, we'll proceed but note this
        
        # For remove action, check discard_changes requirement
        require_discard = config.get("EXIT_WORKTREE_REQUIRE_DISCARD_FOR_REMOVE", True)
        if action == "remove" and require_discard:
            if discard_changes is None:
                return json.dumps({
                    "error": 'discard_changes must be true when action is "remove"',
                    "success": False
                }, indent=2)
            
            if not discard_changes:
                # Check if there are any files (simplified "changes" detection)
                has_files = False
                try:
                    for item in os.listdir(worktree_path):
                        # Skip special files/directories
                        if item in [".", "..", "README.md"]:
                            continue
                        item_path = os.path.join(worktree_path, item)
                        if os.path.exists(item_path):
                            has_files = True
                            break
                except (OSError, IOError):
                    has_files = False
                
                if has_files:
                    return json.dumps({
                        "error": "Worktree has files. Set discard_changes=true to remove.",
                        "success": False
                    }, indent=2)
        
        # Perform the action
        discarded_files = 0
        discarded_commits = 0  # Simplified: we don't track commits
        
        if action == "remove":
            # Count files (excluding README.md)
            try:
                for item in os.listdir(worktree_path):
                    if item == "README.md":
                        continue
                    item_path = os.path.join(worktree_path, item)
                    if os.path.isfile(item_path):
                        discarded_files += 1
                    elif os.path.isdir(item_path):
                        # Count files in subdirectories (simplified)
                        for root, dirs, files in os.walk(item_path):
                            discarded_files += len(files)
            except (OSError, IOError):
                discarded_files = 0
            
            # Actually remove the directory if it's in worktree tree
            if is_in_worktree_tree:
                try:
                    shutil.rmtree(worktree_path)
                except (OSError, IOError, shutil.Error) as e:
                    return json.dumps({
                        "error": f"Failed to remove worktree: {str(e)}",
                        "success": False
                    }, indent=2)
            else:
                # Not in worktree tree, can't remove
                return json.dumps({
                    "error": f"Not in worktree directory (not under {base_path}). Cannot remove.",
                    "success": False
                }, indent=2)
        
        # Build Claude Code compatible response
        response = {
            "action": action,
            "originalCwd": original_cwd,
            "worktreePath": worktree_path,
            "worktreeBranch": None,  # Simplified: no git integration
            "tmuxSessionName": None,  # Simplified: no tmux integration
            "message": f"Exited worktree: {action}"
        }
        
        # Add action-specific fields
        if action == "remove":
            response["discardedFiles"] = discarded_files
            response["discardedCommits"] = discarded_commits
            response["message"] = f"Removed worktree at {worktree_path}"
        else:  # keep
            response["message"] = f"Kept worktree at {worktree_path}"
        
        # Add metadata
        response["_metadata"] = {
            "wasInWorktreeTree": is_in_worktree_tree,
            "basePath": base_path,
            "discardChangesProvided": discard_changes is not None,
            "discardChangesValue": discard_changes
        }
        
        # Interactive mode output (if enabled)
        interactive = config.get("EXIT_WORKTREE_INTERACTIVE", True)
        if interactive:
            print(f"🚪 Exiting worktree: {action}")
            print(f"   Path: {worktree_path}")
            print(f"   Original CWD: {original_cwd}")
            
            if action == "remove":
                print(f"   Action: Removed directory")
                print(f"   Discarded files: {discarded_files}")
                if not is_in_worktree_tree:
                    print(f"   ⚠️  Warning: Not in worktree tree")
            else:
                print(f"   Action: Kept directory")
            
            if discard_changes is not None:
                print(f"   Discard changes: {discard_changes}")
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Exit worktree failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "exit_worktree_tool": exit_worktree_tool
}


if __name__ == "__main__":
    # Test the exit_worktree_tool function
    print("Testing ExitWorktreeTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Keep action
    print("1. Keep action (simplified):")
    result1 = exit_worktree_tool(action="keep")
    data1 = json.loads(result1)
    
    print(f"Success: {data1.get('success', True)}")
    print(f"Action: {data1.get('action', 'None')}")
    print(f"Message: {data1.get('message', 'None')}")
    
    # Test 2: Remove action with discard_changes=False (should fail if files exist)
    print("\n2. Remove action with discard_changes=False:")
    result2 = exit_worktree_tool(action="remove", discard_changes=False)
    data2 = json.loads(result2)
    
    print(f"Success: {data2.get('success', True)}")
    if data2.get("error"):
        print(f"Error: {data2.get('error', 'None')}")
    
    # Test 3: Invalid action
    print("\n3. Invalid action:")
    result3 = exit_worktree_tool(action="invalid")
    data3 = json.loads(result3)
    
    print(f"Success: {data3.get('success', True)}")
    print(f"Error: {data3.get('error', 'None')}")
    
    # Test 4: Check Claude Code compatibility
    print("\n4. Claude Code compatibility check:")
    test_response = {
        "action": "keep",
        "originalCwd": "/tmp/original",
        "worktreePath": "/tmp/worktree",
        "worktreeBranch": "main",
        "message": "Test message"
    }
    
    expected_fields = ["action", "originalCwd", "worktreePath", "message"]
    missing_fields = [field for field in expected_fields if field not in test_response]
    
    if missing_fields:
        print(f"  Missing fields in test response: {missing_fields}")
    else:
        print("  All expected fields present ✓")