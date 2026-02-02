"""
Markdown IO module - contains file reading and writing functions.
"""

from .markdown_base import _read_file_content, _write_file_content

def read_markdown_file(file_path: str, encoding: str = 'utf-8') -> str:
    '''
    Read a markdown file and return its content.
    
    :param file_path: Path to the markdown file
    :type file_path: str
    :param encoding: File encoding (default: 'utf-8')
    :type encoding: str
    :return: Markdown content or error message
    :rtype: str
    '''
    return _read_file_content(file_path, encoding)

def write_markdown_file(file_path: str, content: str, mode: str = 'w', encoding: str = 'utf-8') -> str:
    '''
    Write content to a markdown file.
    
    :param file_path: Path to the markdown file
    :type file_path: str
    :param content: Markdown content to write
    :type content: str
    :param mode: File mode: 'w' for write (overwrite), 'a' for append
    :type mode: str
    :param encoding: File encoding (default: 'utf-8')
    :type encoding: str
    :return: Success message or error message
    :rtype: str
    '''
    return _write_file_content(file_path, content, mode, encoding)

__all__ = ["read_markdown_file", "write_markdown_file"]