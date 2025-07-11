from backend.serializer import MyTokenObtainPairSerializer
from rest_framework.serializers import CharField
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError


class SignInUserSerializer(MyTokenObtainPairSerializer):
    """
    Serializer for user sign-in.
    """

    def validate(self, attrs):
        # Normalize email to lowercase to make it case-insensitive
        if "email" in attrs:
            attrs["email"] = attrs["email"].lower()

        return super().validate(attrs)


class LogoutSerializer(Serializer):
    """
    Serializer for logging out a user by invalidating the refresh token.
    """

    refresh = CharField()

    def validate(self, attrs):
        """
        Validate the refresh token.
        """
        refresh_token = attrs.get("refresh")
        try:
            # Attempt to create a RefreshToken instance
            token = RefreshToken(refresh_token)
            # Blacklist (invalidate) the refresh token
            token.blacklist()
            return attrs
        except Exception as e:
            # If there's an error, raise a validation error
            raise ValidationError(str(e))
