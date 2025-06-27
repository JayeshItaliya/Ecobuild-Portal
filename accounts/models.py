from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.enums import LoginMethodChoices, VerificationStatusChoices
from backend.enums import UserRoleChoices
from backend.enums import UserTypeChoices
from backend.models import BaseModel


class User(AbstractUser, BaseModel):
    email = models.EmailField(
        verbose_name="Email Address",
        max_length=255,
        unique=True,
        db_index=True,
    )
    role = models.CharField(
        max_length=50, choices=UserRoleChoices.choices, default=UserRoleChoices.USER
    )
    full_name = models.CharField(max_length=50, null=True, blank=True)
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
    login_method = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    profile_image = models.URLField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatusChoices,
        default=VerificationStatusChoices.PENDING,
        blank=True,
        db_index=True,
    )
    language = models.ForeignKey(
        language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    organization = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"  # Can change to 'email' if you want email login

    def __str__(self):
        return self.username


class Role(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class language(BaseModel):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
