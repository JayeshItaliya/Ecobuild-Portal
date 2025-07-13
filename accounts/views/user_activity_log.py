from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from accounts.models import ActivityLog
from accounts.serializers.user_activity_log import UserActivityLogSerializer


class UserActivityLogListAPIView(ListAPIView):
    queryset = ActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer
    pagination_class = None

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
