from base import function_ai, parameters_func, property_param

import os

__WRITE_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file to be written.",
    t="string",
    required=True,
)

__WRITE_PROPERTY_TWO__ = property_param(
    name="content",
    description="The content to write to the file.",
    t="string",
    required=True,
)

__WRITE_PROPERTY_THREE__ = property_param(
    name="mode",
    description="The mode in which to write the file, 'w' for write (overwrite), 'wb' for binary write.",
    t="string",
)

__WRITE_PROPERTY_5__ = property_param(
    name="encoding",
    description="The encoding to use when writing the file.",
    t="string",
)

__WRITE_FUNCTION__ = function_ai(
    name="write",
    description="This function writes content to a file. It can create new files or overwrite existing files.",
    parameters=parameters_func(
        [
            __WRITE_PROPERTY_ONE__,
            __WRITE_PROPERTY_TWO__,
            __WRITE_PROPERTY_THREE__,
            __WRITE_PROPERTY_5__,
        ]
    ),
)

tools = [__WRITE_FUNCTION__]


def write_file(
    file_path: str, content: str, mode: str = "w", encoding: str = "utf-8"
) -> str:
    """
    Writes content to a file. Can create new files or overwrite existing files.

    :param file_path: Path of the file to write
    :type file_path: str
    :param content: Content to write (base64 encoded for binary modes)
    :type content: str
    :param mode: Write mode - 'w' (text), 'wb' (binary)
    :type mode: str
    :param encoding: File encoding for text modes
    :type encoding: str
    :return: Success or error message
    :rtype: str
    """
    try:
        import os
        import base64

        file_path = os.path.normpath(file_path)

        # Validate mode
        if mode not in ["w", "wb"]:
            return f"Error: Invalid mode '{mode}'. Use 'w' (text) or 'wb' (binary)."

        # Handle binary mode content
        if mode == "wb":
            try:
                # content should be base64 encoded for binary mode
                if content.startswith("BASE64:"):
                    content = content[7:]  # Remove BASE64: prefix
                binary_content = base64.b64decode(content)
                content_to_write = binary_content
            except Exception as e:
                return f"Error: Invalid base64 content for binary mode: {str(e)}"
        else:
            content_to_write = content

        # Write file
        with open(
            file_path, mode, encoding=encoding if mode == "w" else None
        ) as file:
            file.write(content_to_write)

        return f"Successfully wrote to {file_path}"

    except Exception as e:
        return f"Error: Unexpected error when writing to file: {str(e)}"


TOOL_CALL_MAP = {
    "write": write_file,
}