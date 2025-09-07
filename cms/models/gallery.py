from django.db import models
from django.db.models import JSONField

from backend.models import BaseTranslatableModel
from cms.enums import GALLERY_TYPE


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
    """Gallery model."""

    image = models.ImageField(upload_to="gallery", null=True, blank=True)
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE)
    video = models.FileField(upload_to="gallery", null=True, blank=True)


    class Meta:
        db_table = "gallery"
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
