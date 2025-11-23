"""
Serializers for Permission and RolePermission models
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from accounts.models import Permission
from accounts.models import Role
from accounts.models import RolePermission


class PermissionSerializer(ModelSerializer):
    """Serializer for Permission model"""

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "codename",
            "resource_type",
            "action",
            "description",
            "is_active",
            "api_endpoint",
            "http_methods",
        ]
        read_only_fields = ["id"]


class PermissionResponseSerializer(ModelSerializer):
    """Simplified serializer for permission responses"""

    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "resource_type", "action", "description"]


class RolePermissionDetailSerializer(ModelSerializer):
    """Detailed serializer for RolePermission with permission details"""

    permission = PermissionResponseSerializer(read_only=True)

    class Meta:
        model = RolePermission
        fields = ["id", "permission", "is_granted", "subscription_level"]


class RolePermissionSerializer(ModelSerializer):
    """Basic serializer for creating/updating RolePermission"""

    permission_id = serializers.IntegerField(write_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "permission_id",
            "permission_name",
            "is_granted",
            "subscription_level",
        ]

    def validate_permission_id(self, value):
        """Validate that the permission exists"""
        try:
            Permission.objects.get(id=value)
        except Permission.DoesNotExist:
            raise serializers.ValidationError("Permission does not exist")
        return value


class PermissionListSerializer(serializers.Serializer):
    """Serializer for listing permissions by resource type"""

    resource_type = serializers.CharField()
    permissions = PermissionResponseSerializer(many=True)


class RolePermissionBulkUpdateSerializer(serializers.Serializer):
    """Serializer for bulk updating role permissions"""

    role_id = serializers.IntegerField()
    permissions = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of permission dictionaries with 'permission_id', 'is_granted', and optional 'subscription_level'",
    )

    def validate(self, data):
        """Validate the bulk update data"""
        role_id = data.get("role_id")
        try:
            Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role does not exist")

        permissions = data.get("permissions", [])
        for perm_data in permissions:
            if "permission_id" not in perm_data:
                raise serializers.ValidationError(
                    "Each permission must have a permission_id"
                )
            try:
                Permission.objects.get(id=perm_data["permission_id"])
            except Permission.DoesNotExist:
                raise serializers.ValidationError(
                    f"Permission with id {perm_data['permission_id']} does not exist"
                )

        return data
