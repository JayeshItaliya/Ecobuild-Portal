from django.db import models


class BaseStatusChoices(models.TextChoices):
    @classmethod
    def is_valid_choice(cls, value):
        return value in cls.values


class UserTypeChoices(BaseStatusChoices):
    ADMIN = "admin", "Admin"
    ARCHITECT = "architect", "Architect"
    BUILDER = "builder", "Builder"
    ENGINEER = "engineer", "Engineer"
    CONSULTANT = "consultant", "Consultant"
    DISTRIBUTOR = "distributor", "Distributor"
    DEALER = "dealer", "Dealer"
    DEVELOPER = "developer", "Developer"
    HOMEOWNER = "homeowner", "Homeowner"


class LoginMethodChoices(BaseStatusChoices):
    EMAIL = "email", "Email"
    GOOGLE = "google", "Google"
    LINKEDIN = "linkedin", "LinkedIn"


class UserRoleChoices(BaseStatusChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"
    GUEST = "guest", "Guest"
