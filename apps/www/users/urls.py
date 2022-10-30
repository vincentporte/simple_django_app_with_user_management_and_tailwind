from django.contrib.auth.urls import views as auth_views
from django.urls import path, reverse_lazy

from apps.www.users.views import (
    HostView,
    LoginView,
    SignUpView,
    UpdatePasswordView,
    UpdateProfileView,
    UserProfileView,
    complete_verification,
    log_out,
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
    path(
        "reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
]
