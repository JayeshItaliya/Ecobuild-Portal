from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.serializers.register import ValidateTokenAPIView
from accounts.views.auth.auth_views import LogoutAPIView
from accounts.views.auth.auth_views import SigninView
from accounts.views.auth.facebook import FacebookLogin
from accounts.views.auth.password_view import ChangePasswordAPIView
from accounts.views.auth.password_view import ForgotPasswordView
from accounts.views.auth.password_view import PasswordResetConfirmAPIView
from accounts.views.auth.registration_views import SignupView
from accounts.views.user.team_members import TeamMemberListAPIView
from accounts.views.user.user_role import RoleListCreateAPIView
from accounts.views.user.user_role import RoleRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("facebook/", FacebookLogin.as_view(), name="facebook_login"),
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
    path(
        "team-members/",
        TeamMemberListAPIView.as_view(),
        name="team-members-list",
    ),
    path(
        "role/",
        RoleListCreateAPIView.as_view(),
        name="role-list-create",
    ),
    path(
        "role/<str:pk>/",
        RoleRetrieveUpdateDestroyAPIView.as_view(),
        name="role-detail",
    ),
]
