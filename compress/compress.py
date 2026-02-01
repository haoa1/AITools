from base import function_ai, parameters_func, property_param

import os
import sys
import gzip
import bz2
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional

__COMPRESS_PROPERTY_ONE__ = property_param(
    name="source_path",
    description="Path to the file or directory to compress.",
    t="string",
    required=True
)

__COMPRESS_PROPERTY_TWO__ = property_param(
    name="destination_path",
    description="Path for the compressed output file.",
    t="string"
)

__COMPRESS_PROPERTY_THREE__ = property_param(
    name="compression_type",
    description="Type of compression: gzip, bzip2, zip, tar, tar.gz, tar.bz2.",
    t="string"
)

__COMPRESS_PROPERTY_4__ = property_param(
    name="files",
    description="List of files to include in archive.",
    t="array"
)

__COMPRESS_PROPERTY_5__ = property_param(
    name="compression_level",
    description="Compression level (1-9, where 9 is highest).",
    t="integer"
)

__COMPRESS_PROPERTY_6__ = property_param(
    name="archive_path",
    description="Path to the archive file.",
    t="string",
    required=True
)

__COMPRESS_PROPERTY_7__ = property_param(
    name="extract_dir",
    description="Directory to extract files to.",
    t="string"
)

__COMPRESS_PROPERTY_8__ = property_param(
    name="include_base_dir",
    description="Include base directory in archive.",
    t="boolean"
)

__COMPRESS_PROPERTY_9__ = property_param(
    name="password",
    description="Password for encrypted zip files.",
    t="string"
)

__COMPRESS_PROPERTY_10__ = property_param(
    name="recursive",
    description="Include subdirectories recursively.",
    t="boolean"
)

__COMPRESS_FILE_FUNCTION__ = function_ai(name="compress_file",
                                         description="Compress a file using various algorithms.",
                                         parameters=parameters_func([__COMPRESS_PROPERTY_ONE__, __COMPRESS_PROPERTY_TWO__, __COMPRESS_PROPERTY_THREE__, __COMPRESS_PROPERTY_5__]))

__COMPRESS_DECOMPRESS_FUNCTION__ = function_ai(name="decompress_file",
                                               description="Decompress a compressed file.",
                                               parameters=parameters_func([__COMPRESS_PROPERTY_6__, __COMPRESS_PROPERTY_7__]))

__COMPRESS_ARCHIVE_FUNCTION__ = function_ai(name="archive_files",
                                            description="Create an archive (tar/zip) from files.",
                                            parameters=parameters_func([__COMPRESS_PROPERTY_4__, __COMPRESS_PROPERTY_TWO__, __COMPRESS_PROPERTY_THREE__, __COMPRESS_PROPERTY_8__, __COMPRESS_PROPERTY_10__, __COMPRESS_PROPERTY_9__]))

__COMPRESS_EXTRACT_FUNCTION__ = function_ai(name="extract_archive",
                                            description="Extract files from an archive.",
                                            parameters=parameters_func([__COMPRESS_PROPERTY_6__, __COMPRESS_PROPERTY_7__, __COMPRESS_PROPERTY_9__]))

__COMPRESS_LIST_FUNCTION__ = function_ai(name="list_archive",
                                         description="List contents of an archive.",
                                         parameters=parameters_func([__COMPRESS_PROPERTY_6__]))

tools = [
    __COMPRESS_FILE_FUNCTION__,
    __COMPRESS_DECOMPRESS_FUNCTION__,
    __COMPRESS_ARCHIVE_FUNCTION__,
    __COMPRESS_EXTRACT_FUNCTION__,
    __COMPRESS_LIST_FUNCTION__,
]

