"""PDF utility functions and shared constants."""

import os
import json
import base64
import traceback

# Attempt to import PDF processing libraries
try:
    import pypdf
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from reportlab.lib.pagesizes import letter, A4, legal, landscape
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Helper functions
def _check_file_exists(file_path):
    """Check if file exists and is readable"""
    file_path = os.path.normpath(file_path)
    if not os.path.exists(file_path):
        return False, f"Error: File does not exist: {file_path}"
    if not os.path.isfile(file_path):
        return False, f"Error: Path is not a file: {file_path}"
    if not os.access(file_path, os.R_OK):
        return False, f"Error: No read permission for file: {file_path}"
    return True, ""

def _ensure_dir_exists(file_path):
    """Ensure output directory exists"""
    dir_path = os.path.dirname(os.path.normpath(file_path))
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            return False, f"Error: Failed to create directory {dir_path}: {str(e)}"
    return True, ""

def _parse_page_range(page_range_str, total_pages):
    """Parse page range string, e.g., '1-5' or 'all'"""
    if page_range_str.lower() == 'all':
        return list(range(1, total_pages + 1)), ""
    
    try:
        if '-' in page_range_str:
            start_str, end_str = page_range_str.split('-')
            start = int(start_str.strip())
            end = int(end_str.strip())
            if start < 1 or end > total_pages or start > end:
                return None, f"Error: Invalid page range {page_range_str}. Must be between 1 and {total_pages}, start <= end."
            return list(range(start, end + 1)), ""
        else:
            # Single page
            page = int(page_range_str.strip())
            if page < 1 or page > total_pages:
                return None, f"Error: Invalid page {page}. Must be between 1 and {total_pages}."
            return [page], ""
    except ValueError:
        return None, f"Error: Invalid page range format '{page_range_str}'. Use 'start-end' or 'all'."

def _contains_chinese(text):
    """Check if text contains Chinese characters"""
    import re
    # Regular expression for matching Chinese characters
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))

def _setup_chinese_font():
    """Setup Chinese font support"""
    try:
        # Attempt to register STSong-Light font (ReportLab built-in Chinese font)
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        return 'STSong-Light'
    except Exception:
        # If failed, try other Chinese fonts
        try:
            pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
            return 'SimHei'
        except Exception:
            try:
                pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'msyh.ttf'))
                return 'MicrosoftYaHei'
            except Exception:
                # Fallback to default font
                return 'Helvetica'