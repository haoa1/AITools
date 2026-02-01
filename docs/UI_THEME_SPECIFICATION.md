# AITools CLI UI Theme and Layout Specification

## Overview

Inspired by elegant terminal interface design, this specification defines the complete UI design system for AITools CLI. The design focuses on usability, aesthetics, and developer experience.

## Design Principles

1. **Clarity Over Cleverness** - Interface should be immediately understandable
2. **Progressive Disclosure** - Show simple information first, details on demand  
3. **Consistency** - Maintain consistent patterns across all UI components
4. **Responsive Design** - Adapt to terminal size and capabilities
5. **Accessibility** - Ensure good contrast and readability

## Color Palette

### Primary Colors
- **Primary Blue**: `#3498db` - Main actions, headers, highlights
- **Success Green**: `#2ecc71` - Success states, positive actions
- **Warning Orange**: `#f39c12` - Warnings, cautions
- **Danger Red**: `#e74c3c` - Errors, destructive actions
- **Accent Purple**: `#9b59b6` - Highlights, secondary actions

### Neutral Colors
- **Dark Blue**: `#2c3e50` - Headers, important text
- **Medium Gray**: `#95a5a6` - Secondary text, disabled states
- **Light Gray**: `#ecf0f1` - Backgrounds, panels
- **Code Green**: `#27ae60` - Code, technical content

### Semantic Colors
- **Information**: Cyan variants
- **Success**: Green variants  
- **Warning**: Yellow/Orange variants
- **Error**: Red variants
- **Highlight**: Blue on light background

## Typography

### Font Weights
- **Normal**: Standard weight for body text
- **Bold**: For emphasis and headers
- **Dim**: For secondary information

### Text Styles
- **Headers**: Bold + Primary color + Optional emoji
- **Body**: Normal weight, high contrast
- **Code**: Monospace, code green
- **Links**: Underlined + primary color
- **Disabled**: Dim + medium gray

## Component Specifications

### 1. Tables
- **Border Style**: Rounded (`box.ROUNDED`) for modern look
- **Header**: Bold cyan, centered
- **Rows**: Alternating subtle background for readability
- **Alignment**: Left-aligned text, right-aligned numbers
- **Padding**: (0, 1) for compact but readable layout

### 2. Panels
- **Border**: Thin border with primary color
- **Padding**: (1, 2) for comfortable content spacing
- **Title**: Centered, bold, with emoji if appropriate
- **Content**: Clean alignment, proper line spacing

### 3. Lists
- **Bulleted Lists**: Cyan bullet points, proper indentation
- **Numbered Lists**: Sequential numbers with right alignment
- **Tree Views**: Hierarchical with connecting lines

### 4. Progress Indicators
- **Spinner**: Animated for short operations
- **Progress Bar**: For long-running operations with percentage
- **Status**: Clear text description of current operation

### 5. Interactive Elements
- **Prompts**: Clear question formatting with input area
- **Confirmations**: Yes/No with default highlighted
- **Selection**: Numbered options with keyboard navigation
- **Multi-select**: Checkbox-style selection

## Layout System

### Screen Regions
1. **Header Area**: Application title and status
2. **Content Area**: Main content display
3. **Sidebar**: Optional for help or context (if terminal width > 120 cols)
4. **Footer**: Status bar or command hints

### Responsive Breakpoints
- **Small (< 80 cols)**: Single column, simplified tables
- **Medium (80-120 cols)**: Standard layout, compact tables
- **Large (> 120 cols)**: Multi-column, detailed views

### Spacing System
- **Unit**: 1 space character = basic unit
- **Small**: 1 unit (between closely related items)
- **Medium**: 2 units (between sections)
- **Large**: 4 units (between major groups)

## Interaction Patterns

### 1. Command Execution Flow
```
[User types command] → [Validation] → [Execution] → [Result display] → [Status feedback]
```

