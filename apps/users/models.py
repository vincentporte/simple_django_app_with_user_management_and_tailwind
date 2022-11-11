import uuid

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.users import enums as users_enums


class CustomUserManager(UserManager):  # Here
    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.UUIDField(default=uuid.uuid4, editable=False)
    email = models.EmailField("email address", unique=True)  # Here
    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(max_length=20, default="", blank=True)

    date_joined = models.DateTimeField("date joined", default=timezone.now)

    country = models.CharField(
        max_length=3,
        verbose_name="country",
        blank=False,
        default=users_enums.Country.FR,
        choices=users_enums.Country.choices,
    )
    bio = models.TextField(verbose_name="bio", blank=True)
    birthdate = models.DateField(blank=True, null=True)

    USERNAME_FIELD = "email"  # Here
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        permissions = (("host", "Host"),)

    def __str__(self):
        return str(self.email)

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"slug": self.username})

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            html_message = render_to_string(
                "emails/verify_email.html",
                {
                    "url": reverse("users:complete-verification", kwargs={"key": secret}),
                    "protocol": settings.PROTOCOL,
                    "fqdn": settings.FQDN,
                },
            )
            send_mail(
                "Verify Account",
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email],
                fail_silently=False,
                html_message=html_message,
            )
            self.save()
