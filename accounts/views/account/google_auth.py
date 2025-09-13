import requests
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.utils import create_google_user
from backend import settings
from backend.enums import LoginMethodChoices
from backend.utils import generic_response


class GoogleLoginView(APIView):
    """
    Redirect the user to Google's OAuth dialog.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&response_type=code"
            f"&scope=openid%20email%20profile"
        )
        return Response(
            data={
                "data": {
                    "url": google_auth_url,
                },
                "message": "Success",
            },
            status=status.HTTP_200_OK,
        )


class GoogleAuthCallBack(APIView):
    """
    Handles Google OAuth 2.0 callback by exchanging authorization code
    for access token, fetching user info, and returning JWT tokens.
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Handle Google OAuth callback to exchange code for an access token
        and retrieve user info.
        """
        code = request.query_params.get("code")
        if not code:
            return generic_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message="Authorization code is required.",
            )

        # Exchange the code for an access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        try:
            token_res = requests.post(token_url, data=token_data).json()
            if "access_token" not in token_res:
                raise ValueError({"error": "Access token not found in response"})
            access_token = token_res["access_token"]
        except requests.exceptions.RequestException:
            return generic_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message="Failed to retrieve access token from Google.",
            )

        # Use the access token to fetch user info
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        user_info_headers = {"Authorization": f"Bearer {access_token}"}

        try:
            user_info_res = requests.get(
                user_info_url, headers=user_info_headers
            ).json()
            if "email" not in user_info_res:
                raise ValueError(
                    {"error": "Failed to retrieve required user information."}
                )
            email = user_info_res["email"]
            google_account_id = user_info_res["sub"]
            first_name = user_info_res.get("given_name")
            last_name = user_info_res.get("family_name")
            name = (
                f"{first_name} {last_name}" if first_name and last_name else first_name
            )
        except requests.exceptions.RequestException:
            return generic_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_message="Failed to retrieve user information from Google.",
            )

        try:
            user = User.objects.get(email=email)
            if user.is_active == False:
                user.is_active = True
                user.save()

        except User.DoesNotExist:
            user = create_google_user(
                self,
                email=email,
                google_account_id=google_account_id,
                full_name=name,
                auth=LoginMethodChoices.GOOGLE,
            )

        # Generate JWT refresh token
        refresh = RefreshToken.for_user(user)

        # Define frontend redirect URL
        frontend_redirect_url = f"{settings.DOMAIN_URL}"
        # Append authentication data as query parameters
        frontend_redirect_url += f"?access_token={str(refresh.access_token)}&refresh_token={str(refresh)}&email={email}&auth_type=google"
        # Redirect the user to the frontend
        return redirect(frontend_redirect_url)
