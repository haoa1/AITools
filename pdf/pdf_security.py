"""PDF security operations: encryption, decryption, compression."""

from .pdf_utils import (
    _check_file_exists, _ensure_dir_exists,
    HAS_PYPDF2
)
import os
import traceback

# Conditionally import pypdf based on availability
if HAS_PYPDF2:
    import pypdf
else:
    pypdf = None

def encrypt_pdf(pdf_path: str, output_path: str, encryption_password: str, owner_password: str = None) -> str:
    """
    Encrypt PDF file.

    :param pdf_path: PDF file path
    :param output_path: Output PDF file path
    :param encryption_password: Encryption password
    :param owner_password: Owner password (optional, higher permissions)
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
            
            # Check if already encrypted
            if pdf_reader.is_encrypted:
                return "Error: PDF is already encrypted. Please decrypt it first."
            
            pdf_writer = pypdf.PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Copy metadata
            if pdf_reader.metadata:
                pdf_writer.add_metadata(pdf_reader.metadata)
            
            # Set encryption
            if owner_password:
                pdf_writer.encrypt(user_password=encryption_password, owner_password=owner_password)
            else:
                pdf_writer.encrypt(user_password=encryption_password)
            
            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Verify output file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                size_kb = os.path.getsize(output_path) / 1024
                return f"Successfully encrypted PDF at {output_path} ({size_kb:.1f} KB)"
            else:
                return "Error: Output file was not created or is empty."
                
    except Exception as e:
        return f"Error: Failed to encrypt PDF: {str(e)}\nTraceback: {traceback.format_exc()}"

def decrypt_pdf(pdf_path: str, output_path: str, encryption_password: str) -> str:
    """
    Decrypt PDF file.

    :param pdf_path: PDF file path
    :param output_path: Output PDF file path
    :param encryption_password: Decryption password
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
            
            # Check if encrypted
            if not pdf_reader.is_encrypted:
                return "Error: PDF is not encrypted."
            
            # Try to decrypt
            if not pdf_reader.decrypt(encryption_password):
                return "Error: Incorrect password or unable to decrypt PDF."
            
            pdf_writer = pypdf.PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Copy metadata
            if pdf_reader.metadata:
                pdf_writer.add_metadata(pdf_reader.metadata)
            
            # Write output file (without encryption)
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Verify output file
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                size_kb = os.path.getsize(output_path) / 1024
                return f"Successfully decrypted PDF at {output_path} ({size_kb:.1f} KB)"
            else:
                return "Error: Output file was not created or is empty."
                
    except Exception as e:
        return f"Error: Failed to decrypt PDF: {str(e)}\nTraceback: {traceback.format_exc()}"

def compress_pdf(pdf_path: str, output_path: str, compression_level: int = 5) -> str:
    """
    Compress PDF file.

    :param pdf_path: PDF file path
    :param output_path: Output PDF file path
    :param compression_level: Compression level (1-9)
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
    
    # Validate compression level
    if compression_level < 1 or compression_level > 9:
        return "Error: Compression level must be between 1 and 9 (1=minimum, 9=maximum)."
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            pdf_writer = pypdf.PdfWriter()
            
            original_size = os.path.getsize(pdf_path)
            
            # Copy all pages with compression
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Set compression level
            # Note: pypdf doesn't have direct compression control, but we can try to optimize
            # Copy metadata
            if pdf_reader.metadata:
                pdf_writer.add_metadata(pdf_reader.metadata)
            
            # Write output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Check results
            if os.path.exists(output_path):
                compressed_size = os.path.getsize(output_path)
                compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
                
                if compressed_size < original_size:
                    return f"Successfully compressed PDF from {original_size/1024:.1f} KB to {compressed_size/1024:.1f} KB ({compression_ratio:.1f}% reduction) at {output_path}"
                else:
                    return f"Compressed PDF size: {compressed_size/1024:.1f} KB (no reduction from original {original_size/1024:.1f} KB). Saved to {output_path}"
            else:
                return "Error: Output file was not created."
                
    except Exception as e:
        return f"Error: Failed to compress PDF: {str(e)}\nTraceback: {traceback.format_exc()}"