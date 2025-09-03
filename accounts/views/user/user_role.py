from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from accounts.models import Role
from accounts.serializers.user_role import RoleResponseSerializer
from accounts.serializers.user_role import RoleSerializer


class BaseRoleAPIView(TranslatedResponseMixin):
    """Base API view for Role, provides queryset, serializer, and permissions."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    response_serializer_class = RoleResponseSerializer
    permission_classes = [IsAuthenticated]


class RoleListCreateAPIView(BaseRoleAPIView, ListCreateAPIView):
    """API view to list and create roles."""

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            data = self.response_serializer_class(page, many=True).data
            return self.get_paginated_response({"data": data})
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(instance).data,
                "message": "Role created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class RoleRetrieveUpdateDestroyAPIView(BaseRoleAPIView, RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete a specific Role instance."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific role."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """Partially update a specific role."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=self.request.user)
        return Response(
            {
                "data": self.response_serializer_class(instance).data,
                "message": "Role updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific role."""
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            {"message": "Role deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )
