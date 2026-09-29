from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("OWNER", "Owner"),
        ("TENANT", "Tenant"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="TENANT",
    )

    def __str__(self):
        return self.email