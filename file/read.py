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
    description="The position in the file to start reading from (1-indexed).",
    t="integer",
)

__LIMIT_PROPERTY__ = property_param(
    name="limit",
    description="The maximum number of bytes/characters to read. Omit or set to 0 to read to end of file.",
    t="integer",
)

__MODE_PROPERTY__ = property_param(
    name="mode",
    description="The mode in which to read the file - 'r' for text mode (default) or 'rb' for binary mode.",
    t="string",
)

__READ_FUNCTION__ = function_ai(
    name="read",
    description="This function reads a file and returns its contents. Use offset and limit for paginated reading.",
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
        with open(file_path, mode) as f:
            f.seek(0, 2)
            file_size = f.tell()

            byte_offset = offset - 1
            if byte_offset > file_size:
                return f"Error: Offset {offset} is beyond file size {file_size}"

            f.seek(byte_offset)

            if limit > 0:
                content = f.read(limit)
            else:
                content = f.read()

            if mode == "rb":
                import base64

                return f"BASE64:{base64.b64encode(content).decode('utf-8')}"

            return content
    except Exception as e:
        return f"Error: Unexpected error when reading file: {str(e)}"


TOOL_CALL_MAP = {
    "read": read_file,
}
