from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from backend.utils import CustomPagination
from cms.models import BlogPost
from cms.serializers.blog_management import BlogManagementSerializer


class BaseBlogManagement:
    queryset = BlogPost.objects.all()
    list_serializer_class = BlogManagementSerializer
    serializer_class = BlogManagementSerializer
    response_serializer_class = BlogManagementSerializer
    pagination_class = CustomPagination


class BlogManagementListCreateAPIVIew(BaseBlogManagement, ListCreateAPIView):

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
                "message": "Blog created successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class BlogManagementRetrieveUpdateDestroyAPIView(
    BaseBlogManagement, RetrieveUpdateDestroyAPIView
):

    http_method_names = ["get", "patch", "delete"]
    # queryset = Measure.objects.select_related("measure_type", "created_by")

    def get(self, request, *args, **kwargs):
        """
        Handles GET request to retrieve Measures created by the authenticated user.
        Retrieves Measures from the database, serializes them, and returns a response.
        """
        instance = self.get_object()
        serializer = self.response_serializer_class(instance)
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH request to partially update a specific BaseMeasureElements.
        Validates incoming data, performs partial update, and returns a response.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            data={
                "data": self.response_serializer_class(updated_data).data,
                "message": "Blog updated successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        Handles DELETE request to delete a specific Measures.
        Checks permission, deletes the instance, and returns a response.
        """
        instance = self.get_object()
        instance.delete(self.request.user)
        return Response(
            data={
                "message": "Blog deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
