from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import CharField
from rest_framework.serializers import EmailField
from rest_framework.serializers import Serializer
from rest_framework.serializers import ValidationError


class ChangePasswordSerializer(Serializer):

    password = CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = CharField(write_only=True, required=True)
    old_password = CharField(write_only=True, required=True)

    def validate(self, attrs):

        if attrs["old_password"] == attrs["password"]:
            raise ValidationError(
                "New password cannot be the same as the old password."
            )

        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError("The passwords do not match. Please try again.")

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationError("Old password is incorrect.")
        return value

    def save(self):
        """
        Save the new password for the user.
        """
        user = self.context["request"].user
        password = self.validated_data["password"]
        user.set_password(password)
        user.save()
        return user


class ForgotPasswordSerializer(Serializer):
    """
    Serializer for validating and parsing data for forgot password request.
    """

    email = EmailField()


class ResetPasswordSerializer(Serializer):
    """
    Serializer for validating and handling user password change.
    """

    password = CharField(write_only=True, required=True, validators=[validate_password])
