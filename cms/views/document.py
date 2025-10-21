from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from accounts.permissions import CanViewDocuments
from accounts.permissions import HasResourcePermission
from cms.models.document import Document
from cms.models.document import DocumentAccess
from cms.serializers.document_serializer import DocumentAccessSerializer
from cms.serializers.document_serializer import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Document objects. Supports CRUD operations, search, and ordering."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name", "created_by"]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [CanViewDocuments]
        elif self.action == "create":
            permission_classes = [HasResourcePermission("document", "create")]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [HasResourcePermission("document", "update")]
        elif self.action == "destroy":
            permission_classes = [HasResourcePermission("document", "delete")]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]


class DocumentAccessViewSet(viewsets.ModelViewSet):
    """ViewSet for managing DocumentAccess objects. Admin-only access."""

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = DocumentAccess.objects.select_related("user", "document")
    serializer_class = DocumentAccessSerializer
    permission_classes = [permissions.IsAdminUser]
