from base import function_ai, parameters_func, property_param
import os, sys

# 已有属性...
__READ_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file to be read.",
    t="string",
    required=True
)

__READ_PROPERTY_TWO__ = property_param(
    name="offset",
    description="The position in the file to start reading from.",
    t="integer",
    required=True
)

__READ_PROPERTY_THREE__ = property_param(
    name="length",
    description="The number of characters/bytes to read from the file. Use 0 to read to end of file.",
    t="integer",
    required=True
)

__READ_PROPERTY_4__ = property_param(
    name="mode",
    description="The mode in which to read the file - 'r' for text mode (default) or 'rb' for binary mode.",
    t="string"
)

__READ_PROPERTY_5__ = property_param(
    name="n",
    description="The number of lines to read from the start of the file.",
    t="integer"
)

# 新属性
__FILE_SIZE_PROPERTY__ = property_param(
    name="unit",
    description="The unit for file size: 'bytes' (default), 'KB', 'MB', or 'GB'.",
    t="string"
)

__LINE_NUMBER_PROPERTY__ = property_param(
    name="line_number",
    description="The line number to center the context around (1-indexed).",
    t="integer",
    required=True
)

__CONTEXT_LINES_PROPERTY__ = property_param(
    name="context_lines",
    description="The number of lines to read before and after the specified line.",
    t="integer",
    required=True
)

# 已有函数...
__READ_FUNCTION__ = function_ai(name="read_file",
                                description="This function reads a file and returns its contents.",
                                parameters=parameters_func([__READ_PROPERTY_ONE__, __READ_PROPERTY_4__]))

__READ_OFFSET_FUNCTION__ = function_ai(name="read_file_by_offset",
                                description="This function reads a file from a specific offset and returns its contents.",
                                parameters=parameters_func([__READ_PROPERTY_ONE__, __READ_PROPERTY_TWO__, __READ_PROPERTY_THREE__, __READ_PROPERTY_4__]))

__READ_START_LINES_FUNCTION__ = function_ai(name="read_start_lines",
                                description="This function reads the first n lines of a file and returns them as a list to str.",
                                parameters=parameters_func([__READ_PROPERTY_ONE__, __READ_PROPERTY_5__]))

__READ_TAIL_LINES_FUNCTION__ = function_ai(name="read_tail_lines",
                                description="This function reads the last n lines of a file and returns them as a list to str.",
                                parameters=parameters_func([__READ_PROPERTY_ONE__, __READ_PROPERTY_5__]))

# 新函数
__GET_FILE_SIZE_FUNCTION__ = function_ai(name="get_file_size",
                                        description="This function gets the size of a file in specified units without reading the entire file.",
                                        parameters=parameters_func([__READ_PROPERTY_ONE__, __FILE_SIZE_PROPERTY__]))

__READ_LINE_CONTEXT_FUNCTION__ = function_ai(name="read_line_context",
                                            description="This function reads a specific line and its surrounding context lines without reading the entire file.",
                                            parameters=parameters_func([__READ_PROPERTY_ONE__, __LINE_NUMBER_PROPERTY__, __CONTEXT_LINES_PROPERTY__]))

__READ_LINES_RANGE_FUNCTION__ = function_ai(name="read_lines_range",
                                            description="This function reads a range of lines from a file without reading the entire file.",
                                            parameters=parameters_func([
                                                __READ_PROPERTY_ONE__,
                                                property_param(name="start_line", description="The starting line number (1-indexed).", t="integer", required=True),
                                                property_param(name="end_line", description="The ending line number (1-indexed).", t="integer", required=True)
                                            ]))

tools=[__READ_FUNCTION__, __READ_OFFSET_FUNCTION__, __READ_START_LINES_FUNCTION__, __READ_TAIL_LINES_FUNCTION__,
       __GET_FILE_SIZE_FUNCTION__, __READ_LINE_CONTEXT_FUNCTION__, __READ_LINES_RANGE_FUNCTION__]

