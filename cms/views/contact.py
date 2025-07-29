from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cms.models import ContactMessage
from cms.serializers import ContactMessageListSerializer
from cms.serializers import ContactMessageSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contact messages.

    This viewSet provides CRUD operations for ContactMessage model.
    - Anyone can create a contact message (no authentication required)
    - Only authenticated users (admins) can view, update, or delete messages

    Filtering:
    - Filter by is_read status
    - Search by name, email, subject, or message content

    Ordering:
    - Default ordering is by created_at (newest first)
    - Can be ordered by any field
    """

    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageSerializer
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
        """
        - Allow anyone to create a contact message
        - Require authentication for all other actions
        """
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Use different serializers for list and detail views.
        """
        if self.action == "list":
            return ContactMessageListSerializer
        return ContactMessageSerializer

    def list(self, request, *args, **kwargs):
        """
        Get a list of all contact messages.
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact messages retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Get a single contact message by ID.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "data": serializer.data,
                "message": "Contact message retrieved successfully",
            },
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """
        Create a new contact message.
        """
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
        """
        Update an existing contact message.
        """
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
        """
        Delete a contact message.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Contact message deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def perform_update(self, serializer):
        """
        Custom update logic to handle marking messages as read.
        """
        # If is_read is being set to True and it wasn't before, update the timestamp
        if (
            "is_read" in serializer.validated_data
            and serializer.validated_data["is_read"]
            and not serializer.instance.is_read
        ):
            serializer.save()
        else:
            serializer.save()
