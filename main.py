"""
Enhanced test script with better error handling, interaction tools, and streaming thought display.
Uses cache system to avoid re-analyzing project structure on every run.
"""

import sys
import os
import argparse


# Import UI helper for friendly display
from cli.ui_helper import get_ui

# Initialize UI
ui = get_ui(verbose=False)


def load_manual_imports():
    """Load imports manually without cache."""
    ui.print_warning("⚠️  Falling back to manual imports...")
    
    # Manual imports (original code)
    from file.read import tools as read_tools
    from file.write import tools as write_tools
    from file.delete import tools as delete_tools
    from file.replace import tools as replace_tools
    from file.read import TOOL_CALL_MAP as read_tool_map
    from file.write import TOOL_CALL_MAP as write_tool_map
    from file.delete import TOOL_CALL_MAP as delete_tool_map
    from file.replace import TOOL_CALL_MAP as replace_tool_map

    from git.git import tools as git_tools
    from git.git import TOOL_CALL_MAP as git_tool_map

    from shell.bash import tools as bash_tools
    from shell.bash import TOOL_CALL_MAP as bash_tool_map

    from workspace.workspace import tools as workspace_tools
    from workspace.workspace import TOOL_CALL_MAP as workspace_tool_map


    # from compress.compress import tools as compress_tools
    # from compress.compress import TOOL_CALL_MAP as compress_tool_map

    from network.network import tools as network_tools
    from network.network import TOOL_CALL_MAP as network_tool_map

    from interaction.interaction import tools as interaction_tools
    from interaction.interaction import TOOL_CALL_MAP as interaction_tool_map

    # Import enhanced interaction module with additional tools
    from interaction.enhanced_interaction import tools as enhanced_interaction_tools
    from interaction.enhanced_interaction import TOOL_CALL_MAP as enhanced_interaction_tool_map

    # Import database module
    from database.database import tools as database_tools
    from database.database import TOOL_CALL_MAP as database_tool_map

    # Import web_search module
    from web_search.web_search import tools as web_search_tools
    from web_search.web_search import TOOL_CALL_MAP as web_search_tool_map

    # Import stock module
    from stock.stock import tools as stock_tools
    from stock.stock import TOOL_CALL_MAP as stock_tool_map

    # Import summary module
    from summary.summary import tools as summary_tools
    from summary.summary import TOOL_CALL_MAP as summary_tool_map

    from diagram.diagram import tools as diagram_tools
    from diagram.diagram import TOOL_CALL_MAP as diagram_tool_map

    # Import project_context module
    from project_context.project_context import tools as project_context_tools
    from project_context.project_context import TOOL_CALL_MAP as project_context_tool_map
    
    from architect.architect import tools as architect_tools
    from architect.architect import TOOL_CALL_MAP as architect_tool_map

    from pdf.pdf import tools as pdf_tools
    from pdf.pdf import TOOL_CALL_MAP as pdf_tool_map

    # Import markdown module
    from markdown.markdown import tools as markdown_tools
    from markdown.markdown import TOOL_CALL_MAP as markdown_tool_map

    tools = (read_tools + write_tools + delete_tools + replace_tools + 
             git_tools + bash_tools + workspace_tools + 
             network_tools + enhanced_interaction_tools +
             database_tools + web_search_tools + stock_tools + summary_tools + project_context_tools + diagram_tools + architect_tools + pdf_tools + markdown_tools)

    # Combine all tool maps
    tool_call_maps = {}
    tool_call_maps.update(read_tool_map)
    tool_call_maps.update(write_tool_map)
    tool_call_maps.update(delete_tool_map)
    tool_call_maps.update(replace_tool_map)
    tool_call_maps.update(git_tool_map)
    tool_call_maps.update(bash_tool_map)
    tool_call_maps.update(workspace_tool_map)
    # tool_call_maps.update(compress_tool_map)
    tool_call_maps.update(network_tool_map)
    # tool_call_maps.update(interaction_tool_map)
    tool_call_maps.update(enhanced_interaction_tool_map)
    tool_call_maps.update(database_tool_map)
    tool_call_maps.update(web_search_tool_map)
    tool_call_maps.update(stock_tool_map)
    tool_call_maps.update(summary_tool_map)
    tool_call_maps.update(project_context_tool_map)
    tool_call_maps.update(diagram_tool_map)
    tool_call_maps.update(architect_tool_map)  # Architect tools last
    tool_call_maps.update(pdf_tool_map)
    tool_call_maps.update(markdown_tool_map)
    
    ui.print_warning(f"⚠️  Loaded {len(tools)} tools manually (no cache)")
    ui.print_info(f"📊 Includes {len(summary_tools)} context management tools")
    return tools, tool_call_maps

