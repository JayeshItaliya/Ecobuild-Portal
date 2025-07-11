from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView

from accounts.models import User
from accounts.serializers.team_member import TeamMembersListSerializer
from backend.utils import CustomPagination


class BaseUserListAPIView(ListAPIView):
    """
    API view for listing team members.
    """

    queryset = User.objects.exclude(deleted_at__isnull=False)
    # permission_classes = [IsAuthenticated]


class TeamMemberListAPIView(BaseUserListAPIView, CreateAPIView):
    pagination_class = CustomPagination
    serializer_class = TeamMembersListSerializer
