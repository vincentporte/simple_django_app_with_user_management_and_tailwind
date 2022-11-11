from django.forms import widgets
from django.test import TestCase

from apps.users.factories import DEFAULT_PASSWORD, UserFactory
from apps.www.users.forms import LoginForm, SignUpForm, UpdateProfileForm


class LoginFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_required_fields(self):
        form_data = {}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Ce champ est obligatoire.", form.errors["email"])
        self.assertIn("Ce champ est obligatoire.", form.errors["password"])

    def test_wrong_password(self):
        form_data = {
            "email": self.user.email,
            "password": "wrongpass",
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["Password is wrong"])

    def test_unknown_user(self):
        form_data = {
            "email": "failed@test.com",
            "password": DEFAULT_PASSWORD,
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["User does not exist"])

    def test_login_valid(self):
        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())


class SignUpFormTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_required_fields(self):
        form_data = {}
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Ce champ est obligatoire.", form.errors["email"])
        self.assertIn("Ce champ est obligatoire.", form.errors["password"])

    def test_email_exists(self):
        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("That email is already taken", form.errors["email"])

    def test_signup_ok(self):
        form_data = {
            "email": "test@test.com",
            "password": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())


class UpdateProfileFormTest(TestCase):
    def test_fields(self):
        form = UpdateProfileForm()
        self.assertIn("first_name", form.fields)
        self.assertIn("last_name", form.fields)
        self.assertIn("country", form.fields)
        self.assertIn("bio", form.fields)
        self.assertIn("birthdate", form.fields)

        self.assertIsInstance(form.fields["birthdate"].widget, widgets.DateInput)
        self.assertIsInstance(form.fields["country"].widget, widgets.Select)
