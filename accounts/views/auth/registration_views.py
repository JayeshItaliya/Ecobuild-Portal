from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from accounts.serializers.register import RegisterUserSerializer


class SignupView(CreateAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request):
        """
        Handle user sign-up request.

        Args:
            request: HTTP request object.

        Returns:
            Response indicating success or failure of user sign-up.
        """
        # Validate user data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # new_generated_password = generate_password()
            new_generated_password = "password"
            serializer.save(
                password=new_generated_password,
            )
            # Save user data

        # Return successful response with user data, refresh token, and access token
        return Response(
            data={
                "message": "Registration successful. Your account is pending verification. You'll be notified once approved. Thank you for joining us.",
            },
            status=status.HTTP_200_OK,
        )
