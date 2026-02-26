from django.contrib import admin

from .models import ActivityLog
from .models import CompanyInfo
from .models import Language
from .models import Role
from .models import SocialLink
from .models import User


def _json_value(value, fallback="-"):
    if isinstance(value, dict):
        return value.get("en") or next(iter(value.values()), fallback)
    return value or fallback


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1
    fields = ("platform", "url", "icon", "is_active")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name_display",
        "email",
        "user_type",
        "verification_status",
        "is_active",
        "is_staff",
        "created_at",
    )
    search_fields = ("email", "phone", "organization")
    list_filter = (
        "user_type",
        "login_method",
        "verification_status",
        "is_active",
        "is_staff",
        "is_superuser",
        "language",
        "created_at",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_login")
    autocomplete_fields = ("role", "language")
    list_select_related = ("role", "language")
    fieldsets = (
        ("Account", {"fields": ("email", "password", "last_login")}),
        (
            "Profile",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "organization",
                    "profile_image",
                    "language",
                    "role",
                )
            },
        ),
        ("Auth", {"fields": ("user_type", "login_method", "verification_status")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )

    def full_name_display(self, obj):
        return _json_value(obj.full_name)

    full_name_display.short_description = "Full Name"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name_display", "description_display", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name__en", "description__en")

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"

    def description_display(self, obj):
        return _json_value(obj.description)

    description_display.short_description = "Description"


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action",
        "object_id",
        "details_display",
        "time_stamp",
    )
    list_filter = ("action", "time_stamp")
    search_fields = ("user__email", "object_id", "details__en")
    ordering = ("-time_stamp",)
    readonly_fields = ("time_stamp",)
    list_select_related = ("user",)

    def details_display(self, obj):
        return _json_value(obj.details)

    details_display.short_description = "Details"


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_display",
        "address_display",
        "phone",
        "email",
        "created_at",
    )
    search_fields = ("name__en", "address__en", "email", "phone")
    readonly_fields = ("created_at", "updated_at")
    inlines = [SocialLinkInline]
    ordering = ("-created_at",)

    def name_display(self, obj):
        return _json_value(obj.name)

    name_display.short_description = "Name"

    def address_display(self, obj):
        return _json_value(obj.address)

    address_display.short_description = "Address"


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "code", "note", "created_at")
    search_fields = ("name", "code", "note")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "platform", "url", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("company__name__en", "url", "icon")
    autocomplete_fields = ("company",)
