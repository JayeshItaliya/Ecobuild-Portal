from rest_framework import status
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from cms.models.gallery import GalleryCategory

from cms.serializers.gallery_category_serializer import (
    GalleryCategoryChoicesSerializer,
    GalleryCategoryListSerializer,
)
from cms.serializers.gallery_category_serializer import (
    GalleryCategoryResponseSerializer,
)
from cms.serializers.gallery_category_serializer import GalleryCategorySerializer


class BaseGalleryCategory(TranslatedResponseMixin):
    queryset = GalleryCategory.objects.order_by("-created_at")
    serializer_class = GalleryCategorySerializer
    list_serializer_class = GalleryCategoryListSerializer
    response_serializer_class = GalleryCategoryResponseSerializer


class GalleryCategoryListCreateAPIView(BaseGalleryCategory, ListCreateAPIView):
    def get(self, request, *args, **kwargs):
        """
        Handles GET request to retrieve gallery categories.
        Applies translation and pagination if applicable.
        """
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            data = self.list_serializer_class(
                page, many=True, context={"request": request}
            ).data
            return self.get_paginated_response(data)

        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            data={
                "data": serializer.data,
                "message": "Gallery categories fetched successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to create a new gallery category.
        Validates and saves the data, then returns the result.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        gallery_category = serializer.save()

        return Response(
            data={
                "data": self.response_serializer_class(gallery_category).data,
                "message": "Gallery category created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class GalleryCategoryRetrieveUpdateDestroyAPIView(
    BaseGalleryCategory, RetrieveUpdateDestroyAPIView
):
    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to retrieve a specific gallery category.
        Applies language translation if available.
        """
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response(
            data={
                "data": serializer.data,
                "message": "Gallery category fetched successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH request to update a specific gallery category.
        Applies partial update and returns the result.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        return Response(
            data={
                "data": self.response_serializer_class(updated_instance).data,
                "message": "Gallery category updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE request to remove a specific gallery category.
        """
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            data={
                "message": "Gallery category deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class GalleryCategoryChoicesAPIView(TranslatedResponseMixin, ListAPIView):
    """
    API view to list gallery category choices.
    It uses the GalleryCategoryChoicesSerializer to serialize the data.
    """

    queryset = GalleryCategory.objects.all()
    serializer_class = GalleryCategoryChoicesSerializer

    def get_queryset(self):
        user = self.request.user
        # if user.is_anonymous:
        #     return self.queryset.none()
        type = self.request.query_params.get("type", "Image")
        if type:
            self.queryset = self.queryset.filter(type=type)

        return self.queryset

    def get(self, request):
        """
        Handle GET requests to retrieve all user roles.
        Returns:
            Response: A DRF Response object containing serialized role data.
        """
        queryset = self.get_queryset()
        lang_code = self.get_language_code(request)
        translated_queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.serializer_class(translated_queryset, many=True)
        return Response(serializer.data)
