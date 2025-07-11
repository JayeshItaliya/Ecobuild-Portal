from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from accounts.models import Role
from accounts.serializers.user_role import RoleResponseSerializer
from accounts.serializers.user_role import RoleSerializer


class BaseRoleAPIView:
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    response_serializer_class = RoleResponseSerializer


class RoleListCreateAPIView(BaseRoleAPIView, ListCreateAPIView):

    def get(self, request):

        # Apply search filter
        instance = self.filter_queryset(self.get_queryset())

        # Paginate the queryset
        page = self.paginate_queryset(instance)

        if page is not None:
            # Serialize paginated data
            data = self.response_serializer_class(page, many=True).data
            return self.get_paginated_response(data)

        serializer = self.response_serializer_class(instance=instance, many=True)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class RoleRetrieveUpdateDestroyAPIView(BaseRoleAPIView, RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific Initiative instance.

    Inherits from RetrieveUpdateDestroyAPIView to handle GET (retrieve), PATCH (update),
    and DELETE requests. Includes optimized queryset with related fields.
    """

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to retrieve initiatives created by the authenticated user.
        Retrieves initiatives from the database, serializes them, and returns a response.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH request to partially update a specific Initiative.
        Validates incoming data, performs partial update, and returns a response.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(updated_by=self.request.user)

        return Response(
            data={
                "data": self.get_serializer(instance).data,
                "message": "Role updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE request to delete a specific Initiative.
        Checks permission, deletes the instance, and returns a response.
        """
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            data={
                "message": "Role deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
