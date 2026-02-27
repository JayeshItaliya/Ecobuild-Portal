from django.contrib import admin

from .models import FAQ
from .models import AboutUsPage
from .models import AdminNotification
from .models import BlogPost
from .models import BroadcastNews
from .models import BroadcastNewsDetail
from .models import Category
from .models import CompanyAchievement
from .models import CompanyTimeline
from .models import ContactMessage
from .models import Document
from .models import DocumentAccess
from .models import Gallery
from .models import GalleryCategory
from .models import Product
from .models import ProductCategory
from .models import ProductGalleryImage
from .models import ProductSection
from .models import Tag
from .models import TeamMember


def _json_value(value, fallback="-"):
    if isinstance(value, dict):
        return value.get("en") or next(iter(value.values()), fallback)
    return value or fallback


class ProductGalleryImageInline(admin.TabularInline):
    model = ProductGalleryImage
    extra = 1
    fields = ("image", "caption")


class ProductSectionInline(admin.TabularInline):
    model = ProductSection
    extra = 1
    fields = (
        "order",
        "section_type",
        "content_text",
        "content_image",
        "image_position",
    )


class BroadcastNewsDetailInline(admin.TabularInline):
    model = BroadcastNewsDetail
    extra = 1
    fields = ("speaker_display", "content_display", "timestamp", "order")
    readonly_fields = ("speaker_display", "content_display")
    ordering = ("order",)

    def speaker_display(self, obj):
        return _json_value(obj.speaker)

    speaker_display.short_description = "Speaker"

    def content_display(self, obj):
        return _json_value(obj.content)

    content_display.short_description = "Content"


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name_display", "parent", "category_type", "created_at")
    list_filter = ("category_type", "created_at")
    search_fields = ("name__en", "parent__name__en")
    ordering = ("category_type", "created_at")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("parent",)

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question_display", "is_active", "order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("question__en", "answer__en")
    ordering = ("order", "-created_at")
    readonly_fields = ("created_at", "updated_at")

    def question_display(self, obj):
        return _json_value(obj.question)

    question_display.short_description = "Question"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_display",
        "email",
        "subject_display",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = ("email", "name__en", "subject__en", "message__en")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"

    def subject_display(self, obj):
        return _json_value(obj.subject)

    subject_display.short_description = "Subject"


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "slug",
        "status",
        "views_count",
        "reading_time",
        "created_at",
    )
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "slug", "content", "meta_title", "meta_description")
    ordering = ("-created_at",)
    autocomplete_fields = ("category", "tags")
    readonly_fields = ("views_count", "reading_time", "created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title_display", "subtitle_display", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title__en", "subtitle__en", "category__name__en")
    ordering = ("-created_at",)
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductSectionInline]

    def title_display(self, obj):
        return _json_value(obj.title)

    title_display.short_description = "Title"

    def subtitle_display(self, obj):
        return _json_value(obj.subtitle)

    subtitle_display.short_description = "Subtitle"


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "order",
        "section_type",
        "content_text_display",
        "image_position",
    )
    list_filter = ("section_type", "image_position")
    search_fields = ("product__title__en", "content_text__en")
    ordering = ("product", "order")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductGalleryImageInline]

    def content_text_display(self, obj):
        return _json_value(obj.content_text)

    content_text_display.short_description = "Content"


@admin.register(ProductGalleryImage)
class ProductGalleryImageAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "image", "caption", "created_at")
    search_fields = ("caption", "section__product__title__en")
    ordering = ("-created_at",)
    autocomplete_fields = ("section",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AboutUsPage)
class AboutUsPageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "company_name_display",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("company_name__en", "hero_title__en")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def company_name_display(self, obj):
        return _json_value(obj.company_name)

    company_name_display.short_description = "Company Name"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name_display",
        "job_title_display",
        "is_leadership",
        "is_active",
        "display_order",
    )
    list_filter = ("is_leadership", "is_active")
    search_fields = ("full_name__en", "job_title__en", "bio__en")
    ordering = ("display_order", "id")
    readonly_fields = ("created_at", "updated_at")

    def full_name_display(self, obj):
        return _json_value(obj.full_name)

    full_name_display.short_description = "Full Name"

    def job_title_display(self, obj):
        return _json_value(obj.job_title)

    job_title_display.short_description = "Job Title"


