from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers.sign_in_seralizer import LogoutSerializer
from accounts.serializers.sign_in_seralizer import SignInUserSerializer
from backend.utils import generic_response


class SigninView(TokenObtainPairView):
    """
    Handles user sign-in and JWT token generation.
    """

    serializer_class = SignInUserSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate user and return JWT tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Optionally check verification status here

        # serializer.user.verification_status

        # if verification_status == VerificationStatusChoices.PENDING:
        #     message = "Your account is pending verification. Please wait for approval before logging in. Thank you for your patience."
        #     return Response(
        #         data={"message": message}, status=status.HTTP_401_UNAUTHORIZED
        #     )
        # elif verification_status == VerificationStatusChoices.REJECTED:
        #     message = "Your account verification was rejected. Please contact support for further assistance."
        #     return Response(
        #         data={"message": message}, status=status.HTTP_401_UNAUTHORIZED
        #     )

        token_data = serializer.validated_data
        response_data = {
            "data": {
                "access": token_data["access"],
                "refresh": token_data["refresh"],
            },
            "message": "Sign in successful.",
        }
        return generic_response(
            status_code=status.HTTP_200_OK,
            data=response_data,
        )


class LogoutAPIView(CreateAPIView):
    """
    API view for logging out a user by invalidating the refresh token.
    """

    serializer_class = LogoutSerializer

    def create(self, request, *args, **kwargs):
        """Handle POST requests to invalidate the refresh token and log the user out."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return generic_response(
            status_code=status.HTTP_200_OK,
            message="User successfully logged out.",
        )
