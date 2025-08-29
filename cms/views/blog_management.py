from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.utils import CustomPagination
from cms.models.module import BlogPost
from cms.serializers.blog_management import BlogManagementSerializer
from cms.serializers.blog_management import BlogResponseSerializer


class BaseBlogManagement:
    """Base API view for Blog Management, provides queryset, serializer, and permissions."""

    queryset = BlogPost.objects.all()
    list_serializer_class = BlogManagementSerializer
    serializer_class = BlogManagementSerializer
    response_serializer_class = BlogResponseSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]


class BlogManagementListCreateAPIVIew(BaseBlogManagement, ListCreateAPIView):
    """API view to list and create blog posts."""

    def get(self, request, *args, **kwargs):
        instance = self.get_queryset()
        page = self.paginate_queryset(instance)
        if page is not None:
            data = self.list_serializer_class(
                page, many=True, context={"request": request}
            ).data
            return self.get_paginated_response({"data": data})
        serializer = self.list_serializer_class(
            instance=instance, many=True, context={"request": request}
        )
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        blog_post = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(blog_post).data,
                "message": "Blog created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class BlogManagementRetrieveUpdateDestroyAPIView(
    BaseBlogManagement, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific blog post."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.response_serializer_class(instance)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(instance).data,
                "message": "Blog updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            {"message": "Blog deleted successfully."}, status=status.HTTP_204_NO_CONTENT
        )
