from django.contrib import admin

from cms.models.faq import FAQ

from .models.blog import BlogPost, Category, ContactMessage, Tag
from .models.product import (
    Product,
    ProductCategory,
    ProductGalleryImage,
    ProductSection,
)


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
        "tags",
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
