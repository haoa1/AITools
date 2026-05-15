#!/usr/bin/env python3
"""
GlobTool implementation for AITools (Claude Code compatible version - simplified).
Provides glob pattern matching functionality aligned with Claude Code's GlobTool.
Based on analysis of Claude Code source: restored-src/src/tools/GlobTool/GlobTool.ts
Simplified version focusing on basic glob pattern matching.

Safety features added:
- Timeout guard (30s) — terminates before iglob can hang
- Skip huge system dirs (Library, node_modules, etc.)
- Max depth limit (8 levels) for ** patterns
- Max scanned file limit (5000)
- Per-entry timeout checks via os.scandir (not iglob which blocks internally)
"""

import os
import fnmatch
import json
import time
from base import function_ai, parameters_func, property_param

# Safety limits for recursive glob patterns
_GLOB_TIMEOUT_SECONDS = 30       # Max time for any glob search
_GLOB_RECURSIVE_MAX_DEPTH = 8    # Max directory depth for ** patterns
_GLOB_RECURSIVE_MAX_FILES = 5000 # Max intermediate files before giving up
_GLOB_RESULT_LIMIT = 100         # Default result limit (matches Claude Code)

# Directories to skip during recursive search (common huge/system dirs)
_GLOB_SKIP_DIRS = frozenset({
    "Library", "node_modules", ".git", "__pycache__", ".cache",
    ".npm", ".yarn", ".cocoapods", "Pods", "build", "dist",
    ".venv", "venv", ".tox", ".eggs", "egg-info", "site-packages",
    "Caches", "Trash", ".Trash", "tmp", "temp", ".tmp",
})

# Property definitions for GlobTool
__PATTERN_PROPERTY__ = property_param(
    name="pattern",
    description="The glob pattern to match files against",
    t="string",
    required=True,
)

__PATH_PROPERTY__ = property_param(
    name="path",
    description="The directory to search in. If not specified, the current working directory will be used.",
    t="string",
    required=False,
)

# Function metadata
__GLOB_TOOL_FUNCTION__ = function_ai(
    name="glob",
    description="Find files by name pattern or wildcard. Compatible with Claude Code's GlobTool (simplified version).",
    parameters=parameters_func([
        __PATTERN_PROPERTY__,
        __PATH_PROPERTY__,
    ]),
)

tools = [__GLOB_TOOL_FUNCTION__]


def _safe_recursive_glob(pattern, search_dir, max_results, deadline):
    """
    Recursively find files matching a glob pattern, with per-entry timeout checks.
    
    Uses os.scandir instead of glob.iglob because iglob blocks internally at the
    C level when traversing large directories — making Python-level timeout checks
    impossible. With os.scandir, we inspect every single entry and can bail out
    immediately if we exceed the deadline.
    
    Returns (all_files, timed_out, search_cancelled)
    """
    all_files = []
    timed_out = False
    search_cancelled = False
    total_scanned = 0
    
    def _scan(root_dir, depth=0):
        nonlocal timed_out, search_cancelled, total_scanned
        
        if timed_out or search_cancelled:
            return
        if depth > _GLOB_RECURSIVE_MAX_DEPTH:
            return
        
        # Timeout check before entering each directory
        if time.time() > deadline:
            timed_out = True
            return
        
        try:
            with os.scandir(root_dir) as entries:
                for entry in entries:
                    if timed_out or search_cancelled:
                        return
                    
                    # Per-entry timeout check
                    if time.time() > deadline:
                        timed_out = True
                        return
                    
                    # Skip known huge/system directories entirely
                    if entry.is_dir(follow_symlinks=False) and entry.name in _GLOB_SKIP_DIRS:
                        continue
                    
                    total_scanned += 1
                    
                    # Max total scanned guard
                    if total_scanned > _GLOB_RECURSIVE_MAX_FILES:
                        search_cancelled = True
                        return
                    
                    # Get relative path for pattern matching
                    try:
                        rel = os.path.relpath(entry.path, search_dir)
                    except ValueError:
                        continue
                    
                    # Don't include files inside skipped dirs (but we already skip dirs above)
                    rel_parts = rel.replace("\\", "/").split("/")
                    if any(p in _GLOB_SKIP_DIRS for p in rel_parts[:-1]):
                        continue
                    
                    # Check if this entry matches the pattern
                    if fnmatch.fnmatch(rel, pattern):
                        all_files.append(entry.path)
                        if len(all_files) >= max_results:
                            return
                    
                    # Recurse into directories
                    if entry.is_dir(follow_symlinks=False):
                        _scan(entry.path, depth + 1)
                        if len(all_files) >= max_results:
                            return
                        
        except PermissionError:
            pass
        except OSError:
            pass
    
    _scan(search_dir, depth=0)
    return all_files, timed_out, search_cancelled


