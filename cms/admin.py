from django.contrib import admin

from cms.models.about_us import AboutUsPage
from cms.models.about_us import CompanyAchievement
from cms.models.about_us import CompanyTimeline
from cms.models.about_us import TeamMember
from cms.models.faq import FAQ

from .models.blog import BlogPost
from .models.blog import Category
from .models.blog import ContactMessage
from .models.blog import Tag
from .models.broadcast_news import BroadcastNews
from .models.broadcast_news import BroadcastNewsDetail
from .models.product import Product
from .models.product import ProductCategory
from .models.product import ProductGalleryImage
from .models.product import ProductSection


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "category_type")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")


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
        # "tags",
        "content",
        "featured_image",
        "meta_title",
        "meta_description",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "subtitle", "category")


@admin.register(ProductSection)
class ProductSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "order",
        "section_type",
        "content_text",
        "content_image",
        "content_file",
        "image_position",
    )


@admin.register(ProductGalleryImage)
class ProductGalleryImageAdmin(admin.ModelAdmin):
    list_display = ("id", "section", "image", "caption")


# About Us Admin
@admin.register(AboutUsPage)
class AboutUsPageAdmin(admin.ModelAdmin):
    list_display = ("id", "company_name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("company_name",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "job_title",
        "is_leadership",
        "is_active",
        "display_order",
    )
    list_filter = ("is_leadership", "is_active")
    search_fields = ("full_name", "email")
    ordering = ("display_order", "full_name")


@admin.register(CompanyTimeline)
class CompanyTimelineAdmin(admin.ModelAdmin):
    list_display = ("id", "year", "title", "is_active", "display_order")
    list_filter = ("is_active", "year")
    ordering = ("-year", "display_order")


@admin.register(CompanyAchievement)
class CompanyAchievementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "year", "is_active", "display_order")
    list_filter = ("is_active", "year")
    ordering = ("display_order", "-year")


# Broadcast News Admin
class BroadcastNewsDetailInline(admin.TabularInline):
    model = BroadcastNewsDetail
    extra = 1
    fields = ("speaker", "content", "timestamp", "order")
    ordering = ("order",)


@admin.register(BroadcastNews)
class BroadcastNewsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "channel_name",
        "interview_date",
        "broadcast_date",
        "status",
        "is_featured",
        "views_count",
        "display_order",
        "created_at",
    )
    list_filter = ("status", "is_featured", "interview_date", "broadcast_date")
    search_fields = ("title", "channel_name", "interviewer_name", "interviewee_name")
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
        ("Media", {"fields": ("thumbnail_image", "video_url", "video_file")}),
        (
            "SEO & Analytics",
            {"fields": ("meta_title", "meta_description", "views_count")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(BroadcastNewsDetail)
class BroadcastNewsDetailAdmin(admin.ModelAdmin):
    list_display = ("id", "broadcast_news", "speaker", "order", "timestamp")
    list_filter = ("broadcast_news",)
    search_fields = ("speaker", "content", "broadcast_news__title")
    ordering = ("broadcast_news", "order")
