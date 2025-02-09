from django.urls import path

from authentication.views import *

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("reset-password/", ResetPasswordApiView.as_view(), name="reset_password"),
    path("request-reset-password/", RequestPasswordResetApiView.as_view(), name="request_reset_password"),
    path("check-login/", CheckAuth.as_view(), name="check_login"),
    path("session-login/", SessionLogin.as_view(), name="session_login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
