from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Permission


class Command(BaseCommand):
    """Command to create default permissions for various resources."""

    help = "Create default permissions for various resources"

    def add_default_permissions(self):
        """Add default permissions for all resources."""
        default_permissions = [
            # User permissions
            {
                "action": "view",
                "resource": "user",
                "name": {
                    "en": "View Users",
                    "ar": "عرض المستخدمين",
                    "he": "צפה במשתמשים",
                },
                "description": {
                    "en": "Can view user details",
                    "ar": "يمكن عرض تفاصيل المستخدم",
                    "he": "יכול לצפות בפרטי משתמש",
                },
            },
            {
                "action": "create",
                "resource": "user",
                "name": {
                    "en": "Create Users",
                    "ar": "إنشاء مستخدمين",
                    "he": "צור משתמשים",
                },
                "description": {
                    "en": "Can create new users",
                    "ar": "يمكن إنشاء مستخدمين جدد",
                    "he": "יכול ליצור משתמשים חדשים",
                },
            },
            # Role permissions
            {
                "action": "view",
                "resource": "role",
                "name": {"en": "View Roles", "ar": "عرض الأدوار", "he": "צפה בתפקידים"},
                "description": {
                    "en": "Can view role details",
                    "ar": "يمكن عرض تفاصيل الدور",
                    "he": "יכול לצפות בפרטי תפקיד",
                },
            },
            {
                "action": "manage",
                "resource": "role",
                "name": {
                    "en": "Manage Roles",
                    "ar": "إدارة الأدوار",
                    "he": "נהל תפקידים",
                },
                "description": {
                    "en": "Can create, update and delete roles",
                    "ar": "يمكن إنشاء وتحديث وحذف الأدوار",
                    "he": "יכול ליצור, לעדכן ולמחוק תפקידים",
                },
            },
            # Permission management
            {
                "action": "view",
                "resource": "permission",
                "name": {
                    "en": "View Permissions",
                    "ar": "عرض الصلاحيات",
                    "he": "צפה בהרשאות",
                },
                "description": {
                    "en": "Can view permission details",
                    "ar": "يمكن عرض تفاصيل الصلاحيات",
                    "he": "יכול לצפות בפרטי הרשאות",
                },
            },
            {
                "action": "manage",
                "resource": "permission",
                "name": {
                    "en": "Manage Permissions",
                    "ar": "إدارة الصلاحيات",
                    "he": "נהל הרשאות",
                },
                "description": {
                    "en": "Can create, update and delete permissions",
                    "ar": "يمكن إنشاء وتحديث وحذف الصلاحيات",
                    "he": "יכול ליצור, לעדכן ולמחוק הרשאות",
                },
            },
        ]

        for perm_data in default_permissions:
            permission, created = Permission.objects.get_or_create(
                action=perm_data["action"],
                resource=perm_data["resource"],
                defaults={
                    "name": perm_data["name"],
                    "description": perm_data["description"],
                },
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status}: {perm_data['action']}_{perm_data['resource']}"
                )
            )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        """Create default permissions."""
        self.stdout.write("Creating default permissions...")
        self.add_default_permissions()
        self.stdout.write(
            self.style.SUCCESS("Successfully created default permissions")
        )
