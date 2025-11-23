from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import TranslatedResponseMixin
from accounts.models import Role
from accounts.permissions import CanManageRoles
from accounts.serializers.user_role import RoleResponseSerializer
from accounts.serializers.user_role import RoleSerializer
from backend.utils import CustomPagination
from backend.utils import generic_response


class BaseRoleAPIView(TranslatedResponseMixin):
    """Base API view for Role, provides queryset, serializer, and permissions."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    pagination_class = CustomPagination
    response_serializer_class = RoleResponseSerializer
    permission_classes = [IsAuthenticated, CanManageRoles]


class RoleListCreateAPIView(BaseRoleAPIView, ListCreateAPIView):
    """API view to list and create roles."""

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Roles fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Role created successfully.",
            data=response_data,
        )


class RoleRetrieveUpdateDestroyAPIView(BaseRoleAPIView, RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete a specific Role instance."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific role."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Role fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific role."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=self.request.user)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Role updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific role."""
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Role deleted successfully.",
        )
