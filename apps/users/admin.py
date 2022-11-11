from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import forms

from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            "Personal info",
            {
                "fields": (
                    "country",
                    "first_name",
                    "last_name",
                    "email",
                    "email_secret",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "email_verified",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "country",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    add_form = forms.UserCreationForm
    form = forms.UserChangeForm
    change_password_form = forms.AdminPasswordChangeForm
    list_display = ("email", "first_name", "last_name", "is_staff", "email_verified")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
