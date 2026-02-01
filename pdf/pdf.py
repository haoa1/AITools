from base import function_ai, parameters_func, property_param
import os
import json
import base64
import traceback

# Import PDF functions from submodules
from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists, _parse_page_range,
    _contains_chinese, _setup_chinese_font,
    HAS_PYPDF2, HAS_PDF2IMAGE, HAS_PDFPLUMBER, HAS_REPORTLAB, HAS_PIL
)

# Import actual implementations from submodules
from .pdf_basic import (
    extract_text_from_pdf,
    get_pdf_metadata,
    merge_pdfs,
    split_pdf
)

from .pdf_images import (
    convert_pdf_to_images,
    create_pdf_from_images,
    extract_images_from_pdf
)

from .pdf_forms import (
    check_fillable_fields,
    extract_form_field_info,
    fill_fillable_fields,
    extract_tables_from_pdf
)

from .pdf_enhance import (
    create_pdf,
    add_watermark_to_pdf,
    add_page_numbers_to_pdf,
    fill_pdf_with_annotations
)

from .pdf_security import (
    encrypt_pdf,
    decrypt_pdf,
    compress_pdf
)

# ============= Property Definitions =============

__PDF_FILE_PATH_PROPERTY__ = property_param(
    name="pdf_path",
    description="The path to the PDF file.",
    t="string",
    required=True
)

__PDF_OUTPUT_PATH_PROPERTY__ = property_param(
    name="output_path",
    description="The path where the output file should be saved.",
    t="string",
    required=True
)

__PDF_PAGE_RANGE_PROPERTY__ = property_param(
    name="page_range",
    description="Page range in format 'start-end' (1-indexed, inclusive). Example: '1-5' for pages 1 to 5. Use 'all' for all pages.",
    t="string",
    required=True
)

__PDF_PAGES_PROPERTY__ = property_param(
    name="pages",
    description="List of page numbers to extract (1-indexed). Example: [1, 3, 5]",
    t="array",
    required=True
)

__PDF_MERGE_LIST_PROPERTY__ = property_param(
    name="pdf_paths",
    description="List of PDF file paths to merge, in order.",
    t="array",
    required=True
)

__PDF_PASSWORD_PROPERTY__ = property_param(
    name="password",
    description="Password for encrypted PDF (optional).",
    t="string",
    required=False
)

__PDF_OUTPUT_DIR_PROPERTY__ = property_param(
    name="output_dir",
    description="Directory to save output files.",
    t="string",
    required=True
)

__PDF_IMAGE_PATHS_PROPERTY__ = property_param(
    name="image_paths",
    description="List of image file paths.",
    t="array",
    required=True
)

__PDF_PAGE_SIZE_PROPERTY__ = property_param(
    name="page_size",
    description="Page size: 'A4' (default), 'Letter', 'Legal', 'A4_Landscape', 'Letter_Landscape', 'Legal_Landscape', or 'WIDTHxHEIGHT' (e.g., '210x297' for A4 in mm).",
    t="string",
    required=False
)

__PDF_DPI_PROPERTY__ = property_param(
    name="dpi",
    description="DPI for image quality (default: 200).",
    t="integer",
    required=False
)

__PDF_SPLIT_TYPE_PROPERTY__ = property_param(
    name="split_type",
    description="Type of split: 'range' for page range, 'pages' for specific pages.",
    t="string",
    required=True
)

__PDF_JSON_DATA_PROPERTY__ = property_param(
    name="json_data",
    description="JSON data for field values or annotations.",
    t="string",
    required=True
)

__PDF_WATERMARK_TEXT_PROPERTY__ = property_param(
    name="watermark_text",
    description="Watermark text.",
    t="string",
    required=True
)

__PDF_OPACITY_PROPERTY__ = property_param(
    name="opacity",
    description="Opacity of watermark (0.0 to 1.0, default: 0.3).",
    t="number",
    required=False
)

__PDF_ANGLE_PROPERTY__ = property_param(
    name="angle",
    description="Rotation angle in degrees (default: 45).",
    t="integer",
    required=False
)

__PDF_FONT_SIZE_PROPERTY__ = property_param(
    name="font_size",
    description="Font size for watermark (default: 60).",
    t="integer",
    required=False
)

__PDF_POSITION_PROPERTY__ = property_param(
    name="position",
    description="Position: 'bottom-center' (default), 'bottom-left', 'bottom-right', 'top-center', 'top-left', 'top-right'.",
    t="string",
    required=False
)

