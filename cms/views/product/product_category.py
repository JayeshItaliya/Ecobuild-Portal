from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
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


class BaseProductCategoryAPIView(TranslatedResponseMixin):
    """
    Base API view for Product Category with queryset, serializers, and filters.
    """

    queryset = ProductCategory.objects.all().order_by("-created_at")
    serializer_class = ProductCategorySerializer
    list_serializer_class = ProductCategoryListSerializer
    response_serializer_class = ProductCategoryResponseSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]


class ProductCategoryListCreateAPIView(BaseProductCategoryAPIView, ListCreateAPIView):
    """API view to list and create product categories."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())

        # Only root categories
        queryset = queryset.filter(parent__isnull=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            data = self.list_serializer_class(
                page, many=True, context={"request": request}
            ).data
            response = self.get_paginated_response(data)
            response.data["message"] = "Product categories fetched successfully"
            return response

        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "data": serializer.data,
                "message": "Product categories fetched successfully",
            },
            status=status.HTTP_200_OK,
        )

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
    BaseProductCategoryAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific product category."""

    http_method_names = ["get", "patch", "delete"]

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response(
            {
                "data": serializer.data,
                "message": "Product category fetched successfully",
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(updated_instance).data,
                "message": "Product category updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(request.user)
        return Response(
            {"message": "Product category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
