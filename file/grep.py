from base import function_ai, parameters_func, property_param
import os
import re
import fnmatch

__GREP_PROPERTY_ONE__ = property_param(
    name="pattern",
    description="The regular expression pattern to search for in file contents.",
    t="string",
    required=True,
)

__GREP_PROPERTY_TWO__ = property_param(
    name="path",
    description="File or directory to search in. Defaults to current directory.",
    t="string",
)

__GREP_PROPERTY_THREE__ = property_param(
    name="glob",
    description="Glob pattern to filter files (e.g., '*.py', '*.txt').",
    t="string",
)

__GREP_PROPERTY_FOUR__ = property_param(
    name="output_mode",
    description="Output mode: 'content' shows matching lines, 'files' shows file paths, 'count' shows match count.",
    t="string",
)

__GREP_PROPERTY_FIVE__ = property_param(
    name="case_sensitive",
    description="Whether search is case-sensitive. Defaults to true (case-sensitive).",
    t="boolean",
)

__GREP_PROPERTY_SIX__ = property_param(
    name="context_lines",
    description="Number of lines to show before and after each match.",
    t="number",
)

__GREP_PROPERTY_SEVEN__ = property_param(
    name="show_line_numbers",
    description="Whether to show line numbers in output.",
    t="boolean",
)

__GREP_PROPERTY_EIGHT__ = property_param(
    name="max_results",
    description="Maximum number of results to return.",
    t="number",
)

__GREP_FUNCTION__ = function_ai(
    name="grep",
    description="Search for text patterns in files using regular expressions. Supports file filtering with glob patterns.",
    parameters=parameters_func(
        [
            __GREP_PROPERTY_ONE__,
            __GREP_PROPERTY_TWO__,
            __GREP_PROPERTY_THREE__,
            __GREP_PROPERTY_FOUR__,
            __GREP_PROPERTY_FIVE__,
            __GREP_PROPERTY_SIX__,
            __GREP_PROPERTY_SEVEN__,
            __GREP_PROPERTY_EIGHT__,
        ]
    ),
)

tools = [__GREP_FUNCTION__]


def grep(
    pattern: str,
    path: str = ".",
    glob: str = None,
    output_mode: str = "content",
    case_sensitive: bool = True,
    context_lines: int = 0,
    show_line_numbers: bool = True,
    max_results: int = 100,
) -> str:
    """
    Search for text patterns in files using regular expressions.
    
    Args:
        pattern: Regular expression pattern to search for
        path: File or directory to search in (default: current directory)
        glob: Glob pattern to filter files (e.g., '*.py', '*.txt')
        output_mode: 'content' (show matching lines), 'files' (show file paths), 'count' (show match count)
        case_sensitive: Whether search is case-sensitive
        context_lines: Number of lines to show before and after each match
        show_line_numbers: Whether to show line numbers
        max_results: Maximum number of results to return
    
    Returns:
        String containing search results
    """
    try:
        # Validate and normalize path
        if not path:
            path = "."
        
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return f"Error: Path does not exist: {path}"
        
        # Compile regex pattern
        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            return f"Error: Invalid regular expression pattern: {e}"
        
        # Determine if we're searching a single file or directory
        if os.path.isfile(path):
            files_to_search = [path]
        else:
            # Get all files in directory (and subdirectories)
            files_to_search = []
            for root, dirs, filenames in os.walk(path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    
                    # Apply glob filter if specified
                    if glob:
                        # Check if filename matches glob pattern
                        if not fnmatch.fnmatch(filename, glob):
                            # Also check with relative path from search root
                            rel_path = os.path.relpath(filepath, path)
                            if not fnmatch.fnmatch(rel_path, glob):
                                continue
                    
                    files_to_search.append(filepath)
        
        results = []
        total_matches = 0
        files_with_matches = 0
        
        for filepath in files_to_search:
            # Skip if can't read
            if not os.access(filepath, os.R_OK):
                continue
            
            # Skip binary files
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, IOError):
                continue  # Skip binary or unreadable files
            
            lines = content.splitlines()
            file_matches = []
            
            for i, line in enumerate(lines, 1):  # 1-based line numbers
                if regex.search(line):
                    file_matches.append((i, line))
                    total_matches += 1
            
            if file_matches:
                files_with_matches += 1
                
                if output_mode == "files":
                    # Just record file path
                    results.append(f"📄 {filepath}")
                
                elif output_mode == "content":
                    # Record matching lines with context
                    if context_lines > 0:
                        # Group consecutive matches for context
                        processed_lines = set()
                        for line_num, line in file_matches:
                            if line_num in processed_lines:
                                continue
                            
                            # Get context range
                            start_line = max(1, line_num - context_lines)
                            end_line = min(len(lines), line_num + context_lines)
                            
                            # Add context block
                            results.append(f"\n{'='*60}")
                            results.append(f"📄 {filepath} (lines {start_line}-{end_line})")
                            results.append(f"{'='*60}")
                            
                            for ctx_line_num in range(start_line, end_line + 1):
                                ctx_line = lines[ctx_line_num - 1]
                                prefix = "  "
                                if ctx_line_num == line_num:
                                    prefix = "→ "
                                elif any(m[0] == ctx_line_num for m in file_matches):
                                    prefix = "* "
                                
                                line_num_str = f"{ctx_line_num:4d}" if show_line_numbers else ""
                                results.append(f"{prefix}{line_num_str}: {ctx_line}")
                                processed_lines.add(ctx_line_num)
                    else:
                        # No context, just show matches
                        for line_num, line in file_matches:
                            line_num_str = f"{line_num:4d}" if show_line_numbers else ""
                            results.append(f"📄 {filepath}:{line_num_str}  {line}")
                
                # Check max results
                if output_mode == "content" and len(results) >= max_results * 2:  # Approximate limit
                    results.append(f"\n⚠️  Results limited to first {max_results} matches")
                    break
        
        # Format final output based on output_mode
        if output_mode == "count":
            return f"Found {total_matches} matches in {files_with_matches} files"
        
        elif output_mode == "files":
            if not results:
                return f"No files contain pattern: {pattern}"
            header = f"Files containing pattern '{pattern}' ({files_with_matches} files):\n"
            return header + "\n".join(results[:max_results])
        
        elif output_mode == "content":
            if not results:
                return f"No matches found for pattern: {pattern}"
            
            if context_lines > 0:
                # Context mode already has its own formatting
                output = "\n".join(results[:max_results * 3])  # Approximate limit
            else:
                header = f"Matches for pattern '{pattern}' ({total_matches} matches in {files_with_matches} files):\n"
                output = header + "\n".join(results[:max_results])
            
            if total_matches > max_results:
                output += f"\n\n⚠️  Showing first {max_results} matches out of {total_matches} total"
            
            return output
        
        else:
            return f"Error: Invalid output_mode '{output_mode}'. Use 'content', 'files', or 'count'."
    
    except Exception as e:
        return f"Error during grep search: {str(e)}"


TOOL_CALL_MAP = {
    "grep": grep,
}