__PDF_FORMAT_PROPERTY__ = property_param(
    name="format",
    description="Page number format: 'Page {page} of {total}' (default), or custom format with {page} and {total} placeholders.",
    t="string",
    required=False
)

__PDF_ENCRYPTION_PASSWORD_PROPERTY__ = property_param(
    name="encryption_password",
    description="Password for encrypting or decrypting PDF.",
    t="string",
    required=True
)

__PDF_OWNER_PASSWORD_PROPERTY__ = property_param(
    name="owner_password",
    description="Owner password for PDF encryption (with higher permissions).",
    t="string",
    required=False
)

__PDF_COMPRESSION_LEVEL_PROPERTY__ = property_param(
    name="compression_level",
    description="Compression level for PDF (1-9, where 9 is maximum compression).",
    t="integer",
    required=False
)

# ============= Function Definitions =============

__EXTRACT_TEXT_FUNCTION__ = function_ai(
    name="extract_text_from_pdf",
    description="Extract text content from a PDF file.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_PASSWORD_PROPERTY__
    ])
)

__GET_METADATA_FUNCTION__ = function_ai(
    name="get_pdf_metadata",
    description="Get metadata from a PDF file (page count, author, title, etc.).",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_PASSWORD_PROPERTY__
    ])
)

__MERGE_PDFS_FUNCTION__ = function_ai(
    name="merge_pdfs",
    description="Merge multiple PDF files into a single PDF file.",
    parameters=parameters_func([
        __PDF_MERGE_LIST_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__
    ])
)

__SPLIT_PDF_FUNCTION__ = function_ai(
    name="split_pdf",
    description="Split a PDF file by page range or extract specific pages.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        property_param(name="split_type", description="Type of split: 'range' for page range, 'pages' for specific pages.", t="string", required=True),
        __PDF_OUTPUT_PATH_PROPERTY__,
        property_param(name="page_range", description="Page range in format 'start-end' (required if split_type='range').", t="string", required=False),
        __PDF_PAGES_PROPERTY__
    ])
)

__CONVERT_TO_IMAGES_FUNCTION__ = function_ai(
    name="convert_pdf_to_images",
    description="Convert PDF pages to images (PNG format).",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_DIR_PROPERTY__,
        __PDF_DPI_PROPERTY__,
        __PDF_PAGES_PROPERTY__
    ])
)

__CREATE_PDF_FROM_IMAGES_FUNCTION__ = function_ai(
    name="create_pdf_from_images",
    description="Create a PDF file from a list of image files.",
    parameters=parameters_func([
        __PDF_IMAGE_PATHS_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_PAGE_SIZE_PROPERTY__
    ])
)

__CHECK_FILLABLE_FIELDS_FUNCTION__ = function_ai(
    name="check_fillable_fields",
    description="Check if a PDF has fillable form fields.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__
    ])
)

__EXTRACT_FORM_FIELD_INFO_FUNCTION__ = function_ai(
    name="extract_form_field_info",
    description="Extract information about fillable form fields from a PDF.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__
    ])
)

__FILL_FILLABLE_FIELDS_FUNCTION__ = function_ai(
    name="fill_fillable_fields",
    description="Fill fillable form fields in a PDF using JSON data.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_JSON_DATA_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__
    ])
)

__EXTRACT_TABLES_FUNCTION__ = function_ai(
    name="extract_tables_from_pdf",
    description="Extract tables from a PDF file using pdfplumber.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_PAGES_PROPERTY__
    ])
)

__CREATE_PDF_FUNCTION__ = function_ai(
    name="create_pdf",
    description="Create a new PDF document with text content and enhanced styling options.",
    parameters=parameters_func([
        __PDF_OUTPUT_PATH_PROPERTY__,
        property_param(name="content", description="Text content to add to the PDF. Supports Markdown-like formatting: # for H1, ## for H2, > for quotes, - for lists, ``` for code.", t="string", required=True),
        __PDF_PAGE_SIZE_PROPERTY__,
        property_param(name="title", description="Title of the PDF document.", t="string", required=False),
        property_param(name="author", description="Author of the PDF document.", t="string", required=False),
        property_param(name="font_name", description="Font name: 'Helvetica', 'Times-Roman', 'Courier', or Chinese fonts.", t="string", required=False),
        property_param(name="font_size", description="Font size for body text (default: 12).", t="integer", required=False),
        property_param(name="line_spacing", description="Line spacing multiplier (default: 1.2).", t="number", required=False),
        property_param(name="margin", description="Page margin in centimeters (default: 2.0).", t="number", required=False),
        property_param(name="header", description="Header text for each page.", t="string", required=False),
        property_param(name="footer", description="Footer text for each page.", t="string", required=False)
    ])
)

