"""
Advanced Terminal Scrolling Display for AITools CLI.

This module provides fixed-area scrolling functionality with:
- Fixed header/top area (doesn't scroll)
- Dynamic scrolling content area
- Circular buffer scrolling (clears and reprints when full)
- Terminal height awareness
"""

import sys
import os
import time
import shutil
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

# Try to import rich for enhanced display
try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich import box
    from rich.style import Style
    
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ScrollMode(Enum):
    """Scroll display modes."""
    FIXED_TOP = "fixed_top"        # Fixed header, scrolling content
    CIRCULAR = "circular"          # Circular buffer, clears when full
    PAGINATED = "paginated"        # Paginated display with navigation


@dataclass
class ScrollConfig:
    """Configuration for scroll display."""
    fixed_lines: int = 3           # Lines in fixed top area
    max_scroll_lines: int = None   # Max lines in scroll area (auto-calc if None)
    scroll_mode: ScrollMode = ScrollMode.FIXED_TOP
    auto_refresh: bool = False     # Auto refresh display on content change
    show_line_numbers: bool = True
    title: Optional[str] = None
    separator: str = "-" * 50
    clear_on_full: bool = True     # Clear scroll area when full
    preserve_history: bool = True  # Keep history in fixed area


class TerminalScrollDisplay:
    """
    Advanced terminal scrolling display with fixed top area.
    
    Features:
    1. Fixed header/top area that doesn't scroll
    2. Scrolling content area with circular buffer
    3. Terminal height awareness
    4. Cross-platform compatibility
    5. Rich text support (if available)
    
    Usage:
            """
    
    def __init__(self, config: Optional[ScrollConfig] = None):
        """Initialize scroll display."""
        self.config = config or ScrollConfig()
        self.fixed_content: List[str] = []
        self.scroll_content: List[str] = []
        self.scroll_index = 0
        
        # Terminal info
        self._update_terminal_size()
        
        # Console for output
        self.console = Console() if RICH_AVAILABLE else None
        
        # Display state
        self.is_showing = False
        self.last_display_height = 0
        
    def _update_terminal_size(self):
        """Update terminal dimensions."""
        try:
            self.terminal_size = shutil.get_terminal_size()
            self.terminal_height = self.terminal_size.lines
            self.terminal_width = self.terminal_size.columns
            
            # Calculate max scroll lines
            if self.config.max_scroll_lines is None:
                # Reserve space for fixed area, separator, and bottom margin
                reserved = self.config.fixed_lines + 3  # +1 separator, +2 margin
                self.config.max_scroll_lines = max(5, self.terminal_height - reserved)
        except (OSError, AttributeError):
            # Fallback values
            self.terminal_height = 24
            self.terminal_width = 80
            self.config.max_scroll_lines = 15
    
    def clear(self):
        """Clear the display (platform-specific)."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def add_fixed_line(self, line: str, index: Optional[int] = None):
        """
        Add a line to the fixed (non-scrolling) area.
        
        Args:
            line: Text to add
            index: Position to insert (append if None)
        """
        if index is None:
            self.fixed_content.append(line)
        else:
            self.fixed_content.insert(index, line)
        
        # Trim if exceeds fixed lines
        if len(self.fixed_content) > self.config.fixed_lines:
            self.fixed_content = self.fixed_content[-self.config.fixed_lines:]
        
        if self.config.auto_refresh and self.is_showing:
            self.refresh()
    
    def add_scroll_line(self, line: str):
        """
        Add a line to the scrolling area.
        
        Args:
            line: Text to add (will be truncated to terminal width)
        """
        # Truncate line to terminal width
        if len(line) > self.terminal_width - 10:  # Allow for line numbers
            line = line[:self.terminal_width - 13] + "..."
        
        self.scroll_content.append(line)
        
        # Manage scroll buffer based on mode
        if self.config.scroll_mode == ScrollMode.CIRCULAR:
            # Keep only last N lines
            if len(self.scroll_content) > self.config.max_scroll_lines:
                self.scroll_content = self.scroll_content[-self.config.max_scroll_lines:]
                self.scroll_index = 0  # Reset index
        elif self.config.scroll_mode == ScrollMode.FIXED_TOP:
            # Fixed top mode - just trim if too many
            if len(self.scroll_content) >= self.config.max_scroll_lines:
                self.scroll_content = self.scroll_content[-self.config.max_scroll_lines:]
        
        if self.config.auto_refresh and self.is_showing:
            self.refresh()
    def add_scroll_content(self, content: str):
        lines = content.split("\n")
        self.scroll_content.extend(lines)
        
    def add_scroll_lines(self, lines: List[str]):
        """Add multiple lines to scrolling area."""
        self.scroll_content.extend(lines)

    def _print_fixed_area(self):
        """Print the fixed (non-scrolling) area."""
        if self.config.title:
            if RICH_AVAILABLE and self.console:
                title_text = Text(self.config.title, style="bold cyan")
                self.console.print(title_text)
            else:
                print(f"\033[1;36m{self.config.title}\033[0m")  # Cyan bold
        
        # Print separator
        print(self.config.separator)
        
        # Print fixed content
        for i, line in enumerate(self.fixed_content):
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[dim]{line}[/dim]")
            else:
                print(f"\033[2m{line}\033[0m")  # Dim text
        
        # Print separator between fixed and scroll areas
        print(self.config.separator)
    
    def _print_scroll_area(self, clear_first: bool = False):
        """Print the scrolling area."""
        if clear_first and self.config.clear_on_full:
            # Clear only the scroll area (move cursor up)
            if self.last_display_height > 0:
                # Move cursor up by last display height
                sys.stdout.write(f"\033[{self.last_display_height}A")
                # Clear lines
                for _ in range(self.last_display_height):
                    sys.stdout.write("\033[2K\033[1B")
                sys.stdout.write(f"\033[{self.last_display_height}A")
                sys.stdout.flush()
        
        # Print scroll content
        start_idx = max(0, len(self.scroll_content) - self.config.max_scroll_lines - 1)
        scroll_lines = self.scroll_content[start_idx:]
        
        for i, line in enumerate(scroll_lines):
            if line is None or line == "":
                continue
            line_num = start_idx + i + 1
            if self.config.show_line_numbers:
                line_prefix = f"{line_num:3d} │ "
            else:
                line_prefix = ""
            
            if RICH_AVAILABLE and self.console:
                self.console.print(f"[white]{line_prefix}{line}[/white]")
            else:
                print(f"{line_prefix}{line}")
        
        # Update last display height
        self.last_display_height = len(scroll_lines)
    
    def show(self, clear_screen: bool = True):
        """
        Show the display with fixed top and scrolling bottom.
        
        Args:
            clear_screen: Whether to clear screen before showing
        """
        self._update_terminal_size()
        
        if clear_screen:
            self.clear()
        
        self.is_showing = True
        
        # Print fixed area
        self._print_fixed_area()
        
        # Print scroll area
        self._print_scroll_area()
        
        sys.stdout.flush()
    
    def refresh(self, preserve_position: bool = True):
        """
        Refresh the display.
        
        Args:
            preserve_position: If True, try to preserve scroll position
        """
        if not self.is_showing:
            return
        
        # For now, just re-show
        self.show(clear_screen=False)
    
    def update_fixed_line(self, index: int, line: str):
        """
        Update a specific line in the fixed area.
        
        Args:
            index: Line index (0-based)
            line: New line content
        """
        if 0 <= index < len(self.fixed_content):
            self.fixed_content[index] = line
            if self.config.auto_refresh and self.is_showing:
                self.refresh()
    
    def clear_scroll_area(self):
        """Clear the scrolling area."""
        self.scroll_content.clear()
        self.scroll_index = 0
        if self.config.auto_refresh and self.is_showing:
            self.refresh()
    
    def stop(self):
        """Stop displaying."""
        self.is_showing = False


# ============================================================================
# Convenience functions
# ============================================================================

def fixed_area_scroll_display(
    content: str,
    title: Optional[str] = None,
    fixed_lines: int = 3,
    max_scroll_lines: Optional[int] = None,
    show_line_numbers: bool = True
) -> TerminalScrollDisplay:
    """
    Create and show a fixed area scroll display.
    
    Args:
        content: Text content (will be split into lines)
        title: Display title
        fixed_lines: Lines in fixed area
        max_scroll_lines: Max lines in scroll area (auto if None)
        show_line_numbers: Show line numbers in scroll area
    
    Returns:
        TerminalScrollDisplay instance
    """
    config = ScrollConfig(
        fixed_lines=fixed_lines,
        max_scroll_lines=max_scroll_lines,
        scroll_mode=ScrollMode.FIXED_TOP,
        title=title,
        show_line_numbers=show_line_numbers
    )
    
    display = TerminalScrollDisplay(config)
    
    # Add some default fixed content
    display.add_fixed_line(f"Lines: {len(content.splitlines())}")
    display.add_fixed_line(f"Mode: Fixed area scrolling")
    display.add_fixed_line(f"Terminal: {display.terminal_height} lines")
    
    # Add content to scroll area
    lines = content.split('\n')
    display.add_scroll_lines(lines)
    
    return display


def circular_scroll_display(
    content: str,
    title: Optional[str] = None,
    fixed_lines: int = 3,
    max_scroll_lines: Optional[int] = None
) -> TerminalScrollDisplay:
    """
    Create and show a circular buffer scroll display.
    
    Args:
        content: Text content
        title: Display title
        fixed_lines: Lines in fixed area
        max_scroll_lines: Max lines in scroll area
    
    Returns:
        TerminalScrollDisplay instance
    """
    config = ScrollConfig(
        fixed_lines=fixed_lines,
        max_scroll_lines=max_scroll_lines,
        scroll_mode=ScrollMode.CIRCULAR,
        title=title,
        clear_on_full=True
    )
    
    display = TerminalScrollDisplay(config)
    
    # Add some default fixed content
    display.add_fixed_line(f"Mode: Circular buffer")
    display.add_fixed_line(f"Buffer size: {max_scroll_lines or 'auto'}")
    
    # Add content to scroll area
    lines = content.split('\n')
    display.add_scroll_lines(lines)
    
    return display


# ============================================================================
# Integration with existing UI system
# ============================================================================

def create_scroll_display_from_ui(ui_instance, content: str, title: str = None, **kwargs):
    """
    Create a scroll display compatible with existing UI system.
    
    This is a bridge function to integrate with AIToolsUI.
    """
    from cli.ui_helper import get_ui
    
    ui = ui_instance or get_ui()
    
    # Use UI's verbose setting
    config = ScrollConfig(
        title=title or "AITools Display",
        fixed_lines=kwargs.get('fixed_lines', 3),
        show_line_numbers=kwargs.get('show_line_numbers', True)
    )
    
    display = TerminalScrollDisplay(config)
    
    # Add UI context to fixed area
    display.add_fixed_line(f"Context: {ui.current_context}")
    display.add_fixed_line(f"Mode: {'verbose' if ui.verbose else 'normal'}")
    
    # Add content
    lines = content.split('\n')
    display.add_scroll_lines(lines)
    
    return display


# ============================================================================
# Test function
# ============================================================================

def test_scroll_display():
    """Test the scroll display functionality."""
    print("Testing TerminalScrollDisplay...")
    
    # Test 1: Fixed area scrolling
    print("\n1. Testing fixed area scrolling...")
    test_content = "\n".join(f"Test line {i}: This is a test for scrolling display." 
                           for i in range(1, 31))
    
    display = fixed_area_scroll_display(
        content=test_content,
        title="Fixed Area Scroll Test",
        fixed_lines=4,
        max_scroll_lines=10
    )
    
    display.show()
    time.sleep(2)
    
    # Add more lines dynamically
    print("\nAdding more lines...")
    for i in range(31, 36):
        display.add_scroll_line(f"Added line {i}: Dynamic update test.")
        time.sleep(0.3)
    
    time.sleep(1)
    display.stop()
    
    # Test 2: Circular buffer
    print("\n2. Testing circular buffer...")
    display2 = circular_scroll_display(
        content="\n".join(f"Circular line {i}" for i in range(1, 20)),
        title="Circular Buffer Test",
        max_scroll_lines=8
    )
    
    display2.show()
    time.sleep(1)
    
    # Keep adding lines to see circular behavior
    for i in range(20, 30):
        display2.add_scroll_line(f"New circular line {i}")
        time.sleep(0.2)
    
    time.sleep(1)
    display2.stop()
    
    print("\n✅ Scroll display tests completed.")


if __name__ == "__main__":
    #test_scroll_display()

    config = ScrollConfig(
        max_scroll_lines=20,
        scroll_mode=ScrollMode.FIXED_TOP,
        title="System Monitor",
    )
    

    display = TerminalScrollDisplay(config)
    display.add_fixed_line("Status: Running")
    display.add_fixed_line("Status: Running")
    display.add_fixed_line("Status: Running")

    content = ""
    for i in range(0, 30):
        content = content + f"Task {i} completed" + "\n"
    display.add_scroll_content(content)
    display.show()
    #display.stop()
