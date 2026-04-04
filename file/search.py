from base import function_ai, parameters_func, property_param
import os
import glob as glob_module
import time

__PATH_PROPERTY__ = property_param(
    name="path",
    description="The directory to search in. If not specified, the current working directory will be used.",
    t="string",
)

__PATTERN_PROPERTY__ = property_param(
    name="pattern",
    description="The glob pattern to match files against (e.g., '*.py', '**/*.js', 'data/*.txt').",
    t="string",
    required=True,
)

__RECURSIVE_PROPERTY__ = property_param(
    name="recursive",
    description="Whether to search recursively. Use '**' in pattern for recursive search.",
    t="boolean",
)

__MAX_RESULTS_PROPERTY__ = property_param(
    name="max_results",
    description="Maximum number of files to return. Results will be truncated if this limit is exceeded.",
    t="number",
)

__SEARCH_FUNCTION__ = function_ai(
    name="glob",
    description="This function searches for files matching a glob pattern. Similar to Claude Code's GlobTool, it supports pattern matching with optional recursion and result limiting. Returns formatted output with file count, duration, and matched files.",
    parameters=parameters_func(
        [__PATH_PROPERTY__, __PATTERN_PROPERTY__, __RECURSIVE_PROPERTY__, __MAX_RESULTS_PROPERTY__]
    ),
)

tools = [__SEARCH_FUNCTION__]


def _validate_path(path: str) -> str:
    """Validate directory path and return error message if invalid."""
    if not path:
        path = "."
    
    path = os.path.normpath(path)
    
    if not os.path.exists(path):
        return f"Error: Directory does not exist: {path}"
    if not os.path.isdir(path):
        return f"Error: Path is not a directory: {path}"
    if not os.access(path, os.R_OK):
        return f"Error: No read permission for directory: {path}"
    return None


def _get_relative_paths(file_paths: list, base_path: str) -> list:
    """Convert absolute paths to relative paths from base directory."""
    relative_paths = []
    for file_path in file_paths:
        try:
            rel_path = os.path.relpath(file_path, base_path)
            relative_paths.append(rel_path)
        except ValueError:
            # If paths are on different drives (Windows) or other issues, use absolute
            relative_paths.append(file_path)
    return relative_paths


def glob(
    path: str = ".", 
    pattern: str = "*", 
    recursive: bool = False, 
    max_results: int = 100
) -> str:
    """
    Search for files matching a glob pattern.
    
    Args:
        path: The directory to search in (default: current directory)
        pattern: The glob pattern to match files against (required)
        recursive: Whether to search recursively
        max_results: Maximum number of files to return
    
    Returns:
        Formatted string containing search results similar to Claude Code's GlobTool
    """
    start_time = time.time()
    
    # Validate path
    if error := _validate_path(path):
        return error

    try:
        # Build search pattern
        if not pattern:
            pattern = "*"
        
        search_pattern = os.path.join(path, pattern)
        
        # Determine if recursive search is needed
        use_recursive = recursive or "**" in pattern
        
        # Perform glob search
        matches = glob_module.glob(search_pattern, recursive=use_recursive)
        
        # Sort matches for consistent output
        matches.sort()
        
        # Check if results are truncated
        truncated = False
        if max_results > 0 and len(matches) > max_results:
            matches = matches[:max_results]
            truncated = True
        
        # Convert to relative paths
        relative_matches = _get_relative_paths(matches, path)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Build output similar to Claude Code's GlobTool
        output_lines = []
        
        if not relative_matches:
            output_lines.append(f"No files found matching pattern: {pattern}")
        else:
            # Header with statistics
            output_lines.append(f"Found {len(relative_matches)} file{'s' if len(relative_matches) != 1 else ''} in {duration_ms}ms")
            
            if truncated:
                output_lines.append(f"Results truncated to {max_results} files (use max_results parameter to increase limit)")
            
            output_lines.append("")  # Empty line
            
            # List files
            for i, file_path in enumerate(relative_matches, 1):
                output_lines.append(f"{i:4d}. {file_path}")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error: Unexpected error when searching: {str(e)}"


TOOL_CALL_MAP = {
    "glob": glob,
}