# List of tools that require messages parameter
TOOLS_REQUIRING_MESSAGES = [
    'enhance_summary',
    "summary_by_ai",
    "optimize_feature_context"
]

def execute_tool_with_messages_injection(tool_name, args, messages, tool_call_maps):
    """
    Execute a tool with automatic messages injection if needed.
    
    Args:
        tool_name: Name of the tool to execute
        args: Dictionary of arguments provided by the model
        messages: Current conversation messages
        tool_call_maps: Dictionary mapping tool names to functions
    
    Returns:
        Tool execution result
    """
    # Check if tool exists
    if tool_name not in tool_call_maps:
        return f"Tool '{tool_name}' not found in tool call map"
    
    # Get the tool function
    tool_function = tool_call_maps[tool_name]
    
    # Check if this tool requires messages parameter
    if tool_name in TOOLS_REQUIRING_MESSAGES:
        # Inject messages parameter if not already provided
        args['messages'] = messages
    # Execute the tool
    return tool_function(**args)
# ============================================================================
# PARSE COMMAND LINE ARGUMENTS
# ============================================================================

parser = argparse.ArgumentParser(description='AI Tools Enhanced Test Environment')
parser.add_argument('--stream', action='store_true', help='Enable streaming output mode')
parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
args, unknown = parser.parse_known_args()

# Update UI verbosity if needed
if args.verbose:
    ui = get_ui(verbose=True)

# Load tools
tools, tool_call_maps = load_manual_imports()
tools, tool_call_maps = load_manual_imports()

# ============================================================================
# REST OF THE CODE (same as before with cache support)
# ============================================================================

from openai import OpenAI
import os, json, traceback, sys
import threading
import time
from queue import Queue

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/")

def clear_reasoning_content(messages, lines_save=0):
    """Clear reasoning content from messages to avoid context overflow."""
    for i, message in enumerate(messages):
        if hasattr(message, 'reasoning_content') and  i < len(messages) - lines_save:
            message.reasoning_content = None
    

class StreamingThoughtDisplay:
    """Display streaming thoughts without adding extra lines."""
    def __init__(self):
        self.current_display = ""
        self.thought_queue = Queue()
        self.display_thread = None
        self.stop_display = False
        self.last_thought = ""
        
    def _display_thread_func(self):
        """Thread function to display thoughts incrementally."""
        while not self.stop_display:
            try:
                # Get thought from queue with timeout
                thought = self.thought_queue.get(timeout=0.1)
                if thought != self.last_thought:
                    # Clear previous display
                    sys.stdout.write('\r' + ' ' * len(self.current_display) + '\r')
                    # Display new thought
                    sys.stdout.write(f"\r🤔 {thought[:100]}" + ('...' if len(thought) > 100 else ''))
                    sys.stdout.flush()
                    self.current_display = thought[:100] + ('...' if len(thought) > 100 else '')
                    self.last_thought = thought
            except:
                pass
                
    def start(self):
        """Start the streaming thought display."""
        self.stop_display = False
        self.display_thread = threading.Thread(target=self._display_thread_func)
        self.display_thread.daemon = True
        self.display_thread.start()
        
    def add_thought(self, thought):
        """Add a thought to be displayed."""
        if thought and thought.strip():
            self.thought_queue.put(thought.strip())
            
    def stop(self):
        """Stop the streaming thought display."""
        self.stop_display = True
        if self.display_thread:
            self.display_thread.join(timeout=1)
        # Clear the display line
        sys.stdout.write('\r' + ' ' * len(self.current_display) + '\r')
        sys.stdout.flush()
        
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

