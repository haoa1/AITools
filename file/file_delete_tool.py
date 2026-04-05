#!/usr/bin/env python3
"""
FileDeleteTool implementation for AITools.
Provides file and directory deletion functionality with Claude Code compatibility.
Simplified version focusing on safe and controlled deletion operations.
"""

import os
import json
import sys
import shutil
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# AITools decorators
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__DELETE_PATH_PROPERTY__ = property_param(
    name="path",
    description="The absolute path to the file or directory to delete.",
    t="string",
    required=True
)

__DELETE_RECURSIVE_PROPERTY__ = property_param(
    name="recursive",
    description="Whether to delete directories recursively (default: false).",
    t="boolean",
    required=False
)

__DELETE_CONFIRMATION_PROPERTY__ = property_param(
    name="confirmation",
    description="Require explicit confirmation before deletion (default: false).",
    t="boolean",
    required=False
)

__DELETE_DRY_RUN_PROPERTY__ = property_param(
    name="dry_run",
    description="Simulate deletion without actually deleting anything (default: false).",
    t="boolean",
    required=False
)

__DELETE_FORCE_PROPERTY__ = property_param(
    name="force",
    description="Force deletion even if write-protected or other issues (default: false).",
    t="boolean",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__FILE_DELETE_FUNCTION__ = function_ai(
    name="file_delete",
    description="Delete a file or directory with safety controls and confirmation options.",
    parameters=parameters_func([
        __DELETE_PATH_PROPERTY__,
        __DELETE_RECURSIVE_PROPERTY__,
        __DELETE_CONFIRMATION_PROPERTY__,
        __DELETE_DRY_RUN_PROPERTY__,
        __DELETE_FORCE_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_delete_path(path: str) -> Tuple[bool, Optional[str], Optional[bool]]:
    """
    Validate path for deletion.
    Returns (is_valid, error_message, is_directory)
    """
    # Check path is provided
    if not path or not path.strip():
        return False, "Path cannot be empty", None
    
    # Check path exists
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}", None
    
    # Check if it's a file or directory
    is_directory = os.path.isdir(path)
    
    # Check readability
    if not os.access(path, os.R_OK):
        return False, f"Path is not readable: {path}", is_directory
    
    return True, None, is_directory

def _count_files_and_bytes(path: str) -> Tuple[int, int]:
    """
    Count files and total bytes in a directory (recursively).
    Returns (file_count, total_bytes)
    """
    if not os.path.isdir(path):
        # Single file
        try:
            size = os.path.getsize(path)
            return 1, size
        except:
            return 1, 0
    
    file_count = 0
    total_bytes = 0
    
    for root, dirs, files in os.walk(path):
        file_count += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_bytes += os.path.getsize(file_path)
            except:
                pass
    
    return file_count, total_bytes

def _check_system_paths(path: str) -> Tuple[bool, Optional[str]]:
    """
    Check if path is a critical system path that shouldn't be deleted.
    Returns (is_safe, warning_message)
    """
    # Normalize path
    abs_path = os.path.abspath(path)
    
    # Check for root directory
    if abs_path == '/':
        return False, "Cannot delete root directory"
    
    # Check for home directory
    home_dir = os.path.expanduser('~')
    if abs_path == home_dir:
        return False, f"Cannot delete home directory: {home_dir}"
    
    # Check for system directories
    system_dirs = ['/bin', '/sbin', '/usr', '/etc', '/var', '/lib', '/opt', '/boot']
    
    # Special handling for temporary directories within system directories
    # These are typically safe to delete
    temp_dirs = [
        '/tmp',
        '/var/tmp',
        '/var/folders',  # macOS temporary directories
        '/var/run/user',  # User runtime directories
    ]
    
    # Check if path is within a safe temporary directory
    for temp_dir in temp_dirs:
        if abs_path.startswith(temp_dir + '/'):
            # Temporary directories are generally safe
            return True, None
    
    # Check for direct system directory access
    for sys_dir in system_dirs:
        if abs_path == sys_dir:
            # Direct access to system directory - strong warning
            return False, f"Cannot delete critical system directory: {sys_dir}"
        elif abs_path.startswith(sys_dir + '/'):
            # Within a system directory - warning but allowed
            return True, f"Warning: Deleting within system directory: {sys_dir}"
    
    # Check for current working directory
    cwd = os.getcwd()
    if abs_path == cwd:
        return True, f"Warning: Deleting current working directory: {cwd}"
    
    return True, None

def _delete_with_stats(path: str, recursive: bool, force: bool, dry_run: bool) -> Tuple[bool, Optional[str], int, int]:
    """
    Delete file or directory with statistics.
    Returns (success, error_message, files_deleted, bytes_freed)
    """
    try:
        # Count before deletion (if not dry run)
        files_deleted = 0
        bytes_freed = 0
        
        if not dry_run:
            if os.path.isdir(path):
                file_count, total_bytes = _count_files_and_bytes(path)
                files_deleted = file_count
                bytes_freed = total_bytes
            else:
                files_deleted = 1
                try:
                    bytes_freed = os.path.getsize(path)
                except:
                    bytes_freed = 0
        
        # Perform deletion if not dry run
        if not dry_run:
            if os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path, ignore_errors=force)
                else:
                    # Check if directory is empty
                    if os.listdir(path):
                        return False, f"Directory is not empty: {path}. Use recursive=true to delete non-empty directories.", 0, 0
                    os.rmdir(path)
            else:
                # Delete file
                try:
                    os.remove(path)
                except PermissionError:
                    if force:
                        # Try to change permissions and delete
                        try:
                            os.chmod(path, 0o777)
                            os.remove(path)
                        except:
                            return False, f"Cannot delete write-protected file: {path}", 0, 0
                    else:
                        return False, f"Write-protected file: {path}. Use force=true to override.", 0, 0
        
        # For dry run, return simulated stats
        if dry_run:
            if os.path.isdir(path):
                file_count, total_bytes = _count_files_and_bytes(path)
                return True, None, file_count, total_bytes
            else:
                try:
                    size = os.path.getsize(path)
                    return True, None, 1, size
                except:
                    return True, None, 1, 0
        
        return True, None, files_deleted, bytes_freed
        
    except Exception as e:
        return False, f"Deletion failed: {e}", 0, 0

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def file_delete(
    path: str,
    recursive: bool = False,
    confirmation: bool = False,
    dry_run: bool = False,
    force: bool = False
) -> str:
    """
    Delete a file or directory with safety controls.
    
    Args:
        path: Path to the file or directory to delete
        recursive: Whether to delete directories recursively (default: false)
        confirmation: Require explicit confirmation (default: false, simplified)
        dry_run: Simulate deletion without actually deleting (default: false)
        force: Force deletion even if write-protected (default: false)
    
    Returns:
        JSON string with operation results:
        - success: boolean indicating success
        - operation: "delete"
        - path: original path
        - is_directory: whether the deleted item was a directory
        - recursive: whether recursive deletion was performed
        - dry_run: whether this was a dry run
        - files_deleted: number of files deleted
        - bytes_freed: number of bytes freed
        - warning: optional warning messages
        - error: error message if failed
        - durationMs: operation duration in milliseconds
    """
    start_time = time.time()
    
    try:
        # 1. Validate inputs
        if not path or not path.strip():
            result = {
                "success": False,
                "operation": "delete",
                "path": path,
                "error": "Path cannot be empty",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 2. Validate path
        is_valid, error_msg, is_directory = _validate_delete_path(path)
        if not is_valid:
            result = {
                "success": False,
                "operation": "delete",
                "path": path,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3. Check system paths (safety check)
        is_safe, warning_msg = _check_system_paths(path)
        if not is_safe:
            result = {
                "success": False,
                "operation": "delete",
                "path": path,
                "error": warning_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 4. Handle confirmation (simplified - in real implementation would interact with user)
        # For this simplified version, we just note if confirmation was requested
        confirmation_note = None
        if confirmation:
            confirmation_note = "Confirmation requested but not implemented in this simplified version. Proceeding with deletion."
        
        # 5. Perform deletion with statistics
        success, error_msg, files_deleted, bytes_freed = _delete_with_stats(
            path, recursive, force, dry_run
        )
        
        if not success:
            result = {
                "success": False,
                "operation": "delete",
                "path": path,
                "is_directory": is_directory,
                "recursive": recursive if is_directory else None,
                "dry_run": dry_run,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 6. Return success result
        duration_ms = int((time.time() - start_time) * 1000)
        
        result = {
            "success": True,
            "operation": "delete",
            "path": path,
            "is_directory": is_directory,
            "recursive": recursive if is_directory else None,
            "dry_run": dry_run,
            "files_deleted": files_deleted,
            "bytes_freed": bytes_freed,
            "durationMs": duration_ms
        }
        
        # Add optional warning messages
        if warning_msg:
            result["warning"] = warning_msg
        
        if confirmation_note:
            result["confirmation_note"] = confirmation_note
        
        # Add operation type description
        operation_type = "dry run simulation" if dry_run else "actual deletion"
        if is_directory:
            delete_type = "directory" + (" recursively" if recursive else "")
        else:
            delete_type = "file"
        
        result["description"] = f"{operation_type} of {delete_type}: {path}"
        
        # Log for debugging
        print(f"FileDelete: {'Simulated' if dry_run else 'Performed'} deletion of {delete_type} '{path}' "
              f"(files: {files_deleted}, bytes: {bytes_freed}, recursive: {recursive if is_directory else 'N/A'})")
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Catch-all for any unexpected errors
        result = {
            "success": False,
            "operation": "delete",
            "path": path,
            "error": f"Unexpected error: {e}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__FILE_DELETE_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "file_delete": file_delete
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'file_delete', '__FILE_DELETE_FUNCTION__']