from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cms.models.product import ProductCategory
from cms.serializers.product.product_category_serializer import (
    ProductCategoryListSerializer,
)
from cms.serializers.product.product_category_serializer import (
    ProductCategoryResponseSerializer,
)
from cms.serializers.product.product_category_serializer import (
    ProductCategorySerializer,
)


class BaseProductCategory:
    """
    Base API view for Product Category, provides queryset, serializer, and permissions.
    """

    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    list_serializer_class = ProductCategoryListSerializer
    response_serializer_class = ProductCategoryResponseSerializer
    permission_classes = [IsAuthenticated]


class ProductCategoryListCreateAPIView(BaseProductCategory, ListCreateAPIView):
    """API view to list and create product categories."""

    def get(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(parent__isnull=True)
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
        category = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(category).data,
                "message": "Product category created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class ProductCategoryRetrieveUpdateDestroyAPIView(
    BaseProductCategory, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific product category."""

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
                "message": "Product category updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            {"message": "Product category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
