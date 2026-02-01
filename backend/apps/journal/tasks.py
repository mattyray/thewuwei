"""
Celery tasks for the journal app.

Scheduled via Celery Beat:
- create_daily_checkins: runs daily at 00:01
- reset_rate_limits: runs daily at 00:00 UTC
"""

from datetime import date

from celery import shared_task

from apps.users.models import User

from .models import DailyCheckin


@shared_task
def create_daily_checkins():
    """Create a DailyCheckin record for every active user."""
    users = User.objects.filter(is_active=True)
    for user in users:
        DailyCheckin.objects.get_or_create(user=user, date=date.today())


@shared_task
def reset_rate_limits():
    """Reset the daily reflection counter for all users."""
    User.objects.all().update(
        reflections_today=0,
        reflections_reset_date=date.today(),
    )
