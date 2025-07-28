from django.contrib import admin

from .models.module import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    ordering = ("id",)
