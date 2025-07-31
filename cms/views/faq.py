from django.db.models import Q
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from backend.utils import CustomPagination
from cms.models.module import FAQ
from cms.serializers.faq_serializer import FAQListSerializer
from cms.serializers.faq_serializer import FAQSerializer


class FAQViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing FAQ entries.

    Provides CRUD operations for FAQ model with appropriate permissions:
    - Admin users can create, update, and delete FAQs
    - All users can read FAQs

    Supports filtering by active status and searching by keywords in question and answer.
    """

    queryset = FAQ.objects.all().order_by("order", "-created_at")
    serializer_class = FAQSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["question", "answer"]
    ordering_fields = ["order", "created_at"]

    def get_permissions(self):
        """
        Override to set custom permissions:
        - Admin permissions for create, update, delete operations
        - Allow read access to all users
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on the action.
        """
        if self.action == "list":
            return FAQListSerializer
        return FAQSerializer

    def get_queryset(self):
        """
        Filter queryset based on request parameters and user permissions.
        - Admin users can see all FAQs
        - Regular users can only see active FAQs
        - Support search by keywords in question and answer
        """
        queryset = FAQ.objects.all().order_by("order", "-created_at")

        # Only show active FAQs to non-admin users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        # Handle search parameter for keyword search
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(
                Q(question__icontains=search_query) | Q(answer__icontains=search_query)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new FAQ entry.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"data": serializer.data, "message": "FAQ created successfully"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        """
        Update an existing FAQ entry.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"data": serializer.data, "message": "FAQ updated successfully"},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete an FAQ entry.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "FAQ deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