def calculate_cost(usage, cache_discount=0.5):
    """Calculate cost based on token usage."""
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    reasoning_tokens = usage.completion_tokens_details.reasoning_tokens or 0
    
    cache_hit = usage.prompt_cache_hit_tokens
    cache_miss = usage.prompt_cache_miss_tokens
    
    prompt_price_per_million = 0.14  # $0.14 / 1M tokens
    completion_price_per_million = 0.28  # $0.28 / 1M tokens
    
    cache_miss_cost = (cache_miss / 1_000_000) * prompt_price_per_million
    cache_hit_cost = (cache_hit / 1_000_000) * prompt_price_per_million * cache_discount
    completion_cost = (completion_tokens / 1_000_000) * completion_price_per_million
    total_cost = cache_miss_cost + cache_hit_cost + completion_cost
    
    return {
        "cache_miss_cost": cache_miss_cost,
        "cache_hit_cost": cache_hit_cost,
        "completion_cost": completion_cost,
        "total_cost": total_cost,
        "reasoning_tokens_percentage": (reasoning_tokens / completion_tokens) * 100
    }

def run_turn_with_streaming_output(messages, streaming_display=None):
    """Run a turn with true streaming output for reasoning_content and content."""
    sub_turn = 1
    while True:
        try:
            ui.print(f"\n\n{'='*60}")
            ui.print(f"Turn {sub_turn} - Streaming Output")
            ui.print(f"{'='*60}")
            
            # Collect streaming content
            full_reasoning_content = ""
            full_content = ""
            tool_calls_chunks = []
            current_tool_call = None
            
            # Check if messages are too large
            estimated_tokens = estimate_message_tokens(messages)
            if estimated_tokens > 120000:
                ui.print_warning(f"⚠️  Estimated tokens ({estimated_tokens:.0f}) exceed safe threshold. Adding optimization prompt.")
                messages.append({
                    "role": "user",
                    "content": f"## Context Optimization Needed\n\nCurrent estimated token count: {estimated_tokens:.0f}, which exceeds the model's limit. Please use the 'enhance_summary' tool to summarize the conversation history before proceeding."
                })
                # Continue to API call, expecting AI to handle optimization
            
            # Make API call with true streaming
            stream = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                tools=tools,
                stream=True,
                extra_body={ "thinking": { "type": "enabled" } }
            )
            
            ui.print("\n🎯 Streaming response:")
            
            for chunk in stream:
                # Handle reasoning content
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    reasoning_chunk = chunk.choices[0].delta.reasoning_content
                    full_reasoning_content += reasoning_chunk
                    # Display reasoning chunk in real-time
                    if streaming_display:
                        streaming_display.add_thought(full_reasoning_content)
                    else:
                        # Print reasoning content as it comes
                        sys.stdout.write(f"\r🤔 Reasoning: {full_reasoning_content[:100]}" + ('...' if len(full_reasoning_content) > 100 else ''))
                        sys.stdout.flush()
                
                # Handle content
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    # Print content as it comes
                    sys.stdout.write(f"\r💬 Content: {full_content[:100]}" + ('...' if len(full_content) > 100 else ''))
                    sys.stdout.flush()
                
                # Handle tool calls
                if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                    tool_call_chunks = chunk.choices[0].delta.tool_calls
                    for tool_chunk in tool_call_chunks:
                        # This is complex; for simplicity, we'll collect tool calls
                        # but proper handling would require accumulating tool call data
                        pass
            
            # Clear the streaming line and print final results
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            sys.stdout.flush()
            
            # Now make a non-streaming call to get the full message with tool calls
            # This is a workaround because streaming with tool calls is complex
            ui.print("\n📦 Getting complete response with tool calls...")
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                tools=tools,
                stream=False,
                extra_body={ "thinking": { "type": "enabled" } }
            )
            
            cost = calculate_cost(response.usage)
            ui.print(f"💰 Cost: ${cost['total_cost']:.4f}")
            ui.print(f"📊 Total tokens: {response.usage.total_tokens}")
            message = response.choices[0].message
            final_reasoning_content = message.reasoning_content
            final_content = message.content
            final_tool_calls = message.tool_calls
            
            # Display final results
            ui.print(f"\n📊 Final results:")
            if final_reasoning_content:
                ui.print(f"🤔 Reasoning:\n{final_reasoning_content}")
            if final_content:
                ui.print(f"💬 Content: {final_content}")
            
            # Check for tool calls
            if final_tool_calls:
                ui.print_info(f"🔧 Found {len(final_tool_calls)} tool calls")
                
                # Add assistant message to conversation
                messages.append(message.model_dump())
                
                # Execute each tool call
                for tool_call in final_tool_calls:
                    try:
                        tool_name = tool_call.function.name
                        
                        # Parse arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as e:
                            error_msg = f"Error: Invalid JSON arguments for tool '{tool_name}': {str(e)}"
                            ui.print_error(f"❌ {error_msg}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": error_msg,
                            })
                            continue
                        
                        # Execute tool
                        ui.print_info(f"🛠️  Executing: {tool_name}")
                        if args:
                            ui.print_info(f"   Arguments: {args}")
                        
                        tool_result = execute_tool_with_messages_injection(tool_name, args, messages, tool_call_maps)
                        
                        # Truncate if too large
                        if isinstance(tool_result, str) and len(tool_result) > 2000:
                            tool_result = tool_result[:2000] + "... [truncated]"
                        
                        ui.print_success(f"✅ Tool result for {tool_name}: {str(tool_result)[:200]}...")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result),
                        })
                        
                    except Exception as e:
                        error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                        if args.verbose:
                            error_msg += f"\n{traceback.format_exc()}"
                        
                        ui.print_error(f"❌ {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_msg,
                        })
                
                # Continue to next sub-turn
                sub_turn += 1
                continue
            else:
                # No tool calls, we have final answer
                ui.print_success("✅ No tool calls needed - response complete")
                messages.append({"role": "assistant", "content": final_content})
                break
                
        except KeyboardInterrupt:
            if len(messages) > 1:
                msg = messages[-1]
                toolcalls = msg.get("tool_calls", [])
                if len(toolcalls) > 0:
                    messages.pop()

            ui.print_warning("\n\n⚠️  Interrupted by user")
            return None
        except Exception as e:
            error_msg = f"Error in API call or processing: {str(e)}\n{traceback.format_exc()}"
            ui.print_error(f"❌ {error_msg}")
            # Try to recover by asking for clarification
            recovery_msg = "I encountered an error. Please clarify what you want me to do, or try a different approach."
            messages.append({
                "role": "assistant",
                "content": recovery_msg
            })
            ui.print(f"💬 Recovery message: {recovery_msg}")

            break
    
    return response

