import jwt
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import ValidationError

from accounts.models import ActivityLog
from accounts.models import User
from backend import settings


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render the data to JSON, adding custom formatting for API responses.

        Args:
            data (dict): The data to be rendered.
            accepted_media_type (str): The accepted media type for the response.
            renderer_context (dict): Contextual information for the renderer.

        Returns:
            bytes: The rendered JSON data.
        """

        # Initialize the response dictionary
        response_dict = {"code": 200, "data": {}, "message": ""}

        # Extract the response and its status code from the renderer context
        response = renderer_context["response"]
        response_status = response.status_code

        # Check if data contains 'data' key
        if isinstance(data, dict) and "data" in data:
            response_dict["data"] = data["data"]
        else:
            response_dict["data"] = data  # Include the serialized data

        # Check if data contains 'message' key
        if isinstance(data, dict) and "message" in data:
            response_dict["message"] = data["message"]

        # Update the response code in the response dictionary
        response_dict["code"] = response_status

        # Check for serializer errors in the renderer context
        if response_status >= 400:
            errors = response.data
            if isinstance(errors, dict):
                # Get the first error message in the dictionary, if any
                for value in errors.values():
                    if isinstance(value, list) and value:
                        response_dict["message"] = str(value[0])
                        break
                    if not isinstance(value, list):
                        response_dict["message"] = str(value)
                        break

        # Render the response dictionary as JSON
        return super().render(response_dict, accepted_media_type, renderer_context)


def token_validation(token):
    """
    Validate the given JWT token.

    Args:
        token (str): The JWT token to validate.

    Returns:
        User: The user associated with the token if valid.

    Raises:
        ValidationError: If the token is expired or invalid.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        # Extract email and user ID from the payload
        email, user_id = payload.get("email"), payload.get("user_id")

        # Check if email or user ID is provided
        if not email:
            # If email is not provided, use user ID to get the user object
            user = get_object_or_404(User, pk=user_id)
        else:
            # If email is provided, use email to get the user object
            user = get_object_or_404(User, email=email)

        return user
    except jwt.ExpiredSignatureError:
        # Raise validation error if token is expired
        raise ValidationError({"message": "Reset password URL is expired"})
    except jwt.exceptions.DecodeError:
        # Raise validation error if token is invalid
        raise ValidationError({"message": "Invalid Reset password URL"})


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


def create_audit_log(
    user, module, action, object_id=None, details=None, description=None
):
    """
    Utility function to create an audit log entry.

    :param user: The user who performed the action
    :param module: The name of the module where the action occurred
    :param action: The action type (create, edit, delete)
    :param object_id: ID of the affected object (optional)
    :param details: Additional details in JSON format (optional)
    :param description: Human-readable description of the action (optional)
    :return: The created AuditLog object
    """
    # Create a new audit log entry
    audit_log = ActivityLog.objects.create(
        user=user,
        module=module if module else None,
        action=action,
        object_id=object_id,
        details=details,
    )

    return audit_log
