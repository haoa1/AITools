# AITools Framework

A modular AI tools framework for command-line interfaces and tool integration. This framework provides a comprehensive collection of tools for file operations, Git, shell commands, workspace management, environment variables, network operations, PDF processing, diagram generation, stock data, and more.



## Features

- **File Operations**: Read, write, delete, replace, and compare files with various strategies
- **Git Integration**: Full Git operations including clone, commit, push, pull, branch management
- **Shell Commands**: Execute bash commands and scripts with proper output handling
- **Workspace Management**: Create, delete, and manage development workspaces
- **Environment Variables**: Get, set, list, and manage environment variables
- **Network Operations**: HTTP requests, web search, connectivity checks, DNS lookup
- **PDF Processing**: Extract text, merge, split, convert to images, fill forms
- **Diagram Generation**: Create architecture diagrams, flowcharts, sequence diagrams
- **Stock Data**: Real-time stock quotes, historical data, company information
- **Database Operations**: SQLite, MySQL, PostgreSQL database interactions
- **Web Search**: Google search, webpage extraction, content summarization
- **Interactive Tools**: User interaction wizards, feedback collection, validations

## Installation

### From GitHub via pip

You can install directly from the GitHub repository:

```bash
pip install git+ssh://git@github.com/haoa1/AITools.git
```

For development installation (editable mode):

```bash
pip install -e git+https://github.com/haoa1/AITools.git#egg=aitools-framework
```

suggestion docker
git@github.com:haoa1/docker_ai.git


### From Source

```bash
git clone https://github.com/haoa1/AITools.git
cd AITools
pip install -e .
```


### Optional Dependencies

Install additional features with extras:

```bash
# AI capabilities (OpenAI, tokenization)
pip install aitools-framework[ai]

# Web development tools
pip install aitools-framework[web]

# PDF processing (note: PDF dependencies are already included as required)
pip install aitools-framework[pdf]

# Data analysis
pip install aitools-framework[data]

# Database operations
pip install aitools-framework[database]

# Development tools
pip install aitools-framework[dev]

# All extras
pip install aitools-framework[all]
```

## Quick Start

### Command Line Interface

The framework provides multiple CLI entry points:

```bash
# Main interface with enhanced features
export DEEPSEEK_API_KEY="your deepseek api key" 
aitools




## Modules Overview

| Module | Description | Key Functions |
|--------|-------------|---------------|
| **file** | File system operations | `read_file`, `write_file`, `delete_file`, `replace_in_file` |
| **git** | Git version control | `git_clone`, `git_commit`, `git_push`, `git_status` |
| **shell** | Shell command execution | `execute_command`, `execute_multiple_commands` |
| **workspace** | Workspace management | `create_workspace`, `delete_workspace`, `list_workspaces` |
| **env** | Environment variables | `get_env`, `set_env`, `list_env`, `load_env_file` |
| **network** | Network operations | `http_get`, `http_post`, `download_file`, `ping_host` |
| **pdf** | PDF processing | `extract_text_from_pdf`, `merge_pdfs`, `split_pdf`, `create_pdf` |
| **diagram** | Diagram generation | `create_architecture_diagram`, `create_flowchart`, `create_sequence_diagram` |
| **stock** | Stock market data | `get_stock_quote`, `get_stock_history`, `search_stock` |
| **database** | Database operations | `connect_database`, `execute_query`, `create_table`, `drop_table` |
| **project** | Project context management | `detect_project`, `create_development_plan`, `get_project_summary` |
| **web_search** | Web search and content extraction | `fetch_webpage`, `search_webpage`, `google_search`, `web_search` |
| **interaction** | User interaction tools | `ask_user_with_options`, `get_user_feedback`, `blocking_confirmation` |
| **tmux** | Tmux session management | `create_tmux_session`, `list_tmux_sessions`, `send_keys_to_tmux` |
| **summary** | Conversation summarization | `enhance_summary`, `optimize_feature_context` |
| **main** | Main CLI interface | `main`, `run_aitools`, `run_ai_version` |
| **base** | Base classes and utilities | `BaseTool`, `BaseConfig`, `BaseHandler` |
| **cli** | CLI utilities | `ArgumentParser`, `CommandLineInterface`, `CLIFormatter` |
| **compress** | Data compression utilities | `compress_data`, `decompress_data`, `compress_file` |
| **docker** | Docker container management | `build_docker_image`, `run_docker_container`, `stop_docker_container` |
| **stock** | Stock data utilities | `StockDataFetcher`, `StockAnalyzer`, `PortfolioManager` |

## Development

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/haoa1/AITools.git
   cd AITools
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .[dev]
   ```

## License

MIT License - see LICENSE file for details.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## FAQ

### How can I get api key?
Please visit "https://platform.deepseek.com/usage"

### Can I use SSH to install from GitHub?
Yes, you can use SSH URLs:
```bash
pip install git+ssh://git@github.com/haoa1/AITools.git
```

### What if installation fails due to missing dependencies?
All required dependencies are specified in `pyproject.toml` and should be automatically installed. If you encounter issues:
1. Ensure you have the latest pip version: `pip install --upgrade pip`
2. Check your Python version (requires Python 3.8+)
3. Try installing with `--no-cache-dir` flag

### How do I verify the installation?
After installation, run:
```bash
aitools --help
```
You should see the help message for AITools.

## Troubleshooting

### Common Issues

1. **"ModuleNotFoundError" for PDF dependencies**:
   ```bash
   pip install pypdf>=3.0.0 reportlab>=4.0.0 pdf2image>=1.16.0
   ```

2. **"Command not found: aitools"**:
   Ensure the pip installation directory is in your PATH, or use:
   ```bash
   python -m aitools
   ```

3. **Permission errors**:
   Use virtual environments or install with `--user` flag:
   ```bash
   pip install --user git+https://github.com/haoa1/AITools.git
   ```

For more help, open an issue on GitHub.