def compress_file(source_path: str, destination_path: str = None, 
                  compression_type: str = "gzip", compression_level: int = 9) -> str:
    '''
    Compress a file using various compression algorithms.
    
    :param source_path: Path to file to compress
    :type source_path: str
    :param destination_path: Output file path (optional)
    :type destination_path: str
    :param compression_type: Compression type (gzip, bzip2)
    :type compression_type: str
    :param compression_level: Compression level 1-9
    :type compression_level: int
    :return: Compression status message
    :rtype: str
    '''
    try:
        if not os.path.exists(source_path):
            return f"Error: Source file does not exist: {source_path}"
        
        if not os.path.isfile(source_path):
            return f"Error: Source path is not a file: {source_path}"
        
        # Determine destination path
        if destination_path is None:
            if compression_type.lower() == "gzip":
                destination_path = source_path + ".gz"
            elif compression_type.lower() == "bzip2":
                destination_path = source_path + ".bz2"
            else:
                destination_path = source_path + ".compressed"
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        compression_type = compression_type.lower()
        
        if compression_type == "gzip":
            with open(source_path, 'rb') as f_in:
                with gzip.open(destination_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Get compression ratio
            original_size = os.path.getsize(source_path)
            compressed_size = os.path.getsize(destination_path)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return f"File compressed with gzip: {destination_path}\n" \
                   f"Original size: {original_size} bytes\n" \
                   f"Compressed size: {compressed_size} bytes\n" \
                   f"Compression ratio: {ratio:.1f}%"
        
        elif compression_type == "bzip2":
            with open(source_path, 'rb') as f_in:
                with bz2.open(destination_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            original_size = os.path.getsize(source_path)
            compressed_size = os.path.getsize(destination_path)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return f"File compressed with bzip2: {destination_path}\n" \
                   f"Original size: {original_size} bytes\n" \
                   f"Compressed size: {compressed_size} bytes\n" \
                   f"Compression ratio: {ratio:.1f}%"
        
        else:
            return f"Error: Unsupported compression type: {compression_type}. Use 'gzip' or 'bzip2'."
    
    except PermissionError as e:
        return f"Error: Permission denied: {str(e)}"
    except Exception as e:
        return f"Error compressing file: {str(e)}"

def decompress_file(archive_path: str, extract_dir: str = None) -> str:
    '''
    Decompress a compressed file.
    
    :param archive_path: Path to compressed file
    :type archive_path: str
    :param extract_dir: Directory to extract to (default: same as archive)
    :type extract_dir: str
    :return: Decompression status message
    :rtype: str
    '''
    try:
        if not os.path.exists(archive_path):
            return f"Error: Archive file does not exist: {archive_path}"
        
        if not os.path.isfile(archive_path):
            return f"Error: Archive path is not a file: {archive_path}"
        
        # Determine extraction directory
        if extract_dir is None:
            extract_dir = os.path.dirname(archive_path) or "."
        
        os.makedirs(extract_dir, exist_ok=True)
        
        archive_name = os.path.basename(archive_path)
        
        # Determine compression type based on extension
        if archive_name.endswith('.gz') and not archive_name.endswith('.tar.gz'):
            # Gzip file
            output_name = archive_name[:-3] if archive_name.endswith('.gz') else archive_name
            output_path = os.path.join(extract_dir, output_name)
            
            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return f"File decompressed: {output_path}"
        
        elif archive_name.endswith('.bz2') and not archive_name.endswith('.tar.bz2'):
            # Bzip2 file
            output_name = archive_name[:-4] if archive_name.endswith('.bz2') else archive_name
            output_path = os.path.join(extract_dir, output_name)
            
            with bz2.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return f"File decompressed: {output_path}"
        
        elif archive_name.endswith('.zip'):
            # Zip file
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            return f"Zip file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
            # Tar gzip
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar.gz file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar.bz2') or archive_name.endswith('.tbz2'):
            # Tar bzip2
            with tarfile.open(archive_path, 'r:bz2') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar.bz2 file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar'):
            # Tar uncompressed
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar file extracted to: {extract_dir}"
        
        else:
            return f"Error: Unsupported archive format: {archive_name}. Supported: .gz, .bz2, .zip, .tar, .tar.gz, .tar.bz2"
    
    except zipfile.BadZipFile as e:
        return f"Error: Invalid zip file: {str(e)}"
    except tarfile.ReadError as e:
        return f"Error: Invalid tar file: {str(e)}"
    except PermissionError as e:
        return f"Error: Permission denied: {str(e)}"
    except Exception as e:
        return f"Error decompressing file: {str(e)}"

def archive_files(files: list, destination_path: str, compression_type: str = "zip",
                  include_base_dir: bool = False, recursive: bool = True, password: str = None) -> str:
    '''
    Create an archive (tar/zip) from files.
    
    :param files: List of files/directories to archive
    :type files: list
    :param destination_path: Output archive path
    :type destination_path: str
    :param compression_type: Archive type: zip, tar, tar.gz, tar.bz2
    :type compression_type: str
    :param include_base_dir: Include base directory in archive
    :type include_base_dir: bool
    :param recursive: Include subdirectories recursively
    :type recursive: bool
    :param password: Password for zip encryption (zip only)
    :type password: str
    :return: Archive creation status message
    :rtype: str
    '''
    try:
        if not files:
            return "Error: No files specified for archiving"
        
        # Validate files exist
        valid_files = []
        for file_path in files:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                return f"Error: File does not exist: {file_path}"
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        
        compression_type = compression_type.lower()
        archive_name = os.path.basename(destination_path)
        
        if compression_type == "zip" or archive_name.endswith('.zip'):
            # Create zip file
            compression = zipfile.ZIP_DEFLATED
            try:
                with zipfile.ZipFile(destination_path, 'w', compression) as zipf:
                    for file_path in valid_files:
                        if os.path.isfile(file_path):
                            # Add file
                            arcname = os.path.basename(file_path) if not include_base_dir else file_path
                            zipf.write(file_path, arcname)
                        elif os.path.isdir(file_path):
                            # Add directory
                            for root, dirs, filenames in os.walk(file_path):
                                for filename in filenames:
                                    full_path = os.path.join(root, filename)
                                    if not recursive and root != file_path:
                                        continue
                                    arcname = os.path.relpath(full_path, file_path if include_base_dir else '.')
                                    zipf.write(full_path, arcname)
            
                # Set password if provided
                if password:
                    # Note: zipfile doesn't support password protection in write mode directly
                    # Would need to use external library or subprocess
                    return f"Zip archive created: {destination_path}\nNote: Password protection not implemented in this version."
                
                return f"Zip archive created: {destination_path}"
            
            except Exception as e:
                return f"Error creating zip archive: {str(e)}"
        
        elif compression_type in ["tar", "tar.gz", "tgz", "tar.bz2", "tbz2"]:
            # Determine tar mode
            if compression_type.endswith('.gz') or compression_type == 'tgz' or archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
                mode = 'w:gz'
            elif compression_type.endswith('.bz2') or compression_type == 'tbz2' or archive_name.endswith('.tar.bz2') or archive_name.endswith('.tbz2'):
                mode = 'w:bz2'
            else:
                mode = 'w'
            
            try:
                with tarfile.open(destination_path, mode) as tarf:
                    for file_path in valid_files:
                        if os.path.isfile(file_path):
                            arcname = os.path.basename(file_path) if not include_base_dir else file_path
                            tarf.add(file_path, arcname=arcname, recursive=False)
                        elif os.path.isdir(file_path):
                            tarf.add(file_path, arcname=os.path.basename(file_path) if not include_base_dir else file_path, recursive=recursive)
                
                return f"Tar archive created: {destination_path}"
            
            except Exception as e:
                return f"Error creating tar archive: {str(e)}"
        
        else:
            return f"Error: Unsupported archive type: {compression_type}. Use 'zip', 'tar', 'tar.gz', or 'tar.bz2'."
    
    except PermissionError as e:
        return f"Error: Permission denied: {str(e)}"
    except Exception as e:
        return f"Error creating archive: {str(e)}"

def extract_archive(archive_path: str, extract_dir: str = None, password: str = None) -> str:
    '''
    Extract files from an archive.
    
    :param archive_path: Path to archive file
    :type archive_path: str
    :param extract_dir: Directory to extract to (default: same as archive)
    :type extract_dir: str
    :param password: Password for encrypted zip files
    :type password: str
    :return: Extraction status message
    :rtype: str
    '''
    try:
        if not os.path.exists(archive_path):
            return f"Error: Archive file does not exist: {archive_path}"
        
        if not os.path.isfile(archive_path):
            return f"Error: Archive path is not a file: {archive_path}"
        
        # Determine extraction directory
        if extract_dir is None:
            extract_dir = os.path.dirname(archive_path) or "."
            # Create subdirectory based on archive name
            archive_name = os.path.basename(archive_path)
            base_name = os.path.splitext(archive_name)[0]
            if base_name.endswith('.tar'):
                base_name = os.path.splitext(base_name)[0]
            extract_dir = os.path.join(extract_dir, base_name)
        
        os.makedirs(extract_dir, exist_ok=True)
        
        archive_name = os.path.basename(archive_path)
        
        # Determine archive type and extract
        if archive_name.endswith('.zip'):
            # Zip file
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                if password:
                    zip_ref.setpassword(password.encode())
                zip_ref.extractall(extract_dir)
            
            return f"Zip file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
            # Tar gzip
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar.gz file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar.bz2') or archive_name.endswith('.tbz2'):
            # Tar bzip2
            with tarfile.open(archive_path, 'r:bz2') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar.bz2 file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.tar'):
            # Tar uncompressed
            with tarfile.open(archive_path, 'r') as tar_ref:
                tar_ref.extractall(extract_dir)
            
            return f"Tar file extracted to: {extract_dir}"
        
        elif archive_name.endswith('.gz') and not archive_name.endswith('.tar.gz'):
            # Gzip file
            output_name = archive_name[:-3] if archive_name.endswith('.gz') else archive_name
            output_path = os.path.join(extract_dir, output_name)
            
            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return f"Gzip file extracted to: {output_path}"
        
        elif archive_name.endswith('.bz2') and not archive_name.endswith('.tar.bz2'):
            # Bzip2 file
            output_name = archive_name[:-4] if archive_name.endswith('.bz2') else archive_name
            output_path = os.path.join(extract_dir, output_name)
            
            with bz2.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            return f"Bzip2 file extracted to: {output_path}"
        
        else:
            return f"Error: Unsupported archive format: {archive_name}"
    
    except zipfile.BadZipFile as e:
        return f"Error: Invalid zip file: {str(e)}"
    except tarfile.ReadError as e:
        return f"Error: Invalid tar file: {str(e)}"
    except RuntimeError as e:
        if "password" in str(e).lower():
            return f"Error: Incorrect password or encrypted zip file"
        return f"Error: {str(e)}"
    except PermissionError as e:
        return f"Error: Permission denied: {str(e)}"
    except Exception as e:
        return f"Error extracting archive: {str(e)}"

def list_archive(archive_path: str) -> str:
    '''
    List contents of an archive.
    
    :param archive_path: Path to archive file
    :type archive_path: str
    :return: Archive contents listing
    :rtype: str
    '''
    try:
        if not os.path.exists(archive_path):
            return f"Error: Archive file does not exist: {archive_path}"
        
        if not os.path.isfile(archive_path):
            return f"Error: Archive path is not a file: {archive_path}"
        
        archive_name = os.path.basename(archive_path)
        result = [f"Archive Contents: {archive_name}"]
        result.append("=" * 80)
        
        if archive_name.endswith('.zip'):
            # Zip file
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                result.append(f"Files: {len(file_list)}")
                result.append("-" * 80)
                
                for file_info in file_list:
                    # Try to get file info
                    try:
                        info = zip_ref.getinfo(file_info)
                        size = info.file_size
                        compressed_size = info.compress_size
                        ratio = (1 - compressed_size / size) * 100 if size > 0 else 0
                        result.append(f"{file_info:<50} {size:>10} bytes -> {compressed_size:>10} bytes ({ratio:.1f}%)")
                    except:
                        result.append(f"{file_info}")
        
        elif archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz') or \
             archive_name.endswith('.tar.bz2') or archive_name.endswith('.tbz2') or \
             archive_name.endswith('.tar'):
            # Tar file
            if archive_name.endswith('.tar.gz') or archive_name.endswith('.tgz'):
                mode = 'r:gz'
            elif archive_name.endswith('.tar.bz2') or archive_name.endswith('.tbz2'):
                mode = 'r:bz2'
            else:
                mode = 'r'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                members = tar_ref.getmembers()
                
                result.append(f"Files: {len(members)}")
                result.append("-" * 80)
                
                for member in members:
                    size = member.size
                    permissions = oct(member.mode)[-3:]
                    mtime = member.mtime
                    import time
                    mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                    result.append(f"{member.name:<50} {size:>10} bytes {permissions} {mtime_str}")
        
        elif archive_name.endswith('.gz') and not archive_name.endswith('.tar.gz'):
            # Single gzip file
            import gzip
            with gzip.open(archive_path, 'rb') as f:
                # Get uncompressed size by reading?
                # Could be inefficient for large files
                pass
            result.append("Single gzip compressed file")
        
        elif archive_name.endswith('.bz2') and not archive_name.endswith('.tar.bz2'):
            result.append("Single bzip2 compressed file")
        
        else:
            return f"Error: Unsupported archive format: {archive_name}"
        
        # Add archive size
        archive_size = os.path.getsize(archive_path)
        result.append("-" * 80)
        result.append(f"Archive size: {archive_size} bytes")
        
        return "\n".join(result)
    
    except zipfile.BadZipFile as e:
        return f"Error: Invalid zip file: {str(e)}"
    except tarfile.ReadError as e:
        return f"Error: Invalid tar file: {str(e)}"
    except Exception as e:
        return f"Error listing archive contents: {str(e)}"

TOOL_CALL_MAP = {
    "compress_file": compress_file,
    "decompress_file": decompress_file,
    "archive_files": archive_files,
    "extract_archive": extract_archive,
    "list_archive": list_archive,
}