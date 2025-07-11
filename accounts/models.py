from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import JSONField

from backend import settings
from backend.enums import LoginMethodChoices
from backend.enums import UserRoleChoices
from backend.enums import UserTypeChoices
from backend.enums import VerificationStatusChoices
from backend.models import BaseModel
from utils.model_translation import AutoTranslateMixin


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


class BaseTranslatableModel(BaseModel, AutoTranslateMixin):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.auto_translate_fields()
        super().save(*args, **kwargs)


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


class Module(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Module")

    class Meta:
        db_table = "mst_module"
        verbose_name = "Module"
        verbose_name_plural = "Modules"


class Course(BaseTranslatableModel):
    title = JSONField(default=dict)
    description = JSONField(null=True, blank=True)
    thumbnail = models.ImageField(
        upload_to="courses/thumbnails/", null=True, blank=True
    )

    TRANSLATABLE_FIELDS = ["title", "description"]

    def __str__(self):
        return self.title.get("en", "Untitled Course")

    class Meta:
        db_table = "course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class ProductCategory(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Category")

    class Meta:
        db_table = "product_category"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"


class Product(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(default=dict)
    category = models.ForeignKey(
        "ProductCategory", on_delete=models.SET_NULL, null=True
    )
    image = models.ImageField(upload_to="products/", null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Product")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class ContentType(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Type")

    class Meta:
        db_table = "content_type"
        verbose_name = "Content Type"
        verbose_name_plural = "Content Types"


class Content(BaseTranslatableModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    title = JSONField(default=dict)
    body = JSONField(default=dict)
    publish_date = models.DateTimeField(null=True, blank=True)
    expire_date = models.DateTimeField(null=True, blank=True)
    meta_title = JSONField(null=True, blank=True)
    meta_tag = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["title", "body", "meta_title", "meta_tag"]

    def __str__(self):
        return self.title.get("en", "Untitled")

    class Meta:
        db_table = "content"
        verbose_name = "Content"
        verbose_name_plural = "Contents"


class Document(BaseTranslatableModel):
    name = JSONField(default=dict)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    file_url = models.URLField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name"]

    def __str__(self):
        return self.name.get("en", "Unnamed Document")

    class Meta:
        db_table = "document"
        verbose_name = "Document"
        verbose_name_plural = "Documents"


class DocumentAccess(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.email} - {self.document.name.get('en', 'Unnamed Document')}"

    class Meta:
        db_table = "document_access"
        verbose_name = "Document Access"
        verbose_name_plural = "Document Accesses"
        unique_together = ("user", "document")


class ActivityLog(BaseTranslatableModel):
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    module_id = models.ForeignKey(
        "Module", on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=100)
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


class Lead(BaseTranslatableModel):
    name = JSONField(default=dict)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    score = models.IntegerField()
    status = models.CharField(max_length=50)

    TRANSLATABLE_FIELDS = ["name"]

    def __str__(self):
        return self.name.get("en", "Unnamed Lead")

    class Meta:
        verbose_name = "Lead"
        verbose_name_plural = "Leads"


class Contact(BaseTranslatableModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    name = JSONField(default=dict)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    job_title = JSONField(null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "job_title"]

    def __str__(self):
        return self.name.get("en", "Unnamed Contact")

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
