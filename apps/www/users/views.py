# import requests  # to be changed to httpx
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

# from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.utils import translation
from django.views.generic import DetailView, FormView, UpdateView
from django.views.generic.base import TemplateView

from apps.users.models import User
from apps.www.users.forms import LoginForm, SignUpForm


class HostView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):

    template_name = "users/host.html"
    permission_required = "users.host"


class LoginView(FormView):

    template_name = "users/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        return reverse("home:homepage")


def log_out(request):
    messages.info(request, "See you later")
    logout(request)
    return redirect(reverse("home:homepage"))


class SignUpView(SuccessMessageMixin, FormView):

    template_name = "users/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("home:homepage")
    success_message = "Successfully signed up. Please check your mailbox to complete email verification"

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        messages.info(request, "Your email is verified")
    except User.DoesNotExist:
        messages.warning(request, "Something gets wrong")
    return redirect(reverse("home:homepage"))


class UserProfileView(LoginRequiredMixin, DetailView):

    model = User
    context_object_name = "user_obj"
    slug_field = "username"


class UpdateProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    template_name = "users/update-profile.html"
    fields = (
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthdate",
        "language",
    )
    success_message = "Profile Updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last name"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birthdate"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        return form


class UpdatePasswordView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    PasswordChangeView,
):

    template_name = "users/update-password.html"
    success_message = "Password Updated"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "Confirm new password"}
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return HttpResponse(status=200)
