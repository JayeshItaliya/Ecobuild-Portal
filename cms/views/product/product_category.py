from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
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
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    list_serializer_class = ProductCategoryListSerializer
    response_serializer_class = ProductCategoryResponseSerializer


class ProductCategoryListCreateAPIView(BaseProductCategory, ListCreateAPIView):

    def get(self, request):
        """
        Handles GET request to retrieve initiatives created by the authenticated user.
        Retrieves initiatives from the database, serializes them, and returns a response.
        """
        # instance = self.get_filtered_queryset()

        # Apply search filter
        instance = self.get_queryset().filter(parent__isnull=True)

        # Paginate the queryset
        page = self.paginate_queryset(instance)

        if page is not None:
            # Serialize paginated data
            data = self.list_serializer_class(
                page, many=True, context={"request": request}
            ).data
            return self.get_paginated_response(data)

        serializer = self.list_serializer_class(
            instance=instance, many=True, context={"request": request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to create a new measures.
        Validates incoming data, performs object creation, and returns a response.
        """

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        blog_post = serializer.save()

        return Response(
            data={
                "data": self.response_serializer_class(blog_post).data,
                "message": "Product category created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class ProductCategoryRetrieveUpdateDestroyAPIView(
    BaseProductCategory, RetrieveUpdateDestroyAPIView
):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    list_serializer_class = ProductCategoryListSerializer
    response_serializer_class = ProductCategoryResponseSerializer

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """
        Retrieve a single Product Category.

        Fetches the product category specified by the URL parameter `pk` (or UUID).
        Serializes the object using the response serializer and returns it.
        """
        instance = self.get_object()
        serializer = self.response_serializer_class(instance)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """
        Partially update a Product Category.

        Accepts only the fields to be updated and leaves other fields unchanged.
        Validates the incoming data, applies changes, and returns the updated object
        in the response serializer format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={
                "data": self.response_serializer_class(serializer.data).data,
                "message": "Product category updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        Delete a Product Category.

        Soft-deletes or permanently deletes the category instance (depending on model logic).
        Requires appropriate permissions. Returns a confirmation message.
        """
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            data={
                "message": "Product category deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
