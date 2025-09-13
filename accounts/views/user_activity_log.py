from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.models import ActivityLog
from accounts.serializers.user_activity_log import UserActivityLogSerializer
from backend.utils import generic_response


class UserActivityLogListAPIView(ListAPIView):
    """API view to list all user activity logs."""

    queryset = ActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="User activity logs fetched successfully",
            data=response_data,
        )
