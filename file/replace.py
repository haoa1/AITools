from base import function_ai, parameters_func, property_param

import os

__EDIT_PROPERTY_ONE__ = property_param(
    name="file_path",
    description="The path of the file to modify.",
    t="string",
    required=True,
)

__EDIT_PROPERTY_TWO__ = property_param(
    name="old_text",
    description="The text to replace.",
    t="string",
    required=True,
)

__EDIT_PROPERTY_THREE__ = property_param(
    name="new_text",
    description="The new text to replace with.",
    t="string",
    required=True,
)

__EDIT_PROPERTY_4__ = property_param(
    name="replace_all",
    description="Whether to replace all occurrences. If false, only replaces the first occurrence.",
    t="boolean",
)

__EDIT_PROPERTY_5__ = property_param(
    name="case_sensitive",
    description="Whether the replacement is case-sensitive.",
    t="boolean",
)

__EDIT_FUNCTION__ = function_ai(
    name="edit",
    description="This function edits a file by replacing text. It can replace specific occurrences or all occurrences.",
    parameters=parameters_func(
        [
            __EDIT_PROPERTY_ONE__,
            __EDIT_PROPERTY_TWO__,
            __EDIT_PROPERTY_THREE__,
            __EDIT_PROPERTY_4__,
            __EDIT_PROPERTY_5__,
        ]
    ),
)

tools = [__EDIT_FUNCTION__]


def edit_file(
    file_path: str,
    old_text: str,
    new_text: str,
    replace_all: bool = False,
    case_sensitive: bool = True,
) -> str:
    """
    Edits a file by replacing text. Can replace specific occurrences or all occurrences.

    :param file_path: Path of the file to edit
    :type file_path: str
    :param old_text: Text to replace
    :type old_text: str
    :param new_text: New text to replace with
    :type new_text: str
    :param replace_all: Whether to replace all occurrences (default: False, only first)
    :type replace_all: bool
    :param case_sensitive: Whether replacement is case-sensitive (default: True)
    :type case_sensitive: bool
    :return: Success message with number of replacements
    :rtype: str
    """
    try:
        import re
        
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return f"Error: File does not exist: {file_path}"
        
        # Check for empty old_text (would match everywhere)
        if old_text == "":
            return "Error: Old text cannot be empty"
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if old_text exists in the file
        if old_text == new_text:
            return f"No changes needed: old_text and new_text are identical"
        
        # Perform replacement
        if case_sensitive:
            if replace_all:
                new_content = content.replace(old_text, new_text)
                replacements = content.count(old_text)
            else:
                # Replace only the first occurrence
                if old_text not in content:
                    replacements = 0
                    new_content = content
                else:
                    new_content = content.replace(old_text, new_text, 1)
                    replacements = 1 if old_text in content else 0
        else:
            # Case-insensitive replacement
            flags = re.IGNORECASE
            if replace_all:
                new_content, replacements = re.subn(
                    re.escape(old_text), new_text, content, flags=flags
                )
            else:
                # Replace only the first occurrence
                pattern = re.compile(re.escape(old_text), flags)
                new_content, replacements = pattern.subn(
                    new_text, content, count=1
                )
        
        # Only write if changes were made
        if replacements > 0:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            return f"Successfully made {replacements} replacement(s) in {file_path}"
        else:
            return f"No replacements made in {file_path} (text not found)"
            
    except Exception as e:
        return f"Error: Unexpected error when editing file: {str(e)}"


TOOL_CALL_MAP = {
    "edit": edit_file,
}