from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.db.models import JSONField
from django.utils import timezone

from accounts.enums import PermissionResourceChoices
from accounts.enums import PlatformChoices
from accounts.enums import SubscriptionTypeChoices
from accounts.manager import CustomUserManager
from backend.enums import ActionType
from backend.enums import LoginMethodChoices
from backend.enums import UserTypeChoices
from backend.enums import VerificationStatusChoices
from backend.models import BaseModel
from backend.models import BaseTranslatableModel


class Language(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "language"
        verbose_name = "Language"
        verbose_name_plural = "Languages"


class CompanyInfo(BaseTranslatableModel):
    """Main company details shown in Contact Us / Footer."""

    name = JSONField(default=dict)
    address = JSONField(default=dict)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    description = JSONField(default=dict, blank=True, null=True)
    weekday_hours = models.CharField(max_length=100, null=True, blank=True)
    weekend_hours = models.CharField(max_length=100, null=True, blank=True)
    logo = models.FileField(upload_to="company_logos/", null=True, blank=True)

    TRANSLATABLE_FIELDS = ["name", "address", "description"]

    class Meta:
        db_table = "company_info"
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"

    def __str__(self):
        return self.name.get("en", "Unnamed Role")


class SocialLink(models.Model):
    company = models.ForeignKey(
        CompanyInfo, on_delete=models.CASCADE, related_name="social_links"
    )
    platform = models.CharField(max_length=50, choices=PlatformChoices.choices)
    url = models.URLField()
    icon = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "social_links"
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.platform} - {self.company.name}"


class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    role = models.ForeignKey("Role", on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.JSONField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    user_type = models.CharField(
        max_length=50,
        choices=UserTypeChoices.choices,
        default=UserTypeChoices.HOMEOWNER,
    )
    login_method = models.CharField(
        max_length=50,
        choices=LoginMethodChoices.choices,
        default=LoginMethodChoices.EMAIL,
    )
    profile_image = models.FileField(upload_to="profile_images/", null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatusChoices.choices,
        default=VerificationStatusChoices.PENDING,
        db_index=True,
    )
    language = models.ForeignKey(
        Language, on_delete=models.SET_NULL, null=True, blank=True
    )
    organization = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Subscription information
    subscription_type = models.CharField(
        max_length=20,
        choices=SubscriptionTypeChoices.choices,
        default=SubscriptionTypeChoices.FREE,
        help_text="User's current subscription level",
    )
    subscription_expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When the subscription expires"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    TRANSLATABLE_FIELDS = ["full_name"]

    def __str__(self):
        return self.email

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        """
        Check if user has a specific permission.
        First checks superuser status, then role-based permissions.
        """
        if self.is_superuser:
            return True

        if not self.is_active:
            return False

        # Check role-based permissions
        return self.has_permission(perm)

    def has_permission(self, permission_codename):
        """Check if user has a specific permission through their role"""
        if not self.role or not self.role.is_active:
            return False

        # Check if role has the permission
        try:
            role_permission = RolePermission.objects.select_related("permission").get(
                role=self.role, permission__codename=permission_codename
            )

            # Check if permission is granted
            if not role_permission.is_granted:
                return False

            # Check subscription level if specified
            required_sub = (
                role_permission.subscription_level or self.role.subscription_required
            )
            return self._check_subscription_level(required_sub)

        except RolePermission.DoesNotExist:
            return False

    def has_permission_for_resource(self, resource_type, action):
        """Check if user has permission for a specific resource and action"""
        permission_codename = f"{action.lower()}_{resource_type.lower()}"
        return self.has_permission(permission_codename)

    def _check_subscription_level(self, required_level):
        """Check if user's subscription meets the required level"""
        subscription_levels = {
            SubscriptionTypeChoices.FREE: 0,
            SubscriptionTypeChoices.BASIC: 1,
            SubscriptionTypeChoices.PREMIUM: 2,
            SubscriptionTypeChoices.ENTERPRISE: 3,
        }

        user_level = subscription_levels.get(self.subscription_type, 0)
        required_level_value = subscription_levels.get(required_level, 0)

        # Check if subscription has expired
        if (
            self.subscription_expires_at
            and self.subscription_expires_at < timezone.now()
        ):
            return required_level_value == 0  # Only allow free content if expired

        return user_level >= required_level_value

    def get_all_permissions(self):
        """Get all permissions for this user"""
        if not self.role or not self.role.is_active:
            return []

        permissions = []
        role_permissions = RolePermission.objects.select_related("permission").filter(
            role=self.role, is_granted=True
        )

        for rp in role_permissions:
            if self._check_subscription_level(
                rp.subscription_level or self.role.subscription_required
            ):
                permissions.append(rp.permission.codename)

        return permissions

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"


class Role(BaseTranslatableModel):
    name = JSONField(default=dict)
    description = JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(
        default=False, help_text="System roles cannot be deleted"
    )

    # Subscription requirements for this role
    subscription_required = models.CharField(
        max_length=20,
        choices=SubscriptionTypeChoices.choices,
        default=SubscriptionTypeChoices.FREE,
        help_text="Minimum subscription level required for this role",
    )

    TRANSLATABLE_FIELDS = ["name", "description"]

    def __str__(self):
        return self.name.get("en", "Unnamed Role")

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class Permission(BaseModel):
    """Model to define granular permissions for different resources"""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique permission name (e.g., 'view_product', 'edit_blog')",
    )
    codename = models.CharField(
        max_length=100, unique=True, help_text="Permission codename for API usage"
    )
    resource_type = models.CharField(
        max_length=50,
        choices=PermissionResourceChoices.choices,
        help_text="Type of resource this permission applies to",
    )
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        help_text="Action that can be performed",
    )
    description = models.TextField(
        blank=True, null=True, help_text="Description of what this permission allows"
    )
    is_active = models.BooleanField(default=True)

    # API endpoint information for dynamic permission checking
    api_endpoint = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="API endpoint pattern this permission protects",
    )
    http_methods = models.JSONField(
        default=list,
        blank=True,
        help_text="List of HTTP methods this permission applies to",
    )

    def __str__(self):
        return f"{self.action.title()} {self.resource_type.replace('_', ' ').title()}"

    class Meta:
        db_table = "custom_permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        unique_together = ("resource_type", "action", "codename")


class RolePermission(BaseModel):
    """Model to link roles with permissions"""

    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="role_permissions"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="permission_roles"
    )
    is_granted = models.BooleanField(
        default=True,
        help_text="Whether this permission is granted (True) or explicitly denied (False)",
    )

    # Optional constraints
    subscription_level = models.CharField(
        max_length=20,
        choices=SubscriptionTypeChoices.choices,
        blank=True,
        null=True,
        help_text="Required subscription level for this permission (overrides role default)",
    )

    def __str__(self):
        status = "Granted" if self.is_granted else "Denied"
        return f"{self.role} - {self.permission} ({status})"

    class Meta:
        db_table = "role_permissions"
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        unique_together = ("role", "permission")


class ActivityLog(BaseTranslatableModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    action = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        db_index=True,
    )
    object_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )

    details = JSONField(null=True, blank=True)
    time_stamp = models.DateTimeField(auto_now_add=True)

    TRANSLATABLE_FIELDS = ["details"]

    class Meta:
        db_table = "activity_log"
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
