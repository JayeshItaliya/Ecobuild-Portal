import datetime

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from backend.utils import token_validation

from accounts.serializers.password import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


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
        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
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
            Response indicating success or failure of forgot password request.
        """
        # Deserialize the request data using the serializer

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract email from validated data
        email = serializer.validated_data["email"]
        email = email if email else None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        payload = {
            "email": email,
            "exp": datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(minutes=10),
        }

        # Generate JWT token for password reset link using the email
        token = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm="HS256",
        )

        # Construct password reset URL using the generated token
        reset_url = f"http://127.0.0.1:8000/reset-password/{token}"

        # Prepare email data for sending password reset email
        email_data = {
            "email_body": "",  # Add email body content if necessary
            "to_email": user.email,
            "email_subject": "Password Reset",
        }

        # Send email containing the password reset link
        Utils.send_email(
            email_data,
            # "password_reset_email.html",  # HTML template for the email
            {
                "user_name": user.full_name if user.full_name else "User",
                "reset_url": reset_url,
            },  # Additional context data for the template
        )

        # Return success response indicating that reset link has been sent to the user's email
        return Response(
            {"message": "Password reset link has been sent to your email."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(CreateAPIView):
    """
    View for handling password reset confirmation.

    This endpoint is used to confirm a password reset by setting the new password
    provided in the request data.

    """

    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to process password reset form submission.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments. Expected to contain the token.

        Returns:
            Response: HTTP response indicating success or failure of password reset.

        """
        # Extract the token from URL kwargs
        token = kwargs.get("token")

        # Initialize the serializer with request data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Validate the token and retrieve the associated user
            user = token_validation(token)

            # Extract the new password from the validated data
            password = serializer.validated_data["password"]

            # Set the new password for the user
            user.set_password(password)

            # Save the updated user details
            user.save()

            # Return success response
            return Response(
                {"message": "User password has been set successfully."},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            # Return error response if validation fails
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
