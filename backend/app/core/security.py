"""
Security utilities
"""
import os
from pathlib import Path

def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    return ext in [f".{ext}" for ext in allowed_extensions]

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return file_size <= max_size

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename"""
    import uuid
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4()}{ext}"





