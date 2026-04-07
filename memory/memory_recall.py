from base import function_ai, parameters_func, property_param
import os
import sys
import json

# Define properties for memory_recall tool
__MEMORY_RECALL_QUERY_PROPERTY__ = property_param(
    name="query",
    description="Natural language query to search for in memory files.",
    t="string",
    required=True,
)

__MEMORY_RECALL_LIMIT_PROPERTY__ = property_param(
    name="limit",
    description="Maximum number of relevant memories to return (default: 5).",
    t="integer",
    required=False,
)

__MEMORY_RECALL_MAX_TURNS_PROPERTY__ = property_param(
    name="max_turns",
    description="Maximum number of turns for the sub-agent memory search (default: 5).",
    t="integer",
    required=False,
)

__MEMORY_RECALL_DETAIL_LEVEL_PROPERTY__ = property_param(
    name="detail_level",
    description="Level of detail: 'brief' (summary only), 'detailed' (full content), 'balanced' (default).",
    t="string",
    required=False,
)

# Define the memory_recall function
__MEMORY_RECALL_FUNCTION__ = function_ai(
    name="memory_recall",
    description="Search and recall relevant memories from workspace memory files. This tool launches a sub-agent specifically designed for intelligent memory searching.",
    parameters=parameters_func([
        __MEMORY_RECALL_QUERY_PROPERTY__,
        __MEMORY_RECALL_LIMIT_PROPERTY__,
        __MEMORY_RECALL_MAX_TURNS_PROPERTY__,
        __MEMORY_RECALL_DETAIL_LEVEL_PROPERTY__,
    ]),
)

tools = [__MEMORY_RECALL_FUNCTION__]


def truncate_tool_result(result, max_length=4000):
    """Truncate tool result to avoid context overflow."""
    if not isinstance(result, str):
        result = str(result)
    
    if len(result) <= max_length:
        return result
    
    # Truncate and add indicator
    truncated = result[:max_length]
    if len(result) > max_length:
        truncated += f"\n\n...[Result truncated, total length: {len(result)} characters]"
    
    return truncated


def memory_recall(query: str, limit: int = 5, max_turns: int = 5, detail_level: str = "balanced") -> str:
    """
    SIMPLIFIED VERSION: Search for relevant memories in memory files.
    
    This is a simplified version that directly searches memory files without
    launching a sub-agent.
    
    Args:
        query: Natural language query to search for
        limit: Maximum number of relevant memories to return
        max_turns: Maximum turns for sub-agent search (ignored in this version)
        detail_level: Level of detail in results
        
    Returns:
        Formatted memory search results
    """
    # IMMEDIATE TEST RETURN with file logging
    test_file = "/tmp/memory_recall_test.txt"
    with open(test_file, "a") as f:
        f.write(f"Tool called: query='{query}', limit={limit}, detail_level={detail_level}\\n")
    return f"TEST: memory_recall tool is working! Query: '{query}', Limit: {limit}, Detail: {detail_level}. Log written to {test_file}"
    
    print(f"[SIMPLIFIED memory_recall] Searching for: '{query}'")
    
    results = []
    debug_info = []
    
    # Define memory file locations
    memory_locations = [
        ("Long-term memory", "/home/li/.garuda/workspace/MEMORY.md"),
        ("Today's memory", "/home/li/.garuda/workspace/memory/2026-04-06.md"),
        ("Previous memory", "/home/li/.garuda/workspace/memory/2026-04-04.md"),
        ("Memory directory", "/home/li/.garuda/workspace/memory/"),
    ]
    
    debug_info.append(f"Search query: '{query}'")
    debug_info.append(f"Limit: {limit}")
    debug_info.append(f"Detail level: {detail_level}")
    
    # Search in memory files
    for name, path in memory_locations:
        if os.path.exists(path):
            if os.path.isdir(path):
                # If it's a directory, search for all .md files
                try:
                    md_files = [f for f in os.listdir(path) if f.endswith('.md')]
                    debug_info.append(f"{name}: {path} - Directory with {len(md_files)} .md files")
                    
                    for md_file in md_files[:3]:  # Limit to first 3 files
                        file_path = os.path.join(path, md_file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            query_lower = query.lower()
                            content_lower = content.lower()
                            
                            if query_lower in content_lower:
                                # Found match
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines):
                                    if query_lower in line.lower():
                                        start = max(0, i-2)
                                        end = min(len(lines), i+3)
                                        context = '\n'.join(lines[start:end])
                                        matching_lines.append(f"Line {i+1}: {context}")
                                
                                if matching_lines:
                                    results.append(f"## {name}: {md_file}")
                                    results.append(f"Found {len(matching_lines)} matching sections")
                                    results.extend(matching_lines[:min(limit, 3)])
                        except Exception as e:
                            debug_info.append(f"  Error reading {md_file}: {str(e)}")
                except Exception as e:
                    debug_info.append(f"  Error listing directory {path}: {str(e)}")
            else:
                # It's a file
                debug_info.append(f"{name}: {path} - File")
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    debug_info.append(f"  File size: {len(content)} chars")
                    
                    query_lower = query.lower()
                    content_lower = content.lower()
                    
                    if query_lower in content_lower:
                        debug_info.append(f"  QUERY FOUND in {name}")
                        # Extract relevant section
                        lines = content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines):
                            if query_lower in line.lower():
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                context = '\n'.join(lines[start:end])
                                matching_lines.append(f"Line {i+1}: {context}")
                        
                        if matching_lines:
                            results.append(f"## {name} ({path})")
                            results.append(f"Found {len(matching_lines)} matching sections")
                            results.extend(matching_lines[:min(limit, 3)])
                    else:
                        debug_info.append(f"  Query NOT FOUND in {name}")
                        # Show sample of content for debugging
                        sample = content[:200] if len(content) > 200 else content
                        debug_info.append(f"  Content sample: {sample}")
                except Exception as e:
                    error_msg = f"Error reading {path}: {str(e)}"
                    debug_info.append(error_msg)
                    results.append(error_msg)
        else:
            debug_info.append(f"{name}: {path} - NOT FOUND")
    
    # Always include debug info
    debug_header = "## Debug Information\n" + "\n".join(debug_info)
    
    if results:
        result_content = debug_header + "\n\n## Search Results\n\n" + "\n\n".join(results)
    else:
        result_content = debug_header + "\n\n## No matches found in memory files"
    
    # If query contains "debug", return detailed debug info
    if "debug" in query.lower():
        return debug_header
    
    return truncate_tool_result(result_content)


TOOL_CALL_MAP = {
    "memory_recall": memory_recall,
}