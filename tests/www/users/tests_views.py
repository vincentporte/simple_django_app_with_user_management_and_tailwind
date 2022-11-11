import uuid
from datetime import date

from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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
        self.url = reverse("users:login")

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_login_not_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
            "password": "wrongpassword",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)

    def test_login_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
            "password": DEFAULT_PASSWORD,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, reverse("home:homepage"), status_code=302)


class SignUpViewTest(TestCase):
    def setUp(self) -> None:
        self.email = "signup@neuralia.co"
        self.url = reverse("users:signup")

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_signup_not_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=self.email)

    def test_signup_valid(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.email,
            "password": DEFAULT_PASSWORD,
            "password1": DEFAULT_PASSWORD,
            "first_name": "John",
            "last_name": "Woo",
        }
        response = self.client.post(self.url, data=form_data)
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
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("users:update"))

    def test_wrong_slug(self):
        self.client.force_login(self.user)
        url = reverse("users:profile", kwargs={"slug": uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UpdateProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("users:update")

    def test_csrf(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_fields(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.context_data["form"]
        self.assertEqual(
            list(form.fields.keys()),
            ["first_name", "last_name", "country", "bio", "birthdate"],
        )

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:update"),
        )

    def test_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "first_name": "Anton",
            "last_name": "Larikova",
            "country": "FR",
            "bio": "work like a captain, play like a pirat",
            "birthdate": date(1978, 5, 17),
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(response, self.user.get_absolute_url(), status_code=302)

        user = User.objects.get(email=self.user.email)
        self.assertEqual(user.first_name, form_data["first_name"])
        self.assertEqual(user.last_name, form_data["last_name"])
        self.assertEqual(user.country, form_data["country"])
        self.assertEqual(user.bio, form_data["bio"])
        self.assertEqual(user.birthdate, form_data["birthdate"])


class UpdatePasswordViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse("users:password")

    def test_csrf(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:login") + "?next=" + reverse("users:password"),
        )

    def test_wrong_password(self):
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "old_password": DEFAULT_PASSWORD,
            "new_password1": DEFAULT_PASSWORD + "2",
            "new_password2": DEFAULT_PASSWORD + "2",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertRedirects(
            response,
            self.user.get_absolute_url(),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=False,
        )


class PasswordResetViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse("users:password_reset")

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_email_sent(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": self.user.email,
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:password_reset_done"),
        )

        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox[0]

        token = response.context.get("token")
        uid = response.context.get("uid")
        password_reset_token_url = reverse("users:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        self.assertIn(password_reset_token_url, email.body)
        self.assertEqual(
            [
                self.user.email,
            ],
            email.to,
        )

    def test_unknown_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "email": "unknown.email@neuralia.co",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("users:password_reset_done"),
        )

        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneViewTest(TestCase):
    def test_rendered_page(self):
        response = self.client.get(reverse("users:password_reset_done"))
        self.assertEqual(response.status_code, 200)


class PasswordResetConfirmViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))  # .decode()
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse("users:password_reset_confirm", kwargs={"uidb64": self.uid, "token": self.token})

    def test_csrf(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_token(self):
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)

        form_data = {
            "new_password1": DEFAULT_PASSWORD + "1",
            "new_password2": DEFAULT_PASSWORD + "1",
        }
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

    def test_invalid_token(self):
        """
        invalidate the token by changing the password
        """
        self.user.set_password("abcdef123")
        self.user.save()

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "reset link was invalid")


class PasswordResetCompleteViewTest(TestCase):
    def test_rendered_page(self):
        response = self.client.get(reverse("users:password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("users:login"))


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
        self.client.force_login(user)
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
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_with_permission(self):
        user = HostFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