def run_turn_with_enhanced_error_handling(messages, streaming_display=None):
    """Run a turn with enhanced error handling."""
    sub_turn = 1
    while True:
        try:
            ui.print(f"\n\n{'='*60}")
            ui.print(f"Turn {sub_turn} - Enhanced Mode")
            ui.print(f"{'='*60}")
            
            # Make API call with thinking enabled
            response = client.chat.completions.create(
                model='deepseek-chat',
                messages=messages,
                tools=tools,
                extra_body={ "thinking": { "type": "enabled" } }
            )
            
            cost = calculate_cost(response.usage)
            ui.print(f"💰 Cost: ${cost['total_cost']:.4f}")
            ui.print(f"📊 Total tokens: {response.usage.total_tokens}")
            
            message = response.choices[0].message
            reasoning_content = message.reasoning_content
            content = message.content
            tool_calls = message.tool_calls
            
            # Display thinking process
            if reasoning_content:
                ui.print(f"🤔 Reasoning:\n{reasoning_content}")
            
            ui.print(f"💬 Content: {content}")
            if tool_calls:
                ui.print_info(f"🔧 Tool calls: {len(tool_calls)}")
                for i, tool in enumerate(tool_calls):
                    ui.print(f"  {i+1}. {tool.function.name}")
            
            # Convert ChatCompletionMessage to dict for messages list
            messages.append(message.model_dump())
            if tool_calls and len(tool_calls) > 0:
                ui.print(f"📋 Message data: {message.model_dump()}")
            # If there are no tool calls, we have a final answer
            if tool_calls is None:
                break
                
            # Execute tool calls with error handling
            for tool in tool_calls:
                try:
                    tool_name = tool.function.name
                    if tool_name == "update_task_status":
                        clear_reasoning_content(messages, 3)
                    # Check if tool exists
                    if tool_name not in tool_call_maps:
                        error_msg = f"Error: Tool '{tool_name}' not found in tool call map"
                        ui.print_error(f"❌ {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool.id,
                            "content": error_msg,
                        })
                        continue
                    
                    # Parse arguments
                    try:
                        args = json.loads(tool.function.arguments)
                    except json.JSONDecodeError as e:
                        error_msg = f"Error: Invalid JSON arguments for tool '{tool_name}': {str(e)}"
                        ui.print_error(f"❌ {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool.id,
                            "content": error_msg,
                        })
                        continue
                    
                    # Execute tool
                    tool_function = tool_call_maps[tool_name]
                    ui.print_info(f"🛠️  Executing: {tool_name}")
                    ui.print(f"   Arguments: {args}")
                    
                    try:
                        tool_result = execute_tool_with_messages_injection(tool_name, args, messages, tool_call_maps)
                        ui.print_success(f"✅ Tool result for {tool_name}: {tool_result[:500]}{'...' if len(tool_result) > 500 else ''}")
                        
                        # Log to file for debugging
                        with open("tool_execution.log", "a") as log_file:
                            log_file.write(f"\n{'='*60}\n")
                            log_file.write(f"Time: {time.ctime()}\n")
                            log_file.write(f"Tool: {tool_name}\n")
                            log_file.write(f"Args: {args}\n")
                            log_file.write(f"total tokens: {response.usage.total_tokens}\n")
                            log_file.write(f"Result: {tool_result}\n")
                            
                    except Exception as e:
                        error_msg = f"Error executing tool '{tool_name}': {str(e)}\n{traceback.format_exc()}"
                        tool_result = error_msg
                        ui.print_error(f"❌ {error_msg}")
                        
                        # Log error
                        with open("tool_errors.log", "a") as error_file:
                            error_file.write(f"\n{'='*60}\n")
                            error_file.write(f"Time: {time.ctime()}\n")
                            error_file.write(f"Tool: {tool_name}\n")
                            error_file.write(f"Args: {args}\n")
                            error_file.write(f"Error: {str(e)}\n")
                            error_file.write(f"Traceback:\n{traceback.format_exc()}\n")
                    
                    # Add tool result to messages
                    # Truncate if too large
                    truncated_result = truncate_tool_result(tool_result)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool.id,
                        "content": truncated_result,
                    })
                    
                except Exception as e:
                    error_msg = f"Unexpected error processing tool call: {str(e)}\n{traceback.format_exc()}"
                    ui.print_error(f"❌ {error_msg}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool.id if 'tool' in locals() else 'unknown',
                        "content": error_msg,
                    })
            
            sub_turn += 1
            
            avoid_explosion(messages, response, tool_call_maps)

        except KeyboardInterrupt:
            if len(messages) > 1:
                msg = messages[-1]
                toolcalls = msg.get("tool_calls", [])
                if len(toolcalls) > 0:
                    messages.pop()

            ui.print_warning("\n\n⚠️  Interrupted by user")
            return None
        except Exception as e:
            error_msg = f"Error in API call or processing: {str(e)}\n{traceback.format_exc()}"
            ui.print_error(f"❌ {error_msg}")
            # Try to recover by asking for clarification
            recovery_msg = "I encountered an error. Please clarify what you want me to do, or try a different approach."
            messages.append({
                "role": "assistant",
                "content": recovery_msg
            })
            ui.print(f"💬 Recovery message: {recovery_msg}")

            break
    
    return response

