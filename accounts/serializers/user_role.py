from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField

from accounts.models import Permission
from accounts.models import Role
from accounts.models import RolePermission


class PermissionSerializer(ModelSerializer):
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
        ]


class RolePermissionSerializer(ModelSerializer):
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "permission",
            "permission_id",
            "is_granted",
            "subscription_level",
        ]


class RoleSerializer(ModelSerializer):
    permissions = RolePermissionSerializer(
        source="role_permissions", many=True, read_only=True
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of permission IDs to assign to this role",
    )

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "is_system_role",
            "subscription_required",
            "permissions",
            "permission_ids",
        ]

    def create(self, validated_data):
        permission_ids = validated_data.pop("permission_ids", [])
        role = super().create(validated_data)

        # Create RolePermission instances
        for perm_id in permission_ids:
            try:
                permission = Permission.objects.get(id=perm_id)
                RolePermission.objects.create(role=role, permission=permission)
            except Permission.DoesNotExist:
                continue

        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop("permission_ids", None)

        role = super().update(instance, validated_data)

        if permission_ids is not None:
            # Clear existing permissions
            RolePermission.objects.filter(role=role).delete()

            # Add new permissions
            for perm_id in permission_ids:
                try:
                    permission = Permission.objects.get(id=perm_id)
                    RolePermission.objects.create(role=role, permission=permission)
                except Permission.DoesNotExist:
                    continue

        return role


class RoleResponseSerializer(ModelSerializer):
    permissions_count = SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "subscription_required",
            "permissions_count",
        ]

    def get_permissions_count(self, obj):
        return RolePermission.objects.filter(role=obj, is_granted=True).count()
