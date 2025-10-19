import datetime

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import ValidationError

from accounts.models import User
from accounts.serializers.password import ChangePasswordSerializer
from accounts.serializers.password import ForgotPasswordSerializer
from accounts.serializers.password import ResetPasswordSerializer
from backend.utils import generic_response
from backend.utils import token_validation


class ChangePasswordAPIView(UpdateAPIView):
    """
    API view for changing the user's password.
    """

    http_method_names = ["patch"]
    # Serializer class for handling password change
    serializer_class = ChangePasswordSerializer

    # Permission class to ensure user is authenticated
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        """
        Handle password change request.

        Args:
            request: HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response indicating success or failure of password change.
        """

        serializer = self.get_serializer(data=request.data)  # Get serializer instance
        serializer.is_valid(raise_exception=True)  # Validate the serializer data
        serializer.save()  # Save the updated password
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="Password changed successfully.",
        )


class ForgotPasswordView(CreateAPIView):
    """
    API View for handling forgot password requests.
    """

    serializer_class = ForgotPasswordSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests for forgot password functionality.

        Returns:
            Response indicating success of forgot password request.
        """

        # Deserialize and validate request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")

        if not email:
            return generic_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message="Email is required.",
            )

        try:
            user = User.objects.get(email=email)

            # Generate password reset token (valid for 10 minutes)
            payload = {
                "email": email,
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=10),
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            # Build reset URL (use settings for domain if available)
            domain = getattr(settings, "FRONTEND_DOMAIN", "http://127.0.0.1:8000")
            reset_url = f"{domain}/reset-password/{token}"

            # Prepare email data
            email_data = {
                "email_body": "",  # You can add plain text fallback here
                "to_email": user.email,
                "email_subject": "Password Reset",
            }

            # Send reset email (HTML template + context)
            Utils.send_email(
                email_data,
                # "password_reset_email.html",
                {
                    "user_name": getattr(user, "full_name", "User"),
                    "reset_url": reset_url,
                },
            )

        except User.DoesNotExist:
            # Do nothing if user doesn't exist
            pass

        # Always return a generic response
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="If this email exists in our system, a reset link has been sent.",
        )


class PasswordResetConfirmAPIView(CreateAPIView):
    """
    View for handling password reset confirmation.
    This endpoint is used to confirm a password reset by setting the new password provided in the request data.
    """

    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        """Handle POST requests to process password reset form submission."""
        token = kwargs.get("token")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = token_validation(token)
            password = serializer.validated_data["password"]
            user.set_password(password)
            user.save()
            return generic_response(
                status_code=status.HTTP_200_OK,
                message="User password has been set successfully.",
            )
        except ValidationError as e:
            return generic_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message=str(e),
            )
