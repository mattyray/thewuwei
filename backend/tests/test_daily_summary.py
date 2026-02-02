"""
TDD: Daily Summary API Tests

Tests for the daily summary aggregate endpoint and recent summaries.
"""

from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient

from apps.chat.models import ChatMessage
from apps.journal.models import DailyCheckin, GratitudeEntry, JournalEntry
from apps.todos.models import Todo


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


class TestDailySummaryAPI:
    """Tests for GET /api/daily/{date}/ aggregate endpoint."""

    def test_get_summary_for_date(self, auth_client, user, today):
        DailyCheckin.objects.create(
            user=user, date=today, meditation_completed=True
        )
        JournalEntry.objects.create(
            user=user, date=today, content="Today's entry"
        )
        GratitudeEntry.objects.create(
            user=user, date=today, items=["sleep", "coffee"]
        )
        Todo.objects.create(user=user, task="Call doctor")
        ChatMessage.objects.create(user=user, role="user", content="Hello")

        response = auth_client.get(f"/api/daily/{today}/")
        assert response.status_code == 200
        assert response.data["date"] == str(today)
        assert response.data["checkin"]["meditation_completed"] is True
        assert response.data["journal"]["content"] == "Today's entry"
        assert response.data["gratitude"]["items"] == ["sleep", "coffee"]
        assert len(response.data["todos"]) == 1
        assert len(response.data["chat_messages"]) == 1

    def test_get_summary_today_shortcut(self, auth_client, user, today):
        JournalEntry.objects.create(
            user=user, date=today, content="Today's entry"
        )
        response = auth_client.get("/api/daily/today/")
        assert response.status_code == 200
        assert response.data["date"] == str(today)
        assert response.data["journal"]["content"] == "Today's entry"

    def test_get_summary_empty_date(self, auth_client, today):
        response = auth_client.get(f"/api/daily/{today}/")
        assert response.status_code == 200
        assert response.data["checkin"] is None
        assert response.data["journal"] is None
        assert response.data["gratitude"] is None
        assert response.data["todos"] == []
        assert response.data["chat_messages"] == []

    def test_get_summary_invalid_date(self, auth_client):
        response = auth_client.get("/api/daily/not-a-date/")
        assert response.status_code == 400

    def test_summary_scoped_to_user(self, auth_client, other_user, today):
        JournalEntry.objects.create(
            user=other_user, date=today, content="Other's entry"
        )
        response = auth_client.get(f"/api/daily/{today}/")
        assert response.data["journal"] is None

    def test_summary_todos_filtered_by_date(self, auth_client, user, today):
        todo_today = Todo.objects.create(user=user, task="Today task")
        todo_old = Todo.objects.create(user=user, task="Old task")
        # Move old todo's created_at to yesterday
        yesterday = today - timedelta(days=1)
        Todo.objects.filter(pk=todo_old.pk).update(
            created_at=todo_old.created_at - timedelta(days=1)
        )

        response = auth_client.get(f"/api/daily/{today}/")
        assert len(response.data["todos"]) == 1
        assert response.data["todos"][0]["task"] == "Today task"

    def test_requires_auth(self):
        client = APIClient()
        response = client.get(f"/api/daily/{date.today()}/")
        assert response.status_code in (401, 403)


class TestRecentDailySummariesAPI:
    """Tests for GET /api/daily/recent/ endpoint."""

    def test_returns_recent_days_with_activity(self, auth_client, user, today):
        yesterday = today - timedelta(days=1)
        JournalEntry.objects.create(
            user=user, date=yesterday, content="Yesterday's entry"
        )
        response = auth_client.get("/api/daily/recent/")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["date"] == str(yesterday)

    def test_excludes_days_without_activity(self, auth_client, user, today):
        # Only create activity 3 days ago, not yesterday or 2 days ago
        three_days_ago = today - timedelta(days=3)
        JournalEntry.objects.create(
            user=user, date=three_days_ago, content="Old entry"
        )
        response = auth_client.get("/api/daily/recent/")
        assert len(response.data) == 1
        assert response.data[0]["date"] == str(three_days_ago)

    def test_excludes_today(self, auth_client, user, today):
        JournalEntry.objects.create(
            user=user, date=today, content="Today's entry"
        )
        response = auth_client.get("/api/daily/recent/")
        assert len(response.data) == 0

    def test_chat_messages_excluded(self, auth_client, user, today):
        yesterday = today - timedelta(days=1)
        DailyCheckin.objects.create(user=user, date=yesterday)
        ChatMessage.objects.create(user=user, role="user", content="Yesterday msg")
        # Move message to yesterday
        msg = ChatMessage.objects.last()
        ChatMessage.objects.filter(pk=msg.pk).update(
            created_at=msg.created_at - timedelta(days=1)
        )

        response = auth_client.get("/api/daily/recent/")
        assert len(response.data) == 1
        assert response.data[0]["chat_messages"] == []

    def test_custom_days_param(self, auth_client, user, today):
        for i in range(1, 8):
            d = today - timedelta(days=i)
            DailyCheckin.objects.create(user=user, date=d)

        response = auth_client.get("/api/daily/recent/?days=3")
        assert len(response.data) == 3

    def test_capped_at_30_days(self, auth_client, user, today):
        response = auth_client.get("/api/daily/recent/?days=100")
        assert response.status_code == 200
        # Should not crash, just cap at 30

    def test_scoped_to_user(self, auth_client, other_user, today):
        yesterday = today - timedelta(days=1)
        JournalEntry.objects.create(
            user=other_user, date=yesterday, content="Other's entry"
        )
        response = auth_client.get("/api/daily/recent/")
        assert len(response.data) == 0

    def test_requires_auth(self):
        client = APIClient()
        response = client.get("/api/daily/recent/")
        assert response.status_code in (401, 403)
