from cms.models import Document, DocumentAccess
from cms.serializers.document_serializer import DocumentAccessSerializer, DocumentSerializer
from rest_framework import viewsets, permissions

from rest_framework.filters import SearchFilter, OrderingFilter


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['created_at']
    permission_classes = [permissions.IsAuthenticated]


class DocumentAccessViewSet(viewsets.ModelViewSet):
    queryset = DocumentAccess.objects.select_related("user", "document")
    serializer_class = DocumentAccessSerializer
    permission_classes = [permissions.IsAdminUser]
