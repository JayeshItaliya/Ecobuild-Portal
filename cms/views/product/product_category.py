from django.db.models import Count
from django.db.models import Q
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.models.product import ProductCategory
from cms.serializers.product.product_category_serializer import (
    DropDownChoicesListSerializer,
)
from cms.serializers.product.product_category_serializer import (
    ProductCategoryListSerializer,
)
from cms.serializers.product.product_category_serializer import (
    ProductCategorySerializer,
)


class BaseProductCategoryAPIView(TranslatedResponseMixin):
    """
    Base API view for Product Category with queryset, serializers, and filters.
    """

    queryset = (
        ProductCategory.objects.all()
        .prefetch_related("children")
        .order_by("-created_at")
    )
    serializer_class = ProductCategorySerializer
    list_serializer_class = ProductCategoryListSerializer
    response_serializer_class = ProductCategoryListSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
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
            message="Product category with children created successfully.",
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
            message="Product category with children updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product category deleted successfully.",
        )


class DropdownValuesAPIView(BaseProductCategoryAPIView, ListCreateAPIView):
    list_serializer_class = DropDownChoicesListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        type = self.request.query_params.get("type")
        if type:
            queryset = queryset.filter(category_type=type)
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(parent__isnull=True)
            .order_by("created_at")
        )
        serializer = self.list_serializer_class(
            queryset, many=True, context={"request": request}
        )
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Dropdown values fetched successfully",
            data=serializer.data,
        )


class ProductCategoryDropdownAPIView(TranslatedResponseMixin, ListAPIView):
    """
    API view for product category dropdown used during product creation.

    Filtering logic:
    - Hide parent categories that have child categories
    - Show parent categories only if they have NO children AND have NO products
    - Show child categories only if they have NO products assigned
    - Hide any category that is assigned to products
    """

    queryset = ProductCategory.objects.all().prefetch_related("children")
    serializer_class = ProductCategoryListSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by category_type if provided
        category_type = self.request.query_params.get("type")
        if category_type:
            queryset = queryset.filter(category_type=category_type)

        return queryset

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)

        queryset = self.filter_queryset(self.get_queryset())

        # Annotate with counts for children and products
        queryset = queryset.annotate(
            children_count=Count("children"), products_count=Count("products")
        )

        # Filter logic:
        # 1. Show parent categories only if they have NO children AND have NO products
        # 2. Show child categories only if they have NO products
        # 3. Hide any category that is assigned to products
        queryset = queryset.filter(
            Q(
                parent__isnull=True, children_count=0, products_count=0
            )  # Parent categories with no children and no products
            | Q(
                parent__isnull=False, products_count=0
            )  # Child categories with no products
        ).order_by("-created_at")

        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request, "lang_code": lang_code}
        )

        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product category dropdown values fetched successfully",
            data=response_data,
        )
