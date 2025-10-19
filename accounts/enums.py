from django.db import models


class BaseStatusChoices(models.TextChoices):
    @classmethod
    def is_valid_choice(cls, value):
        return value in cls.values



class PlatformChoices(BaseStatusChoices):
    FACEBOOK = "Facebook", "Facebook"
    INSTAGRAM = "Instagram", "Instagram"
    YOUTUBE = "YouTube", "YouTube"
    TWITTER = "Twitter", "Twitter"
    PINTEREST = "Pinterest", "Pinterest"
    LINKEDIN = "LinkedIn", "LinkedIn"
    OTHER = "Other", "Other"
    
