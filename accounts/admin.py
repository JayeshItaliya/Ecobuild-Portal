# Register your models here.

from django.contrib import admin

from .models import ActivityLog
from .models import CompanyInfo
from .models import Permission
from .models import Role
from .models import RolePermission
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "role",
        "subscription_type",
        "is_active",
        "is_staff",
    )
    search_fields = ("full_name", "email", "organization")
    list_filter = (
        "is_staff",
        "is_active",
        "role",
        "subscription_type",
        "user_type",
        "verification_status",
    )
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "profile_image",
                    "language",
                    "organization",
                )
            },
        ),
        (
            "Role & Permissions",
            {"fields": ("role", "user_type", "verification_status")},
        ),
        ("Subscription", {"fields": ("subscription_type", "subscription_expires_at")}),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined"), "classes": ("collapse",)},
        ),
        (
            "Permissions",
            {
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
    )


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    fields = ("permission", "is_granted", "subscription_level")
    autocomplete_fields = ("permission",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "subscription_required",
        "is_active",
        "is_system_role",
    )
    list_filter = ("is_active", "is_system_role", "subscription_required")
    search_fields = ("name", "description")
    ordering = ("id",)
    inlines = [RolePermissionInline]
    readonly_fields = ("is_system_role",)

    fieldsets = (
        (None, {"fields": ("name", "description", "is_active")}),
        ("Subscription", {"fields": ("subscription_required",)}),
        (
            "System",
            {
                "fields": ("is_system_role",),
                "description": "System roles cannot be deleted",
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_system_role:
            return self.readonly_fields + ("name", "description")
        return self.readonly_fields


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "codename", "resource_type", "action", "is_active")
    list_filter = ("resource_type", "action", "is_active")
    search_fields = ("name", "codename", "description")
    ordering = ("resource_type", "action", "name")

    fieldsets = (
        (None, {"fields": ("name", "codename")}),
        (
            "Permission Details",
            {"fields": ("resource_type", "action", "description", "is_active")},
        ),
        (
            "API Configuration",
            {
                "fields": ("api_endpoint", "http_methods"),
                "description": "Configure which API endpoints this permission protects",
            },
        ),
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "permission", "is_granted", "subscription_level")
    list_filter = (
        "is_granted",
        "subscription_level",
        "role",
        "permission__resource_type",
    )
    search_fields = ("role__name", "permission__name", "permission__codename")
    autocomplete_fields = ("role", "permission")
    ordering = ("role", "permission")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "details", "action", "time_stamp")
    ordering = ("-time_stamp",)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "address", "phone", "email")
