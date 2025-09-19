
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.filters.filters import GalleryCategoryFilter
from cms.models.gallery import GalleryCategory
from cms.serializers.gallery_category_serializer import GalleryCategoryChoicesSerializer
from cms.serializers.gallery_category_serializer import GalleryCategoryListSerializer
from cms.serializers.gallery_category_serializer import (
    GalleryCategoryResponseSerializer,
)
from cms.serializers.gallery_category_serializer import GalleryCategorySerializer


class BaseGalleryCategory(TranslatedResponseMixin):
    """Base API view for Gallery Category, provides queryset, serializer, and permissions."""

    queryset = GalleryCategory.objects.order_by("-created_at")
    serializer_class = GalleryCategorySerializer
    list_serializer_class = GalleryCategoryListSerializer
    response_serializer_class = GalleryCategoryResponseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GalleryCategoryFilter
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]


class GalleryCategoryListCreateAPIView(BaseGalleryCategory, ListCreateAPIView):
    """API view to list and create gallery categories."""

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)

        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request, "lang_code": lang_code}
        )
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery categories fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        gallery_category = serializer.save()
        response_data = self.response_serializer_class(gallery_category).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Gallery category created successfully.",
            data=response_data,
        )


class GalleryCategoryRetrieveUpdateDestroyAPIView(
    BaseGalleryCategory, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific gallery category."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery category fetched successfully.",
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
            message="Gallery category updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Gallery category deleted successfully.",
        )


class GalleryCategoryChoicesAPIView(TranslatedResponseMixin, ListAPIView):
    """
    API view to list gallery category choices.
    It uses the GalleryCategoryChoicesSerializer to serialize the data.
    """

    queryset = GalleryCategory.objects.all()
    serializer_class = GalleryCategoryChoicesSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        type_param = self.request.query_params.get("type", "Image")
        if type_param:
            queryset = queryset.filter(type=type_param)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        lang_code = self.get_language_code(request)
        translated_queryset = self.translate_queryset(queryset, lang_code)
        response_data = self.get_serializer(translated_queryset, many=True).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Gallery category choices fetched successfully.",
            data=response_data,
        )
