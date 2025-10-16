"""
Custom storage backends for different types of media files.
This allows for fine-grained control over where different file types are stored.
"""

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    S3 storage backend for user-uploaded media files.
    """

    location = "media"
    file_overwrite = False
    default_acl = "public-read"


class StaticStorage(S3Boto3Storage):
    """
    S3 storage backend for static files (CSS, JS, etc).
    """

    location = "static"
    default_acl = "public-read"
