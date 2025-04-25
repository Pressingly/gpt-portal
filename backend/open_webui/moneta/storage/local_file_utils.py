"""
Utility functions for local file operations.
This module helps avoid circular imports between storage providers.
"""

import os
import logging
from typing import BinaryIO, Tuple

from open_webui.config import UPLOAD_DIR

log = logging.getLogger(__name__)

def upload_file(file: BinaryIO, filename: str) -> Tuple[bytes, str]:
    """
    Upload a file to local storage.
    
    Args:
        file: The file-like object to upload
        filename: The name to give the file in storage
        
    Returns:
        Tuple containing the file contents as bytes and the local file path
        
    Raises:
        ValueError: If the file content is empty
    """
    contents = file.read()
    if not contents:
        raise ValueError("File content is empty")
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    log.debug(f"Saved file locally at {file_path}")
    return contents, file_path

def delete_file(file_path: str) -> None:
    """
    Delete a file from local storage.
    
    Args:
        file_path: The path of the file to delete
    """
    filename = os.path.basename(file_path)
    local_file_path = os.path.join(UPLOAD_DIR, filename)
    
    if os.path.isfile(local_file_path):
        os.remove(local_file_path)
        log.debug(f"Deleted local file {local_file_path}")
    else:
        log.warning(f"File {local_file_path} not found in local storage.")

def delete_all_files() -> None:
    """
    Delete all files from local storage.
    """
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link
                    log.debug(f"Deleted local file {file_path}")
            except Exception as e:
                log.exception(f"Failed to delete {file_path}. Reason: {e}")
    else:
        log.warning(f"Directory {UPLOAD_DIR} not found in local storage.")