# 已有函数实现...
def read_file(file_path: str, mode:str="r") -> str:
    '''
    Reads the entire content of a file.
    
    :param file_path: Path of the file to read
    :type file_path: str
    :param mode: File mode - 'r' for text, 'rb' for binary
    :type mode: str
    :return: File content as string (base64 encoded for binary mode) or error message
    :rtype: str
    '''
    try:
        import os
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if mode not in ['r', 'rb']:
            return f"Error: Invalid mode '{mode}'. Use 'r' for text or 'rb' for binary."
        
        with open(file_path, mode) as file:
            content = file.read()
        
        # Handle binary mode - encode to base64
        if mode == 'rb':
            import base64
            # content is bytes in binary mode
            encoded = base64.b64encode(content).decode('utf-8')
            return f"BASE64:{encoded}"
        else:
            # content is str in text mode
            return content
            
    except Exception as e:
        return f"Error: Unexpected error when reading file: {str(e)}"

def read_file_by_offset(file_path: str, offset: int, length: int, mode: str = "r") -> str:
    """
    Reads content from a file starting at a specific offset.
    
    :param file_path: Path of the file to read
    :type file_path: str
    :param offset: The position to start reading from (in bytes for binary mode, characters for text mode)
    :type offset: int
    :param length: The number of bytes/characters to read
    :type length: int
    :param mode: File mode - 'r' for text, 'rb' for binary
    :type mode: str
    :return: Content as string (base64 encoded for binary mode)
    :rtype: str
    """
    try:
        import os
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if mode not in ['r', 'rb']:
            return f"Error: Invalid mode '{mode}'. Use 'r' for text or 'rb' for binary."
        
        if offset < 0:
            return f"Error: Offset cannot be negative: {offset}"
        
        if length < 0:
            return f"Error: Length cannot be negative: {length}"
        
        with open(file_path, mode) as file:
            # Get file size
            file.seek(0, 2)
            file_size = file.tell()
            
            if offset > file_size:
                return f"Error: Offset {offset} is beyond file size {file_size}"
            
            # Seek to offset and read
            file.seek(offset)
            
            # If length is 0, read to end of file
            read_length = length
            if read_length == 0:
                read_length = file_size - offset
            
            content = file.read(read_length)
        
        # Handle binary mode - encode to base64
        if mode == 'rb':
            import base64
            # content is bytes in binary mode
            encoded = base64.b64encode(content).decode('utf-8')
            return f"BASE64:{encoded}"
        else:
            # content is str in text mode
            return content
            
    except Exception as e:
        return f"Error: Unexpected error when reading file by offset: {str(e)}"

def read_start_lines(file_path: str, n: int) -> str:
    # ... 已有实现保持不变
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if n <= 0:
            return f"Error: Number of lines must be positive: {n}"
        
        lines = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i in range(n):
                line = f.readline()
                if not line:
                    break
                lines.append(line.rstrip('\n'))
        
        return str(lines)
    except Exception as e:
        return f"Error: Unexpected error when reading start lines: {str(e)}"

