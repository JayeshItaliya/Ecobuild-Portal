"""
Management command to create default permissions for the Ecobuild Portal
"""

from django.core.management.base import BaseCommand

from accounts.enums import PermissionResourceChoices
from accounts.enums import SubscriptionTypeChoices
from accounts.models import Permission
from accounts.models import Role
from accounts.models import RolePermission
from backend.enums import ActionType


class Command(BaseCommand):
    help = "Create default permissions and assign them to roles"

    def handle(self, *args, **kwargs):
        self.stdout.write("Setting up default permissions...")

        # Create default permissions
        permissions_data = [
            # Product permissions
            {
                "name": "View Products",
                "codename": "view_product",
                "resource_type": PermissionResourceChoices.PRODUCT,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Products",
                "codename": "create_product",
                "resource_type": PermissionResourceChoices.PRODUCT,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Products",
                "codename": "update_product",
                "resource_type": PermissionResourceChoices.PRODUCT,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Products",
                "codename": "delete_product",
                "resource_type": PermissionResourceChoices.PRODUCT,
                "action": ActionType.DELETE,
            },
            # Product Category permissions
            {
                "name": "View Product Categories",
                "codename": "view_product_category",
                "resource_type": PermissionResourceChoices.PRODUCT_CATEGORY,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Product Categories",
                "codename": "create_product_category",
                "resource_type": PermissionResourceChoices.PRODUCT_CATEGORY,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Product Categories",
                "codename": "update_product_category",
                "resource_type": PermissionResourceChoices.PRODUCT_CATEGORY,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Product Categories",
                "codename": "delete_product_category",
                "resource_type": PermissionResourceChoices.PRODUCT_CATEGORY,
                "action": ActionType.DELETE,
            },
            # Blog permissions
            {
                "name": "View Blogs",
                "codename": "view_blog",
                "resource_type": PermissionResourceChoices.BLOG,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Blogs",
                "codename": "create_blog",
                "resource_type": PermissionResourceChoices.BLOG,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Blogs",
                "codename": "update_blog",
                "resource_type": PermissionResourceChoices.BLOG,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Blogs",
                "codename": "delete_blog",
                "resource_type": PermissionResourceChoices.BLOG,
                "action": ActionType.DELETE,
            },
            # Document permissions
            {
                "name": "View Documents",
                "codename": "view_document",
                "resource_type": PermissionResourceChoices.DOCUMENT,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Documents",
                "codename": "create_document",
                "resource_type": PermissionResourceChoices.DOCUMENT,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Documents",
                "codename": "update_document",
                "resource_type": PermissionResourceChoices.DOCUMENT,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Documents",
                "codename": "delete_document",
                "resource_type": PermissionResourceChoices.DOCUMENT,
                "action": ActionType.DELETE,
            },
            # CAD File permissions (premium content)
            {
                "name": "View CAD Files",
                "codename": "view_cad_file",
                "resource_type": PermissionResourceChoices.CAD_FILE,
                "action": ActionType.VIEW,
                "subscription_level": SubscriptionTypeChoices.PREMIUM,
            },
            {
                "name": "Download CAD Files",
                "codename": "download_cad_file",
                "resource_type": PermissionResourceChoices.CAD_FILE,
                "action": ActionType.VIEW,
                "subscription_level": SubscriptionTypeChoices.PREMIUM,
            },
            # Learning Video permissions (premium content)
            {
                "name": "View Learning Videos",
                "codename": "view_learning_video",
                "resource_type": PermissionResourceChoices.LEARNING_VIDEO,
                "action": ActionType.VIEW,
                "subscription_level": SubscriptionTypeChoices.PREMIUM,
            },
            # User management permissions
            {
                "name": "View Users",
                "codename": "view_user",
                "resource_type": PermissionResourceChoices.USER,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Users",
                "codename": "create_user",
                "resource_type": PermissionResourceChoices.USER,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Users",
                "codename": "update_user",
                "resource_type": PermissionResourceChoices.USER,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Users",
                "codename": "delete_user",
                "resource_type": PermissionResourceChoices.USER,
                "action": ActionType.DELETE,
            },
            # Role management permissions
            {
                "name": "View Roles",
                "codename": "view_role",
                "resource_type": PermissionResourceChoices.ROLE,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create Roles",
                "codename": "create_role",
                "resource_type": PermissionResourceChoices.ROLE,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update Roles",
                "codename": "update_role",
                "resource_type": PermissionResourceChoices.ROLE,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete Roles",
                "codename": "delete_role",
                "resource_type": PermissionResourceChoices.ROLE,
                "action": ActionType.DELETE,
            },
            # Permission management permissions
            {
                "name": "View Permissions",
                "codename": "view_permission",
                "resource_type": PermissionResourceChoices.PERMISSION,
                "action": ActionType.VIEW,
            },
            {
                "name": "Manage Permissions",
                "codename": "update_permission",
                "resource_type": PermissionResourceChoices.PERMISSION,
                "action": ActionType.UPDATE,
            },
            # CMS Content permissions
            {
                "name": "View CMS Content",
                "codename": "view_cms_content",
                "resource_type": PermissionResourceChoices.CMS_CONTENT,
                "action": ActionType.VIEW,
            },
            {
                "name": "Create CMS Content",
                "codename": "create_cms_content",
                "resource_type": PermissionResourceChoices.CMS_CONTENT,
                "action": ActionType.CREATE,
            },
            {
                "name": "Update CMS Content",
                "codename": "update_cms_content",
                "resource_type": PermissionResourceChoices.CMS_CONTENT,
                "action": ActionType.UPDATE,
            },
            {
                "name": "Delete CMS Content",
                "codename": "delete_cms_content",
                "resource_type": PermissionResourceChoices.CMS_CONTENT,
                "action": ActionType.DELETE,
            },
        ]

        # Create permissions
        created_permissions = []
        for perm_data in permissions_data:
            subscription_level = perm_data.pop("subscription_level", None)
            perm_data["description"] = perm_data.get(
                "description",
                f"Allows {perm_data['action'].lower()}ing of {perm_data['resource_type'].replace('_', ' ')}",
            )

            permission, created = Permission.objects.get_or_create(
                codename=perm_data["codename"], defaults=perm_data
            )

            if created:
                created_permissions.append((permission, subscription_level))
                self.stdout.write(
                    self.style.SUCCESS(f"Created permission: {permission.name}")
                )
            else:
                # If permission exists, we still need to track it for role assignment
                created_permissions.append((permission, subscription_level))
                self.stdout.write(
                    self.style.WARNING(f"Permission already exists: {permission.name}")
                )

        # Create default roles if they don't exist
        default_roles = [
            {
                "name": {"en": "Admin"},
                "description": {"en": "Full system administrator with all permissions"},
                "subscription_required": SubscriptionTypeChoices.ENTERPRISE,
                "is_system_role": True,
            },
            {
                "name": {"en": "Editor"},
                "description": {"en": "Can edit content and manage some resources"},
                "subscription_required": SubscriptionTypeChoices.BASIC,
                "is_system_role": True,
            },
            {
                "name": {"en": "Viewer"},
                "description": {"en": "Read-only access to public content"},
                "subscription_required": SubscriptionTypeChoices.FREE,
                "is_system_role": True,
            },
            {
                "name": {"en": "Premium User"},
                "description": {
                    "en": "Premium subscription user with access to learning content"
                },
                "subscription_required": SubscriptionTypeChoices.PREMIUM,
                "is_system_role": False,
            },
        ]

        admin_permissions = [
            p for p, _ in created_permissions
        ]  # All permissions for admin
        viewer_permissions = [
            perm
            for perm, sub_level in Permission.objects.all()
            if perm.resource_type
            in [
                PermissionResourceChoices.PRODUCT,
                PermissionResourceChoices.BLOG,
                PermissionResourceChoices.CMS_CONTENT,
            ]
            and perm.action == ActionType.VIEW
            and (sub_level is None or sub_level == SubscriptionTypeChoices.FREE)
        ]

        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                name__en=role_data["name"][
                    "en"
                ],  # This might need adjustment based on your JSONField usage
                defaults=role_data,
            )

            if created or not RolePermission.objects.filter(role=role).exists():
                self.stdout.write(
                    f"Setting up permissions for role: {role.name.get('en', 'Unknown Role')}"
                )

                # Clear existing permissions
                RolePermission.objects.filter(role=role).delete()

                # Assign permissions based on role
                permissions_to_assign = []
                if role.name.get("en") == "Admin":
                    permissions_to_assign = admin_permissions
                elif role.name.get("en") == "Editor":
                    # Editor gets most permissions except user/role management
                    permissions_to_assign = [
                        perm
                        for perm in admin_permissions
                        if not (
                            perm.resource_type
                            in [
                                PermissionResourceChoices.USER,
                                PermissionResourceChoices.ROLE,
                                PermissionResourceChoices.PERMISSION,
                            ]
                            and perm.action in [ActionType.CREATE, ActionType.DELETE]
                        )
                    ]
                elif role.name.get("en") == "Viewer":
                    permissions_to_assign = viewer_permissions
                elif role.name.get("en") == "Premium User":
                    # Premium users get free content + premium content
                    permissions_to_assign = [
                        perm
                        for perm in Permission.objects.all()
                        if perm.action == ActionType.VIEW
                    ]

                # Create RolePermission instances
                for permission in permissions_to_assign:
                    # Find the subscription level from our created_permissions list
                    permission_subscription_level = None
                    for perm, sub_level in created_permissions:
                        if perm.id == permission.id:
                            permission_subscription_level = sub_level
                            break

                    RolePermission.objects.create(
                        role=role,
                        permission=permission,
                        is_granted=True,
                        subscription_level=permission_subscription_level
                        or role.subscription_required,
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned {len(permissions_to_assign)} permissions to {role.name.get('en', 'Unknown Role')}"
                    )
                )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created role: {role.name.get('en', 'Unknown Role')}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Role already exists: {role.name.get('en', 'Unknown Role')}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully set up {len(created_permissions)} permissions and configured default roles!"
            )
        )
