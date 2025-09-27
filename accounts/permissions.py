from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    """
    Custom permission class to check if user's role has the required permission.
    """

    def __init__(self, required_action, required_resource):
        """
        Initialize with required permission parameters.

        Args:
            required_action (str): The required action e.g., "create", "read", "update"
            required_resource (str): The resource being accessed e.g., "booking", "user"
        """
        self.required_action = required_action
        self.required_resource = required_resource

    def has_permission(self, request, view):
        # Super users bypass all permission checks
        if request.user.is_superuser:
            return True

        # Users must be authenticated and have a role
        user = request.user
        if not user.is_authenticated or not user.role:
            return False

        # Check if the user's role has the required permission
        return user.role.has_permission(self.required_action, self.required_resource)


def permission_required(action, resource):
    """
    Decorator to easily apply HasRolePermission to views.

    Example usage:
    @permission_required('create', 'booking')
    class BookingCreateView(CreateAPIView):
        pass
    """
    return lambda view: type(
        f"{action.title()}{resource.title()}Permission",
        (HasRolePermission,),
        {"__init__": lambda self: HasRolePermission.__init__(self, action, resource)},
    )