def estimate_message_tokens(messages):
    """Estimate token count for messages."""
    import tiktoken
    try:
        encoder = tiktoken.encoding_for_model("gpt-4")
        total_tokens = 0
        for message in messages:
            content = str(message.get('content', ''))
            total_tokens += len(encoder.encode(content))
        return total_tokens
    except:
        # Fallback estimation
        total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)
        return total_chars // 4  # Rough estimate

def truncate_tool_result(result, max_length=4000):
    """Truncate tool result if too large."""
    result_str = str(result)
    if len(result_str) > max_length:
        return result_str[:max_length] + f"... [truncated, original length: {len(result_str)}]"
    return result_str

def avoid_explosion(messages, response, tool_call_maps=None):
    """
    Smart context management to prevent token explosion.
    Automatically suggests context optimization when token usage is high.
    
    Args:
        messages: Conversation messages list
        response: Latest API response with usage info
        tool_call_maps: Tool call maps (optional, for direct optimization)
    """
    if response is None or not hasattr(response, 'usage'):
        return
    
    total_tokens = response.usage.total_tokens
    
    # Configuration
    WARNING_THRESHOLD = 70000  # Start warning at 70k tokens
    CRITICAL_THRESHOLD = 85000  # Critical at 85k tokens
    MAX_MESSAGES = 100  # Max messages before suggesting optimization
    
    # Check conditions
    needs_optimization = (
        total_tokens > WARNING_THRESHOLD  
        #or len(messages) > MAX_MESSAGES
    )
    
    if needs_optimization:
        ui.print_warning(f"⚠️  Context size warning: {total_tokens:,} tokens, {len(messages)} messages")
        
        # Calculate urgency level
        urgency = "HIGH" if total_tokens > CRITICAL_THRESHOLD else "MEDIUM"
        
        # Prepare detailed optimization suggestion
        optimization_prompt = f"""## Context Optimization Needed ({urgency} Priority)

**Current Status:**
- Total tokens: {total_tokens:,}
- Messages count: {len(messages)}
- Token limit warning: {'CRITICAL - Near limit' if total_tokens > CRITICAL_THRESHOLD else 'Warning - Approaching limit'}

**Action Required:**
Please use the 'enhance_summary' tool to optimize the conversation context.

**How to create an effective summary:**
1. **Review the conversation history** and identify key milestones
2. **Extract essential information**:
   - User's original goal/request
   - Major decisions made
   - Completed tasks with results
   - Current task in progress
   - which files include 'TODO' if has.
   - Next planned steps
3. **Format the summary** as a concise narrative

**Summary Template:**
"User initially requested [original goal]. We have completed [completed tasks], 
currently working on [current task], with next steps being [next steps]. 
Key decisions include [key decisions]."

After creating the summary, call 'enhance_summary' with the summary content.
"""

        # Add the optimization prompt as a user message
        messages.append({
            "role": "user",
            "content": optimization_prompt
        })
        
        ui.print_info(f"📝 Added context optimization prompt (urgency: {urgency})")
        
        # If we have tool_call_maps and are in critical state, we could auto-trigger
        # but for now, we just prompt the AI to do it
        
    elif total_tokens > 50000:
        # Early warning for monitoring
        ui.print_info(f"ℹ️  Context monitoring: {total_tokens:,} tokens used")

