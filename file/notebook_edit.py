#!/usr/bin/env python3
"""
NotebookEditTool implementation for AITools.
Provides functionality to edit Jupyter notebook files, aligned with Claude Code's NotebookEditTool.
"""

import os
import sys
import json
import copy
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# AITools decorators - same pattern as other tools
from base import function_ai, parameters_func, property_param

__NOTEBOOK_EDIT_PROPERTY_ONE__ = property_param(
    name="action",
    description="Action to perform on the notebook: 'read', 'write', 'add_cell', 'remove_cell', 'update_cell', 'execute'.",
    t="string",
    required=True,
    enum=["read", "write", "add_cell", "remove_cell", "update_cell", "execute"]
)

__NOTEBOOK_EDIT_PROPERTY_TWO__ = property_param(
    name="filepath",
    description="Path to the notebook file (.ipynb).",
    t="string",
)

__NOTEBOOK_EDIT_PROPERTY_THREE__ = property_param(
    name="content",
    description="Content for write action or cell content for add/update actions.",
    t="string",
)

__NOTEBOOK_EDIT_PROPERTY_FOUR__ = property_param(
    name="cell_type",
    description="Type of cell for add/update actions: 'code', 'markdown'.",
    t="string",
    enum=["code", "markdown"]
)

__NOTEBOOK_EDIT_PROPERTY_FIVE__ = property_param(
    name="cell_index",
    description="Index of cell for remove/update/execute actions (0-based).",
    t="number",
)

__NOTEBOOK_EDIT_PROPERTY_SIX__ = property_param(
    name="output",
    description="Output to set for execute action or cell output.",
    t="string",
)

@function_ai(
    name="notebook_edit",
    description="Edit Jupyter notebook files (.ipynb), similar to Claude Code's NotebookEditTool.",
    category="file"
)
def notebook_edit(
    action: str,
    filepath: str = "",
    content: str = "",
    cell_type: str = "code",
    cell_index: int = -1,
    output: str = ""
) -> str:
    """
    Edit Jupyter notebook files.
    
    This tool mimics Claude Code's NotebookEditTool functionality for working with
    Jupyter notebook (.ipynb) files.
    
    Args:
        action: Action to perform (read, write, add_cell, remove_cell, update_cell, execute)
        filepath: Path to notebook file
        content: Content for write or cell content
        cell_type: Type of cell (code, markdown)
        cell_index: Index of cell (0-based)
        output: Output for execute action or cell output
        
    Returns:
        Result of the operation or notebook content
    """
    try:
        # Validate inputs
        if action in ["read", "write", "add_cell", "remove_cell", "update_cell", "execute"]:
            if action != "write" and not filepath:
                return "Error: filepath is required for this action."
        else:
            return f"Error: Invalid action '{action}'. Must be one of: read, write, add_cell, remove_cell, update_cell, execute"
        
        # Perform the requested action
        if action == "read":
            return read_notebook(filepath)
        elif action == "write":
            return write_notebook(filepath, content)
        elif action == "add_cell":
            return add_cell(filepath, content, cell_type)
        elif action == "remove_cell":
            return remove_cell(filepath, cell_index)
        elif action == "update_cell":
            return update_cell(filepath, cell_index, content, cell_type)
        elif action == "execute":
            return execute_cell(filepath, cell_index, output)
        else:
            return f"Error: Action '{action}' not implemented"
            
    except Exception as e:
        return f"Error in notebook_edit: {str(e)}"


def read_notebook(filepath: str) -> str:
    """
    Read and return notebook content in a readable format.
    """
    if not os.path.exists(filepath):
        return f"Error: Notebook file not found: {filepath}"
    
    if not filepath.endswith('.ipynb'):
        return f"Error: File must have .ipynb extension: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Format notebook info
        return format_notebook_info(notebook, filepath)
        
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in notebook file: {filepath}"
    except Exception as e:
        return f"Error reading notebook: {str(e)}"


def write_notebook(filepath: str, content: str) -> str:
    """
    Write content to a notebook file.
    If file doesn't exist, creates a new notebook.
    """
    try:
        # Parse content if provided, otherwise create empty notebook
        if content:
            try:
                notebook = json.loads(content)
            except json.JSONDecodeError:
                return f"Error: Content must be valid JSON for notebook"
        else:
            # Create empty notebook
            notebook = create_empty_notebook()
        
        # Ensure it has notebook structure
        if not validate_notebook_structure(notebook):
            return "Error: Invalid notebook structure"
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Successfully wrote notebook to: {filepath}\n" + format_notebook_info(notebook, filepath)
        
    except Exception as e:
        return f"Error writing notebook: {str(e)}"


