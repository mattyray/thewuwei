"""
TDD: Journal Models Tests

Tests for JournalEntry, DailyCheckin, GratitudeEntry, WeeklySummary.
These tests drive the schema design for the core daily practice models.
"""

from datetime import date, datetime

import pytest
from django.db import IntegrityError
from django.utils import timezone


class TestJournalEntry:
    """Tests that drive the JournalEntry model design."""

    def test_create_journal_entry(self, user, today):
        from apps.journal.models import JournalEntry

        entry = JournalEntry.objects.create(
            user=user,
            content="Today I practiced being present.",
            date=today,
        )
        assert entry.content == "Today I practiced being present."
        assert entry.date == today
        assert entry.user == user

    def test_journal_entry_has_reflection_field(self, user, today):
        """AI reflection is stored alongside the entry."""
        from apps.journal.models import JournalEntry

        entry = JournalEntry.objects.create(
            user=user,
            content="Feeling anxious about work.",
            date=today,
        )
        assert entry.reflection == ""

    def test_journal_entry_unique_per_user_per_date(self, user, today):
        """Can't have two journal entries for the same user on the same day."""
        from apps.journal.models import JournalEntry

        JournalEntry.objects.create(user=user, content="First", date=today)
        with pytest.raises(IntegrityError):
            JournalEntry.objects.create(user=user, content="Second", date=today)

    def test_different_users_same_date_ok(self, user, other_user, today):
        """Two different users CAN journal on the same day."""
        from apps.journal.models import JournalEntry

        JournalEntry.objects.create(user=user, content="A's entry", date=today)
        JournalEntry.objects.create(user=other_user, content="B's entry", date=today)
        assert JournalEntry.objects.count() == 2

    def test_journal_entry_ordering(self, user):
        """Entries are ordered by date descending (newest first)."""
        from apps.journal.models import JournalEntry

        old = JournalEntry.objects.create(
            user=user, content="Old", date=date(2026, 1, 1)
        )
        new = JournalEntry.objects.create(
            user=user, content="New", date=date(2026, 1, 15)
        )
        entries = list(JournalEntry.objects.filter(user=user))
        assert entries[0] == new
        assert entries[1] == old

    def test_journal_entry_timestamps(self, user, today):
        """Entries track created_at and updated_at."""
        from apps.journal.models import JournalEntry

        entry = JournalEntry.objects.create(
            user=user, content="Test", date=today
        )
        assert entry.created_at is not None
        assert entry.updated_at is not None

    def test_journal_entry_str(self, user, today):
        from apps.journal.models import JournalEntry

        entry = JournalEntry.objects.create(
            user=user, content="Test", date=today
        )
        assert str(today) in str(entry)


class TestDailyCheckin:
    """Tests that drive the DailyCheckin model design."""

    def test_create_checkin(self, user, today):
        from apps.journal.models import DailyCheckin

        checkin = DailyCheckin.objects.create(user=user, date=today)
        assert checkin.user == user
        assert checkin.date == today

    def test_checkin_defaults_all_false(self, user, today):
        """New checkin starts with nothing completed."""
        from apps.journal.models import DailyCheckin

        checkin = DailyCheckin.objects.create(user=user, date=today)
        assert checkin.meditation_completed is False
        assert checkin.gratitude_completed is False
        assert checkin.journal_completed is False

    def test_checkin_meditation_fields(self, user, today):
        """Meditation has completed flag, optional duration, and timestamp."""
        from apps.journal.models import DailyCheckin

        checkin = DailyCheckin.objects.create(user=user, date=today)
        assert checkin.meditation_duration is None
        assert checkin.meditation_completed_at is None

    def test_checkin_log_meditation(self, user, today):
        """Can record meditation with duration."""
        from apps.journal.models import DailyCheckin

        checkin = DailyCheckin.objects.create(user=user, date=today)
        checkin.meditation_completed = True
        checkin.meditation_duration = 20
        checkin.meditation_completed_at = timezone.now()
        checkin.save()

        checkin.refresh_from_db()
        assert checkin.meditation_completed is True
        assert checkin.meditation_duration == 20
        assert checkin.meditation_completed_at is not None

    def test_checkin_unique_per_user_per_date(self, user, today):
        """Only one checkin per user per day."""
        from apps.journal.models import DailyCheckin

        DailyCheckin.objects.create(user=user, date=today)
        with pytest.raises(IntegrityError):
            DailyCheckin.objects.create(user=user, date=today)

    def test_different_users_same_date_checkin(self, user, other_user, today):
        from apps.journal.models import DailyCheckin

        DailyCheckin.objects.create(user=user, date=today)
        DailyCheckin.objects.create(user=other_user, date=today)
        assert DailyCheckin.objects.count() == 2


class TestGratitudeEntry:
    """Tests that drive the GratitudeEntry model design."""

    def test_create_gratitude_entry(self, user, today):
        from apps.journal.models import GratitudeEntry

        entry = GratitudeEntry.objects.create(
            user=user,
            date=today,
            items=["good sleep", "my caregivers", "coffee"],
        )
        assert entry.items == ["good sleep", "my caregivers", "coffee"]
        assert len(entry.items) == 3

    def test_gratitude_items_is_json_list(self, user, today):
        """Items stored as JSON array."""
        from apps.journal.models import GratitudeEntry

        entry = GratitudeEntry.objects.create(
            user=user, date=today, items=["one", "two"]
        )
        entry.refresh_from_db()
        assert isinstance(entry.items, list)
        assert entry.items == ["one", "two"]

    def test_gratitude_default_empty_list(self, user, today):
        from apps.journal.models import GratitudeEntry

        entry = GratitudeEntry.objects.create(user=user, date=today)
        assert entry.items == []

    def test_gratitude_unique_per_user_per_date(self, user, today):
        from apps.journal.models import GratitudeEntry

        GratitudeEntry.objects.create(user=user, date=today, items=["a"])
        with pytest.raises(IntegrityError):
            GratitudeEntry.objects.create(user=user, date=today, items=["b"])

    def test_different_users_same_date_gratitude(self, user, other_user, today):
        from apps.journal.models import GratitudeEntry

        GratitudeEntry.objects.create(user=user, date=today, items=["a"])
        GratitudeEntry.objects.create(user=other_user, date=today, items=["b"])
        assert GratitudeEntry.objects.count() == 2


class TestWeeklySummary:
    """Tests that drive the WeeklySummary model design."""

    def test_create_weekly_summary(self, user):
        from apps.journal.models import WeeklySummary

        monday = date(2026, 1, 27)
        summary = WeeklySummary.objects.create(
            user=user,
            week_start=monday,
            summary="This week you focused on boundaries and sleep.",
            themes=["boundaries", "sleep", "work stress"],
            mood_trend="improving",
        )
        assert summary.summary.startswith("This week")
        assert "boundaries" in summary.themes
        assert summary.mood_trend == "improving"

    def test_weekly_summary_unique_per_user_per_week(self, user):
        from apps.journal.models import WeeklySummary

        monday = date(2026, 1, 27)
        WeeklySummary.objects.create(
            user=user, week_start=monday, summary="First"
        )
        with pytest.raises(IntegrityError):
            WeeklySummary.objects.create(
                user=user, week_start=monday, summary="Second"
            )

    def test_weekly_summary_defaults(self, user):
        from apps.journal.models import WeeklySummary

        summary = WeeklySummary.objects.create(
            user=user,
            week_start=date(2026, 1, 27),
            summary="Test",
        )
        assert summary.themes == []
        assert summary.mood_trend == ""
