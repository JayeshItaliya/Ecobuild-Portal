# Register your models here.

from django.contrib import admin

from .models import Role
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "is_active", "is_staff")
    search_fields = ("full_name", "email")
    list_filter = ("is_staff", "is_active")
    ordering = ("id",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    ordering = ("id",)
