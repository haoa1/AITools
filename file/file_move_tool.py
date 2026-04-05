#!/usr/bin/env python3
"""
FileMoveTool implementation for AITools.
Provides file moving/renaming functionality with Claude Code compatibility.
Simplified version focusing on basic file move/rename operations.
"""

import os
import json
import sys
import shutil
import time
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# AITools decorators
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__SOURCE_PATH_PROPERTY__ = property_param(
    name="source",
    description="The absolute path to the source file or directory to move.",
    t="string",
    required=True
)

__DESTINATION_PATH_PROPERTY__ = property_param(
    name="destination",
    description="The absolute path to the destination (new location or name).",
    t="string",
    required=True
)

__OVERWRITE_PROPERTY__ = property_param(
    name="overwrite",
    description="Whether to overwrite existing files at the destination (default: false).",
    t="boolean",
    required=False
)

__CREATE_PARENT_DIRS_PROPERTY__ = property_param(
    name="create_parent_dirs",
    description="Whether to create parent directories if they don't exist (default: false).",
    t="boolean",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__FILE_MOVE_FUNCTION__ = function_ai(
    name="file_move",
    description="Move or rename a file or directory (simplified version of file move functionality).",
    parameters=parameters_func([
        __SOURCE_PATH_PROPERTY__,
        __DESTINATION_PATH_PROPERTY__,
        __OVERWRITE_PROPERTY__,
        __CREATE_PARENT_DIRS_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_paths(source: str, destination: str) -> tuple[bool, Optional[str]]:
    """
    Validate source and destination paths.
    Returns (is_valid, error_message)
    """
    # Check source exists
    if not os.path.exists(source):
        return False, f"Source path does not exist: {source}"
    
    # Check source is readable
    if not os.access(source, os.R_OK):
        return False, f"Source path is not readable: {source}"
    
    # Check if destination already exists (will be handled by overwrite parameter)
    # For now just check if it's the same as source
    if os.path.abspath(source) == os.path.abspath(destination):
        return False, f"Source and destination are the same: {source}"
    
    return True, None

def _create_parent_dirs_if_needed(destination: str, create_parent_dirs: bool) -> tuple[bool, Optional[str]]:
    """
    Create parent directories for destination if needed.
    Returns (success, error_message)
    """
    dest_dir = os.path.dirname(destination)
    if dest_dir and not os.path.exists(dest_dir):
        if create_parent_dirs:
            try:
                os.makedirs(dest_dir, exist_ok=True)
                return True, None
            except Exception as e:
                return False, f"Failed to create parent directories '{dest_dir}': {e}"
        else:
            return False, f"Parent directory does not exist: {dest_dir}. Set create_parent_dirs=true to create it."
    return True, None

def _check_overwrite(destination: str, overwrite: bool) -> tuple[bool, Optional[str]]:
    """
    Check if destination exists and handle overwrite logic.
    Returns (can_proceed, error_message)
    """
    if os.path.exists(destination):
        if not overwrite:
            return False, f"Destination already exists: {destination}. Set overwrite=true to overwrite."
        
        # Check if destination is writable
        if not os.access(destination, os.W_OK):
            return False, f"Destination exists and is not writable: {destination}"
        
        # Check if destination is a directory (can't overwrite directory with file or vice versa)
        source_is_dir = os.path.isdir(destination)
        # We'll handle this in the main function with actual source
    return True, None

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def file_move(
    source: str,
    destination: str,
    overwrite: bool = False,
    create_parent_dirs: bool = False
) -> str:
    """
    Move or rename a file or directory.
    
    Args:
        source: Path to the source file or directory
        destination: Path to the destination (new location or name)
        overwrite: Whether to overwrite existing destination (default: false)
        create_parent_dirs: Whether to create parent directories (default: false)
    
    Returns:
        JSON string with operation results:
        - success: boolean indicating success
        - operation: "move" or "rename"
        - source: original source path
        - destination: new destination path
        - is_directory: whether the moved item is a directory
        - bytes_moved: number of bytes moved (for files)
        - error: error message if failed
        - durationMs: operation duration in milliseconds
    """
    start_time = time.time()
    
    try:
        # 1. Validate inputs
        if not source or not source.strip():
            result = {
                "success": False,
                "operation": "move",
                "source": source,
                "destination": destination,
                "error": "Source path cannot be empty",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        if not destination or not destination.strip():
            result = {
                "success": False,
                "operation": "move",
                "source": source,
                "destination": destination,
                "error": "Destination path cannot be empty",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 2. Validate paths
        is_valid, error_msg = _validate_paths(source, destination)
        if not is_valid:
            result = {
                "success": False,
                "operation": "move",
                "source": source,
                "destination": destination,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3. Check overwrite
        can_proceed, error_msg = _check_overwrite(destination, overwrite)
        if not can_proceed:
            result = {
                "success": False,
                "operation": "move",
                "source": source,
                "destination": destination,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 4. Create parent directories if needed
        success, error_msg = _create_parent_dirs_if_needed(destination, create_parent_dirs)
        if not success:
            result = {
                "success": False,
                "operation": "move",
                "source": source,
                "destination": destination,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 5. Determine if it's a rename or move to different directory
        source_dir = os.path.dirname(os.path.abspath(source))
        dest_dir = os.path.dirname(os.path.abspath(destination))
        is_rename = (source_dir == dest_dir)
        
        # 6. Check if source is directory or file
        is_directory = os.path.isdir(source)
        
        # 7. Get size before move (for files)
        bytes_moved = 0
        if not is_directory:
            try:
                bytes_moved = os.path.getsize(source)
            except:
                bytes_moved = 0  # Size unknown
        
        # 8. Perform the move operation
        operation = "rename" if is_rename else "move"
        
        if overwrite and os.path.exists(destination):
            # Remove existing destination if overwrite is enabled
            try:
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)
            except Exception as e:
                result = {
                    "success": False,
                    "operation": operation,
                    "source": source,
                    "destination": destination,
                    "error": f"Failed to remove existing destination: {e}",
                    "durationMs": int((time.time() - start_time) * 1000)
                }
                return json.dumps(result, ensure_ascii=False)
        
        # 9. Actually move the file/directory
        try:
            if is_directory:
                shutil.move(source, destination)
            else:
                shutil.move(source, destination)
        except Exception as e:
            result = {
                "success": False,
                "operation": operation,
                "source": source,
                "destination": destination,
                "error": f"Move operation failed: {e}",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 10. Return success result
        duration_ms = int((time.time() - start_time) * 1000)
        
        result = {
            "success": True,
            "operation": operation,
            "source": source,
            "destination": destination,
            "is_directory": is_directory,
            "bytes_moved": bytes_moved,
            "durationMs": duration_ms
        }
        
        # Add some output for logging
        print(f"FileMove: {'Renamed' if is_rename else 'Moved'} '{source}' to '{destination}' (directory: {is_directory}, bytes: {bytes_moved})")
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Catch-all for any unexpected errors
        result = {
            "success": False,
            "operation": "move",
            "source": source,
            "destination": destination,
            "error": f"Unexpected error: {e}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__FILE_MOVE_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "file_move": file_move
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'file_move', '__FILE_MOVE_FUNCTION__']