def add_cell(filepath: str, content: str, cell_type: str = "code") -> str:
    """
    Add a cell to the notebook.
    """
    if not os.path.exists(filepath):
        return f"Error: Notebook file not found: {filepath}"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Create new cell
        if cell_type == "code":
            new_cell = {
                "cell_type": "code",
                "metadata": {},
                "source": content.splitlines(),
                "execution_count": None,
                "outputs": []
            }
        else:  # markdown
            new_cell = {
                "cell_type": "markdown",
                "metadata": {},
                "source": content.splitlines()
            }
        
        # Add cell to notebook
        notebook["cells"].append(new_cell)
        
        # Save back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        cell_index = len(notebook["cells"]) - 1
        return f"Added {cell_type} cell at index {cell_index} to {filepath}"
        
    except Exception as e:
        return f"Error adding cell: {str(e)}"


def remove_cell(filepath: str, cell_index: int) -> str:
    """
    Remove a cell from the notebook.
    """
    if not os.path.exists(filepath):
        return f"Error: Notebook file not found: {filepath}"
    
    if cell_index < 0:
        return "Error: cell_index must be >= 0"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        if cell_index >= len(notebook["cells"]):
            return f"Error: cell_index {cell_index} out of range (notebook has {len(notebook['cells'])} cells)"
        
        # Remove the cell
        removed_cell = notebook["cells"].pop(cell_index)
        cell_type = removed_cell.get("cell_type", "unknown")
        
        # Save back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Removed {cell_type} cell at index {cell_index} from {filepath}"
        
    except Exception as e:
        return f"Error removing cell: {str(e)}"


def update_cell(filepath: str, cell_index: int, content: str, cell_type: str = "code") -> str:
    """
    Update a cell in the notebook.
    """
    if not os.path.exists(filepath):
        return f"Error: Notebook file not found: {filepath}"
    
    if cell_index < 0:
        return "Error: cell_index must be >= 0"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        if cell_index >= len(notebook["cells"]):
            return f"Error: cell_index {cell_index} out of range (notebook has {len(notebook['cells'])} cells)"
        
        # Update the cell
        cell = notebook["cells"][cell_index]
        cell["cell_type"] = cell_type
        cell["source"] = content.splitlines()
        
        # For code cells, reset execution
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        
        # Save back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Updated cell at index {cell_index} to {cell_type} cell in {filepath}"
        
    except Exception as e:
        return f"Error updating cell: {str(e)}"


def execute_cell(filepath: str, cell_index: int, output: str = "") -> str:
    """
    "Execute" a cell (simulated execution for AITools environment).
    In real Claude Code, this would actually execute the code in a kernel.
    Here we simulate by setting outputs.
    """
    if not os.path.exists(filepath):
        return f"Error: Notebook file not found: {filepath}"
    
    if cell_index < 0:
        return "Error: cell_index must be >= 0"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        if cell_index >= len(notebook["cells"]):
            return f"Error: cell_index {cell_index} out of range (notebook has {len(notebook['cells'])} cells)"
        
        cell = notebook["cells"][cell_index]
        if cell.get("cell_type") != "code":
            return f"Error: Cell at index {cell_index} is not a code cell (type: {cell.get('cell_type', 'unknown')})"
        
        # Simulate execution
        cell["execution_count"] = cell.get("execution_count", 0) + 1
        
        # Set output if provided
        if output:
            cell["outputs"] = [{
                "output_type": "execute_result",
                "data": {"text/plain": output},
                "execution_count": cell["execution_count"]
            }]
        else:
            # Default simulated output
            source = "".join(cell.get("source", []))
            cell["outputs"] = [{
                "output_type": "execute_result",
                "data": {"text/plain": f"Simulated execution of: {source[:50]}..."},
                "execution_count": cell["execution_count"]
            }]
        
        # Save back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Simulated execution of code cell at index {cell_index} in {filepath}"
        
    except Exception as e:
        return f"Error executing cell: {str(e)}"