@admin.register(CompanyTimeline)
class CompanyTimelineAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "title_display", "is_active", "display_order")
    list_filter = ("is_active", "year")
    search_fields = ("title__en", "description__en")
    ordering = ("-year", "display_order")
    readonly_fields = ("created_at", "updated_at")

    def title_display(self, obj):
        return _json_value(obj.title)

    title_display.short_description = "Title"


@admin.register(CompanyAchievement)
class CompanyAchievementAdmin(admin.ModelAdmin):
    list_display = ("id", "title_display", "year", "is_active", "display_order")
    list_filter = ("is_active", "year")
    search_fields = ("title__en", "description__en", "awarded_by__en")
    ordering = ("display_order", "-year")
    readonly_fields = ("created_at", "updated_at")

    def title_display(self, obj):
        return _json_value(obj.title)

    title_display.short_description = "Title"


@admin.register(BroadcastNews)
class BroadcastNewsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title_display",
        "channel_name_display",
        "interview_date",
        "broadcast_date",
        "status",
        "is_featured",
        "views_count",
        "display_order",
    )
    list_filter = ("status", "is_featured", "interview_date", "broadcast_date")
    search_fields = (
        "title__en",
        "channel_name__en",
        "interviewer_name__en",
        "interviewee_name__en",
    )
    readonly_fields = ("slug", "views_count", "created_at", "updated_at")
    ordering = ("-broadcast_date", "display_order", "-created_at")
    inlines = [BroadcastNewsDetailInline]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title",
                    "slug",
                    "channel_name",
                    "status",
                    "is_featured",
                    "display_order",
                )
            },
        ),
        (
            "Interview Details",
            {
                "fields": (
                    "interviewer_name",
                    "interviewee_name",
                    "interview_date",
                    "broadcast_date",
                    "duration",
                    "description",
                )
            },
        ),
        (
            "Media",
            {
                "fields": (
                    "thumbnail_image",
                    "video_url",
                    "article_url",
                    "publication_name",
                    "video_file",
                )
            },
        ),
        (
            "SEO & Analytics",
            {"fields": ("meta_title", "meta_description", "views_count")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def title_display(self, obj):
        return _json_value(obj.title)

    title_display.short_description = "Title"

    def channel_name_display(self, obj):
        return _json_value(obj.channel_name)

    channel_name_display.short_description = "Channel"


@admin.register(BroadcastNewsDetail)
class BroadcastNewsDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "broadcast_news", "speaker_display", "order", "timestamp")
    list_filter = ("broadcast_news",)
    search_fields = ("speaker__en", "content__en", "broadcast_news__title__en")
    ordering = ("broadcast_news", "order")
    autocomplete_fields = ("broadcast_news",)
    readonly_fields = ("created_at", "updated_at")

    def speaker_display(self, obj):
        return _json_value(obj.speaker)

    speaker_display.short_description = "Speaker"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "name_display", "file_type", "category", "created_at")
    list_filter = ("file_type", "category", "created_at")
    search_fields = ("name__en", "file_type", "category")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"


@admin.register(DocumentAccess)
class DocumentAccessAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "document", "access_level", "created_at")
    list_filter = ("access_level", "created_at")
    search_fields = ("user__email", "document__name__en")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "document")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user", "document")


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name_display", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name__en", "description__en")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "image", "video", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("category__name__en",)
    ordering = ("-created_at",)
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("category",)


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "contact_message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("message", "contact_message__email")
    ordering = ("-created_at",)
    autocomplete_fields = ("contact_message",)
    readonly_fields = ("created_at", "updated_at")
