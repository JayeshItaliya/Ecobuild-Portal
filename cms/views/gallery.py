from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from cms.models.gallery import GalleryCategory
from cms.serializers.gallery_serializer import GalleryCategoryResponseSerializer
from cms.serializers.gallery_serializer import GalleryCategorySerializer


class BaseGalleryCategoryAPIView(TranslatedResponseMixin):
    queryset = GalleryCategory.objects.all()
    serializer_class = GalleryCategorySerializer
    response_serializer_class = GalleryCategoryResponseSerializer


class GalleryCategoryListCreateAPIView(BaseGalleryCategoryAPIView, ListCreateAPIView):
    """
    API to list and create Gallery Categories
    """

    def get(self, request):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            data = self.response_serializer_class(page, many=True).data
            return self.get_paginated_response(data)

        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class GalleryCategoryRetrieveUpdateDestroyAPIView(
    BaseGalleryCategoryAPIView, RetrieveUpdateDestroyAPIView
):
    """
    API to retrieve, update, or delete a GalleryCategory
    """

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save(updated_by=self.request.user)

        return Response(
            data={
                "data": self.response_serializer_class(updated_instance).data,
                "message": "Gallery category updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            data={"message": "Gallery category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
