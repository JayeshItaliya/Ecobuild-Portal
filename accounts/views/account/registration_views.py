from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from accounts.serializers.register import RegisterUserSerializer


class SignupView(CreateAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        """Handle user sign-up request."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            user = serializer.save()
        return Response(
            {
                "data": self.get_serializer(user).data,
                "message": "Registration successful. Your account is pending verification. You'll be notified once approved. Thank you for joining us.",
            },
            status=status.HTTP_201_CREATED,
        )
