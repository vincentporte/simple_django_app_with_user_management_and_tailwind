"""
Enums fields used in User models.
"""

from django.db import models


class Gender(models.TextChoices):
    M = "M", "Monsieur"
    MME = "MME", "Madame"
    OTH = "OTH", "Autre"


class Language(models.TextChoices):
    EN = "EN", "English"
    FR = "FR", "Français"
    ES = "ES", "Español"
    DE = "DE", "Deutsch"
