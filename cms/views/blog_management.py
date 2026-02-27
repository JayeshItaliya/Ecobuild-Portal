from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.models.blog import BlogPost
from cms.serializers.blog_management import BlogManagementSerializer
from cms.serializers.blog_management import BlogResponseSerializer


class BaseBlogManagement:
    """Base API view for Blog Management, provides queryset, serializer, and permissions."""

    queryset = BlogPost.objects.all()
    serializer_class = BlogManagementSerializer
    response_serializer_class = BlogResponseSerializer

    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = ["status"]

    search_fields = [
        "title",
        "content",
        "created_by__first_name",
        "created_by__last_name",
    ]
    ordering_fields = ["created_at", "title", "updated_at", "is_active"]


class BlogManagementListCreateAPIView(BaseBlogManagement, ListCreateAPIView):
    """API view to list and create blog posts."""

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Blogs fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        blog_post = serializer.save()
        response_data = self.response_serializer_class(
            blog_post, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Blog created successfully.",
            data=response_data,
        )


class BlogManagementRetrieveUpdateDestroyAPIView(
    BaseBlogManagement, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific blog post."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Blog fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Blog updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Blog deleted successfully.",
        )
