"""
Unified file storage utility for handling file uploads.
Supports both local storage (development) and AWS S3 (production).

This module provides a clean, consistent interface for file operations
across the entire project, automatically selecting the appropriate storage
backend based on environment configuration.

Usage:
    from utils.storage import upload_file, delete_file, get_file_url

    # Upload a file
    file_url = upload_file(file_object, 'directory/subdirectory')

    # Delete a file
    delete_file('path/to/file.jpg')

    # Get file URL
    url = get_file_url('path/to/file.jpg')
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile


class FileStorageManager:
    """
    Centralized file storage manager that handles both local and S3 storage.
    """

    # Allowed file extensions by category
    ALLOWED_EXTENSIONS = {
        "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"],
        "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".mkv"],
        "document": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt"],
        "file": [".zip", ".rar", ".7z", ".tar", ".gz"],
    }

    # Maximum file sizes (in bytes) by category
    MAX_FILE_SIZES = {
        "image": 10 * 1024 * 1024,  # 10 MB
        "video": 100 * 1024 * 1024,  # 100 MB
        "document": 20 * 1024 * 1024,  # 20 MB
        "file": 50 * 1024 * 1024,  # 50 MB
    }

    def __init__(self):
        self.use_s3 = getattr(settings, "USE_S3_STORAGE", False)

    def get_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename while preserving the extension.

        Args:
            original_filename: Original name of the uploaded file

        Returns:
            A unique filename with the same extension
        """
        ext = Path(original_filename).suffix.lower()
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    def validate_file(
        self,
        file: UploadedFile,
        file_type: Optional[str] = None,
        max_size: Optional[int] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file based on extension and size.

        Args:
            file: The uploaded file object
            file_type: Category of file (image, video, document, file)
            max_size: Maximum allowed file size in bytes (overrides default)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"

        # Get file extension
        ext = Path(file.name).suffix.lower()

        # Validate extension if file_type specified
        if file_type:
            allowed_extensions = self.ALLOWED_EXTENSIONS.get(file_type, [])
            if ext not in allowed_extensions:
                return (
                    False,
                    f"Invalid file type. Allowed: {', '.join(allowed_extensions)}",
                )

        # Validate file size
        if max_size is None and file_type:
            max_size = self.MAX_FILE_SIZES.get(file_type, 10 * 1024 * 1024)

        if max_size and file.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return (
                False,
                f"File size exceeds maximum allowed size of {max_size_mb:.1f} MB",
            )

        return True, None

    def upload_file(
        self,
        file: UploadedFile,
        upload_path: str,
        file_type: Optional[str] = None,
        use_unique_name: bool = True,
        validate: bool = True,
    ) -> str:
        """
        Upload a file to storage (local or S3).

        Args:
            file: The uploaded file object
            upload_path: Directory path where file should be stored
            file_type: Category of file for validation (image, video, document, file)
            use_unique_name: Whether to generate a unique filename
            validate: Whether to validate the file

        Returns:
            The path/URL of the uploaded file

        Raises:
            ValueError: If file validation fails
        """
        # Validate file if requested
        if validate:
            is_valid, error_message = self.validate_file(file, file_type)
            if not is_valid:
                raise ValueError(error_message)

        # Generate filename
        if use_unique_name:
            filename = self.get_unique_filename(file.name)
        else:
            filename = file.name

        # Construct full path
        full_path = os.path.join(upload_path, filename)

        # Save file using Django's storage backend
        saved_path = default_storage.save(full_path, file)

        return saved_path

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path to the file to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """
        Get the URL for accessing a file.

        Args:
            file_path: Path to the file

        Returns:
            Full URL to access the file
        """
        if not file_path:
            return ""

        return default_storage.url(file_path)

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            file_path: Path to the file

        Returns:
            True if file exists, False otherwise
        """
        return default_storage.exists(file_path)

    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get the size of a file in bytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            if self.file_exists(file_path):
                return default_storage.size(file_path)
            return None
        except Exception:
            return None


# Global instance
storage_manager = FileStorageManager()


# Convenience functions
def upload_file(
    file: UploadedFile,
    upload_path: str,
    file_type: Optional[str] = None,
    use_unique_name: bool = True,
    validate: bool = True,
) -> str:
    """
    Upload a file to storage.

    Args:
        file: The uploaded file object
        upload_path: Directory path where file should be stored (e.g., 'images/products')
        file_type: Category of file for validation (image, video, document, file)
        use_unique_name: Whether to generate a unique filename
        validate: Whether to validate the file

    Returns:
        The path/URL of the uploaded file

    Example:
        file_path = upload_file(
            file=request.FILES['image'],
            upload_path='products/images',
            file_type='image'
        )
    """
    return storage_manager.upload_file(
        file, upload_path, file_type, use_unique_name, validate
    )


def delete_file(file_path: str) -> bool:
    """
    Delete a file from storage.

    Args:
        file_path: Path to the file to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    return storage_manager.delete_file(file_path)


def get_file_url(file_path: str) -> str:
    """
    Get the URL for accessing a file.

    Args:
        file_path: Path to the file

    Returns:
        Full URL to access the file
    """
    return storage_manager.get_file_url(file_path)


def validate_file(
    file: UploadedFile, file_type: Optional[str] = None, max_size: Optional[int] = None
) -> tuple[bool, Optional[str]]:
    """
    Validate an uploaded file.

    Args:
        file: The uploaded file object
        file_type: Category of file (image, video, document, file)
        max_size: Maximum allowed file size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    return storage_manager.validate_file(file, file_type, max_size)
