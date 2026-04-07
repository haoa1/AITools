from base import function_ai, parameters_func, property_param
import os
import sys
import json

# Add garuda directory to path to import from main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../main_Garuda/Garuda"))

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
    Search for relevant memories using a sub-agent specialized in memory retrieval.
    
    This function launches a sub-agent loop with:
    - Tools: Only file reading tools (read, bash for listing files)
    - System prompt: Memory search strategy guide
    - Goal: Find and return relevant memories based on the query
    
    Args:
        query: Natural language query to search for
        limit: Maximum number of relevant memories to return
        max_turns: Maximum turns for sub-agent search
        detail_level: Level of detail in results
        
    Returns:
        Formatted memory search results
    """
    # TEST: Immediate return to check which version is being called
    return f"TEST: memory_recall from AITools project. Query: '{query}', Limit: {limit}."
    
    try:
        # Import necessary modules
        from garuda.main import run_turn_with_config
        from file.read import tools as read_tools
        from file.read import TOOL_CALL_MAP as read_tool_map
        from shell.bash import tools as bash_tools
        from shell.bash import TOOL_CALL_MAP as bash_tool_map
        
        # Define system prompt for memory search sub-agent
        MEMORY_SEARCH_SYSTEM_PROMPT = """You are a memory search specialist. Your ONLY task is to search through memory files and find information relevant to the user's query.

## MEMORY FILE STRUCTURE
1. Long-term memory: /home/li/.garuda/workspace/MEMORY.md (curated important info)
2. Daily memories: /home/li/.garuda/workspace/memory/YYYY-MM-DD.md (daily logs)
3. Session brief logs: /home/li/.garuda/workspace/sessions/brief/brief_YYYYMMDD.md (conversation records)

## SEARCH STRATEGY
1. FIRST, list available memory files to understand what's available
2. THEN, search for the query using smart keyword extraction
3. Read the most promising files first (recent files are usually more relevant)
4. Use pagination (offset/limit) to avoid reading entire large files
5. Focus on finding RELEVANT information, not reading everything

## AVAILABLE TOOLS
- read: Read specific files or sections
- bash: List files, search with grep if needed

## OUTPUT FORMAT
When you find relevant information:
1. Cite the source file
2. Provide a brief summary of what you found
3. Include relevant excerpts (but be concise)
4. If multiple relevant memories, prioritize by recency and relevance

## QUERY TO SEARCH FOR:
{query}

Start by exploring what memory files are available, then search strategically."""
        
        # Format the system prompt with the query
        system_prompt = MEMORY_SEARCH_SYSTEM_PROMPT.format(query=query)
        
        # Create initial messages for sub-agent
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please search for memories related to: '{query}'. Limit results to {limit} most relevant memories. Use {detail_level} level of detail."}
        ]
        
        # Configure tools for sub-agent (only reading tools)
        sub_agent_tools = read_tools + bash_tools
        
        # Configure tool maps for sub-agent
        sub_agent_tool_maps = {}
        sub_agent_tool_maps.update(read_tool_map)
        sub_agent_tool_maps.update(bash_tool_map)
        
        # Configure LLM client for sub-agent (could use cheaper/faster model)
        llm_client_config = {
            "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "base_url": "https://api.deepseek.com/",
            "temperature": 0.1,  # Lower temperature for more focused search
            "max_tokens": 2000
        }
        
        print(f"🔍 Starting memory search for: '{query}' (max turns: {max_turns})")
        
        # Run the sub-agent memory search
        response, sub_agent_messages, search_cost = run_turn_with_config(
            messages=messages,
            tools_config=sub_agent_tools,
            tool_call_maps_config=sub_agent_tool_maps,
            llm_client_config=llm_client_config,
            system_prompt=system_prompt,
            max_turns=max_turns
        )
        
        # Extract the final response from sub-agent
        if response and response.choices:
            final_content = response.choices[0].message.content
            if final_content:
                result = f"## Memory Search Results for: '{query}'\n\n"
                result += final_content
                result += f"\n\n---\n"
                result += f"Search completed in {len(sub_agent_messages)-2} messages. "
                result += f"Estimated search cost: ${search_cost:.4f}"
            else:
                # Check if there's any assistant message in the conversation
                assistant_messages = [msg for msg in sub_agent_messages if msg.get("role") == "assistant" and msg.get("content")]
                if assistant_messages:
                    last_assistant = assistant_messages[-1]
                    result = f"## Memory Search Results for: '{query}'\n\n"
                    result += last_assistant.get("content", "No specific memories found.")
                else:
                    result = f"No relevant memories found for query: '{query}'"
        else:
            # Fallback: extract any assistant content from messages
            assistant_contents = []
            for msg in sub_agent_messages:
                if msg.get("role") == "assistant" and msg.get("content"):
                    assistant_contents.append(msg.get("content"))
            
            if assistant_contents:
                result = f"## Memory Search Results for: '{query}'\n\n"
                result += "\n\n".join(assistant_contents[-3:])  # Last 3 assistant messages
            else:
                result = f"Memory search completed but no results found for: '{query}'"
        
        # Truncate if too long
        return truncate_tool_result(result)
        
    except Exception as e:
        import traceback
        error_msg = f"Error in memory_recall tool: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        return f"Memory search failed: {str(e)[:200]}"


TOOL_CALL_MAP = {
    "memory_recall": memory_recall,
}