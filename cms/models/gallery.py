from django.db import models
from django.db.models import JSONField

from backend.models import BaseTranslatableModel
from cms.enums import GALLERY_TYPE
from utils.storage import delete_file


class GalleryCategory(BaseTranslatableModel):
    """Gallery category model."""

    name = JSONField(default=dict)  # Translatable
    description = JSONField(default=dict)  # Translatable
    type = models.CharField(
        choices=GALLERY_TYPE.choices,
        default=GALLERY_TYPE.IMAGE,
        max_length=255,
    )
    TRANSLATABLE_FIELDS = ["name", "description"]

    class Meta:
        db_table = "gallery_category"
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"


class Gallery(BaseTranslatableModel):
    """
    Gallery model with automatic file cleanup.

    Features:
    - Automatically deletes old files when replaced
    - Cleans up files when gallery item is deleted
    - Works with both local and S3 storage
    """

    image = models.ImageField(upload_to="gallery/", null=True, blank=True)
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE)
    video = models.FileField(upload_to="gallery/", null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save to delete old files when they are replaced"""
        if self.pk:
            try:
                old_instance = Gallery.objects.get(pk=self.pk)

                # Delete old image if it's being replaced
                if old_instance.image and old_instance.image != self.image:
                    delete_file(old_instance.image.name)

                # Delete old video if it's being replaced
                if old_instance.video and old_instance.video != self.video:
                    delete_file(old_instance.video.name)
            except Gallery.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clean up files when gallery item is deleted"""
        # Delete associated files
        if self.image:
            delete_file(self.image.name)
        if self.video:
            delete_file(self.video.name)

        super().delete(*args, **kwargs)

    class Meta:
        db_table = "gallery"
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
