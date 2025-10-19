from django.db import models


class BaseStatusChoices(models.TextChoices):
    @classmethod
    def is_valid_choice(cls, value):
        return value in cls.values


class STATUS_CHOICES(BaseStatusChoices):
    DRAFT = "Draft", "Draft"
    PUBLISHED = "Published", "Published"


class GALLERY_TYPE(BaseStatusChoices):
    IMAGE = "Image", "Image"
    VIDEO = "Video", "Video"


class IMAGE_POSITION_CHOICES(BaseStatusChoices):
    LEFT = "Left", "Left"
    RIGHT = "Right", "Right"
    CENTER = "Center", "Center"


class PAGE_SECTION_TYPES(BaseStatusChoices):
    TEXT = "Text", "Text"
    IMAGE = "Image", "Image"
    VIDEO = "Video", "Video"
    FILE = "File", "File"
    IMAGE_TEXT = "Image Text", "Image Text"
    VIDEO_URL = "Video URL", "Video URL"

class ProductCategoryType(BaseStatusChoices):
    PRODUCTS = "Products", "Products"
    INFORMATION=  "Information", "Information"
    DESIGN= "Design", "Design"