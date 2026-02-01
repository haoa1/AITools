"""PDF enhancement operations: watermark, page numbers, annotations."""

from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists, _contains_chinese, _setup_chinese_font,
    HAS_PYPDF2, HAS_REPORTLAB
)
import os
import json

# Conditionally import libraries based on availability
if HAS_PYPDF2:
    import pypdf
else:
    pypdf = None

if HAS_REPORTLAB:
    from reportlab.lib.pagesizes import letter, A4, legal, landscape
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from io import BytesIO
else:
    # Create dummy objects for type checking
    letter = A4 = legal = landscape = None
    inch = cm = mm = None
    getSampleStyleSheet = ParagraphStyle = None
    TA_LEFT = TA_CENTER = TA_RIGHT = TA_JUSTIFY = None
    SimpleDocTemplate = Paragraph = Spacer = Image = Table = TableStyle = None
    colors = None
    pdfmetrics = UnicodeCIDFont = TTFont = None
    canvas = None
    BytesIO = None

def create_pdf(output_path: str, content: str, page_size: str = "A4",
               title: str = "", author: str = "", font_name: str = "Helvetica",
               font_size: int = 12, line_spacing: float = 1.2, 
               margin: float = 2.0, header: str = "", footer: str = "") -> str:
    """
    Create a new PDF document with text content and enhanced styling options.

    :param output_path: Output PDF file path
    :param content: Text content (supports Markdown-like formatting)
    :param page_size: Page size (A4, Letter, etc.)
    :param title: Title
    :param author: Author
    :param font_name: Font name
    :param font_size: Font size
    :param line_spacing: Line spacing
    :param margin: Page margin (cm)
    :param header: Header text
    :param footer: Footer text
    :return: Success message or error message
    """
    if not HAS_REPORTLAB:
        return "Error: ReportLab library is not installed. Please install it using 'pip install reportlab'."
    
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        # Parse page size
        from .pdf_utils import _parse_page_size
        page_size_obj, error_msg = _parse_page_size(page_size)
        if error_msg:
            return error_msg
        
        # Create document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size_obj,
            leftMargin=margin*cm,
            rightMargin=margin*cm,
            topMargin=margin*cm,
            bottomMargin=margin*cm,
            title=title,
            author=author
        )
        
        # Setup styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            spaceBefore=12,
            spaceAfter=6
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=10,
            spaceAfter=4
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=font_size,
            leading=font_size * line_spacing,
            spaceBefore=6,
            spaceAfter=6
        )
        
        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Code'],
            fontSize=font_size - 2,
            fontName='Courier',
            leading=font_size * line_spacing,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=20,
            backColor=colors.lightgrey
        )
        
        # Prepare content
        story = []
        
        # Add title if provided
        if title:
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
        
        # Parse content with simple Markdown-like formatting
        lines = content.split('\n')
        in_code_block = False
        code_lines = []
        
        for line in lines:
            line = line.rstrip()
            
            # Check for code block
            if line.strip().startswith('```'):
                if in_code_block:
                    # End code block
                    in_code_block = False
                    if code_lines:
                        code_text = '<br/>'.join(code_lines)
                        story.append(Paragraph(code_text, code_style))
                        story.append(Spacer(1, 12))
                        code_lines = []
                else:
                    # Start code block
                    in_code_block = True
                continue
            
            if in_code_block:
                # Add to code block
                code_lines.append(line)
                continue
            
            # Check for headings
            if line.startswith('# '):
                story.append(Paragraph(line[2:], heading1_style))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], heading2_style))
            elif line.startswith('### '):
                story.append(Paragraph(line[4:], heading2_style))
            elif line.startswith('> '):
                # Blockquote
                quote_style = ParagraphStyle(
                    'CustomQuote',
                    parent=normal_style,
                    leftIndent=20,
                    borderColor=colors.grey,
                    borderWidth=1,
                    borderPadding=10,
                    backColor=colors.whitesmoke
                )
                story.append(Paragraph(line[2:], quote_style))
            elif line.startswith('- ') or line.startswith('* '):
                # List item
                story.append(Paragraph(f"• {line[2:]}", normal_style))
            elif line.strip() == '':
                # Empty line
                story.append(Spacer(1, 12))
            else:
                # Normal text
                story.append(Paragraph(line, normal_style))
        
        # Build PDF
        doc.build(story)
        
        return f"Successfully created PDF: {output_path}"
        
    except Exception as e:
        return f"Error: Failed to create PDF: {str(e)}"

