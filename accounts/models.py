from django.contrib.auth.models import AbstractUser
from django.db import models

from backend.enums import LoginMethodChoices
from backend.enums import UserRoleChoices
from backend.enums import UserTypeChoices
from backend.models import BaseModel


class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    user_uid = models.CharField(max_length=255, unique=True)
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

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"  # Can change to 'email' if you want email login

    def __str__(self):
        return self.username
