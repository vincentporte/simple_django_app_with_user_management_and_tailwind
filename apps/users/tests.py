from django.conf import settings
from django.core import mail
from django.db import IntegrityError
from django.shortcuts import reverse
from django.test import TestCase

from apps.users.factories import (
    DEFAULT_PASSWORD,
    HostFactory,
    UserFactory,
    UserWithVerifiedEmailFactory,
)
from apps.users.models import User


class ManagerTest(TestCase):
    def test_create_user(self):
        User.objects.create_user(email="user@neuralia.co", password=DEFAULT_PASSWORD)
        user = User.objects.get(email="user@neuralia.co")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User.objects.create_superuser(email="superuser@neuralia.co", password=DEFAULT_PASSWORD)
        user = User.objects.get(email="superuser@neuralia.co")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class ModelTest(TestCase):
    def test_email_is_unique(self):
        User.objects.create_user(email="user@neuralia.co", password=DEFAULT_PASSWORD)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="user@neuralia.co", password=DEFAULT_PASSWORD)

    def test_get_absolute_url(self):
        user = UserFactory()
        self.assertEqual(
            reverse("users:profile", kwargs={"slug": user.username}),
            user.get_absolute_url(),
        )

    def test_verified_email(self):
        user = UserWithVerifiedEmailFactory()
        user.verify_email()
        user.refresh_from_db()
        self.assertFalse(user.email_secret)
        self.assertEqual(len(mail.outbox), 0)

    def test_unverified_email(self):
        user = UserFactory()
        user.verify_email()
        user.refresh_from_db()
        self.assertIsNotNone(user.email_secret)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to[0], user.email)
        self.assertEqual(
            "Verify Account",
            email.subject,
        )
        self.assertIn(
            f"{settings.PROTOCOL}://{settings.FQDN}/verify/{user.email_secret}",
            email.alternatives[0][0],
        )

    def test_host_permissions(self):
        user = HostFactory()
        self.assertEqual(user.get_user_permissions(), {"users.host"})
