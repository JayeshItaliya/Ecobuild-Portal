from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cms.models.gallery import Gallery
from cms.serializers.gallery_serializer import GalleryListSerializer
from cms.serializers.gallery_serializer import GalleryResponseSerializer
from cms.serializers.gallery_serializer import GallerySerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
class BaseGalleryAPIView:
    """
    Base API view for Gallery, provides queryset, serializer, and permissions.
    """

    queryset = Gallery.objects.order_by("-created_at")
    serializer_class = GallerySerializer
    list_serializer_class = GalleryListSerializer
    response_serializer_class = GalleryResponseSerializer
    permission_classes = [IsAuthenticated]


class GalleryListAPIView(BaseGalleryAPIView, ListCreateAPIView):
    """API view to list and create galleries."""

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
        responses={status.HTTP_201_CREATED: openapi.Response(
            description="Gallery created successfully",
            schema=GalleryResponseSerializer(),
        )},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        gallery = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(gallery).data,
                "message": "Gallery created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class GalleryRetrieveUpdateDestroyAPIView(
    BaseGalleryAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific gallery."""

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
                "message": "Gallery updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            {"message": "Gallery deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
