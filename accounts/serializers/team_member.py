from rest_framework.serializers import ModelSerializer

from accounts.models import User


class TeamMembersListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "role", "user_type"]