def glob(pattern: str, path: str = None) -> str:
    """
    Find files by name pattern or wildcard.
    
    Claude Code compatible version based on GlobTool.ts:
    - pattern: The glob pattern to match files against (required)
    - path: The directory to search in (optional, defaults to current directory)
    
    Returns JSON matching Claude Code's GlobTool output schema (simplified).
    """
    try:
        # Validate inputs
        if not pattern or not isinstance(pattern, str):
            return json.dumps({
                "error": "Pattern must be a non-empty string",
                "success": False
            }, indent=2)
        
        # Expand ~ in pattern if present
        pattern = os.path.expanduser(pattern)
        
        # Determine search directory and expand ~ if present
        search_dir = path or os.getcwd()
        search_dir = os.path.expanduser(search_dir)
        
        # Validate directory exists
        if not os.path.exists(search_dir):
            return json.dumps({
                "error": f"Directory does not exist: {search_dir}",
                "success": False
            }, indent=2)
        
        if not os.path.isdir(search_dir):
            return json.dumps({
                "error": f"Path is not a directory: {search_dir}",
                "success": False
            }, indent=2)
        
        # Record start time
        start_time = time.time()
        deadline = start_time + _GLOB_TIMEOUT_SECONDS
        
        all_files = []
        max_results = _GLOB_RESULT_LIMIT
        timed_out = False
        search_cancelled = False
        
        if "**" in pattern:
            # ----- RECURSIVE pattern: use os.scandir (per-entry timeout) -----
            all_files, timed_out, search_cancelled = _safe_recursive_glob(
                pattern, search_dir, max_results, deadline
            )
        else:
            # ----- Non-recursive pattern: standard glob is fine -----
            import glob as pyglob
            all_files = pyglob.glob(os.path.join(search_dir, pattern))
            
            # Filter out results from skipped system dirs
            filtered = []
            for f in all_files:
                rel = os.path.relpath(f, search_dir) if os.path.isabs(f) else f
                parts = rel.replace("\\", "/").split("/")
                # Only keep files not inside skipped dirs
                if len(parts) <= 1 or not any(p in _GLOB_SKIP_DIRS for p in parts[:-1]):
                    filtered.append(f)
            all_files = filtered
        
        # Sort for consistency
        all_files.sort()
        
        # Apply limit
        truncated = len(all_files) > max_results or timed_out or search_cancelled
        result_files = all_files[:max_results]
        
        # Convert to relative paths
        final_files = []
        for file_path in result_files:
            file_str = str(file_path)
            if os.path.isabs(file_str):
                try:
                    file_str = os.path.relpath(file_str, search_dir)
                except ValueError:
                    pass
            final_files.append(file_str)
        
        # Calculate execution time
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Determine truncation reason
        truncation_reason = None
        if timed_out:
            truncation_reason = f"timed_out after {_GLOB_TIMEOUT_SECONDS}s"
        elif search_cancelled:
            truncation_reason = f"too_many_files_exceeded_{_GLOB_RECURSIVE_MAX_FILES}"
        elif truncated:
            truncation_reason = f"result_limit_{max_results}"
        
        # Build Claude Code compatible response
        response = {
            "durationMs": duration_ms,
            "numFiles": len(final_files),
            "filenames": final_files,
            "truncated": truncated,
            "truncation_reason": truncation_reason,
            "_metadata": {
                "success": True,
                "simplifiedImplementation": True,
                "pattern": pattern,
                "searchDirectory": search_dir,
                "maxResults": max_results,
                "safety": {
                    "timeout_seconds": _GLOB_TIMEOUT_SECONDS,
                    "max_depth": _GLOB_RECURSIVE_MAX_DEPTH,
                    "max_scanned": _GLOB_RECURSIVE_MAX_FILES,
                    "skipped_dirs": sorted(_GLOB_SKIP_DIRS)
                }
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Glob search failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "glob": glob
}
