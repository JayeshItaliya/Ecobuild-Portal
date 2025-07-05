from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.serializers.register import ValidateTokenAPIView
from accounts.views.auth.auth_views import LogoutAPIView, SigninView
from accounts.views.auth.password_view import (
    ChangePasswordAPIView,
    ForgotPasswordView,
    PasswordResetConfirmAPIView,
)
from accounts.views.auth.registration_views import SignupView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("signin/", SigninView.as_view(), name="signin"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path(
        "password-reset-confirm/<str:token>",
        PasswordResetConfirmAPIView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "validate-password-reset-token/<str:token>",
        ValidateTokenAPIView.as_view(),
        name="validate-password-reset-token",
    ),
]
