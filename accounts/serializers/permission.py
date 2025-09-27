from rest_framework.serializers import ModelSerializer

from accounts.mixins import TranslatedField
from accounts.models import Permission


class PermissionSerializer(ModelSerializer):
    """Serializer for creating and updating permissions."""

    class Meta:
        model = Permission
        fields = ["id", "action", "resource", "name", "description"]


class PermissionResponseSerializer(ModelSerializer):
    """Serializer for permission responses with translated fields."""

    name = TranslatedField()
    description = TranslatedField()

    class Meta:
        model = Permission
        fields = ["id", "action", "resource", "name", "description"]


class PermissionChoiceSerializer(ModelSerializer):
    """Simplified serializer for permission choices in role management."""

    name = TranslatedField()

    class Meta:
        model = Permission
        fields = ["id", "action", "resource", "name"]
