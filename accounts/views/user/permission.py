from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import TranslatedResponseMixin
from accounts.models import Permission
from accounts.serializers.permission import PermissionResponseSerializer
from accounts.serializers.permission import PermissionSerializer
from backend.utils import CustomPagination
from backend.utils import generic_response


class BasePermissionAPIView(TranslatedResponseMixin):
    """Base API view for Permission, provides queryset, serializer, and permissions."""

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    response_serializer_class = PermissionResponseSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]


class PermissionListCreateAPIView(BasePermissionAPIView, ListCreateAPIView):
    """API view to list and create permissions."""

    def get(self, request, *args, **kwargs):
        """List all permissions with proper translations."""
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permissions fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        """Create a new permission."""
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
    """API view to retrieve, update, or delete a specific Permission instance."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific permission."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permission fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific permission."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=self.request.user)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Permission updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific permission."""
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Permission deleted successfully.",
        )
