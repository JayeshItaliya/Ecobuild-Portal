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
from cms.models.module import FAQ
from cms.serializers.faq_serializer import FAQListSerializer
from cms.serializers.faq_serializer import FAQSerializer


class BaseFAQAPIView(TranslatedResponseMixin):
    """
    Base API view for FAQ, provides queryset, serializer, and permissions.
    """

    queryset = FAQ.objects.all().order_by("order", "-created_at")
    serializer_class = FAQSerializer
    response_serializer_class = FAQListSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["question", "answer"]
    ordering_fields = ["order", "created_at"]


class FAQListCreateAPIView(BaseFAQAPIView, ListCreateAPIView):
    """API view to list and create FAQs."""

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request, *args, **kwargs):
        """List all FAQs, filtered and translated as needed."""
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            data = self.response_serializer_class(page, many=True).data
            return self.get_paginated_response(
                {"data": data, "message": "FAQs fetched successfully"}
            )
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        return Response(
            {"data": serializer.data, "message": "FAQs fetched successfully"},
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """Create a new FAQ."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(instance).data,
                "message": "FAQ created successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class FAQRetrieveUpdateDestroyAPIView(BaseFAQAPIView, RetrieveUpdateDestroyAPIView):
    """API view to retrieve, update, or delete a specific FAQ."""

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [AllowAny()]

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific FAQ."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response(
            {"data": serializer.data, "message": "FAQ fetched successfully"},
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific FAQ."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save(updated_by=request.user)
        return Response(
            {
                "data": self.response_serializer_class(updated_instance).data,
                "message": "FAQ updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific FAQ."""
        instance = self.get_object()
        instance.delete(request.user)
        return Response(
            {"message": "FAQ deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
