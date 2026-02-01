"""
TDD: Celery Task Tests

Tests for scheduled background tasks:
- Daily check-in creation
- Rate limit reset
- Weekly summary generation (stub for now — needs AI)
"""

from datetime import date, timedelta

import pytest

from apps.journal.models import DailyCheckin
from apps.users.models import User


class TestCreateDailyCheckins:
    """Tests for the daily check-in creation task."""

    def test_creates_checkins_for_all_users(self, user, other_user):
        from apps.journal.tasks import create_daily_checkins

        create_daily_checkins()

        assert DailyCheckin.objects.filter(
            user=user, date=date.today()
        ).exists()
        assert DailyCheckin.objects.filter(
            user=other_user, date=date.today()
        ).exists()

    def test_does_not_duplicate_checkins(self, user):
        from apps.journal.tasks import create_daily_checkins

        DailyCheckin.objects.create(user=user, date=date.today())
        create_daily_checkins()

        assert DailyCheckin.objects.filter(
            user=user, date=date.today()
        ).count() == 1

    def test_creates_for_inactive_check(self, db):
        """Only creates for active users."""
        from apps.journal.tasks import create_daily_checkins

        active = User.objects.create_user(
            email="active@test.com", password="test"
        )
        inactive = User.objects.create_user(
            email="inactive@test.com", password="test", is_active=False
        )

        create_daily_checkins()

        assert DailyCheckin.objects.filter(user=active).exists()
        assert not DailyCheckin.objects.filter(user=inactive).exists()


class TestResetRateLimits:
    """Tests for the daily rate limit reset task."""

    def test_resets_reflection_count(self, user):
        from apps.journal.tasks import reset_rate_limits

        user.reflections_today = 3
        user.save()

        reset_rate_limits()

        user.refresh_from_db()
        assert user.reflections_today == 0

    def test_updates_reset_date(self, user):
        from apps.journal.tasks import reset_rate_limits

        old_date = user.reflections_reset_date
        reset_rate_limits()

        user.refresh_from_db()
        assert user.reflections_reset_date == date.today()
