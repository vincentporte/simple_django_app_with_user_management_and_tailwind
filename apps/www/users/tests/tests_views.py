import uuid
from datetime import date

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.users.factories import (
    DEFAULT_PASSWORD,
    HostFactory,
    UserFactory,
    UserWithVerifiedEmailFactory,
)
from apps.users.models import User


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_login_not_valid(self):
        url = reverse("users:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
            "password": "wrongpassword",
        }
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        url = reverse("users:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
        }
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)


class SignUpViewTest(TestCase):
    def setUp(self) -> None:
        self.email = "signup@neuralia.co"

    def test_signup_not_valid(self):
        url = reverse("users:signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
        }
        response = self.client.post(url, data=form_data)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=self.email)

    def test_signup_valid(self):
        url = reverse("users:signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
            "first_name": "John",
            "last_name": "Woo",
        }
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)
        self.assertIsNotNone(User.objects.get(email=self.email, email_verified=False))
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.email)
        self.assertEqual(
            "Verify Account",
            email.subject,
        )


class UserProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = self.user.get_absolute_url()

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:profile", kwargs={"slug": self.user.username}),
        )

    def test_authenticated(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("users:update"))

    def test_wrong_slug(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        url = reverse("users:profile", kwargs={"slug": uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UpdateProfileView(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("users:update")

    def test_fields(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.context_data["form"]
        self.assertEqual(
            [k for k in form.fields.keys()],
            ["first_name", "last_name", "gender", "bio", "birthdate", "language"],
        )

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:update"),
        )

    def test_authenticated(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "first_name": "Anton",
            "last_name": "Larikova",
            "gender": "M",
            "bio": "work like a captain, play like a pirat",
            "birthdate": date(1978, 5, 17),
            "language": "EN",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, self.user.get_absolute_url(), status_code=302)

        user = User.objects.get(email=self.user.email)
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertEqual(user.gender, form_data["gender"])
        self.assertEqual(user.bio, form_data["bio"])
        self.assertEqual(user.birthdate, form_data["birthdate"])
        self.assertEqual(user.language, form_data["language"])


class UpdatePasswordViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("users:password")

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:password"),
        )

    def test_wrong_password(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "old_password": "wrongpassword",
            "new_password1": DEFAULT_PASSWORD,
            "new_password2": DEFAULT_PASSWORD,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)

    def test_passwords_dont_match(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "old_password": DEFAULT_PASSWORD,
            "new_password1": "wrongpassword",
            "new_password2": DEFAULT_PASSWORD,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)

    def test_valid(self):
        self.client.login(email=self.user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "old_password": DEFAULT_PASSWORD,
            "new_password1": "newpassword",
            "new_password2": "newpassword",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, self.user.get_absolute_url(), status_code=302)


class complete_verificationTest(TestCase):
    def test_email_already_verified(self):
        user = UserWithVerifiedEmailFactory()
        response = self.client.get(reverse("users:complete-verification", kwargs={"key": "99999"}))
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)

        user.refresh_from_db()
        self.assertFalse(user.email_secret)
        self.assertTrue(user.email_verified)

    def test_wrong_verification_key(self):
        user = UserFactory(email_secret="neuralia.co")
        response = self.client.get(reverse("users:complete-verification", kwargs={"key": "99999"}))
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)

        user.refresh_from_db()
        self.assertTrue(user.email_secret)
        self.assertFalse(user.email_verified)

    def test_valid_verification(self):
        user = UserFactory(email_secret="neuralia.co")
        response = self.client.get(reverse("users:complete-verification", kwargs={"key": user.email_secret}))
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)

        user.refresh_from_db()
        self.assertFalse(user.email_secret)
        self.assertTrue(user.email_verified)


class log_outTest(TestCase):
    def test_log_out(self):
        user = UserFactory()
        self.client.login(email=user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)


class HostViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse("users:host")

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:host"),
        )

    def test_without_permission(self):
        user = UserFactory()
        self.client.login(email=user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_with_permission(self):
        user = HostFactory()
        self.client.login(email=user.email, password=DEFAULT_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


# TO BE DONE : test switch_language mecanisms
