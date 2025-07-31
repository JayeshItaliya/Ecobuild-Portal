from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from cms.models.module import ContactMessage
from cms.serializers.contact_serializer import ContactMessageListSerializer
from cms.serializers.contact_serializer import ContactMessageSerializer


class ContactMessageViewSet(TranslatedResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing contact messages.
    - Public can create messages.
    - Authenticated users can list, update, delete.
    - Supports search, filter, ordering, and translations.
    """

    queryset = ContactMessage.objects.all().order_by("-created_at")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_read"]
    search_fields = ["name", "email", "subject", "message"]
    ordering_fields = ["created_at", "name", "email", "subject", "is_read"]
    ordering = ["-created_at"]

    def get_permissions(self):
        return [AllowAny()] if self.action == "create" else [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return ContactMessageListSerializer
        return ContactMessageSerializer

    def list(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact messages retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.get_object()
        instance = self.translate_instance(instance, lang_code)
        serializer = self.get_serializer(instance)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact message retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "data": serializer.data,
                "message": "Your message has been sent successfully. We will get back to you soon.",
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact message updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Contact message deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_update(self, serializer):
        # Optional: auto mark as read if `is_read` updated
        if (
            "is_read" in serializer.validated_data
            and serializer.validated_data["is_read"]
            and not serializer.instance.is_read
        ):
            serializer.save()
        else:
            serializer.save()
