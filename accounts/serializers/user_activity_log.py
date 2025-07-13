from rest_framework.serializers import ModelSerializer

from accounts.models import ActivityLog


class UserActivityLogSerializer(ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = "__all__"
