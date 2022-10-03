from django.test import TestCase

from apps.users.factories import DEFAULT_PASSWORD, UserFactory
from apps.www.users.forms import LoginForm, SignUpForm


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
        self.assertIn("Ce champ est obligatoire.", form.errors["password1"])

    def test_email_exists(self):
        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("That email is already taken", form.errors["email"])

    def test_passwords_dont_match(self):
        form_data = {
            "email": "test@test.com",
            "password": DEFAULT_PASSWORD,
            "password1": "notmatchingpassword",
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Password confirmation does not match", form.errors["password1"])

    def test_signup_ok(self):
        form_data = {
            "email": "test@test.com",
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())
