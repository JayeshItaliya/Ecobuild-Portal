"""
Custom permission classes for role-based access control
"""

from rest_framework import permissions


class CustomPermission(permissions.BasePermission):
    """
    Custom permission class that checks role-based permissions
    """

    def __init__(self, permission_codename=None, resource_type=None, action=None):
        """
        Initialize permission with either:
        - permission_codename: specific permission codename
        - resource_type and action: to build permission codename
        """
        self.permission_codename = permission_codename
        self.resource_type = resource_type
        self.action = action

        if not permission_codename and resource_type and action:
            pass

            # Build permission codename from resource and action
            self.permission_codename = f"{action.lower()}_{resource_type.lower()}"

    def has_permission(self, request, view):
        """
        Check if the user has the required permission
        """
        # Allow superusers
        if request.user and request.user.is_superuser:
            return True

        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user is active
        if not request.user.is_active:
            return False

        if not self.permission_codename:
            return False

        # Check if user has the specific permission
        return request.user.has_permission(self.permission_codename)


class HasResourcePermission(permissions.BasePermission):
    """
    Permission class that checks if user has permission for a specific resource type and action
    """

    def __init__(self, resource_type, action=None):
        self.resource_type = resource_type
        self.action = action or "view"  # Default to view if no action specified

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Get action from request method if not specified
        action = self.action
        if not action:
            action = self._get_action_from_method(request.method)

        return request.user.has_permission_for_resource(self.resource_type, action)

    def _get_action_from_method(self, method):
        """Map HTTP method to action"""
        method_to_action = {
            "GET": "view",
            "POST": "create",
            "PATCH": "update",
            "PUT": "update",
            "DELETE": "delete",
        }
        return method_to_action.get(method.upper(), "view")


class HasSubscriptionLevel(permissions.BasePermission):
    """
    Permission class that checks if user has required subscription level
    """

    def __init__(self, required_subscription_type):
        pass

        self.required_subscription_type = required_subscription_type

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user._check_subscription_level(self.required_subscription_type)


class IsOwnerOrHasPermission(permissions.BasePermission):
    """
    Permission class that allows access if user is the owner or has the specified permission
    """

    def __init__(self, permission_codename=None, owner_field="created_by"):
        self.permission_codename = permission_codename
        self.owner_field = owner_field

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Check if user has the permission
        if self.permission_codename and request.user.has_permission(
            self.permission_codename
        ):
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Check if user is the owner
        owner = getattr(obj, self.owner_field, None)
        if owner and owner == request.user:
            return True

        # Check if user has the permission
        if self.permission_codename and request.user.has_permission(
            self.permission_codename
        ):
            return True

        return False


# Predefined permission classes for common use cases
class CanViewProducts(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="product", action="view")


class CanCreateProducts(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="product", action="create")


class CanEditProducts(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="product", action="update")


class CanDeleteProducts(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="product", action="delete")


class CanViewBlogs(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="blog", action="view")


class CanViewDocuments(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="document", action="view")


class CanDownloadCADFiles(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="cad_file", action="view")


class CanViewLearningVideos(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="learning_video", action="view")


class CanManageUsers(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="user", action="view")


class CanManageRoles(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="role", action="view")


class CanManagePermissions(CustomPermission):
    def __init__(self):
        super().__init__(resource_type="permission", action="view")


class PremiumContentAccess(permissions.BasePermission):
    """
    Permission for premium content that requires subscription
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Check if user has premium subscription
        from accounts.enums import SubscriptionTypeChoices

        return request.user._check_subscription_level(SubscriptionTypeChoices.PREMIUM)
