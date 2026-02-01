"""PDF form and table operations: fillable fields and table extraction."""

from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists,
    HAS_PYPDF2, HAS_PDFPLUMBER
)
import os
import json

# Conditionally import libraries based on availability
if HAS_PYPDF2:
    import pypdf
else:
    pypdf = None

if HAS_PDFPLUMBER:
    import pdfplumber
else:
    pdfplumber = None

def check_fillable_fields(pdf_path: str) -> str:
    """
    Check if a PDF has fillable form fields.

    :param pdf_path: Path to the PDF file
    :return: Check result or error message
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
            fields = pdf_reader.get_fields()
            
            if fields:
                field_count = len(fields)
                return f"This PDF has {field_count} fillable form field(s)."
            else:
                return "This PDF does not have fillable form fields; you will need to visually determine where to enter data."
                
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when checking fillable fields: {str(e)}"

def extract_form_field_info(pdf_path: str, output_path: str) -> str:
    """
    Extract information about fillable form fields from a PDF and save as JSON file.

    :param pdf_path: Path to the PDF file
    :param output_path: Path to output JSON file
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check file
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
            fields = pdf_reader.get_fields()
            
            if not fields:
                return "Error: No fillable form fields found in PDF."
            
            # Convert field information to serializable format
            field_list = []
            for field_id, field in fields.items():
                field_info = {
                    "field_id": field_id,
                    "field_type": str(field.get('/FT', 'Unknown')),
                    "field_value": str(field.get('/V', '')),
                    "field_default_value": str(field.get('/DV', '')),
                    "field_flags": int(field.get('/Ff', 0))
                }
                field_list.append(field_info)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(field_list, f, indent=2, ensure_ascii=False)
            
            return f"Successfully extracted {len(field_list)} form fields to {output_path}"
            
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when extracting form field info: {str(e)}"

def fill_fillable_fields(pdf_path: str, json_data: str, output_path: str) -> str:
    """
    Fill fillable form fields in a PDF using JSON data.

    :param pdf_path: Path to the PDF file
    :param json_data: Field values data in JSON format
    :param output_path: Path to output PDF file
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        # Parse JSON data
        field_data = json.loads(json_data)
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_writer = pypdf.PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Update form fields
            if isinstance(field_data, dict):
                # If JSON is object with field_id: value
                for field_id, value in field_data.items():
                    try:
                        pdf_writer.update_page_form_field_values(pdf_writer.pages[-1], {field_id: value})
                    except Exception as e:
                        return f"Error updating field '{field_id}': {str(e)}"
            elif isinstance(field_data, list):
                # If JSON is array of objects with field_id and value
                for field_item in field_data:
                    if isinstance(field_item, dict) and 'field_id' in field_item:
                        field_id = field_item['field_id']
                        value = field_item.get('value', '')
                        try:
                            pdf_writer.update_page_form_field_values(pdf_writer.pages[-1], {field_id: value})
                        except Exception as e:
                            return f"Error updating field '{field_id}': {str(e)}"
            else:
                return "Error: JSON data must be either a dictionary or a list of field objects."
            
            # Write output PDF
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully filled form fields and saved to {output_path}"
            
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON data. {str(e)}"
    except pypdf.errors.PdfReadError as e:
        return f"Error: Could not read PDF file. It may be corrupted or not a valid PDF. Details: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when filling form fields: {str(e)}"

def extract_tables_from_pdf(pdf_path: str, pages: list) -> str:
    """
    Extract tables from a PDF file using pdfplumber.

    :param pdf_path: Path to the PDF file
    :param pages: List of page numbers to extract (1-indexed)
    :return: Extracted tables or error message
    """
    if not HAS_PDFPLUMBER or pdfplumber is None:
        return "Error: pdfplumber library is not installed. Please install it using 'pip install pdfplumber'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    try:
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in pages:
                if page_num < 1 or page_num > len(pdf.pages):
                    return f"Error: Page {page_num} is out of range (1-{len(pdf.pages)})."
                
                page = pdf.pages[page_num - 1]
                tables = page.extract_tables()
                
                for table_idx, table in enumerate(tables):
                    table_data = {
                        "page": page_num,
                        "table_index": table_idx,
                        "rows": []
                    }
                    
                    for row in table:
                        # Clean up cell values
                        cleaned_row = []
                        for cell in row:
                            if cell is None:
                                cleaned_row.append("")
                            else:
                                cleaned_row.append(str(cell).strip())
                        table_data["rows"].append(cleaned_row)
                    
                    all_tables.append(table_data)
        
        if not all_tables:
            return "No tables found in the specified pages."
        
        # Convert to JSON string for return
        return json.dumps(all_tables, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"Error: Failed to extract tables from PDF: {str(e)}"