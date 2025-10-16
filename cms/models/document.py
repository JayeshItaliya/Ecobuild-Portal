from django.db import models
from django.db.models import JSONField

from accounts.models import User
from backend.models import BaseModel
from backend.models import BaseTranslatableModel
from utils.storage import delete_file
from utils.storage import get_file_url


class Document(BaseTranslatableModel):
    """
    Document model with automatic file management.

    Features:
    - Automatically deletes old files when replaced
    - Cleans up files when document is deleted
    - Provides file URL generation for both local and S3
    """

    name = JSONField(default=dict)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    file_url = models.URLField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name"]

    def save(self, *args, **kwargs):
        """Override save to delete old file when replaced"""
        if self.pk:
            try:
                old_instance = Document.objects.get(pk=self.pk)

                # Delete old file if it's being replaced
                if old_instance.file and old_instance.file != self.file:
                    delete_file(old_instance.file.name)
            except Document.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clean up file when document is deleted"""
        if self.file:
            delete_file(self.file.name)

        super().delete(*args, **kwargs)

    def get_file_url(self):
        """Get the full URL for the document file"""
        if self.file:
            return get_file_url(self.file.name)
        return self.file_url

    def __str__(self):
        return self.name.get("en", "Unnamed Document")

    class Meta:
        db_table = "document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class DocumentAccess(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.email} - {self.document.name.get('en', 'Unnamed Document')}"

    class Meta:
        db_table = "document_access"
        verbose_name = "Document Access"
        verbose_name_plural = "Document Accesses"
        unique_together = ("user", "document")
