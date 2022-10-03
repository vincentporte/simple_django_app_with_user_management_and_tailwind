from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import

# Django settings
# ---------------

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "192.168.0.1"]

# Security.
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

AUTH_PASSWORD_VALIDATORS = []  # Avoid password strength validation in DEV.

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PROTOCOL = "http"
FQDN = "localhost:8000"
