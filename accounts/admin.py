# Register your models here.

from django.contrib import admin

from .models import ActivityLog
from .models import CompanyInfo
from .models import Permission
from .models import Role
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "is_active", "is_staff")
    search_fields = ("full_name", "email")
    list_filter = ("is_staff", "is_active")
    ordering = ("id",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "resource", "name", "description")
    list_filter = ("action", "resource")
    search_fields = ("action", "resource", "name", "description")
    ordering = ("action", "resource")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "get_users_count",
        "get_permissions_count",
    )
    filter_horizontal = ("permissions",)
    list_filter = ("permissions",)
    search_fields = ("name", "description")
    ordering = ("id",)

    def get_users_count(self, obj):
        return obj.user_set.count()

    get_users_count.short_description = "Users"

    def get_permissions_count(self, obj):
        return obj.permissions.count()

    get_permissions_count.short_description = "Permissions"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "details", "action", "time_stamp")
    ordering = ("-time_stamp",)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "phone", "email")
