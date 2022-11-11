"""
Enums fields used in User models.
"""

from django.db import models


class Country(models.TextChoices):
    FR = "FR", "France"
    BE = "BE", "Belgique"
    DE = "DE", "Deutschland"
    EN = "EN", "England"
    ES = "ES", "España"
    IT = "IT", "Italia"
    LT = "LT", "Lietuva"
    PL = "PL", "Polska"
    UA = "UA", "Україна"
