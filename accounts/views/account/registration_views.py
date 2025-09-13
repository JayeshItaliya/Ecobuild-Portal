from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView

from accounts.serializers.register import RegisterUserSerializer
from backend.utils import generic_response


class SignupView(CreateAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        """Handle user sign-up request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()

        response_data = self.get_serializer(user).data
        return generic_response(
            status_code=status.HTTP_201_CREATED,
            message="Registration successful. Your account is pending verification. You'll be notified once approved. Thank you for joining us.",
            data=response_data,
        )
