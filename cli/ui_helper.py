"""
AITools CLI UI Helper with Rich-powered terminal interface.

This module provides beautiful terminal UI components for AITools CLI,
inspired by elegant terminal interface design.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
import sys
import os
from pathlib import Path

try:
    from rich.console import Console, ConsoleOptions, RenderResult
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.tree import Tree
    from rich.markdown import Markdown
    from rich.layout import Layout
    from rich.live import Live
    from rich.columns import Columns
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.status import Status
    from rich.syntax import Syntax
    from rich.style import Style
    from rich.theme import Theme
    from rich import box
    from rich.markup import escape

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback to basic ANSI colors
    class Colors:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        DIM = '\033[2m'

# Import scroll display module
try:
    from cli.scroll_display import (
        TerminalScrollDisplay, ScrollConfig, ScrollMode,
        fixed_area_scroll_display, circular_scroll_display
    )
    SCROLL_DISPLAY_AVAILABLE = True
except ImportError as e:
    SCROLL_DISPLAY_AVAILABLE = False
    print(f"⚠️  Scroll display module not available: {e}")
# Types of UI components
COMMAND = "command"
INFO = "info"
SUCCESS = "success"
WARNING = "warning"
ERROR = "error"
PROGRESS = "progress"
TABLE = "table"
PANEL = "panel"
TREE = "tree"

class AIToolsTheme:
    """AITools UI Theme definition."""
    
    # Color palette inspired by modern terminal design
    COLORS = {
        "primary": "#3498db",      # Blue - main actions
        "secondary": "#2ecc71",    # Green - success/positive
        "accent": "#9b59b6",       # Purple - highlights
        "warning": "#f39c12",      # Orange - warnings
        "danger": "#e74c3c",       # Red - errors
        "dark": "#2c3e50",         # Dark blue - headers
        "light": "#ecf0f1",        # Light gray - backgrounds
        "medium": "#95a5a6",       # Medium gray - secondary text
        "code": "#27ae60",         # Green - code
    }
    
    # Rich theme configuration
    RICH_THEME = Theme({
        "primary": "bold cyan",
        "secondary": "bold green",
        "accent": "bold magenta",
        "warning": "bold yellow",
        "danger": "bold red",
        "dark": "bold blue",
        "light": "white",
        "medium": "dim white",
        "code": "green",
        "success": "bold green",
        "info": "cyan",
        "header": "bold cyan reverse",
        "subheader": "bold blue",
        "param": "yellow",
        "type": "magenta",
        "highlight": "bold white on blue",
        "dim": "dim white",
    })
    
    # Box styles for tables
    TABLE_STYLES = {
        "simple": box.SIMPLE,
        "rounded": box.ROUNDED,
        "double": box.DOUBLE,
        "heavy": box.HEAVY,
        "minimal": box.MINIMAL,
    }
    
    @classmethod
    def get_color(cls, name: str) -> str:
        """Get color by name."""
        return cls.COLORS.get(name, "#3498db")
    
    @classmethod
    def get_style(cls, name: str) -> Style:
        """Get Rich style by name."""
        if RICH_AVAILABLE:
            return Style.parse(cls.RICH_THEME.styles.get(name, ""))
        return Style()


class AIToolsUI:
    """Main UI manager for AITools CLI."""
    
    def __init__(self, verbose: bool = False):
        """Initialize UI manager."""
        self.verbose = verbose
        
        if RICH_AVAILABLE:
            self.console = Console(theme=AIToolsTheme.RICH_THEME)
            self.progress = None
        else:
            self.console = None
            self._init_fallback_colors()
        
        # UI state
        self.current_context = "default"
        self.interactive_mode = False
        
    def _init_fallback_colors(self):
        """Initialize fallback colors when Rich is not available."""
        if not RICH_AVAILABLE:
            self.colors = Colors()
        else:
            self.colors = None
    
    # ==========================================================================
    # Basic Output Methods
    # ==========================================================================
    
    def print(self, *args, **kwargs):
        """Print with appropriate formatting."""
        if self.console and RICH_AVAILABLE:
            self.console.print(*args, **kwargs)
        else:
            # Basic print for fallback
            text = " ".join(str(arg) for arg in args)
            print(text)
    
    def print_header(self, text: str):
        """Print a header."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[bold cyan]╔═ {text} ════════════════════════════════════════[/bold cyan]")
        else:
            print(f"{self.colors.BOLD}{self.colors.CYAN}=== {text} ==={self.colors.ENDC}")
    
    def print_success(self, text: str):
        """Print a success message."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[bold green]✓ {text}[/bold green]")
        else:
            print(f"{self.colors.BOLD}{self.colors.GREEN}✓ {text}{self.colors.ENDC}")
    
    def print_error(self, text: str):
        """Print an error message."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[bold red]✗ {text}[/bold red]")
        else:
            print(f"{self.colors.BOLD}{self.colors.RED}✗ {text}{self.colors.ENDC}")
    
    def print_warning(self, text: str):
        """Print a warning message."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[bold yellow]⚠ {text}[/bold yellow]")
        else:
            print(f"{self.colors.BOLD}{self.colors.YELLOW}⚠ {text}{self.colors.ENDC}")
    
    def print_info(self, text: str):
        """Print an info message."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"[cyan]ℹ {text}[/cyan]")
        else:
            print(f"{self.colors.CYAN}ℹ {text}{self.colors.ENDC}")
    
    # ==========================================================================
    # Advanced Components
    # ==========================================================================
    
    def print_table(self, data: List[Dict[str, Any]], title: str = None, page_size: int = None, interactive: bool = True):
        """Print data as a table with optional pagination.

        Args:
            data: List of dictionaries to display as a table.
            title: Optional table title.
            page_size: Number of rows per page. If None or 0, shows all rows.
                If specified and data exceeds page_size, enables pagination.
            interactive: If True, enables interactive navigation (n/p/q keys).
                If False, only shows the first page with page indicator.
        """
        if not data:
            self.print_info("No data to display")
            return
        
        # If no page_size specified or data fits in one page, use original behavior
        if page_size is None or page_size <= 0 or len(data) <= page_size:
            self._print_table_simple(data, title)
            return
        
        if interactive:
            # Interactive pagination
            self._print_table_paginated(data, title, page_size)
        else:
            # Non-interactive: show first page with page indicator
            page_data = data[:page_size]
            page_title = f"{title} - Page 1/{(len(data) + page_size - 1) // page_size} (showing first {page_size} of {len(data)} rows)" if title else f"Page 1/{(len(data) + page_size - 1) // page_size} (first {page_size} of {len(data)} rows)"
            self._print_table_simple(page_data, page_title)
            self.print_info(f"Use 'page_size={page_size}, interactive=True' to enable page navigation")
    
    def _print_table_simple(self, data: List[Dict[str, Any]], title: str = None):
        """Print table without pagination (original implementation)."""
        if self.console and RICH_AVAILABLE:
            table = Table(title=title, box=AIToolsTheme.TABLE_STYLES["rounded"])
            
            # Add columns
            for key in data[0].keys():
                table.add_column(str(key), style="cyan")
            
            # Add rows
            for row in data:
                table.add_row(*[str(row.get(key, "")) for key in data[0].keys()])
            
            self.console.print(table)
        else:
            # Basic table fallback
            if title:
                print(f"{self.colors.BOLD}{self.colors.CYAN}=== {title} ==={self.colors.ENDC}")
            
            # Determine column widths
            col_widths = {}
            for key in data[0].keys():
                col_widths[key] = len(str(key))
                for row in data:
                    col_widths[key] = max(col_widths[key], len(str(row.get(key, ""))))
            
            # Print header
            header = " | ".join(str(key).ljust(col_widths[key]) for key in data[0].keys())
            print(f"{self.colors.BOLD}{header}{self.colors.ENDC}")
            print("-" * len(header))
            
            # Print rows
            for row in data:
                row_str = " | ".join(str(row.get(key, "")).ljust(col_widths[key]) for key in data[0].keys())
                print(row_str)
    
    def _print_table_paginated(self, data: List[Dict[str, Any]], title: str, page_size: int):
        """Print table with interactive pagination."""
        total_rows = len(data)
        total_pages = (total_rows + page_size - 1) // page_size
        current_page = 1
        
        while True:
            # Calculate page slice
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            page_data = data[start_idx:end_idx]
            
            # Create page title
            page_title = f"{title} - Page {current_page}/{total_pages} ({start_idx+1}-{end_idx} of {total_rows})" if title else f"Page {current_page}/{total_pages} ({start_idx+1}-{end_idx} of {total_rows})"
            
            # Print the current page
            self._print_table_simple(page_data, page_title)
            
            # Show navigation instructions
            if current_page < total_pages:
                if self.console and RICH_AVAILABLE:
                    self.console.print("[dim]n: Next page, p: Previous page, q: Quit[/dim]")
                else:
                    print(f"{self.colors.DIM}n: Next page, p: Previous page, q: Quit{self.colors.ENDC}")
            elif current_page == total_pages and current_page > 1:
                if self.console and RICH_AVAILABLE:
                    self.console.print("[dim]p: Previous page, q: Quit[/dim]")
                else:
                    print(f"{self.colors.DIM}p: Previous page, q: Quit{self.colors.ENDC}")
            else:
                if self.console and RICH_AVAILABLE:
                    self.console.print("[dim]q: Quit[/dim]")
                else:
                    print(f"{self.colors.DIM}q: Quit{self.colors.ENDC}")
            
            # Get user input for navigation
            if self.console and RICH_AVAILABLE:
                action = Prompt.ask("[cyan]Action[/cyan]", choices=["n", "p", "q", ""], default="")
            else:
                action = input(f"{self.colors.CYAN}Action (n/p/q): {self.colors.ENDC}").strip().lower()
            
            # Process action
            if action == "n" and current_page < total_pages:
                current_page += 1
            elif action == "p" and current_page > 1:
                current_page -= 1
            elif action == "q" or action == "":
                break
            else:
                if self.console and RICH_AVAILABLE:
                    self.console.print("[yellow]Invalid action or no more pages. Press q to quit.[/yellow]")
    
    def print_json(self, data: Union[Dict, List], title: str = None):
        """Print JSON data nicely formatted."""
        import json
        
        if self.console and RICH_AVAILABLE:
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.console.print(Syntax(formatted, "json", theme="monokai", line_numbers=True))
        else:
            if title:
                print(f"{self.colors.BOLD}{self.colors.CYAN}=== {title} ==={self.colors.ENDC}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def print_markdown(self, text: str):
        """Print markdown text."""
        if self.console and RICH_AVAILABLE:
            self.console.print(Markdown(text))
        else:
            print(text)
    
    def print_tree(self, tree_data: Dict[str, Any], title: str = None):
        """Print data as a tree."""
        if self.console and RICH_AVAILABLE:
            if title:
                self.console.print(f"[bold cyan]{title}[/bold cyan]")
            
            def add_nodes(node, tree_node):
                if isinstance(node, dict):
                    for key, value in node.items():
                        if isinstance(value, (dict, list)):
                            child = tree_node.add(f"[bold]{key}[/bold]")
                            add_nodes(value, child)
                        else:
                            tree_node.add(f"{key}: [dim]{value}[/dim]")
                elif isinstance(node, list):
                    for i, item in enumerate(node):
                        if isinstance(item, (dict, list)):
                            child = tree_node.add(f"[#{i}]")
                            add_nodes(item, child)
                        else:
                            tree_node.add(f"[dim]{item}[/dim]")
                else:
                    tree_node.add(f"[dim]{node}[/dim]")
            
            root = Tree("[bold]Root[/bold]")
            add_nodes(tree_data, root)
            self.console.print(root)
        else:
            # Basic tree fallback
            def print_node(node, indent=0):
                if isinstance(node, dict):
                    for key, value in node.items():
                        print("  " * indent + f"{key}:")
                        print_node(value, indent + 1)
                elif isinstance(node, list):
                    for i, item in enumerate(node):
                        print("  " * indent + f"[{i}]:")
                        print_node(item, indent + 1)
                else:
                    print("  " * indent + str(node))
            
            if title:
                print(f"{self.colors.BOLD}{self.colors.CYAN}=== {title} ==={self.colors.ENDC}")
            print_node(tree_data)
    
    # ==========================================================================
    # Interactive Components
    # ==========================================================================
    
    def show_progress(self, description: str = "Processing..."):
        """Show a progress indicator."""
        if self.console and RICH_AVAILABLE:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True
            )
            task_id = progress.add_task(description, total=None)
            progress.start()
            return progress
        else:
            print(f"{self.colors.CYAN}{description}{self.colors.ENDC}")
            return None
    
    def stop_progress(self, progress):
        """Stop a progress indicator."""
        if progress and RICH_AVAILABLE:
            progress.stop()
    
    def prompt_confirm(self, question: str, default: bool = True) -> bool:
        """Prompt for confirmation."""
        if self.console and RICH_AVAILABLE:
            return Confirm.ask(f"[cyan]{question}[/cyan]", default=default)
        else:
            suffix = " [Y/n]" if default else " [y/N]"
            response = input(f"{self.colors.CYAN}{question}{suffix}{self.colors.ENDC} ").strip().lower()
            if response == "":
                return default
            return response in ['y', 'yes']
    
    # ==========================================================================
    # Layout Components
    # ==========================================================================
    
    def show_dashboard(self, stats: Dict[str, Any]):
        """Show a dashboard with system statistics."""
        if self.console and RICH_AVAILABLE:
            # Create header panel
            header_content = Text()
            header_content.append("AITools CLI", style="bold cyan reverse")
            header_content.append(" | ", style="dim")
            header_content.append("Modular AI Tools Framework", style="bold")
            
            self.print(Panel(header_content, border_style="cyan", padding=(0, 1)))
            
            # Create stats panel content
            stats_content = Text()
            stats_content.append("📊 System Statistics\n\n", style="bold")
            
            # Display stats in a grid-like format
            items = []
            for key, value in stats.items():
                if key == "modules":
                    items.append(f"[bold]📦 Modules:[/bold] [cyan]{value}[/cyan]")
                elif key == "tools":
                    items.append(f"[bold]🔧 Tools:[/bold] [yellow]{value}[/yellow]")
                elif key == "status":
                    items.append(f"[bold]🚀 Status:[/bold] [green]{value}[/green]")
                elif key == "memory":
                    items.append(f"[bold]💾 Memory:[/bold] [magenta]{value}[/magenta]")
                else:
                    items.append(f"[bold]{key}:[/bold] {value}")
            
            # Display in columns
            columns = Columns(items, equal=False, expand=True)
            self.print(Panel(columns, border_style="blue", title="Statistics"))
        else:
            print(f"{self.colors.BOLD}{self.colors.CYAN}=== AITools Dashboard ==={self.colors.ENDC}")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    
    def clear_screen(self):
        """Clear the screen."""
        if self.console and RICH_AVAILABLE:
            self.console.clear()
        else:
            # Simple clear for basic terminal
            print("\033[2J\033[H")
    
    # ==========================================================================
    # Tool Display Methods
    # ==========================================================================
    
    def show_tools_list(self, tools: List[Dict[str, Any]], module_name: str = None):
        """Show list of tools in a formatted way."""
        if not tools:
            self.print_info("No tools available")
            return
        
        if self.console and RICH_AVAILABLE:
            table = Table(
                title=f"Tools in {module_name}" if module_name else "Available Tools",
                box=AIToolsTheme.TABLE_STYLES["rounded"]
            )
            
            table.add_column("Tool", style="bold cyan")
            table.add_column("Description", style="green")
            table.add_column("Module", style="yellow")
            table.add_column("Parameters", style="dim")
            
            for tool in tools:
                name = tool.get('name', 'Unknown')
                desc = tool.get('description', 'No description')
                module = tool.get('module_name', 'Unknown')
                params = tool.get('parameters', {})
                
                param_count = len(params)
                param_text = f"{param_count} param(s)" if param_count > 0 else "No params"
                
                table.add_row(name, desc[:80] + "..." if len(desc) > 80 else desc, module, param_text)
            
            self.console.print(table)
        else:
            title = f"Tools in {module_name}" if module_name else "Available Tools"
            print(f"{self.colors.BOLD}{self.colors.CYAN}=== {title} ==={self.colors.ENDC}")
            for tool in tools:
                name = tool.get('name', 'Unknown')
                desc = tool.get('description', 'No description')
                module = tool.get('module_name', 'Unknown')
                print(f"  {self.colors.GREEN}{name}{self.colors.ENDC} ({module})")
                print(f"    {desc[:100]}...")
    
    def show_tool_details(self, tool_info: Dict[str, Any]):
        """Show detailed information about a tool."""
        if self.console and RICH_AVAILABLE:
            # Create a panel with tool info
            content = Text()
            
            content.append(f"Tool: ", style="bold")
            content.append(f"{tool_info.get('name', 'Unknown')}\n", style="bold cyan")
            
            content.append("Description: ", style="bold")
            content.append(f"{tool_info.get('description', 'No description')}\n\n", style="green")
            
            content.append("Module: ", style="bold")
            content.append(f"{tool_info.get('module_name', 'Unknown')}\n", style="yellow")
            
            # Show parameters
            params = tool_info.get('parameters', {})
            if params:
                content.append("Parameters:\n", style="bold")
                for param_name, param_info in params.items():
                    param_type = param_info.get('type', 'Any')
                    param_desc = param_info.get('description', 'No description')
                    required = param_info.get('required', False)
                    
                    content.append(f"  {param_name}: ", style="cyan")
                    content.append(f"{param_type}", style="magenta")
                    if required:
                        content.append(" (required)", style="red")
                    else:
                        content.append(" (optional)", style="dim")
                    content.append(f" - {param_desc}\n")
            else:
                content.append("Parameters: None\n", style="dim")
            
            # Show return type
            return_type = tool_info.get('return_type')
            if return_type:
                content.append("Returns: ", style="bold")
                content.append(f"{return_type}\n", style="green")
            
            self.console.print(Panel(content, border_style="cyan", title="Tool Details"))
        else:
            print(f"{self.colors.BOLD}{self.colors.CYAN}=== Tool Details ==={self.colors.ENDC}")
            print(f"Tool: {self.colors.GREEN}{tool_info.get('name', 'Unknown')}{self.colors.ENDC}")
            print(f"Description: {tool_info.get('description', 'No description')}")
            print(f"Module: {tool_info.get('module_name', 'Unknown')}")
            
            params = tool_info.get('parameters', {})
            if params:
                print("Parameters:")
                for param_name, param_info in params.items():
                    param_type = param_info.get('type', 'Any')
                    required = param_info.get('required', False)
                    req_text = "required" if required else "optional"
                    print(f"  {param_name}: {param_type} ({req_text})")
    
    # ==========================================================================
    # Fixed Height Display
    # ==========================================================================
    
    def display_with_fixed_height(self, content: str, title: str = None, max_lines: int = None):
        """
        Display content with fixed height, showing only the last max_lines.
        
        Args:
            content: Text content to display
            title: Optional title for the display
            max_lines: Maximum number of lines to show (default: terminal height - 5)
        """
        if not content:
            self.print_info("No content to display")
            return
        
        # Split content into lines
        lines = content.split('\n')
        total_lines = len(lines)
        
        # Determine max lines to show
        if max_lines is None:
            try:
                # Get terminal height, default to 24 if unavailable
                terminal_height = os.get_terminal_size().lines
                max_lines = max(10, terminal_height - 5)  # Leave room for header/footer
            except (OSError, AttributeError):
                max_lines = 20  # Default fallback
        
        # Show appropriate content
        if total_lines <= max_lines:
            # All content fits
            if title:
                self.print_header(title)
            for line in lines:
                self.print(line)
        else:
            # Show only last max_lines with indicator
            if title:
                self.print_header(f"{title} (showing last {max_lines} of {total_lines} lines)")
            else:
                self.print_header(f"Showing last {max_lines} of {total_lines} lines")
            
            # Print indicator for truncated content
            truncated = total_lines - max_lines
            self.print(f"[dim]{truncated} lines truncated above...[/dim]" if RICH_AVAILABLE else f"{truncated} lines truncated above...")
            
            # Show last max_lines
            for line in lines[-max_lines:]:
                self.print(line)
    
    def display_with_scrolling(self, content: str, title: str = None, 
                               fixed_lines: int = 3, max_scroll_lines: int = None,
                               scroll_mode: str = "fixed_top"):
        """
        Display content with true terminal scrolling (fixed top + scrolling bottom).
        
        Implements the functionality from tests/tmp/test_terminal_scroll.py.
        
        Args:
            content: Text content to display
            title: Optional title for the display
            fixed_lines: Number of lines in fixed top area
            max_scroll_lines: Maximum lines in scroll area (auto-calculated if None)
            scroll_mode: "fixed_top" or "circular"
        """
        if not SCROLL_DISPLAY_AVAILABLE:
            # Fallback to fixed height display
            self.display_with_fixed_height(content, title, max_scroll_lines)
            return
        
        try:
            from cli.scroll_display import fixed_area_scroll_display, circular_scroll_display
            
            if scroll_mode == "circular":
                display = circular_scroll_display(
                    content=content,
                    title=title,
                    fixed_lines=fixed_lines,
                    max_scroll_lines=max_scroll_lines
                )
            else:  # fixed_top
                display = fixed_area_scroll_display(
                    content=content,
                    title=title,
                    fixed_lines=fixed_lines,
                    max_scroll_lines=max_scroll_lines
                )
            
            display.show()
            # Note: Display will stay active until stop() is called
            # For now, we just show and return
            display.stop()
            
        except Exception as e:
            self.print_error(f"Scroll display error: {e}")
            # Fallback to fixed height
            self.display_with_fixed_height(content, title, max_scroll_lines)
    
    
    
    def get_prompt(self, prompt_text: str = "aitools> ") -> str:
        """Get user input with a prompt."""
        if self.console and RICH_AVAILABLE:
            return Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]")
        else:
            return input(f"{self.colors.BOLD}{self.colors.CYAN}{prompt_text}{self.colors.ENDC} ")


