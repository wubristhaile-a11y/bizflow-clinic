from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom BizFlow user.

    We keep Django's standard authentication fields for now,
    while leaving room for BizFlow-specific fields later.
    """

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.username