def add_watermark_to_pdf(pdf_path: str, output_path: str, watermark_text: str,
                        opacity: float = 0.3, angle: int = 45, font_size: int = 60) -> str:
    """
    Add watermark to PDF pages.
    
    :param pdf_path: Input PDF file path
    :param output_path: Output PDF file path
    :param watermark_text: Watermark text
    :param opacity: Opacity
    :param angle: Rotation angle
    :param font_size: Font size
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    if not HAS_REPORTLAB or canvas is None or BytesIO is None:
        return "Error: ReportLab library is not installed. Please install it using 'pip install reportlab'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        # Open original PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_writer = pypdf.PdfWriter()
            
            # Get page dimensions
            page = pdf_reader.pages[0]
            mediabox = page.mediabox
            width = float(mediabox.width)
            height = float(mediabox.height)
            
            # Create watermark for each page
            for page_num in range(len(pdf_reader.pages)):
                # Create watermark PDF
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(width, height))
                
                # Set transparency
                can.setFillAlpha(opacity)
                
                # Calculate watermark position and angle
                can.translate(width/2, height/2)
                can.rotate(angle)
                can.translate(-width/2, -height/2)
                
                # Set font and color
                can.setFont("Helvetica", font_size)
                can.setFillColorRGB(0.7, 0.7, 0.7)  # Light gray
                
                # Add watermark at page center
                text_width = can.stringWidth(watermark_text, "Helvetica", font_size)
                text_height = font_size
                
                # Calculate grid for repeated watermark
                x_spacing = text_width * 1.5
                y_spacing = text_height * 3
                
                # Repeat watermark across entire page
                for y in range(-int(height), int(height*2), int(y_spacing)):
                    for x in range(-int(width), int(width*2), int(x_spacing)):
                        can.drawString(x, y, watermark_text)
                
                can.save()
                
                # Move pointer to start position
                packet.seek(0)
                
                # Create watermark PDF
                watermark_pdf = pypdf.PdfReader(packet)
                watermark_page = watermark_pdf.pages[0]
                
                # Merge watermark with original page
                original_page = pdf_reader.pages[page_num]
                original_page.merge_page(watermark_page)
                
                # Add to writer
                pdf_writer.add_page(original_page)
            
            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully added watermark '{watermark_text}' to PDF and saved to {output_path}"
            
    except Exception as e:
        return f"Error: Failed to add watermark to PDF: {str(e)}"

def add_page_numbers_to_pdf(pdf_path: str, output_path: str,
                           position: str = "bottom-center",
                           format_str: str = "Page {page} of {total}") -> str:
    """
    Add page numbers to PDF.
    
    :param pdf_path: Input PDF file path
    :param output_path: Output PDF file path
    :param position: Position for page numbers
    :param format_str: Format string with {page} and {total} placeholders
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    if not HAS_REPORTLAB or canvas is None or BytesIO is None:
        return "Error: ReportLab library is not installed. Please install it using 'pip install reportlab'."
    
    # Check file
    ok, msg = _check_file_exists(pdf_path)
    if not ok:
        return msg
    
    # Ensure output directory exists
    ok, msg = _ensure_dir_exists(output_path)
    if not ok:
        return msg
    
    try:
        # Open original PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_writer = pypdf.PdfWriter()
            
            total_pages = len(pdf_reader.pages)
            
            # Create page numbers for each page
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                mediabox = page.mediabox
                width = float(mediabox.width)
                height = float(mediabox.height)
                
                # Create page number overlay
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(width, height))
                
                # Format page number text
                page_text = format_str.replace("{page}", str(page_num + 1)).replace("{total}", str(total_pages))
                
                # Calculate position
                if position == "bottom-center":
                    x = width / 2
                    y = 30
                    text_align = "center"
                elif position == "bottom-left":
                    x = 30
                    y = 30
                    text_align = "left"
                elif position == "bottom-right":
                    x = width - 30
                    y = 30
                    text_align = "right"
                elif position == "top-center":
                    x = width / 2
                    y = height - 30
                    text_align = "center"
                elif position == "top-left":
                    x = 30
                    y = height - 30
                    text_align = "left"
                elif position == "top-right":
                    x = width - 30
                    y = height - 30
                    text_align = "right"
                else:
                    return f"Error: Invalid position '{position}'. Must be one of: bottom-center, bottom-left, bottom-right, top-center, top-left, top-right."
                
                # Draw page number
                can.setFont("Helvetica", 10)
                can.setFillColorRGB(0.2, 0.2, 0.2)  # Dark gray
                
                if text_align == "center":
                    can.drawCentredString(x, y, page_text)
                elif text_align == "left":
                    can.drawString(x, y, page_text)
                elif text_align == "right":
                    text_width = can.stringWidth(page_text, "Helvetica", 10)
                    can.drawString(x - text_width, y, page_text)
                
                can.save()
                
                # Move pointer to start position
                packet.seek(0)
                
                # Create overlay PDF
                overlay_pdf = pypdf.PdfReader(packet)
                overlay_page = overlay_pdf.pages[0]
                
                # Merge overlay with original page
                page.merge_page(overlay_page)
                
                # Add to writer
                pdf_writer.add_page(page)
            
            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully added page numbers to PDF and saved to {output_path}"
            
    except Exception as e:
        return f"Error: Failed to add page numbers to PDF: {str(e)}"

