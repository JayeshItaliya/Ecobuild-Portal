from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """
    Custom user manager for handling active users and creating accounts.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password
        """

        if not email:
            raise ValueError("required_messages.EMAIL_FIELD_REQUIRED")
        if not password:
            raise ValueError("required_messages.PASSWORD_FIELD_REQUIRED")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)
