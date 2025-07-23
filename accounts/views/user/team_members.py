from rest_framework.generics import ListAPIView

from accounts.models import User
from accounts.serializers.team_member import TeamMembersListSerializer
from backend.enums import ActionType
from backend.utils import CustomPagination
from backend.utils import create_audit_log


class BaseUserListAPIView(ListAPIView):
    """
    API view for listing team members.
    """

    queryset = User.objects.exclude(deleted_at__isnull=False)
    # permission_classes = [IsAuthenticated]


class TeamMemberListAPIView(BaseUserListAPIView):
    pagination_class = CustomPagination
    serializer_class = TeamMembersListSerializer

    def list(self, request, *args, **kwargs):
        # Log the action
        create_audit_log(request.user, module="", action=ActionType.VIEW)

        # Call the parent `list` to handle response
        return super().list(request, *args, **kwargs)
