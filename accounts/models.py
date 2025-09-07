from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import JSONField

from accounts.enums import PlatformChoices
from backend.enums import ActionType
from backend.enums import LoginMethodChoices
from backend.enums import UserTypeChoices
from backend.enums import VerificationStatusChoices
from backend.models import BaseModel
from backend.models import BaseTranslatableModel


class Language(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"


class CompanyInfo(BaseTranslatableModel):
    """Main company details shown in Contact Us / Footer."""

    name = JSONField(default=dict)
    address = JSONField(default=dict)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    description = JSONField(default=dict, blank=True, null=True)
    weekday_hours = models.CharField(max_length=100, null=True, blank=True)
    weekend_hours = models.CharField(max_length=100, null=True, blank=True)
    logo = models.FileField(upload_to="company_logos/", null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "address", "description"]

    class Meta:
        db_table = "company_info"
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"

    def __str__(self):
        return self.name.get("en", "Unnamed Role")


class SocialLink(models.Model):
    company = models.ForeignKey(
        CompanyInfo, on_delete=models.CASCADE, related_name="social_links"
    )
    platform = models.CharField(max_length=50, choices=PlatformChoices.choices)
    url = models.URLField()
    icon = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "social_links"
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.platform} - {self.company.name}"


class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    role = models.ForeignKey("Role", on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.JSONField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    user_type = models.CharField(
        max_length=50,
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.HOMEOWNER,
    )
    login_method = models.CharField(
        max_length=50,
        choices=LoginMethodChoices.choices,
        default=LoginMethodChoices.EMAIL,
    )
    profile_image = models.FileField(upload_to="profile_images/", null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.PENDING,
        db_index=True,
    )
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True
    )
    organization = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    TRANSLATABLE_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Role")

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class ActivityLog(BaseTranslatableModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        db_index=True,
    )
    object_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )

    details = JSONField(null=True, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    TRANSLATABLE_FIELDS = ["details"]

    class Meta:
        db_table = "activity_log"
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
