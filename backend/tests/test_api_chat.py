"""
TDD: Chat Messages API Tests

Tests for the chat message REST endpoints.
"""

from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient

from apps.chat.models import ChatMessage


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


class TestChatMessageAPI:
    """Tests for the chat message list and by-date endpoints."""

    def test_list_messages(self, auth_client, user):
        ChatMessage.objects.create(user=user, role="user", content="Hello")
        ChatMessage.objects.create(user=user, role="assistant", content="Hi there")
        response = auth_client.get("/api/chat-messages/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_list_messages_ordered_by_created_at(self, auth_client, user):
        msg1 = ChatMessage.objects.create(user=user, role="user", content="First")
        msg2 = ChatMessage.objects.create(user=user, role="assistant", content="Second")
        response = auth_client.get("/api/chat-messages/")
        assert response.data["results"][0]["content"] == "First"
        assert response.data["results"][1]["content"] == "Second"

    def test_get_messages_by_date(self, auth_client, user, today):
        ChatMessage.objects.create(user=user, role="user", content="Today msg")
        ChatMessage.objects.create(user=user, role="assistant", content="Today reply")
        response = auth_client.get(f"/api/chat-messages/{today}/")
        assert response.status_code == 200
        assert len(response.data) == 2

    def test_get_messages_by_date_filters_correctly(self, auth_client, user, today):
        msg_today = ChatMessage.objects.create(
            user=user, role="user", content="Today"
        )
        msg_yesterday = ChatMessage.objects.create(
            user=user, role="user", content="Yesterday"
        )
        # Manually set the created_at to yesterday
        yesterday = today - timedelta(days=1)
        ChatMessage.objects.filter(pk=msg_yesterday.pk).update(
            created_at=msg_yesterday.created_at - timedelta(days=1)
        )

        response = auth_client.get(f"/api/chat-messages/{today}/")
        assert len(response.data) == 1
        assert response.data[0]["content"] == "Today"

    def test_get_messages_by_date_empty(self, auth_client, today):
        response = auth_client.get(f"/api/chat-messages/{today}/")
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_read_only_no_create(self, auth_client):
        response = auth_client.post("/api/chat-messages/", {
            "role": "user",
            "content": "Should not work",
        })
        assert response.status_code == 405

    def test_read_only_no_delete(self, auth_client, user):
        msg = ChatMessage.objects.create(user=user, role="user", content="Hello")
        response = auth_client.delete(f"/api/chat-messages/{msg.pk}/")
        assert response.status_code == 405

    def test_requires_auth(self):
        client = APIClient()
        response = client.get("/api/chat-messages/")
        assert response.status_code in (401, 403)


class TestChatMessageMultiTenancy:
    """User A cannot see User B's chat messages."""

    def test_user_cannot_list_other_users_messages(self, auth_client, other_user):
        ChatMessage.objects.create(
            user=other_user, role="user", content="Private"
        )
        response = auth_client.get("/api/chat-messages/")
        assert len(response.data["results"]) == 0

    def test_user_cannot_access_other_users_message(self, auth_client, other_user):
        msg = ChatMessage.objects.create(
            user=other_user, role="user", content="Private"
        )
        response = auth_client.get(f"/api/chat-messages/{msg.pk}/")
        assert response.status_code == 404

    def test_by_date_scoped_to_user(self, auth_client, other_user, today):
        ChatMessage.objects.create(
            user=other_user, role="user", content="Other's msg"
        )
        response = auth_client.get(f"/api/chat-messages/{today}/")
        assert len(response.data) == 0
