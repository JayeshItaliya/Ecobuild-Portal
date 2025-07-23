from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify

from accounts.models import User
from backend.models import BaseModel
from backend.models import BaseTranslatableModel
from cms.enums import STATUS_CHOICES
from cms.utils import calculate_reading_time


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
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.email} - {self.document.name.get('en', 'Unnamed Document')}"

    class Meta:
        db_table = "document_access"
        verbose_name = "Document Access"
        verbose_name_plural = "Document Accesses"
        unique_together = ("user", "document")


class Lead(BaseTranslatableModel):
    name = JSONField(default=dict)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="blog_posts",
    )
    content = models.TextField()
    featured_image = models.ImageField(
        upload_to="blog_images/",
        blank=True,
        null=True,
    )
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES.choices,
        default=STATUS_CHOICES.DRAFT,
    )
    views_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0)  # in minutes

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.reading_time = calculate_reading_time(self.content)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
