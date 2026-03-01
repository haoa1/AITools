from base import function_ai, parameters_func, property_param
import os
import glob as glob_module

__PATH_PROPERTY__ = property_param(
    name="path",
    description="The directory path to search in.",
    t="string",
    required=True,
)

__PATTERN_PROPERTY__ = property_param(
    name="pattern",
    description="The glob pattern to match files (e.g., '*.py', '**/*.js').",
    t="string",
    required=True,
)

__RECURSIVE_PROPERTY__ = property_param(
    name="recursive",
    description="Whether to search recursively. Use '**' in pattern for recursive search.",
    t="boolean",
)

__SEARCH_FUNCTION__ = function_ai(
    name="glob",
    description="This function searches for files matching a glob pattern.",
    parameters=parameters_func(
        [__PATH_PROPERTY__, __PATTERN_PROPERTY__, __RECURSIVE_PROPERTY__]
    ),
)

tools = [__SEARCH_FUNCTION__]


def _validate_path(path: str) -> str | None:
    path = os.path.normpath(path)
    if not os.path.exists(path):
        return f"Error: Directory does not exist: {path}"
    if not os.path.isdir(path):
        return f"Error: Path is not a directory: {path}"
    if not os.access(path, os.R_OK):
        return f"Error: No read permission for directory: {path}"
    return None


def glob(path: str, pattern: str = "*", recursive: bool = False) -> str:
    if error := _validate_path(path):
        return error

    try:
        search_pattern = os.path.join(path, pattern)

        if "**" in pattern:
            matches = glob_module.glob(search_pattern, recursive=True)
        elif recursive:
            matches = glob_module.glob(search_pattern, recursive=True)
        else:
            matches = glob_module.glob(search_pattern)

        if not matches:
            return "[]"

        return str(matches)
    except Exception as e:
        return f"Error: Unexpected error when searching: {str(e)}"


TOOL_CALL_MAP = {
    "glob": glob,
}