def create_empty_notebook() -> Dict[str, Any]:
    """
    Create an empty Jupyter notebook structure.
    """
    return {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


def validate_notebook_structure(notebook: Dict[str, Any]) -> bool:
    """
    Validate that the dictionary has basic notebook structure.
    """
    required_keys = ["cells", "metadata", "nbformat", "nbformat_minor"]
    return all(key in notebook for key in required_keys)


def format_notebook_info(notebook: Dict[str, Any], filepath: str) -> str:
    """
    Format notebook information for display.
    """
    nbformat = notebook.get("nbformat", "?")
    nbformat_minor = notebook.get("nbformat_minor", "?")
    cells = notebook.get("cells", [])
    
    # Count cell types
    code_cells = sum(1 for cell in cells if cell.get("cell_type") == "code")
    markdown_cells = sum(1 for cell in cells if cell.get("cell_type") == "markdown")
    other_cells = len(cells) - code_cells - markdown_cells
    
    # Get kernel info
    metadata = notebook.get("metadata", {})
    kernelspec = metadata.get("kernelspec", {})
    kernel_name = kernelspec.get("display_name", "Unknown")
    
    # Format cell previews
    cell_previews = []
    for i, cell in enumerate(cells[:5]):  # Show first 5 cells
        cell_type = cell.get("cell_type", "unknown")
        source = "".join(cell.get("source", []))[:100]
        preview = f"  [{i}] {cell_type.upper()}: {source}..."
        cell_previews.append(preview)
    
    result = f"""
Notebook: {os.path.basename(filepath)}
Path: {filepath}
Format: nbformat {nbformat}.{nbformat_minor}
Kernel: {kernel_name}

Cells: {len(cells)} total
  • Code: {code_cells}
  • Markdown: {markdown_cells}
  • Other: {other_cells}

{'=' * 60}
CELL PREVIEWS (first {min(5, len(cells))} of {len(cells)}):
{'=' * 60}
"""
    if cell_previews:
        result += "\n".join(cell_previews)
    else:
        result += "  (No cells)"
    
    if len(cells) > 5:
        result += f"\n  ... and {len(cells) - 5} more cells"
    
    result += f"\n{'=' * 60}"
    
    # Add notebook metadata summary
    if metadata:
        result += "\n\nMETADATA SUMMARY:\n"
        for key, value in list(metadata.items())[:3]:  # Show first 3 items
            if isinstance(value, dict):
                value_str = f"dict with {len(value)} keys"
            elif isinstance(value, list):
                value_str = f"list with {len(value)} items"
            else:
                value_str = str(value)[:50]
            result += f"  {key}: {value_str}\n"
    
    return result.strip()


# Export tools
tools = [notebook_edit]
TOOL_CALL_MAP = {
    "notebook_edit": notebook_edit
}

if __name__ == "__main__":
    # Test the notebook_edit function
    print("Testing NotebookEditTool...")
    print("-" * 60)
    
    # Create a test notebook
    test_file = "test_notebook.ipynb"
    
    # Test 1: Create notebook
    print("1. Creating empty notebook...")
    empty_nb = create_empty_notebook()
    result = notebook_edit("write", test_file, json.dumps(empty_nb))
    print(result[:200] + "..." if len(result) > 200 else result)
    
    # Test 2: Add cells
    print("\n2. Adding cells...")
    print(notebook_edit("add_cell", test_file, "print('Hello, World!')", "code"))
    print(notebook_edit("add_cell", test_file, "# This is a markdown cell", "markdown"))
    
    # Test 3: Read notebook
    print("\n3. Reading notebook...")
    result = notebook_edit("read", test_file)
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Test 4: Execute cell (simulated)
    print("\n4. Executing cell (simulated)...")
    print(notebook_edit("execute", test_file, cell_index=0, output="Hello, World!"))
    
    # Test 5: Update cell
    print("\n5. Updating cell...")
    print(notebook_edit("update_cell", test_file, cell_index=0, content="x = 1\ny = 2\nprint(x + y)"))
    
    # Test 6: Read again
    print("\n6. Reading updated notebook...")
    result = notebook_edit("read", test_file)
    print(result[:400] + "..." if len(result) > 400 else result)
    
    # Cleanup
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\nCleaned up test file: {test_file}")
    
    print("-" * 60)
    print("Test completed!")