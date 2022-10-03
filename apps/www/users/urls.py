from django.urls import path

from apps.www.users.views import (
    HostView,
    LoginView,
    SignUpView,
    UpdatePasswordView,
    UpdateProfileView,
    UserProfileView,
    complete_verification,
    log_out,
    switch_language,
)

app_name = "users"

urlpatterns = [
    path("host/", HostView.as_view(), name="host"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", log_out, name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("verify/<str:key>/", complete_verification, name="complete-verification"),
    path("update-profile/", UpdateProfileView.as_view(), name="update"),
    path("update-password/", UpdatePasswordView.as_view(), name="password"),
    path("profile/<slug:slug>/", UserProfileView.as_view(), name="profile"),
    path("switch-language/", switch_language, name="switch-language"),
]