### 2. Error Handling
- Clear error message with context
- Suggestion for resolution
- Option to see detailed error (verbose mode)

### 3. Help System
- Context-sensitive help
- Command examples
- Parameter descriptions

### 4. Progressive Enhancement
- Basic ANSI colors fallback when Rich not available
- Graceful degradation for limited terminals
- Feature detection for advanced UI components

## Component Library

### Basic Components
- `HeaderPanel`: Application header with title and version
- `InfoPanel`: Information display with formatted content
- `CommandPanel`: Command help and examples
- `ResultPanel`: Tool execution results

### Data Display Components  
- `DataTable`: Formatted data tables
- `TreeView`: Hierarchical data display
- `JSONView`: Syntax-highlighted JSON display
- `MarkdownView`: Formatted markdown content

### Interactive Components
- `InteractiveShell`: REPL-style command interface
- `Wizard`: Step-by-step guided interface
- `Form`: Data entry with validation
- `SelectionMenu`: Interactive menu system

## Theme Variations

### 1. Light Theme (Default)
- High contrast, suitable for most terminals
- Blue-based color scheme

### 2. Dark Theme
- Inverted colors for dark terminal backgrounds
- Reduced brightness for eye comfort

### 3. High Contrast Theme
- Maximum contrast for accessibility
- Simplified color palette

## Implementation Guidelines

### 1. Rich Library Usage
- Use theme system for consistent styling
- Leverage layout system for responsive design
- Implement proper error handling for missing features

### 2. Fallback Strategy
1. Try Rich with full features
2. Fallback to basic Rich without advanced components
3. Fallback to ANSI color codes
4. Final fallback to plain text

### 3. Performance Considerations
- Lazy loading of UI components
- Caching of rendered elements
- Efficient screen updates

### 4. Testing Strategy
- Test with different terminal sizes
- Test color support levels
- Test interactive components
- Verify accessibility compliance

## Example Interfaces

### Dashboard View
```
┌─────────────────────────────────────────────────────┐
│                🚀 AITools Dashboard                  │
├─────────────────────────────────────────────────────┤
│ 📦 Modules: 24    🔧 Tools: 345    🚀 Status: Ready  │
│ Memory: 128MB     Uptime: 2h 15m                    │
└─────────────────────────────────────────────────────┘
```

### Module Listing
```
                        Available Modules                         
╭────────┬──────────┬────────┬───────────────────────────────────╮
│ Module │ Version  │  Tools │ Description                       │
├────────┼──────────┼────────┼───────────────────────────────────┤
│ pdf    │  1.0.0   │     24 │ PDF processing and manipulation   │
│ file   │  1.0.0   │     33 │ File system operations            │
│ git    │  1.0.0   │     23 │ Git version control operations    │
╰────────┴──────────┴────────┴───────────────────────────────────╯
```

### Interactive Shell
```
aitools> list-tools --module pdf
📦 PDF Module Tools (24 total)

1. extract_text_from_pdf
   Extract text content from PDF files
   
2. merge_pdfs  
   Merge multiple PDF files into one
   
3. split_pdf
   Split PDF by page range

Select tool number (or 'q' to quit): 
```

## Roadmap

### Phase 1: Core UI (Current)
- Basic color scheme and components
- Table and panel layouts
- Basic interactive elements

### Phase 2: Advanced Features
- Interactive shell with command history
- Context-aware help system
- Custom theme support

### Phase 3: Enterprise Features
- Multi-window support
- Plugin system for UI components
- Advanced visualization components

## Accessibility Requirements

### Color Contrast
- Minimum 4.5:1 contrast ratio for normal text
- Minimum 3:1 contrast ratio for large text
- Color not used as sole means of conveying information

### Keyboard Navigation
- Tab navigation for all interactive elements
- Arrow key support for menus and lists
- Escape key to cancel operations

### Screen Reader Support
- Semantic markup where possible
- ARIA labels for complex components
- Text alternatives for visual elements