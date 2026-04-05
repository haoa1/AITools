#!/usr/bin/env python3
"""
FileCopyTool implementation for AITools.
Provides file copying functionality with Claude Code compatibility.
Simplified version focusing on basic file copy operations.
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

__COPY_SOURCE_PATH_PROPERTY__ = property_param(
    name="source",
    description="The absolute path to the source file or directory to copy.",
    t="string",
    required=True
)

__COPY_DESTINATION_PATH_PROPERTY__ = property_param(
    name="destination",
    description="The absolute path to the destination (new copy location or name).",
    t="string",
    required=True
)

__COPY_OVERWRITE_PROPERTY__ = property_param(
    name="overwrite",
    description="Whether to overwrite existing files at the destination (default: false).",
    t="boolean",
    required=False
)

__COPY_CREATE_PARENT_DIRS_PROPERTY__ = property_param(
    name="create_parent_dirs",
    description="Whether to create parent directories if they don't exist (default: false).",
    t="boolean",
    required=False
)

__COPY_RECURSIVE_PROPERTY__ = property_param(
    name="recursive",
    description="Whether to copy directories recursively (default: true for directories).",
    t="boolean",
    required=False
)

__COPY_PRESERVE_METADATA_PROPERTY__ = property_param(
    name="preserve_metadata",
    description="Whether to preserve file metadata (timestamps, permissions) (default: true).",
    t="boolean",
    required=False
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__FILE_COPY_FUNCTION__ = function_ai(
    name="file_copy",
    description="Copy a file or directory (simplified version of file copy functionality).",
    parameters=parameters_func([
        __COPY_SOURCE_PATH_PROPERTY__,
        __COPY_DESTINATION_PATH_PROPERTY__,
        __COPY_OVERWRITE_PROPERTY__,
        __COPY_CREATE_PARENT_DIRS_PROPERTY__,
        __COPY_RECURSIVE_PROPERTY__,
        __COPY_PRESERVE_METADATA_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_copy_paths(source: str, destination: str) -> tuple[bool, Optional[str]]:
    """
    Validate source and destination paths for copy operation.
    Returns (is_valid, error_message)
    """
    # Check source exists
    if not os.path.exists(source):
        return False, f"Source path does not exist: {source}"
    
    # Check source is readable
    if not os.access(source, os.R_OK):
        return False, f"Source path is not readable: {source}"
    
    # Check if destination is the same as source
    if os.path.abspath(source) == os.path.abspath(destination):
        return False, f"Source and destination are the same: {source}"
    
    # Check if destination is inside source (for directory copy)
    if os.path.isdir(source):
        source_abs = os.path.abspath(source)
        dest_abs = os.path.abspath(destination)
        if dest_abs.startswith(source_abs + os.sep):
            return False, f"Cannot copy directory into itself: destination '{destination}' is inside source '{source}'"
    
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

def _check_overwrite(destination: str, overwrite: bool, is_directory: bool) -> tuple[bool, Optional[str]]:
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
        
        # Check type mismatch (file vs directory)
        dest_is_dir = os.path.isdir(destination)
        if dest_is_dir != is_directory:
            type_str = "directory" if is_directory else "file"
            dest_type_str = "directory" if dest_is_dir else "file"
            return False, f"Cannot overwrite {dest_type_str} with {type_str}: {destination}"
    
    return True, None

def _count_files_and_bytes(path: str) -> tuple[int, int]:
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

def _copy_with_stats(source: str, destination: str, recursive: bool = True, preserve_metadata: bool = True) -> tuple[bool, Optional[str], int, int]:
    """
    Copy file or directory with statistics.
    Returns (success, error_message, files_copied, bytes_copied)
    """
    try:
        if os.path.isdir(source):
            if recursive:
                # Copy directory recursively
                if preserve_metadata:
                    shutil.copytree(source, destination, copy_function=shutil.copy2)
                else:
                    shutil.copytree(source, destination)
                
                # Count files and bytes
                file_count, total_bytes = _count_files_and_bytes(destination)
                return True, None, file_count, total_bytes
            else:
                # Create directory but don't copy contents
                os.makedirs(destination, exist_ok=True)
                return True, None, 0, 0
        else:
            # Copy single file
            if preserve_metadata:
                shutil.copy2(source, destination)
            else:
                shutil.copy(source, destination)
            
            # Get file size
            try:
                file_size = os.path.getsize(destination)
                return True, None, 1, file_size
            except:
                return True, None, 1, 0
                
    except Exception as e:
        return False, f"Copy operation failed: {e}", 0, 0

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def file_copy(
    source: str,
    destination: str,
    overwrite: bool = False,
    create_parent_dirs: bool = False,
    recursive: bool = True,
    preserve_metadata: bool = True
) -> str:
    """
    Copy a file or directory.
    
    Args:
        source: Path to the source file or directory
        destination: Path to the destination (new copy location or name)
        overwrite: Whether to overwrite existing destination (default: false)
        create_parent_dirs: Whether to create parent directories (default: false)
        recursive: Whether to copy directories recursively (default: true)
        preserve_metadata: Whether to preserve file metadata (default: true)
    
    Returns:
        JSON string with operation results:
        - success: boolean indicating success
        - operation: "copy"
        - source: original source path
        - destination: new destination path
        - is_directory: whether the copied item is a directory
        - files_copied: number of files copied
        - bytes_copied: number of bytes copied
        - recursive: whether recursive copy was performed
        - preserve_metadata: whether metadata was preserved
        - error: error message if failed
        - durationMs: operation duration in milliseconds
    """
    start_time = time.time()
    
    try:
        # 1. Validate inputs
        if not source or not source.strip():
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "error": "Source path cannot be empty",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        if not destination or not destination.strip():
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "error": "Destination path cannot be empty",
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 2. Validate paths
        is_valid, error_msg = _validate_copy_paths(source, destination)
        if not is_valid:
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 3. Determine if source is directory
        is_directory = os.path.isdir(source)
        
        # 4. Check overwrite
        can_proceed, error_msg = _check_overwrite(destination, overwrite, is_directory)
        if not can_proceed:
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "is_directory": is_directory,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 5. Create parent directories if needed
        success, error_msg = _create_parent_dirs_if_needed(destination, create_parent_dirs)
        if not success:
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "is_directory": is_directory,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 6. Remove existing destination if overwrite is enabled
        if overwrite and os.path.exists(destination):
            try:
                if os.path.isdir(destination):
                    shutil.rmtree(destination)
                else:
                    os.remove(destination)
            except Exception as e:
                result = {
                    "success": False,
                    "operation": "copy",
                    "source": source,
                    "destination": destination,
                    "is_directory": is_directory,
                    "error": f"Failed to remove existing destination: {e}",
                    "durationMs": int((time.time() - start_time) * 1000)
                }
                return json.dumps(result, ensure_ascii=False)
        
        # 7. Perform the copy operation with statistics
        copy_success, error_msg, files_copied, bytes_copied = _copy_with_stats(
            source, destination, recursive, preserve_metadata
        )
        
        if not copy_success:
            result = {
                "success": False,
                "operation": "copy",
                "source": source,
                "destination": destination,
                "is_directory": is_directory,
                "error": error_msg,
                "durationMs": int((time.time() - start_time) * 1000)
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 8. Return success result
        duration_ms = int((time.time() - start_time) * 1000)
        
        result = {
            "success": True,
            "operation": "copy",
            "source": source,
            "destination": destination,
            "is_directory": is_directory,
            "files_copied": files_copied,
            "bytes_copied": bytes_copied,
            "recursive": recursive if is_directory else None,
            "preserve_metadata": preserve_metadata,
            "durationMs": duration_ms
        }
        
        # Add some output for logging
        file_type = "directory" if is_directory else "file"
        print(f"FileCopy: Copied {file_type} '{source}' to '{destination}' (files: {files_copied}, bytes: {bytes_copied}, recursive: {recursive if is_directory else 'N/A'})")
        
        return json.dumps(result, ensure_ascii=False)
        
    except Exception as e:
        # Catch-all for any unexpected errors
        result = {
            "success": False,
            "operation": "copy",
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
tools = [__FILE_COPY_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "file_copy": file_copy
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'file_copy', '__FILE_COPY_FUNCTION__']