# Global UI instance
_global_ui: Optional[AIToolsUI] = None


def get_ui(verbose: bool = False) -> AIToolsUI:
    """Get the global UI instance."""
    global _global_ui
    if _global_ui is None:
        _global_ui = AIToolsUI(verbose=verbose)
    
    return _global_ui


# Compatibility functions for existing code
def scrollable_display(content: str, title: str = None, page_size: int = 20):
    """Display content with true terminal scrolling (fixed top + scrolling bottom)."""
    ui = get_ui()
    ui.display_with_scrolling(content, title, max_scroll_lines=page_size)

def scrollable_display_enhanced(content: str, title: str = None, page_size: int = 20,
                                show_line_numbers: bool = True, use_rich: bool = True):
    """Display content with enhanced scrolling display."""
    ui = get_ui()
    # Note: show_line_numbers and use_rich parameters are ignored
    ui.display_with_scrolling(content, title, max_scroll_lines=page_size)

def test_ui():
    """Test UI components."""
    ui = get_ui(verbose=True)
    
    # Test basic messages
    #ui.print_header("AITools UI Test")
    #ui.print_success("This is a success message")
    #ui.print_error("This is an error message")
    #ui.print_warning("This is a warning message")
    #ui.print_info("This is an info message")
    #
    ## Test table
    #test_data = [
    #    {"id": 1, "name": "Alice", "role": "Admin"},
    #    {"id": 2, "name": "Bob", "role": "User"},
    #    {"id": 3, "name": "Charlie", "role": "Moderator"}
    #]
    #ui.print_table(test_data, "Test Table")
    
    # Test paginated table (non-interactive)
    paginated_data = []
    for i in range(1, 15):
        paginated_data.append({
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "status": "Active" if i % 2 == 0 else "Inactive"
        })
    # Test scrolling display
    long_text = "\n".join(f"Line {i}: This is a test line for scrolling display." for i in range(50))
    ui.display_with_scrolling(long_text, "Scrolling Display Test", max_scroll_lines=15)
    
    # Test fixed height display (for backward compatibility)
    #ui.display_with_fixed_height(long_text, "Fixed Height Test", max_lines=15)
    test_json = {
        "name": "Test",
        "value": 123,
        "nested": {"item1": "value1", "item2": "value2"}
    }
    #ui.print_json(test_json, "Test JSON")
    
    ## Test fixed height display
    #long_text = "\n".join(f"Line {i}: This is a test line for scrolling display." for i in range(50))
    #ui.display_with_fixed_height(long_text, "Long Text Test", max_lines=15)

if __name__ == "__main__":
    test_ui()
