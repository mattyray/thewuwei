from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Custom user model with email as the primary identifier."""

    username = None
    email = models.EmailField(unique=True)
    timezone = models.CharField(max_length=50, default="America/New_York")
    daily_reminder_time = models.TimeField(default="20:00")
    reminder_enabled = models.BooleanField(default=True)
    anthropic_api_key = models.CharField(max_length=255, blank=True, default="")

    # Rate limiting
    reflections_today = models.IntegerField(default=0)
    reflections_reset_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
