from django.db import models

from backend.models import BaseModel


class AdminNotification(BaseModel):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    contact_message = models.ForeignKey(
        "cms.ContactMessage", null=True, blank=True, on_delete=models.CASCADE
    )

    db_table = "admin_notification"
    ordering = ["-created_at"]

    def __str__(self):
        return self.message[:50]
