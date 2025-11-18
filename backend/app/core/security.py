# backend/app/core/security.py
"""
Security utilities for file validation and input sanitization.
"""
import os
import re
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.core.exceptions import InvalidFileTypeException, FileTooLargeException

# File validation constants
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Phone number validation pattern (supports various formats)
PHONE_PATTERN = re.compile(r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$")


def validate_file_extension(filename: str, allowed_extensions: set = ALLOWED_RESUME_EXTENSIONS) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (with dots)
    
    Returns:
        True if valid, False otherwise
    """
    ext = Path(filename).suffix.lower()
    return ext in allowed_extensions


def validate_file_size(file: UploadFile, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> Tuple[bool, int]:
    """
    Validate file size by reading content length.
    
    Args:
        file: UploadFile object
        max_size_bytes: Maximum allowed size in bytes
    
    Returns:
        Tuple of (is_valid, file_size_bytes)
    """
    # Read file to determine size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    return file_size <= max_size_bytes, file_size


def validate_resume_file(file: UploadFile) -> None:
    """
    Comprehensive validation for resume file uploads.
    Raises exceptions if validation fails.
    
    Args:
        file: UploadFile object
    
    Raises:
        InvalidFileTypeException: If file type is not allowed
        FileTooLargeException: If file exceeds size limit
    """
    # Validate extension
    if not validate_file_extension(file.filename, ALLOWED_RESUME_EXTENSIONS):
        raise InvalidFileTypeException(
            filename=file.filename,
            allowed_types=list(ALLOWED_RESUME_EXTENSIONS)
        )
    
    # Validate size
    is_valid_size, file_size = validate_file_size(file, MAX_FILE_SIZE_BYTES)
    if not is_valid_size:
        raise FileTooLargeException(
            filename=file.filename,
            max_size_mb=MAX_FILE_SIZE_MB
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and special character issues.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove any directory components
    filename = os.path.basename(filename)
    
    # Replace spaces and special characters with underscores
    filename = re.sub(r'[^\w\s\.-]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    
    return f"{name}{ext}"


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
    
    Returns:
        True if valid format, False otherwise
    """
    if not phone:
        return True  # Empty is valid (optional field)
    
    # Remove common formatting characters for validation
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Check if it matches pattern
    return bool(PHONE_PATTERN.match(phone)) and len(cleaned) >= 7


def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 500) -> None:
    """
    Validate string length.
    
    Args:
        value: String to validate
        field_name: Name of the field (for error messages)
        min_length: Minimum allowed length
        max_length: Maximum allowed length
    
    Raises:
        ValueError: If length is invalid
    """
    if value is None:
        return
    
    length = len(value.strip())
    if length < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long")
    if length > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")
