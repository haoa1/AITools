from base import function_ai, parameters_func, property_param

import os
import re

__REPLACE_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file where content will be replaced.",
    t="string",
    required=True
)

__REPLACE_PROPERTY_TWO__ = property_param(
    name="old_text",
    description="The text to be replaced.",
    t="string",
    required=True
)

__REPLACE_PROPERTY_THREE__ = property_param(
    name="new_text",
    description="The new text to replace with.",
    t="string",
    required=True
)

__REPLACE_PROPERTY_4__ = property_param(
    name="count",
    description="Maximum number of occurrences to replace. -1 for all.",
    t="integer"
)

__REPLACE_PROPERTY_5__ = property_param(
    name="case_sensitive",
    description="Whether the replacement is case-sensitive.",
    t="boolean"
)

__REPLACE_PROPERTY_6__ = property_param(
    name="start_line",
    description="The starting line number to limit replacement (1-based).",
    t="integer"
)

__REPLACE_PROPERTY_7__ = property_param(
    name="end_line",
    description="The ending line number to limit replacement (inclusive).",
    t="integer"
)

__REPLACE_PROPERTY_8__ = property_param(
    name="pattern",
    description="The regular expression pattern to match.",
    t="string",
    required=True
)

__REPLACE_PROPERTY_9__ = property_param(
    name="replacement",
    description="The replacement string (can include backreferences).",
    t="string",
    required=True
)

__REPLACE_STRING_FUNCTION__ = function_ai(name="replace_in_file",
                                         description="This function replaces text in a file.",
                                         parameters=parameters_func([__REPLACE_PROPERTY_ONE__, __REPLACE_PROPERTY_TWO__, __REPLACE_PROPERTY_THREE__, __REPLACE_PROPERTY_4__, __REPLACE_PROPERTY_5__]))

__REPLACE_LINES_FUNCTION__ = function_ai(name="replace_lines",
                                        description="This function replaces lines in a file.",
                                        parameters=parameters_func([__REPLACE_PROPERTY_ONE__, __REPLACE_PROPERTY_6__, __REPLACE_PROPERTY_7__, __REPLACE_PROPERTY_THREE__]))

__REPLACE_REGEX_FUNCTION__ = function_ai(name="replace_with_regex",
                                        description="This function replaces text using regular expressions.",
                                        parameters=parameters_func([__REPLACE_PROPERTY_ONE__, __REPLACE_PROPERTY_8__, __REPLACE_PROPERTY_9__]))

tools = [__REPLACE_STRING_FUNCTION__, __REPLACE_LINES_FUNCTION__, __REPLACE_REGEX_FUNCTION__]

