# Contributing to AITools

Thank you for your interest in contributing to AITools! This document provides guidelines and instructions for contributing to the project. We welcome contributions of all types: bug reports, feature requests, documentation improvements, and code contributions.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment Setup](#development-environment-setup)
4. [Coding Standards](#coding-standards)
5. [Commit Message Guidelines](#commit-message-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation Standards](#documentation-standards)
9. [Reporting Bugs](#reporting-bugs)
10. [Requesting Features](#requesting-features)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to foster a welcoming, inclusive, and respectful environment.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package installer)

### Fork and Clone the Repository

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/AITools.git
   cd AITools
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/haoa1/AITools.git
   ```

## Development Environment Setup

### 1. Create a Virtual Environment

We recommend using a virtual environment to isolate dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

Install the project in development mode with all optional dependencies:

```bash
pip install -e ".[all,dev]"
```

This installs:
- Core dependencies
- All optional feature dependencies
- Development tools (black, isort, flake8, pytest, etc.)

### 3. Install Pre-commit Hooks

We use pre-commit to ensure code quality. Install it with:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run linters and formatters before each commit.

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some project-specific conventions:

- **Maximum line length**: 88 characters (Black-compatible)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for docstrings, single quotes for strings (or follow existing file style)
- **Imports**: Grouped and sorted with isort

### Code Formatting

We use [Black](https://github.com/psf/black) for automatic code formatting:

```bash
black aitools/ tests/
```

### Import Sorting

We use [isort](https://pycqa.github.io/isort/) to organize imports:

```bash
isort aitools/ tests/
```

### Linting

We use [flake8](https://flake8.pycqa.org/) for linting:

```bash
flake8 aitools/ tests/
```

### Type Hints

We encourage using type hints for all function signatures and important variables:

```python
def read_file(file_path: str, mode: str = "r") -> str:
    """Read a file and return its contents."""
    # Implementation
```

### Docstrings

We follow the [Google docstring style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings):

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description with details about what the function does,
    any edge cases, and examples if helpful.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: If something goes wrong.
        FileNotFoundError: If file doesn't exist.
    """
    pass
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring (no functional changes)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates, etc.

### Examples

```
feat: Add PDF watermark functionality

Adds support for adding text watermarks to PDF files with configurable
opacity and rotation.

Closes #123
```

```
fix(file): Handle large file reading efficiently

Fix memory issue when reading very large files by implementing chunked
reading.

Fixes #456
```

## Pull Request Process

1. **Create a Branch**
   - Use descriptive branch names: `feature/short-description`, `fix/issue-description`
   - Keep branches focused on a single change

2. **Make Changes**
   - Follow coding standards
   - Write tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   - Run the full test suite: `pytest`
   - Ensure all tests pass: `pytest --cov=aitools`
   - Run linters: `black`, `isort`, `flake8`

4. **Update Documentation**
   - Update README.md if adding new features
   - Add docstrings for new functions/classes
   - Update any affected examples

5. **Submit Pull Request**
   - Fill out the PR template completely
   - Link related issues
   - Provide a clear description of changes

6. **Review Process**
   - Address reviewer feedback
   - Make requested changes
   - Keep PR updated with the main branch

### PR Requirements
- All tests must pass
- Code coverage should not decrease
- Code must follow style guidelines
- Documentation must be updated
- Changes must be focused and atomic

## Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_file.py

# Run with coverage
pytest --cov=aitools --cov-report=html

# Run tests with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow naming convention: `test_*.py` for test files, `test_*` for test functions
- Use descriptive test names that indicate what's being tested
- Use pytest fixtures for setup/teardown
- Mock external dependencies when appropriate

### Test Structure

```python
import pytest
from aitools import AITools

def test_read_file_success():
    """Test successful file reading."""
    # Setup
    tools = AITools()
    
    # Execute
    result = tools.file.read("/path/to/file.txt")
    
    # Assert
    assert result == "expected content"
    
def test_read_file_not_found():
    """Test file not found error."""
    tools = AITools()
    
    with pytest.raises(FileNotFoundError):
        tools.file.read("/nonexistent/path.txt")
```

## Documentation Standards

### Code Documentation
- All modules should have a docstring at the top
- All functions and classes should have complete docstrings
- Use type hints where possible
- Include examples for complex functions

### User Documentation
- Update README.md for user-facing changes
- Add usage examples for new features
- Document command-line options
- Keep the documentation up to date with code changes

### API Documentation
- Document all public APIs
- Include parameter descriptions and return types
- Document exceptions that can be raised

## Reporting Bugs

### Before Reporting
1. Check if the issue has already been reported
2. Ensure you're using the latest version
3. Try to reproduce the issue with a clean environment

### Bug Report Template
When creating a bug report, please include:

- **Description**: Clear and concise description of the bug
- **Steps to Reproduce**: Step-by-step instructions to reproduce
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, package versions
- **Logs**: Error messages, stack traces, console output
- **Screenshots**: If applicable

## Requesting Features

### Feature Request Template
When requesting a new feature, please include:

- **Problem Statement**: What problem are you trying to solve?
- **Proposed Solution**: How would you like to see it solved?
- **Alternatives Considered**: Other approaches you've considered
- **Use Cases**: Examples of how the feature would be used
- **Additional Context**: Any other relevant information

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check the [README.md](README.md) and inline documentation
- **Email**: For commercial licensing inquiries: hero@example.com

## Recognition

All contributors will be acknowledged in:
- The project's README.md
- Release notes
- GitHub contributors page

Thank you for contributing to AITools! 🚀