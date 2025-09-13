from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.filters.filters import GalleryFilter
from cms.models.gallery import Gallery
from cms.serializers.gallery_serializer import GalleryListSerializer
from cms.serializers.gallery_serializer import GalleryResponseSerializer
from cms.serializers.gallery_serializer import GallerySerializer


class BaseGalleryAPIView(TranslatedResponseMixin):
    """
    Base API view for Gallery, provides queryset, serializer, and permissions.
    """

    queryset = Gallery.objects.order_by("-created_at")
    serializer_class = GallerySerializer
    list_serializer_class = GalleryListSerializer
    response_serializer_class = GalleryResponseSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GalleryFilter
    ordering_fields = ["created_at"]


class GalleryListCreateAPIView(BaseGalleryAPIView, ListCreateAPIView):
    """API view to list and create galleries."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        queryset = self.translate_queryset(page, lang_code)
        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request, "lang_code": lang_code}
        )
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Galleries fetched successfully",
            data=response_data,
        )

    @swagger_auto_schema(
        operation_description="Create a new gallery",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "image": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_BINARY,
                    description="Upload an image file",
                ),
                "video": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_BINARY,
                    description="Upload a video file",
                ),
                "category": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Category ID or name",
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Gallery created successfully",
                schema=GalleryResponseSerializer(),
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        gallery = serializer.save()
        response_data = self.response_serializer_class(gallery).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Gallery created successfully.",
            data=response_data,
        )


class GalleryRetrieveUpdateDestroyAPIView(
    BaseGalleryAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific gallery."""

    http_method_names = ["get", "patch", "delete"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        response_data = self.response_serializer_class(updated_instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery deleted successfully.",
            data={},
        )
