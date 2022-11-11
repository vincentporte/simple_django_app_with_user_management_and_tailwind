import datetime
import functools
import random

import factory
import factory.fuzzy
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.users.enums import Country
from apps.users.models import User

DEFAULT_PASSWORD = "YwiW%j6Hy!9bNu9Gz4"


@functools.cache
def default_password():
    return make_password(DEFAULT_PASSWORD)


class UserFactory(factory.django.DjangoModelFactory):
    """Generates User() objects for unit tests."""

    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda a: "{}.{}@neuralia.co".format(a.first_name, a.last_name).lower())
    password = factory.LazyFunction(default_password)
    birthdate = factory.fuzzy.FuzzyDate(datetime.date(1968, 1, 1), datetime.date(2000, 1, 1))
    country = random.choice(Country.values)


class UserWithVerifiedEmailFactory(UserFactory):
    email_verified = True


class HostFactory(UserWithVerifiedEmailFactory):
    @factory.post_generation
    def set_permission(self, create, extracted, **kwargs):
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(content_type=content_type, codename="host")
        self.user_permissions.add(permission)
        self.save()
