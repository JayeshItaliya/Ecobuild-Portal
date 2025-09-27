from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField

from accounts.mixins import TranslatedField
from accounts.models import Permission
from accounts.models import Role
from accounts.serializers.permission import PermissionChoiceSerializer


class RoleSerializer(ModelSerializer):
    """Serializer for creating and updating roles."""

    permissions = PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False
    )

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions"]


class RoleResponseSerializer(ModelSerializer):
    """Serializer for role responses with translated fields and nested permissions."""

    name = TranslatedField()
    description = TranslatedField()
    permissions = PermissionChoiceSerializer(many=True, read_only=True)
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = ["id", "name", "description", "permissions", "user_count"]

    def get_user_count(self, obj):
        return obj.user_set.count()
