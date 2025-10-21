"""
API views for Permission management
"""

from typing import TYPE_CHECKING

from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView

from accounts.mixins import TranslatedResponseMixin
from accounts.models import Permission
from accounts.models import Role
from accounts.models import RolePermission
from accounts.permissions import CanManagePermissions
from accounts.permissions import CanManageRoles
from accounts.serializers.permission import PermissionResponseSerializer
from accounts.serializers.permission import PermissionSerializer
from accounts.serializers.permission import RolePermissionBulkUpdateSerializer
from accounts.serializers.permission import RolePermissionDetailSerializer
from backend.utils import CustomPagination
from backend.utils import generic_response

if TYPE_CHECKING:
    pass


class BasePermissionAPIView(TranslatedResponseMixin):
    """Base API view for Permission management"""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = CustomPagination
    response_serializer_class = PermissionResponseSerializer
    permission_classes = [CanManagePermissions]


class PermissionListCreateAPIView(BasePermissionAPIView, ListCreateAPIView):
    """API view to list and create permissions"""

    def get(self, request, *args, **kwargs):
        resource_type = request.query_params.get("resource_type")
        queryset = self.get_queryset()

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset) or queryset

        serializer = self.response_serializer_class(queryset, many=True)
        response_data = (
            self.get_paginated_response(serializer.data).data
            if self.paginate_queryset(queryset)
            else serializer.data
        )

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permissions fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Permission created successfully.",
            data=response_data,
        )


class PermissionRetrieveUpdateDestroyAPIView(
    BasePermissionAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific Permission instance"""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permission fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=request.user)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permission updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Permission deleted successfully.",
        )


class PermissionByResourceTypeAPIView(APIView):
    """API view to get permissions grouped by resource type"""

    permission_classes = [CanManagePermissions]

    def get(self, request):
        from accounts.enums import PermissionResourceChoices

        data = []
        for resource_type, display_name in PermissionResourceChoices.choices:
            permissions = Permission.objects.filter(
                resource_type=resource_type, is_active=True
            ).order_by("action", "name")

            serializer = PermissionResponseSerializer(permissions, many=True)
            data.append(
                {
                    "resource_type": resource_type,
                    "resource_type_display": display_name,
                    "permissions": serializer.data,
                }
            )

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permissions by resource type fetched successfully",
            data=data,
        )


class RolePermissionListAPIView(APIView):
    """API view to list permissions for a specific role"""

    permission_classes = [CanManageRoles]

    def get(self, request, role_id):
        # Check if role exists first
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return generic_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Role not found",
                data=None,
            )

        # Query role permissions directly to avoid linter issues with reverse relationships
        # Django's reverse relationship 'role_permissions' is dynamically created
        # We use direct queries for better static analysis support
        role_permissions = RolePermission.objects.filter(role=role).select_related(
            "permission"
        )

        serializer = RolePermissionDetailSerializer(role_permissions, many=True)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Role permissions fetched successfully",
            data=serializer.data,
        )


class RolePermissionBulkUpdateAPIView(APIView):
    """API view to bulk update role permissions"""

    permission_classes = [CanManageRoles]

    @transaction.atomic
    def post(self, request):
        serializer = RolePermissionBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data["role_id"]
        permissions_data = serializer.validated_data["permissions"]

        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return generic_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Role not found",
                data=None,
            )

        # Clear existing permissions
        # Use direct query to avoid linter issues with reverse relationships
        RolePermission.objects.filter(role=role).delete()

        # Create new role permissions
        role_permissions = []
        for perm_data in permissions_data:
            permission = Permission.objects.get(id=perm_data["permission_id"])
            role_permission = RolePermission(
                role=role,
                permission=permission,
                is_granted=perm_data.get("is_granted", True),
                subscription_level=perm_data.get("subscription_level"),
            )
            role_permissions.append(role_permission)

        RolePermission.objects.bulk_create(role_permissions)

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Role permissions updated successfully",
            data={"updated_count": len(role_permissions)},
        )