def read_tail_lines(file_path: str, n: int) -> str:
    # ... 已有实现保持不变
    try:
        import os
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if n <= 0:
            return f"Error: Number of lines must be positive: {n}"
        
        with open(file_path, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            chunk_size = 8192
            total_bytes_read = 0
            data = b''
            lines_found = 0
            
            while total_bytes_read < file_size and lines_found < n + 1:
                bytes_to_read = min(chunk_size, file_size - total_bytes_read)
                f.seek(file_size - total_bytes_read - bytes_to_read)
                chunk = f.read(bytes_to_read)
                total_bytes_read += bytes_to_read
                data = chunk + data
                lines_found = data.count(b'\n')
            
            try:
                text = data.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = data.decode('latin-1')
                except UnicodeDecodeError as e:
                    return f"Error: Could not decode file with any supported encoding: {str(e)}"
            
            all_lines = text.splitlines()
            result_lines = all_lines[-n:] if len(all_lines) >= n else all_lines
            
            return str(result_lines)
    except Exception as e:
        return f"Error: Unexpected error when reading tail lines: {str(e)}"

# 新函数实现
def get_file_size(file_path: str, unit: str = "bytes") -> str:
    '''
    Gets the size of a file in specified units without reading the file contents.
    
    :param file_path: Path of the file
    :type file_path: str
    :param unit: Unit for size - 'bytes', 'KB', 'MB', or 'GB'
    :type unit: str
    :return: File size with unit or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        # Get file size in bytes
        size_bytes = os.path.getsize(file_path)
        
        # Convert to requested unit
        unit = unit.lower()
        if unit == "bytes":
            return f"{size_bytes} bytes"
        elif unit == "kb":
            return f"{size_bytes / 1024:.2f} KB"
        elif unit == "mb":
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif unit == "gb":
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        else:
            return f"Error: Unsupported unit '{unit}'. Use 'bytes', 'KB', 'MB', or 'GB'."
            
    except PermissionError as e:
        return f"Error: Permission denied when accessing file: {str(e)}"
    except FileNotFoundError as e:
        return f"Error: File not found: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when getting file size: {str(e)}"

def read_line_context(file_path: str, line_number: int, context_lines: int) -> str:
    '''
    Reads a specific line and its surrounding context lines without reading the entire file.
    
    :param file_path: Path of the file to read
    :type file_path: str
    :param line_number: The line number to center the context around (1-indexed)
    :type line_number: int
    :param context_lines: Number of lines to read before and after the specified line
    :type context_lines: int
    :return: Context lines as string or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if line_number < 1:
            return f"Error: Line number must be at least 1: {line_number}"
        
        if context_lines < 0:
            return f"Error: Context lines cannot be negative: {context_lines}"
        
        # Calculate line range
        start_line = max(1, line_number - context_lines)
        end_line = line_number + context_lines
        
        return read_lines_range_internal(file_path, start_line, end_line)
        
    except Exception as e:
        return f"Error: Unexpected error when reading line context: {str(e)}"

def read_lines_range(file_path: str, start_line: int, end_line: int) -> str:
    '''
    Reads a range of lines from a file without reading the entire file.
    
    :param file_path: Path of the file to read
    :type file_path: str
    :param start_line: Starting line number (1-indexed)
    :type start_line: int
    :param end_line: Ending line number (1-indexed)
    :type end_line: int
    :return: Selected lines as string or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file: {file_path}"
        
        if start_line < 1:
            return f"Error: Start line must be at least 1: {start_line}"
        
        if end_line < start_line:
            return f"Error: End line ({end_line}) must be greater than or equal to start line ({start_line})"
        
        return read_lines_range_internal(file_path, start_line, end_line)
        
    except Exception as e:
        return f"Error: Unexpected error when reading lines range: {str(e)}"

def read_lines_range_internal(file_path: str, start_line: int, end_line: int) -> str:
    '''
    Internal function to read a range of lines efficiently.
    
    :param file_path: Path of the file to read
    :param start_line: Starting line number (1-indexed)
    :param end_line: Ending line number (1-indexed)
    :return: Selected lines as string
    '''
    lines = []
    try:
        # Try UTF-8 encoding first
        encoding = 'utf-8'
        with open(file_path, 'r', encoding=encoding) as f:
            current_line = 0
            for line in f:
                current_line += 1
                if current_line > end_line:
                    break
                if current_line >= start_line:
                    lines.append(line.rstrip('\n'))
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        try:
            encoding = 'latin-1'
            with open(file_path, 'r', encoding=encoding) as f:
                current_line = 0
                for line in f:
                    current_line += 1
                    if current_line > end_line:
                        break
                    if current_line >= start_line:
                        lines.append(line.rstrip('\n'))
        except UnicodeDecodeError as e:
            return f"Error: Could not decode file with any supported encoding: {str(e)}"
    
    # Check if we got enough lines
    if start_line > 0 and len(lines) == 0:
        # Try to count total lines to give better error message
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                total_lines = sum(1 for _ in f)
            if start_line > total_lines:
                return f"Error: Start line {start_line} is beyond file's total lines ({total_lines})"
        except:
            pass
        return f"Error: Could not read lines {start_line}-{end_line}"
    
    return str(lines)

TOOL_CALL_MAP={
    "read_file": read_file,
    "read_file_by_offset": read_file_by_offset,
    "read_start_lines": read_start_lines,
    "read_tail_lines": read_tail_lines,
    "get_file_size": get_file_size,
    "read_line_context": read_line_context,
    "read_lines_range": read_lines_range,
}