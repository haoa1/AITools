"""Basic PDF operations: text extraction, metadata, merge, split."""

from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists, _parse_page_range,
    _contains_chinese, _setup_chinese_font,
    HAS_PYPDF2, HAS_PDF2IMAGE, HAS_PDFPLUMBER, HAS_REPORTLAB, HAS_PIL
)
import os
import json

# Conditionally import pypdf based on availability
if HAS_PYPDF2:
    import pypdf
else:
    pypdf = None

def extract_text_from_pdf(pdf_path: str, password: str = None) -> str:
    """
    Extract text content from a PDF file.

    :param pdf_path: Path to the PDF file
    :param password: Optional password
    :return: Extracted text or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Check if encrypted
            if pdf_reader.is_encrypted:
                if password:
                    success = pdf_reader.decrypt(password)
                    if not success:
                        return "Error: Incorrect password or unable to decrypt PDF."
                else:
                    return "Error: PDF is encrypted. Please provide a password."
            
            # Extract text from each page
            text_parts = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
            
            if not text_parts:
                return "Warning: No text content found in PDF. The PDF may be scanned or image-based."
            
            return "\n\n".join(text_parts)
            
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when extracting text: {str(e)}"

def get_pdf_metadata(pdf_path: str, password: str = None) -> str:
    """
    Get metadata from a PDF file.

    :param pdf_path: Path to the PDF file
    :param password: Optional password
    :return: Metadata information or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Check if encrypted
            if pdf_reader.is_encrypted:
                if password:
                    success = pdf_reader.decrypt(password)
                    if not success:
                        return "Error: Incorrect password or unable to decrypt PDF."
                else:
                    return "Error: PDF is encrypted. Please provide a password."
            
            metadata = {
                "page_count": len(pdf_reader.pages),
                "is_encrypted": pdf_reader.is_encrypted,
                "metadata": pdf_reader.metadata or {},
                "file_size_bytes": os.path.getsize(pdf_path)
            }
            
            # Format output
            result = []
            result.append(f"PDF Metadata for: {os.path.basename(pdf_path)}")
            result.append(f"File size: {metadata['file_size_bytes']} bytes ({metadata['file_size_bytes']/1024:.2f} KB)")
            result.append(f"Page count: {metadata['page_count']}")
            result.append(f"Is encrypted: {metadata['is_encrypted']}")
            
            if metadata['metadata']:
                result.append("\nDocument metadata:")
                for key, value in metadata['metadata'].items():
                    if key.startswith('/'):
                        key = key[1:]
                    result.append(f"  {key}: {value}")
            
            return "\n".join(result)
            
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when reading PDF metadata: {str(e)}"

def merge_pdfs(pdf_paths: list, output_path: str) -> str:
    """
    Merge multiple PDF files into a single PDF file.

    :param pdf_paths: List of PDF file paths to merge
    :param output_path: Output file path
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check all input files
    for pdf_path in pdf_paths:
        ok, msg = _check_file_exists(pdf_path)
        if not ok:
            return msg
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        pdf_writer = pypdf.PdfWriter()
        
        for pdf_path in pdf_paths:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Successfully merged {len(pdf_paths)} PDF files into {output_path}"
        
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when merging PDFs: {str(e)}"

def split_pdf(pdf_path: str, split_type: str, output_path: str, 
              page_range: str = None, pages: list = None) -> str:
    """
    Split a PDF file by page range or extract specific pages.

    :param pdf_path: Path to the PDF file
    :param split_type: 'range' for page range, 'pages' for specific pages
    :param output_path: Output file path
    :param page_range: Page range string (e.g., '1-5')
    :param pages: List of page numbers to extract
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check input file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Determine pages to extract
            if split_type == 'range':
                if not page_range:
                    return "Error: page_range is required when split_type='range'"
                
                pages_to_extract, error_msg = _parse_page_range(page_range, total_pages)
                if error_msg:
                    return error_msg
                    
            elif split_type == 'pages':
                if not pages:
                    return "Error: pages list is required when split_type='pages'"
                
                pages_to_extract = []
                for page_num in pages:
                    if page_num < 1 or page_num > total_pages:
                        return f"Error: Invalid page number {page_num}. Must be between 1 and {total_pages}."
                    pages_to_extract.append(page_num)
                    
            else:
                return f"Error: Invalid split_type '{split_type}'. Must be 'range' or 'pages'."
            
            # Extract pages
            pdf_writer = pypdf.PdfWriter()
            for page_num in pages_to_extract:
                pdf_writer.add_page(pdf_reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully extracted {len(pages_to_extract)} pages from {pdf_path} to {output_path}"
            
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when splitting PDF: {str(e)}"