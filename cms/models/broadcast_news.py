from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify

from backend.models import BaseTranslatableModel
from cms.enums import STATUS_CHOICES


class BroadcastNews(BaseTranslatableModel):
    """
    Model for storing broadcast news interviews and related details
    """

    title = JSONField(default=dict, help_text="Title of the broadcast news/interview")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title",
    )
    channel_name = JSONField(default=dict, help_text="Name of the news channel")
    interviewer_name = JSONField(
        default=dict, help_text="Name of the interviewer", blank=True
    )
    interviewee_name = JSONField(
        default=dict, help_text="Name of the person being interviewed", blank=True
    )
    interview_date = models.DateField(help_text="Date when the interview was conducted")
    broadcast_date = models.DateTimeField(
        help_text="Date and time when the interview was/will be broadcast",
        null=True,
        blank=True,
    )
    description = JSONField(
        default=dict, help_text="Brief description of the interview"
    )
    thumbnail_image = models.ImageField(
        upload_to="broadcast_news/thumbnails/",
        blank=True,
        null=True,
        help_text="Thumbnail image for the broadcast news",
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to the video of the interview (YouTube, Vimeo, etc.)",
    )
    article_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to the original article or press mention",
    )
    publication_name = JSONField(
        default=dict, help_text="Name of the publication/media outlet", blank=True
    )
    video_file = models.FileField(
        upload_to="broadcast_news/videos/",
        blank=True,
        null=True,
        help_text="Uploaded video file of the interview",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES.choices,
        default=STATUS_CHOICES.DRAFT,
        help_text="Publication status",
    )
    views_count = models.PositiveIntegerField(default=0, help_text="Number of views")
    duration = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Duration of the interview (e.g., '30 minutes')",
    )
    meta_title = JSONField(default=dict, blank=True, help_text="SEO meta title")
    meta_description = JSONField(
        default=dict, blank=True, help_text="SEO meta description"
    )
    is_featured = models.BooleanField(
        default=False, help_text="Mark as featured to display prominently"
    )
    display_order = models.IntegerField(
        default=0, help_text="Order in which the broadcast news should be displayed"
    )

    TRANSLATABLE_FIELDS = [
        "title",
        "channel_name",
        "interviewer_name",
        "interviewee_name",
        "description",
        "meta_title",
        "meta_description",
    ]

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            # Get English title or first available language
            title_text = ""
            if isinstance(self.title, dict):
                title_text = self.title.get("en") or next(iter(self.title.values()), "")
            else:
                title_text = str(self.title)

            base_slug = slugify(title_text)
            slug = base_slug
            counter = 1

            while BroadcastNews.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        if isinstance(self.title, dict):
            return self.title.get("en") or next(
                iter(self.title.values()), "Untitled Broadcast News"
            )
        return str(self.title)

    class Meta:
        db_table = "broadcast_news"
        verbose_name = "Broadcast News"
        verbose_name_plural = "Broadcast News"
        ordering = ["-broadcast_date", "display_order", "-created_at"]


class BroadcastNewsDetail(BaseTranslatableModel):
    """
    Model for storing detailed interview content line by line
    """

    broadcast_news = models.ForeignKey(
        BroadcastNews,
        on_delete=models.CASCADE,
        related_name="details",
        help_text="Related broadcast news",
    )
    speaker = JSONField(
        default=dict, help_text="Name of the speaker (Interviewer/Interviewee)"
    )
    content = JSONField(default=dict, help_text="Content/dialogue of this line")
    timestamp = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Timestamp in the video (e.g., '00:05:30')",
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Order of this line in the interview"
    )

    TRANSLATABLE_FIELDS = ["speaker", "content"]

    def __str__(self):
        speaker_text = ""
        if isinstance(self.speaker, dict):
            speaker_text = self.speaker.get("en") or next(
                iter(self.speaker.values()), "Unknown Speaker"
            )
        else:
            speaker_text = str(self.speaker)
        return f"{speaker_text}: Line {self.order}"

    class Meta:
        db_table = "broadcast_news_detail"
        verbose_name = "Broadcast News Detail"
        verbose_name_plural = "Broadcast News Details"
        ordering = ["broadcast_news", "order"]
