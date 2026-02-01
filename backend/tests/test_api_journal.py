"""
TDD: Journal API Tests

Tests for journal entries, check-ins, and gratitude endpoints.
Drive the viewset design with auth, scoping, and CRUD.
"""

from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.journal.models import DailyCheckin, GratitudeEntry, JournalEntry


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def other_auth_client(other_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=other_user)
    return client


class TestJournalAPI:
    """Tests that drive the journal viewset design."""

    def test_create_journal_entry(self, auth_client, user):
        response = auth_client.post("/api/journal/", {
            "content": "Today I practiced being present.",
        })
        assert response.status_code == 201
        assert response.data["content"] == "Today I practiced being present."
        assert JournalEntry.objects.filter(user=user).count() == 1

    def test_create_journal_auto_sets_date(self, auth_client):
        """If no date provided, defaults to today."""
        response = auth_client.post("/api/journal/", {
            "content": "Test entry",
        })
        assert response.status_code == 201
        assert response.data["date"] == str(date.today())

    def test_create_journal_with_specific_date(self, auth_client):
        response = auth_client.post("/api/journal/", {
            "content": "Backdated entry",
            "date": "2026-01-15",
        })
        assert response.status_code == 201
        assert response.data["date"] == "2026-01-15"

    def test_list_journal_entries(self, auth_client, user):
        JournalEntry.objects.create(user=user, content="Entry 1", date=date(2026, 1, 1))
        JournalEntry.objects.create(user=user, content="Entry 2", date=date(2026, 1, 2))
        response = auth_client.get("/api/journal/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_get_today_entry(self, auth_client, user):
        JournalEntry.objects.create(
            user=user, content="Today's entry", date=date.today()
        )
        response = auth_client.get("/api/journal/today/")
        assert response.status_code == 200
        assert response.data["content"] == "Today's entry"

    def test_get_today_entry_empty(self, auth_client):
        """Returns 404 if no entry for today."""
        response = auth_client.get("/api/journal/today/")
        assert response.status_code == 404

    def test_get_entry_by_date(self, auth_client, user):
        JournalEntry.objects.create(
            user=user, content="Specific day", date=date(2026, 1, 15)
        )
        response = auth_client.get("/api/journal/2026-01-15/")
        assert response.status_code == 200
        assert response.data["content"] == "Specific day"

    def test_update_journal_entry(self, auth_client, user):
        entry = JournalEntry.objects.create(
            user=user, content="Original", date=date.today()
        )
        response = auth_client.patch(f"/api/journal/{entry.pk}/", {
            "content": "Updated content",
        })
        assert response.status_code == 200
        entry.refresh_from_db()
        assert entry.content == "Updated content"


class TestJournalMultiTenancy:
    """User A cannot see or modify User B's journal entries."""

    def test_user_cannot_list_other_users_entries(
        self, auth_client, other_user
    ):
        JournalEntry.objects.create(
            user=other_user, content="Private", date=date.today()
        )
        response = auth_client.get("/api/journal/")
        assert len(response.data["results"]) == 0

    def test_user_cannot_access_other_users_entry(
        self, auth_client, other_user
    ):
        entry = JournalEntry.objects.create(
            user=other_user, content="Private", date=date(2026, 1, 15)
        )
        response = auth_client.get(f"/api/journal/{entry.pk}/")
        assert response.status_code == 404

    def test_user_cannot_update_other_users_entry(
        self, auth_client, other_user
    ):
        entry = JournalEntry.objects.create(
            user=other_user, content="Private", date=date.today()
        )
        response = auth_client.patch(f"/api/journal/{entry.pk}/", {
            "content": "Hacked",
        })
        assert response.status_code == 404


class TestCheckinAPI:
    """Tests for the daily check-in endpoints."""

    def test_get_today_checkin(self, auth_client, user):
        DailyCheckin.objects.create(user=user, date=date.today())
        response = auth_client.get("/api/checkins/today/")
        assert response.status_code == 200
        assert response.data["meditation_completed"] is False

    def test_get_today_checkin_auto_creates(self, auth_client):
        """If no checkin exists for today, create one."""
        response = auth_client.get("/api/checkins/today/")
        assert response.status_code == 200
        assert DailyCheckin.objects.count() == 1

    def test_log_meditation(self, auth_client, user):
        response = auth_client.post("/api/checkins/meditation/", {
            "duration_minutes": 20,
        })
        assert response.status_code == 200
        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.meditation_completed is True
        assert checkin.meditation_duration == 20

    def test_log_meditation_no_duration(self, auth_client, user):
        """Duration is optional."""
        response = auth_client.post("/api/checkins/meditation/", {})
        assert response.status_code == 200
        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.meditation_completed is True
        assert checkin.meditation_duration is None

    def test_checkin_scoped_to_user(self, auth_client, other_user):
        DailyCheckin.objects.create(
            user=other_user,
            date=date.today(),
            meditation_completed=True,
        )
        response = auth_client.get("/api/checkins/today/")
        # Should get a fresh checkin, not other_user's
        assert response.data["meditation_completed"] is False


class TestGratitudeAPI:
    """Tests for the gratitude endpoints."""

    def test_create_gratitude(self, auth_client, user):
        response = auth_client.post("/api/gratitude/", {
            "items": ["good sleep", "coffee", "my caregivers"],
        }, format="json")
        assert response.status_code == 201
        assert len(response.data["items"]) == 3

    def test_create_gratitude_auto_sets_date(self, auth_client):
        response = auth_client.post("/api/gratitude/", {
            "items": ["sunshine"],
        }, format="json")
        assert response.data["date"] == str(date.today())

    def test_get_today_gratitude(self, auth_client, user):
        GratitudeEntry.objects.create(
            user=user, date=date.today(), items=["peace"]
        )
        response = auth_client.get("/api/gratitude/today/")
        assert response.status_code == 200
        assert response.data["items"] == ["peace"]

    def test_list_gratitude(self, auth_client, user):
        GratitudeEntry.objects.create(
            user=user, date=date(2026, 1, 1), items=["a"]
        )
        GratitudeEntry.objects.create(
            user=user, date=date(2026, 1, 2), items=["b"]
        )
        response = auth_client.get("/api/gratitude/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_gratitude_scoped_to_user(self, auth_client, other_user):
        GratitudeEntry.objects.create(
            user=other_user, date=date.today(), items=["secret"]
        )
        response = auth_client.get("/api/gratitude/")
        assert len(response.data["results"]) == 0
