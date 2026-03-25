from base import function_ai, parameters_func, property_param
import os

__PATH_PROPERTY__ = property_param(
    name="file_path",
    description="The path of the file to be read.",
    t="string",
    required=True,
)

__OFFSET_PROPERTY__ = property_param(
    name="offset",
    description="The line number to start reading from (1-indexed). Use 1 for first line.",
    t="integer",
)

__LIMIT_PROPERTY__ = property_param(
    name="limit",
    description="The maximum number of lines to read. Omit or set to 0 to read to end of file.",
    t="integer",
)

__MODE_PROPERTY__ = property_param(
    name="mode",
    description="The mode in which to read the file - 'r' for text mode (default, required for line-based reading). Binary mode ('rb') not supported for line-based reading.",
    t="string",
)

__READ_FUNCTION__ = function_ai(
    name="read",
    description="This function reads lines from a file. Use offset (1-indexed line number) and limit (number of lines) for paginated reading.",
    parameters=parameters_func(
        [__PATH_PROPERTY__, __OFFSET_PROPERTY__, __LIMIT_PROPERTY__, __MODE_PROPERTY__]
    ),
)

tools = [__READ_FUNCTION__]


def _validate_file(file_path: str) -> str:
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        return f"Error: File does not exist: {file_path}"
    if not os.path.isfile(file_path):
        return f"Error: Path is not a file: {file_path}"
    if not os.access(file_path, os.R_OK):
        return f"Error: No read permission for file: {file_path}"
    return None


def read_file(file_path: str, offset: int = 1, limit: int = 0, mode: str = "r") -> str:
    if error := _validate_file(file_path):
        return error
    if mode not in ("r", "rb"):
        return f"Error: Invalid mode '{mode}'. Use 'r' or 'rb'."
    if offset < 1:
        return f"Error: Offset must be at least 1: {offset}"
    if limit < 0:
        return f"Error: Limit cannot be negative: {limit}"

    try:
        # Line-based reading only makes sense for text mode
        if mode == "rb":
            return "Error: Binary mode ('rb') not supported for line-based reading. Use text mode ('r')."
        
        # Convert 1-indexed offset to 0-indexed for internal processing
        offset_0 = offset - 1
        
        # Try UTF-8 encoding first, fallback to latin-1
        lines = []
        lines_collected = 0
        current_line = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if current_line >= offset_0:
                        if limit == 0 or lines_collected < limit:
                            lines.append(line)
                            lines_collected += 1
                        else:
                            break
                    current_line += 1
        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    if current_line >= offset_0:
                        if limit == 0 or lines_collected < limit:
                            lines.append(line)
                            lines_collected += 1
                        else:
                            break
                    current_line += 1
        
        # If offset is beyond total lines, return empty string
        if current_line <= offset_0 and lines_collected == 0:
            return ""
        
        return ''.join(lines)
        
    except Exception as e:
        return f"Error: Unexpected error when reading file: {str(e)}"


TOOL_CALL_MAP = {
    "read": read_file,
}
