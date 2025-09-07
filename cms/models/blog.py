from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify

from accounts.models import User
from backend.models import BaseModel
from backend.models import BaseTranslatableModel
from cms.enums import STATUS_CHOICES
from cms.utils import calculate_reading_time



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


class ContactMessage(BaseTranslatableModel):
    name = JSONField(default=dict, help_text="Name of the person sending the message")
    email = models.EmailField(help_text="Email address for contact")
    phone = models.CharField(
        max_length=20, blank=True, help_text="Phone number (optional)"
    )
    subject = JSONField(default=dict, help_text="Subject of the message")
    message = JSONField(default=dict, help_text="Content of the message")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(
        default=False, help_text="Whether the message has been read"
    )

    TRANSLATABLE_FIELDS = ["name", "subject", "message"]

    def __str__(self):
        if isinstance(self.name, dict):
            return self.name.get("en") or next(
                iter(self.name.values()), "Unnamed Contact"
            )
        return str(self.name)

    class Meta:
        db_table = "contact_message"
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]

