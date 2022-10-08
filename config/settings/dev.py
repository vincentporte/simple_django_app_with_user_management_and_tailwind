from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import # noqa F403

# Django settings
# ---------------

DEBUG = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "192.168.0.1"]

INSTALLED_APPS += ["django_extensions", "debug_toolbar"]  # noqa F405

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405

DEBUG_TOOLBAR_CONFIG = {
    # https://django-debug-toolbar.readthedocs.io/en/latest/panels.html#panels
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # ProfilingPanel makes the django admin extremely slow...
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# Security.
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

AUTH_PASSWORD_VALIDATORS = []  # Avoid password strength validation in DEV.

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PROTOCOL = "http"
FQDN = "localhost:8000"
