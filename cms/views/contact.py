from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from cms.models.module import ContactMessage
from cms.models.notification import AdminNotification
from cms.serializers.contact_serializer import ContactMessageListSerializer
from cms.serializers.contact_serializer import ContactMessageSerializer


class BaseContactMessageAPIView(TranslatedResponseMixin):
    """
    Base API view for Contact Message, provides queryset, serializer, and permissions.
    """

    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageSerializer
    response_serializer_class = ContactMessageListSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_read"]
    search_fields = ["name", "email", "subject", "message"]
    ordering_fields = ["created_at", "name", "email", "subject", "is_read"]


class ContactMessageListCreateAPIView(BaseContactMessageAPIView, ListCreateAPIView):
    """API view to list and create contact messages."""

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "POST" else [IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        """List all contact messages, filtered and translated as needed."""
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.translate_queryset(page, lang_code)
            serializer = self.response_serializer_class(page, many=True)
            return self.get_paginated_response(
                {
                    "data": serializer.data,
                    "message": "Contact messages retrieved successfully.",
                }
            )
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.response_serializer_class(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact messages retrieved successfully.",
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """Create a new contact message and notify admin."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Create admin notification
        name = request.data.get("name", "")
        subject = request.data.get("subject", "")
        message = f"New contact message from {name}: {subject}"

        notification = AdminNotification.objects.create(
            message=message, contact_message=instance
        )

        # Send notification to WebSocket group
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer

            from cms.serializers.notification import AdminNotificationSerializer

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",
                {
                    "type": "send_notification",
                    "notification": AdminNotificationSerializer(notification).data,
                },
            )
        except Exception:
            pass  # Optionally log error

        return Response(
            {
                "data": self.response_serializer_class(instance).data,
                "message": "Your message has been sent successfully.",
            },
            status=status.HTTP_201_CREATED,
        )


class ContactMessageRetrieveUpdateDestroyAPIView(
    BaseContactMessageAPIView, RetrieveUpdateDestroyAPIView
):
    """API view to retrieve, update, or delete a specific contact message."""

    http_method_names = ["get", "patch", "delete"]

    def get(self, request, *args, **kwargs):
        """Retrieve a specific contact message."""
        lang_code = self.get_language_code(request)
        instance = self.translate_instance(self.get_object(), lang_code)
        serializer = self.response_serializer_class(instance)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact message retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        """Partially update a specific contact message."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        return Response(
            {
                "data": self.response_serializer_class(updated_instance).data,
                "message": "Contact message updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """Delete a specific contact message."""
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Contact message deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
