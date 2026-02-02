"""
Markdown parse module - contains markdown parsing and HTML conversion functions.
"""

import re
import json
from typing import List, Dict, Any, Optional

# Import helper functions from base module
from .markdown_base import _extract_headings_from_text, _convert_line_to_html

def parse_markdown(markdown_text: str, include_metadata: bool = False) -> str:
    '''
    Parse markdown text and extract structure (headings, lists, code blocks, etc.).
    
    :param markdown_text: Markdown text to parse
    :type markdown_text: str
    :param include_metadata: Whether to include metadata in output
    :type include_metadata: bool
    :return: JSON string with parsed structure
    :rtype: str
    '''
    try:
        structure = {
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "code_blocks": [],
            "links": [],
            "images": [],
            "tables": [],
            "blockquotes": []
        }
        
        lines = markdown_text.split('\n')
        current_paragraph = ""
        
        for i, line in enumerate(lines):
            line = line.rstrip()
            
            # Parse headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                structure["headings"].append({
                    "level": level,
                    "text": text,
                    "line_number": i + 1
                })
                continue
            
            # Parse code blocks
            if line.startswith('```'):
                # Start or end of code block
                continue
            
            # Parse lists
            if re.match(r'^[\-\*\+]\s+.+$', line) or re.match(r'^\d+\.\s+.+$', line):
                structure["lists"].append({
                    "text": line.strip(),
                    "line_number": i + 1
                })
                continue
            
            # Parse links
            link_matches = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            for match in link_matches:
                structure["links"].append({
                    "text": match[0],
                    "url": match[1],
                    "line_number": i + 1
                })
            
            # Parse images
            image_matches = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            for match in image_matches:
                structure["images"].append({
                    "alt_text": match[0],
                    "url": match[1],
                    "line_number": i + 1
                })
            
            # Parse blockquotes
            if line.startswith('>'):
                structure["blockquotes"].append({
                    "text": line[1:].strip(),
                    "line_number": i + 1
                })
                continue
            
            # Parse tables (simplified)
            if '|' in line and not line.startswith('|') and not line.endswith('|'):
                # Skip table separator lines
                if re.match(r'^[\|\-\s]+$', line):
                    continue
                structure["tables"].append({
                    "row": line.strip(),
                    "line_number": i + 1
                })
                continue
            
            # Parse paragraphs
            if line.strip():
                current_paragraph += line + " "
            elif current_paragraph:
                structure["paragraphs"].append({
                    "text": current_paragraph.strip(),
                    "line_number_start": i - len(current_paragraph.split('\n')) + 1,
                    "line_number_end": i
                })
                current_paragraph = ""
        
        # Add the last paragraph if exists
        if current_paragraph:
            structure["paragraphs"].append({
                "text": current_paragraph.strip(),
                "line_number_start": len(lines) - len(current_paragraph.split('\n')) + 1,
                "line_number_end": len(lines)
            })
        
        if include_metadata:
            structure["metadata"] = {
                "total_lines": len(lines),
                "total_headings": len(structure["headings"]),
                "total_paragraphs": len(structure["paragraphs"]),
                "total_code_blocks": len(structure["code_blocks"]),
                "total_links": len(structure["links"]),
                "total_images": len(structure["images"])
            }
        
        return json.dumps(structure, indent=2, ensure_ascii=False)
    
    except Exception as e:
        return f"Error parsing markdown: {str(e)}"

def convert_markdown_to_html(markdown_text: str, html_output_path: Optional[str] = None, include_css: bool = True) -> str:
    '''
    Convert markdown text to HTML.
    
    :param markdown_text: Markdown text to convert
    :type markdown_text: str
    :param html_output_path: Path to save HTML output file (optional)
    :type html_output_path: str
    :param include_css: Whether to include CSS styling in HTML output
    :type include_css: bool
    :return: HTML content or success message
    :rtype: str
    '''
    try:
        # Simple markdown to HTML conversion
        html_parts = []
        
        if include_css:
            css = """
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1, h2, h3, h4, h5, h6 { margin-top: 1.5em; margin-bottom: 0.5em; }
                h1 { border-bottom: 2px solid #eee; padding-bottom: 0.3em; }
                h2 { border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
                p { margin: 1em 0; }
                pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
                code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
                blockquote { border-left: 4px solid #ddd; padding-left: 16px; margin-left: 0; color: #666; }
                ul, ol { padding-left: 2em; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f6f8fa; }
                a { color: #0366d6; text-decoration: none; }
                a:hover { text-decoration: underline; }
                img { max-width: 100%; height: auto; }
            </style>
            """
            html_parts.append(css)
        
        lines = markdown_text.split('\n')
        in_code_block = False
        code_block_content = []
        code_block_lang = ""
        
        for line in lines:
            # Handle code blocks
            if line.startswith('```'):
                if not in_code_block:
                    # Start of code block
                    in_code_block = True
                    code_block_lang = line[3:].strip()
                    code_block_content = []
                else:
                    # End of code block
                    in_code_block = False
                    code_html = f'<pre><code class="language-{code_block_lang}">'
                    code_html += '\n'.join(code_block_content)
                    code_html += '</code></pre>'
                    html_parts.append(code_html)
                continue
            
            if in_code_block:
                code_block_content.append(line)
                continue
            
            # Convert headings
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                html_parts.append(f'<h{level}>{text}</h{level}>')
                continue
            
            # Use helper function for basic conversions
            line = _convert_line_to_html(line)
            
            # Convert blockquotes
            if line.startswith('>'):
                quote_text = line[1:].strip()
                html_parts.append(f'<blockquote>{quote_text}</blockquote>')
                continue
            
            # Convert lists
            if re.match(r'^[\-\*\+]\s+.+$', line):
                list_item = line[2:].strip()
                html_parts.append(f'<li>{list_item}</li>')
                continue
            
            if re.match(r'^\d+\.\s+.+$', line):
                list_item = re.sub(r'^\d+\.\s+', '', line)
                html_parts.append(f'<li>{list_item}</li>')
                continue
            
            # Handle empty lines (paragraph breaks)
            if not line.strip():
                html_parts.append('')
                continue
            
            # Regular paragraph
            html_parts.append(f'<p>{line}</p>')
        
        html_content = '\n'.join(html_parts)
        
        # Wrap in HTML document structure
        full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Markdown to HTML Conversion</title>
</head>
<body>
{html_content}
</body>
</html>'''
        
        # Save to file if output path provided
        if html_output_path:
            try:
                with open(html_output_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                return f"Successfully converted markdown to HTML and saved to {html_output_path}"
            except Exception as e:
                return f"Error saving HTML to file: {str(e)}\n\nHTML content:\n{full_html}"
        
        return full_html
    
    except Exception as e:
        return f"Error converting markdown to HTML: {str(e)}"

__all__ = ["parse_markdown", "convert_markdown_to_html"]