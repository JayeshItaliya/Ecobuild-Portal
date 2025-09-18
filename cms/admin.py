from django.contrib import admin

from cms.models.faq import FAQ

from .models.blog import BlogPost, ContactMessage
from .models.product import ProductCategory

admin.site.register(ProductCategory)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "order")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "slug", "status", "views_count", "reading_time","tags","content","featured_image","meta_title","meta_description")
     