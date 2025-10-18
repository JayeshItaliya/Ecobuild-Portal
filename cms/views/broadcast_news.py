from django.db.models import F
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from accounts.mixins import TranslatedResponseMixin
from backend.utils import CustomPagination
from backend.utils import generic_response
from cms.models.broadcast_news import BroadcastNews
from cms.serializers.broadcast_news_serializer import (
    BroadcastNewsCreateUpdateSerializer,
)
from cms.serializers.broadcast_news_serializer import BroadcastNewsDetailedSerializer
from cms.serializers.broadcast_news_serializer import BroadcastNewsFeaturedSerializer
from cms.serializers.broadcast_news_serializer import BroadcastNewsListSerializer


class BaseBroadcastNewsManagement(TranslatedResponseMixin):
    """Base class for Broadcast News Management with common configurations"""

    queryset = BroadcastNews.objects.filter(deleted_at__isnull=True)
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        "title",
        "channel_name",
        "interviewer_name",
        "interviewee_name",
        "description",
    ]
    ordering_fields = [
        "broadcast_date",
        "interview_date",
        "created_at",
        "display_order",
        "views_count",
    ]


class BroadcastNewsManagementViewSet(BaseBroadcastNewsManagement, ModelViewSet):
    """
    ViewSet for admin to manage broadcast news (CRUD operations)
    Requires authentication
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BroadcastNewsCreateUpdateSerializer
        elif self.action == "retrieve":
            return BroadcastNewsDetailedSerializer
        return BroadcastNewsListSerializer

    def get_queryset(self):
        queryset = super().queryset

        # Filter by status if provided
        status_param = self.request.query_params.get("status", None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by featured
        is_featured = self.request.query_params.get("is_featured", None)
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == "true"
            queryset = queryset.filter(is_featured=is_featured_bool)

        return queryset

    def list(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.get_serializer(queryset, many=True)
        response_data = self.get_paginated_response(serializer.data).data

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Broadcast news fetched successfully",
            data=response_data,
        )

    def retrieve(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.get_object()
        instance = self.translate_instance(instance, lang_code)
        serializer = self.get_serializer(instance)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Broadcast news details fetched successfully",
            data=serializer.data,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Set created_by if user is authenticated
        if request.user.is_authenticated:
            serializer.save(created_by=request.user)
        else:
            serializer.save()

        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Broadcast news created successfully",
            data=serializer.data,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Set updated_by if user is authenticated
        if request.user.is_authenticated:
            serializer.save(updated_by=request.user)
        else:
            serializer.save()

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Broadcast news updated successfully",
            data=serializer.data,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete(deleted_by_user=request.user)
        return generic_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Broadcast news deleted successfully",
        )


class BroadcastNewsPublicListView(BaseBroadcastNewsManagement, ListAPIView):
    """
    Public API to list published broadcast news
    No authentication required
    """

    permission_classes = [AllowAny]
    serializer_class = BroadcastNewsListSerializer

    def get_queryset(self):
        queryset = super().queryset.filter(status="Published")
        return queryset

    def get(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        queryset = self.filter_queryset(self.get_queryset())
        queryset = self.paginate_queryset(queryset) or queryset
        queryset = self.translate_queryset(queryset, lang_code)
        serializer = self.get_serializer(queryset, many=True)
        response_data = self.get_paginated_response(serializer.data).data

        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Broadcast news fetched successfully",
            data=response_data,
        )


class BroadcastNewsPublicDetailView(BaseBroadcastNewsManagement, RetrieveAPIView):
    """
    Public API to view a single broadcast news item with all interview details
    No authentication required
    Increments view count when accessed
    """

    permission_classes = [AllowAny]
    serializer_class = BroadcastNewsDetailedSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return BroadcastNews.objects.filter(status="Published", deleted_at__isnull=True)

    def retrieve(self, request, *args, **kwargs):
        lang_code = self.get_language_code(request)
        instance = self.get_object()

        # Increment views count
        BroadcastNews.objects.filter(pk=instance.pk).update(
            views_count=F("views_count") + 1
        )
        instance.refresh_from_db()

        instance = self.translate_instance(instance, lang_code)
        serializer = self.get_serializer(instance)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Broadcast news details fetched successfully",
            data=serializer.data,
        )


class BroadcastNewsFeaturedView(ListAPIView):
    """
    Public API to get featured broadcast news
    No authentication required
    """

    permission_classes = [AllowAny]
    serializer_class = BroadcastNewsFeaturedSerializer
    pagination_class = None  # No pagination for featured items

    def get_queryset(self):
        return BroadcastNews.objects.filter(
            status="Published", is_featured=True, deleted_at__isnull=True
        ).order_by("-broadcast_date", "display_order")[
            :5
        ]  # Limit to 5 featured items

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Featured broadcast news fetched successfully",
            data=serializer.data,
        )
