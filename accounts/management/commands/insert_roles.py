from django.core.management.base import BaseCommand

from accounts.models import Role



class Command(BaseCommand):
    help = "Insert default roles (Admin, Editor, Viewer) with generated UUIDs"

    def handle(self, *args, **kwargs):
        default_roles = [
            {"name": "Editor", "description": "Can edit content, limited settings."},
            {"name": "Viewer", "description": "Read-only access."},
            {"name": "Guest", "description": "Limited access for guest users."},
        ]

        for role_data in default_roles:
            role, created = Role.objects.get_or_create(
                name=role_data["name"],
                defaults={
                    "description": role_data["description"],
                    "created_by": None,
                    "updated_by": None,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created role: {role.name}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Role already exists: {role.name}")
                )
