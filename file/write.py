from base import function_ai, parameters_func, property_param

import os

__WRITE_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file to be written.",
    t="string",
    required=True
)

__WRITE_PROPERTY_TWO__ = property_param(
    name="content",
    description="The content to write to the file.",
    t="string",
    required=True
)

__WRITE_PROPERTY_THREE__ = property_param(
    name="mode",
    description="The mode in which to write the file, 'w' for write (overwrite), 'wb' for binary write, 'a' for append, 'ab' for binary append.",
    t="string"
)

__WRITE_PROPERTY_4__ = property_param(
    name="offset",
    description="The position in the file to start writing from.",
    t="integer"
)

__WRITE_PROPERTY_5__ = property_param(
    name="encoding",
    description="The encoding to use when writing the file.",
    t="string"
)

__WRITE_FUNCTION__ = function_ai(name="write_file",
                                 description="This function writes content to a file.",
                                 parameters=parameters_func([__WRITE_PROPERTY_ONE__, __WRITE_PROPERTY_TWO__, __WRITE_PROPERTY_THREE__, __WRITE_PROPERTY_5__]))

__WRITE_APPEND_FUNCTION__ = function_ai(name="append_to_file",
                                       description="This function appends content to the end of a file.",
                                       parameters=parameters_func([__WRITE_PROPERTY_ONE__, __WRITE_PROPERTY_TWO__, __WRITE_PROPERTY_THREE__, __WRITE_PROPERTY_5__]))

__WRITE_AT_OFFSET_FUNCTION__ = function_ai(name="write_at_offset",
                                          description="This function writes content at a specific offset in a file.",
                                          parameters=parameters_func([__WRITE_PROPERTY_ONE__, __WRITE_PROPERTY_TWO__, __WRITE_PROPERTY_THREE__, __WRITE_PROPERTY_4__, __WRITE_PROPERTY_5__]))

tools = [__WRITE_FUNCTION__, __WRITE_APPEND_FUNCTION__, __WRITE_AT_OFFSET_FUNCTION__]

def write_file(file_path: str, content: str, mode: str = "w", encoding: str = "utf-8") -> str:
    '''
    Writes content to a file.
    
    :param file_path: Path of the file to write
    :type file_path: str
    :param content: Content to write (base64 encoded for binary modes)
    :type content: str
    :param mode: Write mode - 'w' (text), 'wb' (binary), 'a' (append), 'ab' (binary append)
    :type mode: str
    :param encoding: File encoding for text modes
    :type encoding: str
    :return: Success or error message
    :rtype: str
    '''
    try:
        import os
        file_path = os.path.normpath(file_path)
        
        # Validate mode
        if mode not in ['w', 'wb', 'a', 'ab']:
            return f"Error: Invalid mode '{mode}'. Use 'w' (text), 'wb' (binary), 'a' (append), or 'ab' (binary append)."
        
        # Handle binary mode content
        if mode in ['wb', 'ab']:
            import base64
            try:
                # content should be base64 encoded for binary mode
                if content.startswith('BASE64:'):
                    content = content[7:]  # Remove BASE64: prefix
                binary_content = base64.b64decode(content)
            except Exception as e:
                return f"Error: Invalid base64 content for binary mode: {str(e)}"
            content_to_write = binary_content
        else:
            content_to_write = content
        
        # Write file
        with open(file_path, mode, encoding=encoding if mode in ['w', 'a'] else None) as file:
            file.write(content_to_write)
        
        if mode in ['a', 'ab']:
            return f"Successfully appended to {file_path}"
        else:
            return f"Successfully wrote to {file_path}"
            
    except Exception as e:
        return f"Error: Unexpected error when writing to file: {str(e)}"

def append_to_file(file_path: str, content: str, mode: str = "a", encoding: str = "utf-8") -> str:
    '''
    Appends content to the end of a file.
    
    :param file_path: Path of the file to append to
    :type file_path: str
    :param content: Content to append (base64 encoded for binary mode)
    :type content: str
    :param mode: Append mode - 'a' (text append), 'ab' (binary append)
    :type mode: str
    :param encoding: File encoding for text mode
    :type encoding: str
    :return: Success or error message
    :rtype: str
    '''
    try:
        import os
        file_path = os.path.normpath(file_path)
        
        # Validate mode
        if mode not in ['a', 'ab']:
            return f"Error: Invalid append mode '{mode}'. Use 'a' (text append) or 'ab' (binary append)."
        
        # Handle binary mode content
        if mode == 'ab':
            import base64
            try:
                # content should be base64 encoded for binary mode
                if content.startswith('BASE64:'):
                    content = content[7:]  # Remove BASE64: prefix
                binary_content = base64.b64decode(content)
            except Exception as e:
                return f"Error: Invalid base64 content for binary mode: {str(e)}"
            content_to_write = binary_content
        else:
            content_to_write = content
        
        # Append to file
        with open(file_path, mode, encoding=encoding if mode == 'a' else None) as file:
            file.write(content_to_write)
        
        return f"Successfully appended to {file_path}"
            
    except Exception as e:
        return f"Error: Unexpected error when appending to file: {str(e)}"

