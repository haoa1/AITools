from base import function_ai, parameters_func, property_param

import os
import difflib

__COMPARE_PROPERTY_ONE__ = property_param(
    name="file1",
    description="The path of the first file to compare.",
    t="string",
    required=True
)

__COMPARE_PROPERTY_TWO__ = property_param(
    name="file2",
    description="The path of the second file to compare.",
    t="string",
    required=True
)

__COMPARE_PROPERTY_THREE__ = property_param(
    name="ignore_whitespace",
    description="Whether to ignore whitespace differences when comparing.",
    t="boolean"
)

__COMPARE_PROPERTY_4__ = property_param(
    name="show_diff",
    description="Whether to show detailed differences between files.",
    t="boolean"
)

__COMPARE_FUNCTION__ = function_ai(name="compare_files",
                                   description="This function compares two files and returns their differences.",
                                   parameters=parameters_func([__COMPARE_PROPERTY_ONE__, __COMPARE_PROPERTY_TWO__, __COMPARE_PROPERTY_THREE__, __COMPARE_PROPERTY_4__]))

tools = [__COMPARE_FUNCTION__]

def compare_files(file1: str, file2: str, ignore_whitespace: bool = False, show_diff: bool = False) -> str:
    '''
    Compares two files and returns their differences.
    
    :param file1: Path of the first file
    :type file1: str
    :param file2: Path of the second file
    :type file2: str
    :param ignore_whitespace: Whether to ignore whitespace differences
    :type ignore_whitespace: bool
    :param show_diff: Whether to show detailed differences
    :type show_diff: bool
    :return: Comparison result as string
    :rtype: str
    '''
    try:
        file1 = os.path.normpath(file1)
        file2 = os.path.normpath(file2)
        
        # Check if files exist
        if not os.path.exists(file1):
            return f"Error: File does not exist: {file1}"
        if not os.path.exists(file2):
            return f"Error: File does not exist: {file2}"
        
        # Check if paths are files
        if not os.path.isfile(file1):
            return f"Error: Path is not a file: {file1}"
        if not os.path.isfile(file2):
            return f"Error: Path is not a file: {file2}"
        
        # Check read permissions
        if not os.access(file1, os.R_OK):
            return f"Error: No read permission for file: {file1}"
        if not os.access(file2, os.R_OK):
            return f"Error: No read permission for file: {file2}"
        
        # Read file contents
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        # Handle encoding fallback if UTF-8 fails
        except_list = []
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                content1 = f.read()
        except UnicodeDecodeError:
            try:
                with open(file1, 'r', encoding='latin-1') as f:
                    content1 = f.read()
            except Exception as e:
                except_list.append(f"Error reading {file1}: {str(e)}")
        
        try:
            with open(file2, 'r', encoding='utf-8') as f:
                content2 = f.read()
        except UnicodeDecodeError:
            try:
                with open(file2, 'r', encoding='latin-1') as f:
                    content2 = f.read()
            except Exception as e:
                except_list.append(f"Error reading {file2}: {str(e)}")
        
        if except_list:
            return "\\n".join(except_list)
        
        # Prepare content for comparison
        if ignore_whitespace:
            content1 = '\\n'.join([line.rstrip() for line in content1.splitlines()])
            content2 = '\\n'.join([line.rstrip() for line in content2.splitlines()])
        
        # Compare contents
        if content1 == content2:
            return "Files are identical."
        else:
            # Count differences in lines
            lines1 = content1.splitlines()
            lines2 = content2.splitlines()
            
            diff_count = sum(1 for a, b in zip(lines1, lines2) if a != b)
            # Account for different number of lines
            diff_count += abs(len(lines1) - len(lines2))
            
            result = f"Files differ: {diff_count} lines different."
            
            if show_diff:
                diff = difflib.unified_diff(
                    lines1,
                    lines2,
                    fromfile=file1,
                    tofile=file2,
                    lineterm=''
                )
                diff_text = '\\n'.join(diff)
                if diff_text:
                    result += f"\\n\\nDifferences:\\n{diff_text}"
                else:
                    result += "\\n(No detailed diff available)"
            
            return result
            
    except FileNotFoundError as e:
        return f"Error: File not found: {str(e)}"
    except PermissionError as e:
        return f"Error: Permission denied when reading file: {str(e)}"
    except IOError as e:
        return f"Error: I/O error when reading file: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when comparing files: {str(e)}"

TOOL_CALL_MAP = {
    "compare_files": compare_files,
}