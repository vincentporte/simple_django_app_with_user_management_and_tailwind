from django.test import TestCase
from django.urls import reverse

from apps.users.factories import UserFactory


class HomepageTest(TestCase):
    def setUp(self):
        self.url = reverse("home:homepage")

    def test_anonymous_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bienvenue")
        self.assertContains(response, reverse("users:signup"))
        self.assertContains(response, reverse("users:login"))

    def test_authenticated_access(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("users:profile", kwargs={"slug": user.username}))
