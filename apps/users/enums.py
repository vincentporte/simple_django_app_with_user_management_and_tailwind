"""
Enums fields used in User models.
"""

from django.db import models


class Gender(models.TextChoices):
    M = "M", "Monsieur"
    MME = "MME", "Madame"
    OTH = "OTH", "Autre"