def fill_pdf_with_annotations(pdf_path: str, json_data: str, output_path: str) -> str:
    """
    Fill non-fillable PDF form using annotations (bounding boxes).
    
    :param pdf_path: Input PDF file path
    :param json_data: JSON data with field annotations
    :param output_path: Output PDF file path
    :return: Success message or error message
    """
    if not HAS_PYPDF2 or pypdf is None:
        return "Error: pypdf library is not installed. Please install it using 'pip install pypdf'."
    
    if not HAS_REPORTLAB or canvas is None or BytesIO is None:
        return "Error: ReportLab library is not installed. Please install it using 'pip install reportlab'."
    
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
        annotations = json.loads(json_data)
        
        # Open original PDF
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_writer = pypdf.PdfWriter()
            
            # Process each annotation
            for annotation in annotations:
                if not all(key in annotation for key in ['page', 'x', 'y', 'width', 'height', 'text']):
                    return "Error: Annotation must include page, x, y, width, height, and text fields."
                
                page_num = annotation['page'] - 1  # Convert to 0-indexed
                if page_num < 0 or page_num >= len(pdf_reader.pages):
                    return f"Error: Page {page_num + 1} is out of range (1-{len(pdf_reader.pages)})."
                
                # Get page dimensions
                page = pdf_reader.pages[page_num]
                mediabox = page.mediabox
                page_width = float(mediabox.width)
                page_height = float(mediabox.height)
                
                # Create annotation overlay
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(page_width, page_height))
                
                # Convert coordinates (assuming JSON uses points)
                x = annotation['x']
                y = page_height - annotation['y'] - annotation['height']  # Convert from top-left to bottom-left origin
                width = annotation['width']
                height = annotation['height']
                text = annotation['text']
                
                # Draw text box
                can.setFont("Helvetica", 10)
                can.setFillColorRGB(1, 1, 1)  # White background
                can.rect(x, y, width, height, fill=1)
                
                can.setFillColorRGB(0, 0, 0)  # Black text
                can.drawString(x + 2, y + height - 12, str(text)[:100])  # Truncate long text
                
                can.save()
                
                # Move pointer to start position
                packet.seek(0)
                
                # Create overlay PDF
                overlay_pdf = pypdf.PdfReader(packet)
                overlay_page = overlay_pdf.pages[0]
                
                # Merge overlay with page
                page.merge_page(overlay_page)
            
            # Copy all pages to writer
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return f"Successfully added annotations to PDF and saved to {output_path}"
            
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON data. {str(e)}"
    except Exception as e:
        return f"Error: Failed to add annotations to PDF: {str(e)}"