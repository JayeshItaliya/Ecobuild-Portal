from django_filters.rest_framework import DjangoFilterBackend
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

        queryset = self.filter_queryset(self.get_queryset()).filter(parent__isnull=True)
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)

        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request, "lang_code": lang_code}
        )

        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product categories fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        response_data = self.response_serializer_class(category).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Product category created successfully.",
            data=response_data,
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
        response_data = self.response_serializer_class(instance).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product category fetched successfully",
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
            message="Product category updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product category deleted successfully.",
        )