def write_at_offset(file_path: str, content: str, mode: str = "w", offset: int = 0, encoding: str = "utf-8") -> str:
    '''
    Writes content at a specific offset in a file.
    
    :param file_path: Path of the file
    :type file_path: str
    :param content: Content to write (base64 encoded for binary modes)
    :type content: str
    :param mode: Write mode - 'w' (text overwrite), 'wb' (binary overwrite), 'a' (text append), 'ab' (binary append)
    :type mode: str
    :param offset: Position to start writing (for insert operations)
    :type offset: int
    :param encoding: File encoding for text modes
    :type encoding: str
    :return: Success or error message
    :rtype: str
    '''
    try:
        import os
        file_path = os.path.normpath(file_path)
        
        # Validate parameters
        if mode not in ['w', 'wb', 'a', 'ab']:
            return f"Error: Invalid mode '{mode}'. Use 'w' (text), 'wb' (binary), 'a' (append), or 'ab' (binary append)."
        
        if offset < 0:
            return f"Error: Offset cannot be negative: {offset}"
        
        # Check if file exists for offset validation (except for append modes)
        file_exists = os.path.exists(file_path)
        if file_exists and not os.path.isfile(file_path):
            return f"Error: Path is not a file: {file_path}"
        
        # Handle binary mode content
        if mode in ['wb', 'ab']:
            import base64
            try:
                # content should be base64 encoded for binary mode
                if content.startswith('BASE64:'):
                    content = content[7:]  # Remove BASE64: prefix
                binary_content = base64.b64decode(content)
            except Exception as e:
                return f"Error: Invalid base64 content for binary mode: {str(e)}"
            content_to_write = binary_content
            open_mode = 'ab' if mode == 'ab' else 'wb'
        else:
            content_to_write = content
            open_mode = 'a' if mode == 'a' else 'w'
        
        # Handle different write scenarios
        if mode in ['a', 'ab']:
            # Append mode - simple append to end
            with open(file_path, open_mode) as file:
                file.write(content_to_write)
            return f"Successfully appended to {file_path}"
        
        elif offset == 0:
            # Write at beginning (overwrite entire file)
            with open(file_path, open_mode) as file:
                file.write(content_to_write)
            return f"Successfully wrote to {file_path}"
        
        else:
            # Insert at specific offset - requires reading existing content
            if not file_exists:
                return f"Error: Cannot write at offset {offset} in non-existent file. Use offset=0 to create new file."
            
            # For large files, use efficient block-based approach
            import tempfile
            import shutil
            
            temp_path = None
            try:
                # Create temp file
                with tempfile.NamedTemporaryFile(mode='wb' if mode == 'wb' else 'w', 
                                               delete=False, 
                                               encoding=encoding if mode == 'w' else None) as temp_file:
                    temp_path = temp_file.name
                    
                    # Copy first part (up to offset) to temp file
                    with open(file_path, 'rb' if mode == 'wb' else 'r', 
                            encoding=encoding if mode == 'w' else None) as src_file:
                        # Read up to offset
                        if offset > 0:
                            chunk_size = 8192
                            bytes_read = 0
                            while bytes_read < offset:
                                chunk = src_file.read(min(chunk_size, offset - bytes_read))
                                if not chunk:
                                    break
                                temp_file.write(chunk)
                                bytes_read += len(chunk)
                    
                    # Write new content
                    temp_file.write(content_to_write)
                    
                    # Copy remaining content
                    with open(file_path, 'rb' if mode == 'wb' else 'r', 
                            encoding=encoding if mode == 'w' else None) as src_file:
                        src_file.seek(offset)
                        chunk_size = 8192
                        while True:
                            chunk = src_file.read(chunk_size)
                            if not chunk:
                                break
                            temp_file.write(chunk)
                
                # Replace original file with temp file
                shutil.move(temp_path, file_path)
                return f"Successfully wrote at offset {offset} in {file_path}"
                
            except Exception as e:
                # Clean up temp file on error
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise e
                
    except Exception as e:
        return f"Error: Unexpected error when writing at offset: {str(e)}"

TOOL_CALL_MAP = {
    "write_file": write_file,
    "append_to_file": append_to_file,
    "write_at_offset": write_at_offset,
}