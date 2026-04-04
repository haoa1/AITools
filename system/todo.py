from base import function_ai, parameters_func, property_param
import os
import json
import tempfile
from typing import List, Dict, Any

__TODOS_PROPERTY__ = property_param(
    name="todos",
    description="The updated todo list as a JSON array. Each todo item should have 'content', 'status' ('pending', 'in_progress', or 'completed'), and 'activeForm' fields.",
    t="string",
    required=True,
)

__TODO_FUNCTION__ = function_ai(
    name="todo_write",
    description="Manage the session task checklist. Similar to Claude Code's TodoWriteTool, this updates the todo list with new items. Returns the previous and updated todo lists.",
    parameters=parameters_func(
        [__TODOS_PROPERTY__]
    ),
)

tools = [__TODO_FUNCTION__]

# Todo file path
_TODO_FILE = os.path.join(tempfile.gettempdir(), "aitools_todos.json")

def _load_todos() -> Dict[str, List[Dict[str, Any]]]:
    """Load todos from file."""
    if not os.path.exists(_TODO_FILE):
        return {}
    
    try:
        with open(_TODO_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_todos(todos: Dict[str, List[Dict[str, Any]]]) -> bool:
    """Save todos to file."""
    try:
        with open(_TODO_FILE, 'w') as f:
            json.dump(todos, f, indent=2)
        return True
    except IOError:
        return False

def _validate_todo_item(todo: Dict[str, Any]) -> str:
    """Validate a single todo item."""
    if not isinstance(todo, dict):
        return "Todo item must be a JSON object"
    
    # Check required fields
    required_fields = ['content', 'status', 'activeForm']
    for field in required_fields:
        if field not in todo:
            return f"Missing required field: {field}"
    
    # Validate content
    content = todo.get('content', '')
    if not content or not isinstance(content, str):
        return "Content must be a non-empty string"
    
    # Validate status
    status = todo.get('status', '')
    if status not in ['pending', 'in_progress', 'completed']:
        return "Status must be one of: 'pending', 'in_progress', 'completed'"
    
    # Validate activeForm
    active_form = todo.get('activeForm', '')
    if not active_form or not isinstance(active_form, str):
        return "ActiveForm must be a non-empty string"
    
    return ""

def todo_write(todos: str) -> str:
    """
    Update the todo list with new items.
    
    Args:
        todos: JSON string containing array of todo items
    
    Returns:
        Formatted string with operation result
    """
    # Parse the todos JSON
    try:
        todos_list = json.loads(todos)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format for todos: {str(e)}"
    
    # Validate it's a list
    if not isinstance(todos_list, list):
        return "Error: Todos must be a JSON array"
    
    # Validate each todo item
    for i, todo in enumerate(todos_list):
        error = _validate_todo_item(todo)
        if error:
            return f"Error in todo item {i+1}: {error}"
    
    # Load existing todos
    all_todos = _load_todos()
    
    # Use a default key for simplicity (in Claude Code it's sessionId or agentId)
    todo_key = "default"
    
    # Get old todos
    old_todos = all_todos.get(todo_key, [])
    
    # Check if all todos are completed
    all_done = all(todo.get('status') == 'completed' for todo in todos_list)
    
    # Update todos (if all done, clear the list)
    new_todos = [] if all_done else todos_list
    all_todos[todo_key] = new_todos
    
    # Save to file
    if not _save_todos(all_todos):
        return f"Error: Failed to save todos to {_TODO_FILE}"
    
    # Build response
    response_lines = []
    response_lines.append("✅ Todos have been updated successfully.")
    response_lines.append("")
    
    if old_todos:
        response_lines.append("Previous todos:")
        for i, todo in enumerate(old_todos, 1):
            status_icon = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(todo.get('status', 'pending'), '⏳')
            response_lines.append(f"  {i}. {status_icon} {todo.get('content', '')}")
        response_lines.append("")
    
    if new_todos:
        response_lines.append("Updated todos:")
        for i, todo in enumerate(new_todos, 1):
            status_icon = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅'
            }.get(todo.get('status', 'pending'), '⏳')
            response_lines.append(f"  {i}. {status_icon} {todo.get('content', '')}")
    else:
        response_lines.append("All todos completed! List cleared.")
    
    # Add verification nudge if all done and had 3+ items (similar to Claude Code)
    if all_done and len(todos_list) >= 3:
        response_lines.append("")
        response_lines.append("📝 Note: You've completed 3+ tasks. Consider verifying your work before finalizing.")
    
    return "\n".join(response_lines)

TOOL_CALL_MAP = {
    "todo_write": todo_write,
}