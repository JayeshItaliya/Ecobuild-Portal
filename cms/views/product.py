from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from cms.models.product import ProductCategory
from cms.serializers.product.product_category_serializer import (
    ProductCategorySerializer,
)


class ProductCategoryListCreateAPIView(ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def get(self, request):
        """
        Handles GET request to retrieve initiatives created by the authenticated user.
        Retrieves initiatives from the database, serializes them, and returns a response.
        """
        # instance = self.get_filtered_queryset()

        # Apply search filter
        instance = self.get_queryset()

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
