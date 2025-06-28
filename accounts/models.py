from django.contrib.auth.models import AbstractUser
from django.db import models

from backend import settings
from backend.enums import LoginMethodChoices
from backend.enums import UserRoleChoices
from backend.enums import UserTypeChoices
from backend.enums import VerificationStatusChoices
from backend.models import BaseModel


class User(AbstractUser, BaseModel):
    email = models.EmailField(
        verbose_name="Email Address",
        max_length=255,
        unique=True,
        db_index=True,
    )
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
    is_active = models.BooleanField(default=True)
    profile_image = models.URLField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.PENDING,
        db_index=True,
    )
    language = models.ForeignKey(
        language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    organization = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"  # Can change to 'email' if you want email login

    def __str__(self):
        return self.username


class Role(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class language(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Professional(BaseModel):
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
    profile_summary = models.TextField(null=True, blank=True)
    region = models.ForeignKey(
        "Region", on_delete=models.SET_NULL, null=True, blank=True
    )
    specializations = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "professional"


class Company(BaseModel):
    name = models.CharField(max_length=255)
    industry_type = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mst_company"


class Region(BaseModel):
    name = models.CharField(max_length=50)
    country = models.ForeignKey("Country", on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mst_region"


class ActivityLog(BaseModel):
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    module_id = models.IntegerField()
    action = models.CharField(max_length=100)
    details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "activity_log"


class UsageLog(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    response_time_ms = models.IntegerField()

    class Meta:
        db_table = "usage_log"


class Country(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mst_country"


class ContentType(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content_type"


class Content(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    body = models.TextField()
    publish_date = models.DateTimeField(null=True, blank=True)
    expire_date = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_tag = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content"


class Module(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "mst_module"


class Course(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to="courses/thumbnails/", null=True, blank=True
    )

    def __str__(self):
        return self.title

    class Meta:
        db_table = "course"


class ProductCategory(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product_category"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "product"


class Document(BaseModel):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "document"


class DocumentAccess(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50)  # e.g., read-only, downloadable

    def __str__(self):
        return f"{self.user.email} - {self.document.name}"

    class Meta:
        db_table = "document_access"
        unique_together = ("user", "document")