def replace_in_file(file_path: str, old_text: str, new_text: str, count: int = -1, case_sensitive: bool = True) -> str:
    '''
    Replaces text in a file.
    
    :param file_path: Path of the file
    :type file_path: str
    :param old_text: Text to be replaced
    :type old_text: str
    :param new_text: New text to replace with
    :type new_text: str
    :param count: Maximum number of replacements (-1 for all)
    :type count: int
    :param case_sensitive: Whether replacement is case-sensitive
    :type case_sensitive: bool
    :return: Success message with number of replacements
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Perform replacement
        if case_sensitive:
            if count == -1:
                new_content = content.replace(old_text, new_text)
                replacements = content.count(old_text)
            else:
                new_content = content.replace(old_text, new_text, count)
                actual_count = min(count, content.count(old_text))
                replacements = actual_count
        else:
            import re
            flags = re.IGNORECASE
            if count == -1:
                new_content, replacements = re.subn(re.escape(old_text), new_text, content, flags=flags)
            else:
                new_content, replacements = re.subn(re.escape(old_text), new_text, content, count, flags=flags)
        
        # Only write if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return f"Successfully replaced {replacements} occurrence(s) in {file_path}"
        else:
            return f"No replacements made in {file_path}"
    except Exception as e:
        return f"Error: Unexpected error when replacing text: {str(e)}"

def replace_lines(file_path: str, start_line: int, end_line: int, new_text: str) -> str:
    '''
    Replaces lines in a file with new text.
    
    :param file_path: Path of the file
    :type file_path: str
    :param start_line: Starting line number (1-based)
    :type start_line: int
    :param end_line: Ending line number (inclusive)
    :type end_line: int
    :param new_text: New text to replace the lines
    :type new_text: str
    :return: Success or error message
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        if start_line < 1 or end_line < 1 or start_line > end_line:
            return f"Error: Invalid line range: {start_line}-{end_line}"
        
        # Read all lines with preserved line endings
        with open(file_path, 'r', encoding='utf-8', newline='') as file:
            lines = file.readlines()
        
        # Check if line numbers are valid
        if start_line > len(lines) or end_line > len(lines):
            return f"Error: Line numbers out of range. File has {len(lines)} lines."
        
        # Determine the line ending to use
        # First, try to get line ending from surrounding context
        line_ending = None
        
        # Check line before the replacement range
        if start_line > 1:
            prev_line = lines[start_line - 2]
            if prev_line.endswith('\r\n'):
                line_ending = '\r\n'
            elif prev_line.endswith('\n'):
                line_ending = '\n'
            elif prev_line.endswith('\r'):
                line_ending = '\r'
        
        # If not found, check line after the replacement range
        if line_ending is None and end_line < len(lines):
            next_line = lines[end_line]
            if next_line.endswith('\r\n'):
                line_ending = '\r\n'
            elif next_line.endswith('\n'):
                line_ending = '\n'
            elif next_line.endswith('\r'):
                line_ending = '\r'
        
        # If still not found, check first line being replaced
        if line_ending is None and start_line <= len(lines):
            first_line = lines[start_line - 1]
            if first_line.endswith('\r\n'):
                line_ending = '\r\n'
            elif first_line.endswith('\n'):
                line_ending = '\n'
            elif first_line.endswith('\r'):
                line_ending = '\r'
        
        # Default to Unix line endings if still not determined
        if line_ending is None:
            line_ending = '\n'
        
        # Split new text into lines using splitlines(keepends=True)
        # This preserves any line endings already in new_text
        new_lines = new_text.splitlines(keepends=True)
        
        # Process the new lines
        if new_lines:
            # If new_text doesn't end with a newline, we need to ensure
            # the last line has proper line ending
            if not new_text.endswith('\n') and not new_text.endswith('\r'):
                # Remove any trailing newline characters that might be there
                # (splitlines(keepends=True) doesn't include newline for last line
                # if the string doesn't end with newline)
                new_lines[-1] = new_lines[-1].rstrip('\n\r') + line_ending
            else:
                # new_text ends with newline, so splitlines(keepends=True) already
                # included it. But we might need to normalize it to the file's
                # line ending style.
                # Actually, if new_text has its own line endings, we should
                # preserve them. So we won't change existing line endings in new_text.
                pass
        else:
            # new_text is empty string or only contains newlines
            if not new_text:
                # Empty string - no lines
                new_lines = []
            else:
                # new_text contains only newline characters
                # splitlines(keepends=True) returns empty list for strings with only newlines
                # We need to handle this specially
                # Count how many lines new_text represents
                line_count = new_text.count('\n') + new_text.count('\r') - new_text.count('\r\n')
                new_lines = [line_ending] * line_count
        
        # Replace lines (adjusting for 0-based index)
        lines[start_line-1:end_line] = new_lines
        
        # Write back to file with preserved line endings
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            file.writelines(lines)
        
        return f"Successfully replaced lines {start_line}-{end_line} in {file_path}"
    except Exception as e:
        return f"Error: Unexpected error when replacing lines: {str(e)}"
def replace_with_regex(file_path: str, pattern: str, replacement: str) -> str:
    '''
    Replaces text in a file using regular expressions.
    
    :param file_path: Path of the file
    :type file_path: str
    :param pattern: Regular expression pattern to match
    :type pattern: str
    :param replacement: Replacement string (can include backreferences)
    :type replacement: str
    :return: Success message with number of replacements
    :rtype: str
    '''
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        import re
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Perform regex replacement
        new_content, replacements = re.subn(pattern, replacement, content, flags=re.MULTILINE)
        
        # Only write if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return f"Successfully replaced {replacements} occurrence(s) using regex in {file_path}"
        else:
            return f"No replacements made in {file_path}"
    except re.error as e:
        return f"Error: Invalid regex pattern: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when replacing with regex: {str(e)}"

TOOL_CALL_MAP = {
    "replace_in_file": replace_in_file,
    "replace_lines": replace_lines,
    "replace_with_regex": replace_with_regex,
}