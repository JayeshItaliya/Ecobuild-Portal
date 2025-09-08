from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from cms.filters.filters import DocumentFilter
from cms.models.document import Document
from cms.models.document import DocumentAccess
from cms.serializers.document_serializer import DocumentAccessSerializer
from cms.serializers.document_serializer import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Document objects. Supports CRUD operations, search, and ordering."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentFilter
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "created_by"]
    permission_classes = [permissions.IsAuthenticated]


class DocumentAccessViewSet(viewsets.ModelViewSet):
    """ViewSet for managing DocumentAccess objects. Admin-only access."""

    queryset = DocumentAccess.objects.select_related("user", "document")
    serializer_class = DocumentAccessSerializer
    permission_classes = [permissions.IsAdminUser]
