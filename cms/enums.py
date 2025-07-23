from django.db import models


class BaseStatusChoices(models.TextChoices):
    @classmethod
    def is_valid_choice(cls, value):
        return value in cls.values


class STATUS_CHOICES(BaseStatusChoices):
    DRAFT = "Draft", "Draft"
    PUBLISHED = "Published", "Published"
