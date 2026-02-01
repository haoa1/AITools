"""PDF image-related operations: conversion between PDF and images."""

from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists,
    HAS_PDF2IMAGE, HAS_PIL, HAS_PYPDF2, HAS_PDFPLUMBER
)
import os
import traceback

# Conditionally import libraries based on availability
if HAS_PYPDF2:
    import pypdf
else:
    pypdf = None

if HAS_PDF2IMAGE:
    from pdf2image import convert_from_path
else:
    convert_from_path = None

if HAS_PIL:
    from PIL import Image as PILImage
else:
    PILImage = None

def convert_pdf_to_images(pdf_path: str, output_dir: str, 
                         dpi: int = 200, pages: list = None) -> str:
    """
    Convert PDF pages to images.

    :param pdf_path: Path to the PDF file
    :param output_dir: Output directory
    :param dpi: DPI for image quality
    :param pages: List of page numbers to convert (default: all pages)
    :return: Success message or error message
    """
    if not HAS_PDF2IMAGE or convert_from_path is None:
        return "Error: pdf2image library is not installed. Please install it using 'pip install pdf2image'. Also ensure poppler-utils is installed on your system."
    
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Create output directory
    output_dir = os.path.normpath(output_dir)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return f"Error: Failed to create output directory {output_dir}: {str(e)}"
    
    try:
        # Get total page count
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
        
        # Determine pages to convert
        if pages is None:
            pages_to_convert = list(range(1, total_pages + 1))
        else:
            pages_to_convert = []
            for page_num in pages:
                if not isinstance(page_num, int):
                    try:
                        page_num = int(page_num)
                    except ValueError:
                        return f"Error: Invalid page number '{page_num}'. Must be integer."
                if page_num < 1 or page_num > total_pages:
                    return f"Error: Page {page_num} is out of range (1-{total_pages})."
                pages_to_convert.append(page_num)
        
        # Convert pages
        # Note: pdf2image's convert_from_path requires pages parameter to be 1-based list
        images = convert_from_path(pdf_path, dpi=dpi, 
                                  first_page=min(pages_to_convert), 
                                  last_page=max(pages_to_convert))
        
        # Save images
        saved_files = []
        for i, image in enumerate(images):
            actual_page = pages_to_convert[i]
            output_path = os.path.join(output_dir, f"page_{actual_page:03d}.png")
            image.save(output_path, 'PNG')
            saved_files.append(output_path)
        
        return f"Successfully converted {len(saved_files)} pages to PNG images in {output_dir}. Files: {', '.join([os.path.basename(f) for f in saved_files])}"
        
    except Exception as e:
        return f"Error: Failed to convert PDF to images: {str(e)}"

def create_pdf_from_images(image_paths: list, output_path: str, 
                          page_size: str = "A4") -> str:
    """
    Create PDF from image files.

    :param image_paths: List of image file paths
    :param output_path: Output PDF file path
    :param page_size: Page size (A4, Letter, Legal, etc.)
    :return: Success message or error message
    """
    if not HAS_PIL or PILImage is None:
        return "Error: PIL/Pillow library is not installed. Please install it using 'pip install Pillow'."
    
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Check input files
    for img_path in image_paths:
        ok, msg = _check_file_exists(img_path)
        if not ok:
            return f"Error with image file {img_path}: {msg}"
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    # Parse page size
    from .pdf_utils import _parse_page_size
    page_size_obj, error_msg = _parse_page_size(page_size)
    if error_msg:
        return error_msg
    
    try:
        pdf_writer = pypdf.PdfWriter()
        
        for img_path in image_paths:
            # Open image with PIL
            img = PILImage.open(img_path)
            
            # Convert image to PDF page
            # Create a new PDF page with the image
            img_page = pypdf.PageObject.create_blank_page(
                width=page_size_obj[0], 
                height=page_size_obj[1]
            )
            
            # Calculate scaling to fit image within page
            img_width, img_height = img.size
            page_width, page_height = page_size_obj
            
            # Maintain aspect ratio
            width_ratio = page_width / img_width
            height_ratio = page_height / img_height
            scale = min(width_ratio, height_ratio)
            
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center image on page
            x_offset = (page_width - scaled_width) / 2
            y_offset = (page_height - scaled_height) / 2
            
            # Create a temporary PDF for the image
            temp_pdf_path = os.path.join(os.path.dirname(output_path), f"temp_{os.path.basename(img_path)}.pdf")
            img.save(temp_pdf_path, 'PDF', resolution=100.0)
            
            # Merge image PDF into main PDF
            temp_pdf_reader = pypdf.PdfReader(temp_pdf_path)
            img_page.merge_page(temp_pdf_reader.pages[0])
            
            pdf_writer.add_page(img_page)
            
            # Clean up temporary file
            try:
                os.remove(temp_pdf_path)
            except:
                pass
        
        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        return f"Successfully created PDF from {len(image_paths)} images: {output_path}"
        
    except Exception as e:
        return f"Error: Failed to create PDF from images: {str(e)}"

def extract_images_from_pdf(pdf_path: str, output_dir: str, pages: list = None) -> str:
    """
    Extract images from PDF file.

    :param pdf_path: Path to the PDF file
    :param output_dir: Output directory
    :param pages: List of page numbers to extract images from (default: all pages)
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    if not HAS_PIL or PILImage is None:
        return "Error: PIL/Pillow library is not installed. Please install it using 'pip install Pillow'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Create output directory
    output_dir = os.path.normpath(output_dir)
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            return f"Error: Failed to create output directory {output_dir}: {str(e)}"
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            total_pages = len(pdf_reader.pages)
        
        # Determine pages to process
        if pages is None:
            pages_to_process = list(range(1, total_pages + 1))
        else:
            pages_to_process = []
            for page_num in pages:
                if not isinstance(page_num, int):
                    try:
                        page_num = int(page_num)
                    except ValueError:
                        return f"Error: Invalid page number '{page_num}'. Must be integer."
                if page_num < 1 or page_num > total_pages:
                    return f"Error: Page {page_num} is out of range (1-{total_pages})."
                pages_to_process.append(page_num)
        
        extracted_count = 0
        for page_num in pages_to_process:
            page = pdf_reader.pages[page_num - 1]
            
            # Extract images from page
            if '/Resources' in page and '/XObject' in page['/Resources']:
                x_object = page['/Resources']['/XObject'].get_object()
                
                for obj_name in x_object:
                    obj = x_object[obj_name]
                    
                    if obj['/Subtype'] == '/Image':
                        # Extract image data
                        if '/Filter' in obj:
                            filter_name = obj['/Filter']
                            
                            if filter_name == '/FlateDecode':
                                # PNG image
                                image_data = obj.get_data()
                                image_ext = 'png'
                            elif filter_name == '/DCTDecode':
                                # JPEG image
                                image_data = obj.get_data()
                                image_ext = 'jpg'
                            elif filter_name == '/JPXDecode':
                                # JPEG2000 image
                                image_data = obj.get_data()
                                image_ext = 'jp2'
                            else:
                                # Unsupported format
                                continue
                            
                            # Save image
                            output_path = os.path.join(
                                output_dir, 
                                f"page_{page_num:03d}_{obj_name[1:]}.{image_ext}"
                            )
                            
                            with open(output_path, 'wb') as img_file:
                                img_file.write(image_data)
                            
                            extracted_count += 1
        
        if extracted_count == 0:
            return "Warning: No images found in the specified PDF pages."
        
        return f"Successfully extracted {extracted_count} images from PDF to {output_dir}"
        
    except Exception as e:
        return f"Error: Failed to extract images from PDF: {str(e)}"