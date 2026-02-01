from base import function_ai, parameters_func, property_param

import os

__DELETE_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file or directory to be deleted.",
    t="string",
    required=True
)

__DELETE_PROPERTY_TWO__ = property_param(
    name="start_line",
    description="The starting line number to delete from (1-based).",
    t="integer"
)

__DELETE_PROPERTY_THREE__ = property_param(
    name="end_line",
    description="The ending line number to delete to (inclusive).",
    t="integer"
)

__DELETE_PROPERTY_4__ = property_param(
    name="recursive",
    description="Whether to delete directories recursively.",
    t="boolean"
)

__DELETE_PROPERTY_5__ = property_param(
    name="offset",
    description="The position in the file to start deleting from.",
    t="integer"
)

__DELETE_PROPERTY_6__ = property_param(
    name="length",
    description="The number of characters/bytes to delete from the file.",
    t="integer"
)

__DELETE_PROPERTY_7__ = property_param(
    name="mode",
    description="The mode for deletion - 'r' (text mode, default) or 'rb' (binary mode).",
    t="string"
)

__DELETE_FILE_FUNCTION__ = function_ai(name="delete_file",
                                       description="This function deletes a file or directory.",
                                       parameters=parameters_func([__DELETE_PROPERTY_ONE__, __DELETE_PROPERTY_4__]))

__DELETE_LINES_FUNCTION__ = function_ai(name="delete_lines",
                                       description="This function deletes specific lines from a file.",
                                       parameters=parameters_func([__DELETE_PROPERTY_ONE__, __DELETE_PROPERTY_TWO__, __DELETE_PROPERTY_THREE__]))

__DELETE_AT_OFFSET_FUNCTION__ = function_ai(name="delete_at_offset",
                                           description="This function deletes characters at a specific offset in a file.",
                                           parameters=parameters_func([__DELETE_PROPERTY_ONE__, __DELETE_PROPERTY_5__, __DELETE_PROPERTY_6__, __DELETE_PROPERTY_7__]))

tools = [__DELETE_FILE_FUNCTION__, __DELETE_LINES_FUNCTION__, __DELETE_AT_OFFSET_FUNCTION__]

def delete_file(file_path: str, recursive: bool = False) -> str:
    '''
    Deletes a file or directory.
    
    :param file_path: Path of the file or directory to delete
    :type file_path: str
    :param recursive: Whether to delete directories recursively
    :type recursive: bool
    :return: Success or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"File or directory does not exist: {file_path}"
        
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"Successfully deleted file: {file_path}"
        elif os.path.isdir(file_path):
            if recursive:
                import shutil
                shutil.rmtree(file_path)
                return f"Successfully deleted directory recursively: {file_path}"
            else:
                # Check if directory is empty
                if not os.listdir(file_path):
                    os.rmdir(file_path)
                    return f"Successfully deleted empty directory: {file_path}"
                else:
                    return f"Directory is not empty. Use recursive=True to delete non-empty directories: {file_path}"
        else:
            return f"Path is neither a file nor a directory: {file_path}"
    except Exception as e:
        return f"Error deleting file/directory: {str(e)}"

def delete_lines(file_path: str, start_line: int, end_line: int = None) -> str:
    '''
    Deletes specific lines from a file.
    
    :param file_path: Path of the file
    :type file_path: str
    :param start_line: Starting line number (1-based)
    :type start_line: int
    :param end_line: Ending line number (inclusive, optional)
    :type end_line: int
    :return: Success or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"File does not exist: {file_path}"
        
        if end_line is None:
            end_line = start_line
        
        if start_line < 1 or end_line < 1 or start_line > end_line:
            return f"Invalid line range: {start_line}-{end_line}"
        
        # Read all lines
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Check if line numbers are valid
        if start_line > len(lines) or end_line > len(lines):
            return f"Line numbers out of range. File has {len(lines)} lines."
        
        # Delete lines (adjusting for 0-based index)
        del lines[start_line-1:end_line]
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        return f"Successfully deleted lines {start_line}-{end_line} from {file_path}"
    except Exception as e:
        return f"Error deleting lines: {str(e)}"

def delete_at_offset(file_path: str, offset: int, length: int, mode: str = "r") -> str:
    '''
    Deletes characters/bytes at a specific offset in a file.
    
    :param file_path: Path of the file
    :type file_path: str
    :param offset: Position to start deleting from
    :type offset: int
    :param length: Number of characters/bytes to delete
    :type length: int
    :param mode: Deletion mode - 'r' (text mode, default) or 'rb' (binary mode)
    :type mode: str
    :return: Success or error message
    :rtype: str
    '''
    try:
        import os
        file_path = os.path.normpath(file_path)
        
        # Validate parameters
        if mode not in ['r', 'rb']:
            return f"Error: Invalid mode '{mode}'. Use 'r' (text) or 'rb' (binary)."
        
        if offset < 0:
            return f"Error: Offset cannot be negative: {offset}"
        
        if length <= 0:
            return f"Error: Length must be a positive integer: {length}"
        
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        # For large files, use efficient block-based approach
        import tempfile
        import shutil
        
        temp_path = None
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='wb' if mode == 'rb' else 'w', 
                                           delete=False, 
                                           encoding='utf-8' if mode == 'r' else None) as temp_file:
                temp_path = temp_file.name
                
                # Copy file content up to offset
                with open(file_path, 'rb' if mode == 'rb' else 'r', 
                        encoding='utf-8' if mode == 'r' else None) as src_file:
                    
                    # Copy first part (up to offset)
                    if offset > 0:
                        chunk_size = 8192
                        bytes_read = 0
                        while bytes_read < offset:
                            chunk = src_file.read(min(chunk_size, offset - bytes_read))
                            if not chunk:
                                # Reached EOF before offset
                                return f"Error: Offset {offset} is beyond file size {bytes_read}"
                            temp_file.write(chunk)
                            bytes_read += len(chunk)
                    
                    # Skip the part to be deleted
                    if length > 0:
                        bytes_to_skip = length
                        while bytes_to_skip > 0:
                            chunk = src_file.read(min(chunk_size, bytes_to_skip))
                            if not chunk:
                                # Reached EOF while skipping
                                break
                            bytes_to_skip -= len(chunk)
                    
                    # Copy remaining content
                    chunk_size = 8192
                    while True:
                        chunk = src_file.read(chunk_size)
                        if not chunk:
                            break
                        temp_file.write(chunk)
            
            # Replace original file with temp file
            shutil.move(temp_path, file_path)
            
            unit = "bytes" if mode == 'rb' else "characters"
            return f"Successfully deleted {length} {unit} at offset {offset} from {file_path}"
                
        except Exception as e:
            # Clean up temp file on error
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            if "is beyond file size" in str(e):
                return f"Error: Offset {offset} is beyond file size"
            else:
                return f"Error: Unexpected error when deleting at offset: {str(e)}"
                
    except Exception as e:
        return f"Error: Unexpected error when deleting at offset: {str(e)}"

TOOL_CALL_MAP = {
    "delete_file": delete_file,
    "delete_lines": delete_lines,
    "delete_at_offset": delete_at_offset,
}