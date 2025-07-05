from rest_framework.serializers import CharField
from rest_framework.serializers import EmailField
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from accounts.models import User
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import make_password
from rest_framework import status
from backend.utils import token_validation
from rest_framework.views import APIView
from rest_framework.response import Response 

def validate_email_case_insensitive(email):
    """
    Validate that the email address is unique and normalize it.
    """
    # Normalize email to lowercase
    email = email.lower()

    # Check for existing users with the same email (case-insensitive)
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError("A user with this email already exists.")

    return email


class RegisterUserSerializer(ModelSerializer):
    """
    Serializer for registering a new user.
    """

    # Define password field with write-only access and password validation
    password = CharField(
        write_only=True, validators=[validate_password], required=False
    )
    email = EmailField(validators=[validate_email_case_insensitive])

    class Meta:
        model = User
        # Define fields to include in serialization
        fields = [
            "email",
            "full_name",
            "verification_status",
            "password",
        ]

    def create(self, validated_data):
        """
        Create a new user instance with hashed password and handle school assignment for principals.
        """
        validated_data["password"] = make_password(validated_data["password"])

        # Create the user instance
        user = super().create(validated_data)

        return user




class ValidateTokenAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Validate a JWT token.

        This endpoint is used to validate a JWT token. It checks if the token is valid and returns
        a success message if it is, or an error message if it is not.

        Args:
            request: The HTTP request.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments. Expected to contain the token.

        Returns:
            Response: HTTP response indicating success or failure of token validation.

        """
        token = kwargs.get("token")
        try:
            # Call the token_validation function to validate the token
            _ = token_validation(token)
            # Return success response if validation succeeds
            return Response(
                {"message": "Success"},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            # Return error response if validation fails
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
