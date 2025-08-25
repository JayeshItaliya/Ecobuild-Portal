from django.db import models

from backend.models import BaseTranslatableModel
from cms.enums import IMAGE_POSITION_CHOICES
from cms.enums import PAGE_SECTION_TYPES


class ProductCategory(BaseTranslatableModel):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_category"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


class Product(BaseTranslatableModel):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return self.title


class ProductSection(BaseTranslatableModel):

    product = models.ForeignKey(
        Product, related_name="sections", on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField()
    section_type = models.CharField(max_length=20, choices=PAGE_SECTION_TYPES.choices)

    # Shared fields
    content_text = models.TextField(
        blank=True,
        null=True,
    )
    content_image = models.ImageField(
        upload_to="product_images/",
        blank=True,
        null=True,
    )
    content_file = models.FileField(
        upload_to="product_files/",
        blank=True,
        null=True,
    )

    # Layout controls
    image_position = models.CharField(
        max_length=10,
        choices=IMAGE_POSITION_CHOICES.choices,
        default=IMAGE_POSITION_CHOICES.CENTER,
        blank=True,
    )

    class Meta:
        ordering = ["order"]
        db_table = "product_section"
        verbose_name = "Product Section"
        verbose_name_plural = "Product Sections"


class ProductGalleryImage(BaseTranslatableModel):
    section = models.ForeignKey(
        ProductSection, related_name="gallery_images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="product_gallery/")
    caption = models.CharField(max_length=255, blank=True)
