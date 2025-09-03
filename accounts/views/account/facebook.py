from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.permissions import AllowAny


class FacebookLogin(SocialLoginView):
    """API view for Facebook social login using Allauth and dj_rest_auth."""

    adapter_class = FacebookOAuth2Adapter
    permission_classes = [AllowAny]
    # Handles Facebook OAuth2 login flow
