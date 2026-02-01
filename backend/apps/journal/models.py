from django.conf import settings
from django.db import models


class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    reflection = models.TextField(blank=True, default="")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]
        verbose_name_plural = "journal entries"

    def __str__(self) -> str:
        return f"Journal {self.date} ({self.user})"


class DailyCheckin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()

    # Meditation
    meditation_completed = models.BooleanField(default=False)
    meditation_duration = models.IntegerField(null=True, blank=True)
    meditation_completed_at = models.DateTimeField(null=True, blank=True)

    # Gratitude
    gratitude_completed = models.BooleanField(default=False)
    gratitude_completed_at = models.DateTimeField(null=True, blank=True)

    # Journal
    journal_completed = models.BooleanField(default=False)
    journal_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["user", "date"]

    def __str__(self) -> str:
        return f"Checkin {self.date} ({self.user})"


class GratitudeEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    items = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "date"]
        verbose_name_plural = "gratitude entries"

    def __str__(self) -> str:
        return f"Gratitude {self.date} ({self.user})"


class WeeklySummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    week_start = models.DateField()
    summary = models.TextField()
    themes = models.JSONField(default=list)
    mood_trend = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "week_start"]
        verbose_name_plural = "weekly summaries"

    def __str__(self) -> str:
        return f"Weekly {self.week_start} ({self.user})"
