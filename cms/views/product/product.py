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
from cms.models.product import Product
from cms.serializers.product.product_serializer import ProductResponseSerializer
from cms.serializers.product.product_serializer import ProductSerializer


class BaseProductAPIView(TranslatedResponseMixin):
    """
    Base API view for Product with queryset, serializers, and filters.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    serializer_class = ProductSerializer
    response_serializer_class = ProductResponseSerializer
    queryset = (
        Product.objects.select_related("category", "category__parent")
        .all()
        .order_by("-created_at")
    )
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]


class ProductListCreateAPIView(BaseProductAPIView, ListCreateAPIView):
    """API view to list and create products."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        """
        List products with optional filtering by category and subcategory.

        Query Parameters:
            - category: Filter by category ID (can be parent category or subcategory)
            - parent_category: Filter by parent category ID only
            - subcategory: Filter by subcategory ID only (category with a parent)
        """
        queryset = self.get_queryset()

        # Filter by category (handles both parent and subcategory)
        category_id = request.query_params.get("category")
        if category_id:
            try:
                queryset = queryset.filter(category_id=category_id)
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid category ID format.",
                    data={},
                )

        # Filter by parent category only
        parent_category_id = request.query_params.get("parent_category")
        if parent_category_id:
            try:
                queryset = queryset.filter(category__parent_id=parent_category_id)
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid parent category ID format.",
                    data={},
                )

        # Filter by subcategory only (category with a parent)
        subcategory_id = request.query_params.get("subcategory")
        if subcategory_id:
            try:
                queryset = queryset.filter(
                    category_id=subcategory_id, category__parent__isnull=False
                )
            except ValueError:
                return generic_response(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    error_message="Invalid subcategory ID format.",
                    data={},
                )

        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(queryset)
        queryset = self.paginate_queryset(queryset) or queryset
        products = self.translate_queryset(queryset, lang_code)

        serializer = self.response_serializer_class(
            products, many=True, context={"request": request}
        )
        response_data = self.get_paginated_response(serializer.data).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Products fetched successfully",
            data=response_data,
        )

    def post(self, request, *args, **kwargs):
        """Create a new product with category validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Translate instance based on user's language preference (like about_us.py)
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(instance, lang_code)

        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Product created successfully.",
            data=response_data,
        )


class ProductRetrieveUpdateDestroyAPIView(
    BaseProductAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific product."""

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific product."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product fetched successfully",
            data=response_data,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific product."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Translate instance based on user's language preference (like about_us.py)
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(instance, lang_code)

        response_data = self.response_serializer_class(
            instance, context={"request": request}
        ).data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Product updated successfully.",
            data=response_data,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific product."""
        instance = self.get_object()
        instance.delete(self.request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Product deleted successfully.",
        )
