from rest_framework import generics
from rest_framework import permissions

from cms.models.notification import AdminNotification
from cms.serializers.notification import AdminNotificationSerializer


class AdminNotificationListAPIView(generics.ListAPIView):
    queryset = AdminNotification.objects.all().order_by("-created_at")
    serializer_class = AdminNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optionally, filter for unread notifications only
        unread = self.request.query_params.get("unread")
        qs = super().get_queryset()
        if unread == "1":
            qs = qs.filter(is_read=False)
        return qs