__ADD_WATERMARK_FUNCTION__ = function_ai(
    name="add_watermark_to_pdf",
    description="Add watermark to PDF pages.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_WATERMARK_TEXT_PROPERTY__,
        __PDF_OPACITY_PROPERTY__,
        __PDF_ANGLE_PROPERTY__,
        __PDF_FONT_SIZE_PROPERTY__
    ])
)

__ADD_PAGE_NUMBERS_FUNCTION__ = function_ai(
    name="add_page_numbers_to_pdf",
    description="Add page numbers to PDF.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_POSITION_PROPERTY__,
        __PDF_FORMAT_PROPERTY__
    ])
)

__ENCRYPT_PDF_FUNCTION__ = function_ai(
    name="encrypt_pdf",
    description="Encrypt a PDF file with password protection.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_ENCRYPTION_PASSWORD_PROPERTY__,
        __PDF_OWNER_PASSWORD_PROPERTY__
    ])
)

__DECRYPT_PDF_FUNCTION__ = function_ai(
    name="decrypt_pdf",
    description="Decrypt a password-protected PDF file.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_ENCRYPTION_PASSWORD_PROPERTY__
    ])
)

__COMPRESS_PDF_FUNCTION__ = function_ai(
    name="compress_pdf",
    description="Compress a PDF file to reduce file size.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__,
        __PDF_COMPRESSION_LEVEL_PROPERTY__
    ])
)

__EXTRACT_IMAGES_FUNCTION__ = function_ai(
    name="extract_images_from_pdf",
    description="Extract images from a PDF file.",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_OUTPUT_DIR_PROPERTY__,
        __PDF_PAGES_PROPERTY__
    ])
)

__FILL_WITH_ANNOTATIONS_FUNCTION__ = function_ai(
    name="fill_pdf_with_annotations",
    description="Fill non-fillable PDF form using annotations (bounding boxes).",
    parameters=parameters_func([
        __PDF_FILE_PATH_PROPERTY__,
        __PDF_JSON_DATA_PROPERTY__,
        __PDF_OUTPUT_PATH_PROPERTY__
    ])
)

# Initialize tool call mapping
try:
    from base import TOOL_CALL_MAP
except ImportError:
    TOOL_CALL_MAP = {}

tools = [
    __EXTRACT_TEXT_FUNCTION__,
    __GET_METADATA_FUNCTION__,
    __MERGE_PDFS_FUNCTION__,
    __SPLIT_PDF_FUNCTION__,
    __CONVERT_TO_IMAGES_FUNCTION__,
    __CREATE_PDF_FROM_IMAGES_FUNCTION__,
    __CHECK_FILLABLE_FIELDS_FUNCTION__,
    __EXTRACT_FORM_FIELD_INFO_FUNCTION__,
    __FILL_FILLABLE_FIELDS_FUNCTION__,
    __EXTRACT_TABLES_FUNCTION__,
    __CREATE_PDF_FUNCTION__,
    __ADD_WATERMARK_FUNCTION__,
    __ADD_PAGE_NUMBERS_FUNCTION__,
    __ENCRYPT_PDF_FUNCTION__,
    __DECRYPT_PDF_FUNCTION__,
    __COMPRESS_PDF_FUNCTION__,
    __EXTRACT_IMAGES_FUNCTION__,
    __FILL_WITH_ANNOTATIONS_FUNCTION__,
]

# ============= Update Tool Call Mapping =============
TOOL_CALL_MAP.update({
    "extract_text_from_pdf": extract_text_from_pdf,
    "get_pdf_metadata": get_pdf_metadata,
    "merge_pdfs": merge_pdfs,
    "split_pdf": split_pdf,
    "convert_pdf_to_images": convert_pdf_to_images,
    "create_pdf_from_images": create_pdf_from_images,
    "check_fillable_fields": check_fillable_fields,
    "extract_form_field_info": extract_form_field_info,
    "fill_fillable_fields": fill_fillable_fields,
    "extract_tables_from_pdf": extract_tables_from_pdf,
    "create_pdf": create_pdf,
    "add_watermark_to_pdf": add_watermark_to_pdf,
    "add_page_numbers_to_pdf": add_page_numbers_to_pdf,
    "encrypt_pdf": encrypt_pdf,
    "decrypt_pdf": decrypt_pdf,
    "compress_pdf": compress_pdf,
    "extract_images_from_pdf": extract_images_from_pdf,
    "fill_pdf_with_annotations": fill_pdf_with_annotations,
})