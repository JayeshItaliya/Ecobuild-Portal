from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from accounts.serializers.team_member import TeamMembersListSerializer
from backend.enums import ActionType
from backend.utils import CustomPagination
from backend.utils import create_audit_log


class BaseUserListAPIView(ListAPIView):
    """Base API view for listing team members."""

    queryset = User.objects.exclude(deleted_at__isnull=False)
    permission_classes = [IsAuthenticated]


class TeamMemberListAPIView(BaseUserListAPIView):
    """API view to list all team members with pagination and audit logging."""

    pagination_class = CustomPagination
    serializer_class = TeamMembersListSerializer

    def list(self, request, *args, **kwargs):
        # Log the action
        create_audit_log(request.user, module="", action=ActionType.VIEW)
        response = super().list(request, *args, **kwargs)
        # Wrap the response data in a 'data' key for consistency
        if (
            hasattr(response, "data")
            and isinstance(response.data, dict)
            and "results" in response.data
        ):
            response.data = {
                "data": response.data["results"],
                "count": response.data.get("count", 0),
            }
        elif hasattr(response, "data"):
            response.data = {"data": response.data}
        return response
