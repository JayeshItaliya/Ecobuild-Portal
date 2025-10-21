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


class PermissionResourceChoices(BaseStatusChoices):
    """Enum for different resource types that can have permissions"""

    PRODUCT = "product", "Product"
    PRODUCT_CATEGORY = "product_category", "Product Category"
    BLOG = "blog", "Blog"
    DOCUMENT = "document", "Document"
    GALLERY = "gallery", "Gallery"
    USER = "user", "User"
    ROLE = "role", "Role"
    PERMISSION = "permission", "Permission"
    CMS_CONTENT = "cms_content", "CMS Content"
    LEARNING_VIDEO = "learning_video", "Learning Video"
    CAD_FILE = "cad_file", "CAD File"
    COMPANY_INFO = "company_info", "Company Info"
    NOTIFICATION = "notification", "Notification"
    FAQ = "faq", "FAQ"


class SubscriptionTypeChoices(BaseStatusChoices):
    """Enum for subscription types"""

    FREE = "free", "Free"
    BASIC = "basic", "Basic"
    PREMIUM = "premium", "Premium"
    ENTERPRISE = "enterprise", "Enterprise"
