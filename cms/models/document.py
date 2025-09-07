from django.db import models
from django.db.models import JSONField

from accounts.models import User
from backend.models import BaseModel
from backend.models import BaseTranslatableModel

class Document(BaseTranslatableModel):
    name = JSONField(default=dict)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    file_url = models.URLField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name"]

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

