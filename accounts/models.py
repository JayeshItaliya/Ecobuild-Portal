from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import JSONField

from backend.enums import ActionType, LoginMethodChoices
from backend.enums import UserRoleChoices
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


class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    role = models.CharField(
        max_length=50, choices=UserRoleChoices.choices, default=UserRoleChoices.USER
    )
    full_name = models.CharField(max_length=50, null=True, blank=True)
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
    profile_image = models.URLField(null=True, blank=True)
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


class Professional(BaseTranslatableModel):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="professional_profile"
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.ForeignKey(
        "Company", on_delete=models.SET_NULL, null=True, blank=True
    )
    role = models.ForeignKey("Role", on_delete=models.SET_NULL, null=True, blank=True)
    profile_summary = JSONField(null=True, blank=True)
    region = models.ForeignKey(
        "Region", on_delete=models.SET_NULL, null=True, blank=True
    )
    specializations = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["profile_summary", "specializations"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "professional"
        verbose_name = "Professional"
        verbose_name_plural = "Professionals"


class Company(BaseTranslatableModel):
    name = JSONField(default=dict)
    industry_type = JSONField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "industry_type"]

    def __str__(self):
        return self.name.get("en", "Unnamed Company")

    class Meta:
        db_table = "mst_company"
        verbose_name = "Company"
        verbose_name_plural = "Companies"


class Region(BaseTranslatableModel):
    name = JSONField(default=dict)
    country = models.ForeignKey("Country", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=10, null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name"]

    def __str__(self):
        return self.name.get("en", "Unnamed Region")

    class Meta:
        db_table = "region"
        verbose_name = "Region"
        verbose_name_plural = "Regions"


class Country(BaseTranslatableModel):
    name = JSONField(default=dict)
    code = models.CharField(max_length=10)
    flag = models.ImageField(upload_to="flags/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "notes"]

    def __str__(self):
        return self.name.get("en", "Unnamed Country")

    class Meta:
        db_table = "mst_country"
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class ActivityLog(BaseTranslatableModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )

    module = models.ForeignKey(
        "Module",
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


class UsageLog(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    response_time_ms = models.IntegerField()

    class Meta:
        db_table = "usage_log"
        verbose_name = "Usage Log"
        verbose_name_plural = "Usage Logs"
