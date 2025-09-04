from rest_framework import serializers

from cms.models.notification import AdminNotification


class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = ["id", "message", "is_read", "created_at", "contact_message"]