def run_interactive_session(streaming_mode=False):
    """Run an interactive session with the user."""
    messages = [
        {"role": "system", "content": """
You are a software expert with access to tools for operating systems, files, networks, Git, and more.

## Core Development Principles:
1. **Small Feature Focus**: Work on one atomic, completable feature .
2. **Incremental Completion**: After each feature: use 'optimize_feature_context' tool to clear intermediate data, load TODO.md, and prepare for next feature.
3. **Token Management**: Proactively use 'enhance_summary' tool to prevent token overflow (>10w tokens).
4. **Task Tracking**: Update TODO.md and project context after each feature completion.

## Key Workflow:
- Break tasks into small, executable features
- After feature completion: use 'optimize_feature_context' tool → clear intermediate data → load TODO.md → discuss next feature
- Use 'enhance_summary' when context grows large (>70k tokens)
- Maintain clear communication of next steps

## Context Optimization Strategy:
- **After each atomic feature completion**: Use 'optimize_feature_context' to clear intermediate data and prepare for next feature
- **When token usage is high (>70k)**: Use 'enhance_summary' to:
  1. Summarize conversation milestones
  2. Extract completed tasks and current progress
  3. Preserve key decisions and next steps
  4. Optimize while retaining essential context

## File operation
- Don`t make file more than 500 lines.

Keep responses concise and focused on the current feature.

## Tool Usage Guide:
- **optimize_feature_context**: Use AFTER completing an atomic feature to clear intermediate data and load TODO.md for next feature
- **enhance_summary**: Use WHEN token count is high (>70k) to summarize conversation while preserving context

Remember: Complete one atomic feature at a time, then use optimize_feature_context before moving to the next feature.
"""}]
    # Try to auto-detect project context
    try:
        # Dynamically import project_context module
        from project_context.project_context import generate_context_summary_for_ai
        context_summary = generate_context_summary_for_ai(".")
        
        # Add context summary as user message if meaningful
        if context_summary and "Failed to generate context summary" not in context_summary and "Failed to generate context summary" not in context_summary:
            messages.append({
                "role": "user", 
                "content": context_summary + "\n\n💡 **Request**\nPlease check the current project status, then continue previous work or start new tasks. se available project context tools to manage development plans."
            })
            ui.print_success("✅ Loaded project context automatically")

        else:
            # No context or error
            messages.append({
                "role": "user",
                "content": "No project context file (.aitools_context.json) detected. You can use detect_project to view current directory project information, or use create_development_plan to create development plans."
            })
            ui.print_info("ℹ️  No project context found. Starting fresh session.")
    except ImportError as e:
        messages.append({
            "role": "user",
            "content": "Project context module failed to load. Please ensure the project_context module is properly installed."
        })
        ui.print_warning(f"⚠️  Project context module not available: {e}")
    except Exception as e:
        messages.append({
            "role": "user",
            "content": f"Error automatically loading project context: {str(e)}"
        })
        ui.print_warning(f"⚠️  Error loading project context: {e}")
    
    ui.print_header("🤖 AI Tools Enhanced Test Environment")
    if streaming_mode:
        ui.print_info("🌟 Streaming Output Mode Enabled")
    ui.print("="*60)
    ui.print("Available tools: File ops, Git, Shell, Workspace, Environment,")
    ui.print("                Compression, Network, Interaction, Database, Web Search, Stock, Context Management")
    ui.print("="*60)
    ui.print("Type 'quit' or 'exit' to end the session")
    ui.print("Type 'clear' to clear the conversation history")
    ui.print("Type 'mode' to toggle streaming mode")
    ui.print("Type 'rescan' to rescan project and reload tools")
    ui.print("Type 'mode' to toggle streaming output")
    ui.print("Type 'clear' to clear conversation history")
    ui.print("="*60 + "\\n")
    ui.print("="*60 + "\n")
    
    # Store current cache type
    
    # Ask for initial user input
    user_input = input("💭 What would you like me to help with? > ")
    
    while user_input.lower() not in ['quit', 'exit', 'q']:
        if user_input.lower() == 'clear':
            messages = [messages[0]]  # Keep system message
            ui.print_info("🗑️  Conversation history cleared.")
            
        elif user_input.lower() == 'mode':
            streaming_mode = not streaming_mode
            ui.print_info(f"🔄 Streaming mode {'enabled' if streaming_mode else 'disabled'}")
            
        elif user_input.lower() == 'rescan':
            ui.print_info("🔄 Rescanning project and reloading tools...")
            global tools, tool_call_maps
            
            try:
                # Directly reload tools using load_manual_imports
                tools, tool_call_maps = load_manual_imports()
                ui.print_success(f"✅ Rescan complete. Now have {len(tools)} tools.")
                
            except Exception as e:
                ui.print_error(f"❌ Error during rescan: {e}")
            except ImportError:
                ui.print_error("❌ Cache module not available. Cannot rescan.")
            except Exception as e:
                ui.print_error(f"❌ Error during rescan: {e}")
                
        elif user_input.lower() == "show messages":
            ui.print(f"Current conversation messages:\n{json.dumps(messages, indent=2)}")
            
        elif user_input.strip():
            messages.append({"role": "user", "content": user_input})
            
            if streaming_mode:
                # Run with true streaming output
                ui.print_info("\n🚀 Starting streaming response...")
                with StreamingThoughtDisplay() as stream_display:
                    response = run_turn_with_streaming_output(messages, stream_display)
            else:
                # Run with enhanced error handling
                with StreamingThoughtDisplay() as stream_display:
                    response = run_turn_with_enhanced_error_handling(messages, stream_display)
            
            if response and response.choices[0].message.content:
                ui.print(f"\n🤖 Assistant: {response.choices[0].message.content}")
        
        # Get next user input
        user_input = input("\n💭 Next request? > ")
    
    ui.print_info("\n👋 Session ended. Goodbye!")

def main():
    """Entry point for console script."""
    run_interactive_session(streaming_mode=args.stream)

if __name__ == "__main__":
    main()
