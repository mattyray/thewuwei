"""
TDD: WebSocket Consumer Tests

Tests for the chat WebSocket consumer that bridges
the frontend to the LangGraph agent.

These test connection auth, message handling, chat history
persistence, and user scoping.

Note: Async tests need transaction=True because database_sync_to_async
runs in a separate thread, so the standard test rollback doesn't apply.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model

from apps.chat.consumers import ChatConsumer
from apps.chat.models import ChatMessage

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


@database_sync_to_async
def create_user(email=None, password="testpass123"):
    if email is None:
        email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    return User.objects.create_user(email=email, password=password)


@database_sync_to_async
def get_message_count(user):
    return ChatMessage.objects.filter(user=user).count()


def make_communicator(user):
    """Create a WebSocket communicator with an authenticated user."""
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    communicator.scope["user"] = user
    return communicator


@pytest.mark.asyncio
class TestWebSocketAuth:
    """WebSocket connections require authentication."""

    async def test_authenticated_user_connects(self):
        user = await create_user()
        communicator = make_communicator(user)
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_unauthenticated_rejected(self):
        from django.contrib.auth.models import AnonymousUser

        communicator = make_communicator(AnonymousUser())
        connected, code = await communicator.connect()
        assert connected is False


@pytest.mark.asyncio
class TestWebSocketMessages:
    """Message handling and persistence."""

    async def test_user_message_saved(self):
        user = await create_user()
        communicator = make_communicator(user)
        await communicator.connect()

        with patch(
            "apps.chat.consumers.ChatConsumer.get_agent_response",
            new_callable=AsyncMock,
            return_value="Logged.",
        ):
            await communicator.send_json_to({
                "type": "message",
                "content": "Did my meditation",
            })

            response = await communicator.receive_json_from(timeout=5)
            assert response["type"] in ("token", "complete")

        count = await get_message_count(user)
        assert count >= 1

        await communicator.disconnect()

    async def test_assistant_response_saved(self):
        user = await create_user()
        communicator = make_communicator(user)
        await communicator.connect()

        with patch(
            "apps.chat.consumers.ChatConsumer.get_agent_response",
            new_callable=AsyncMock,
            return_value="Great, meditation logged!",
        ):
            await communicator.send_json_to({
                "type": "message",
                "content": "Hello",
            })

            response = await communicator.receive_json_from(timeout=5)
            while response.get("type") != "complete":
                response = await communicator.receive_json_from(timeout=5)

        count = await get_message_count(user)
        assert count == 2  # user + assistant

        await communicator.disconnect()

    async def test_complete_message_includes_content(self):
        user = await create_user()
        communicator = make_communicator(user)
        await communicator.connect()

        with patch(
            "apps.chat.consumers.ChatConsumer.get_agent_response",
            new_callable=AsyncMock,
            return_value="Namaste.",
        ):
            await communicator.send_json_to({
                "type": "message",
                "content": "Hi",
            })

            response = await communicator.receive_json_from(timeout=5)
            assert response["type"] == "complete"
            assert response["content"] == "Namaste."

        await communicator.disconnect()


@pytest.mark.asyncio
class TestWebSocketScoping:
    """User scoping — messages belong to the user who sent them."""

    async def test_messages_scoped_to_user(self):
        user_a = await create_user("a@test.com")
        user_b = await create_user("b@test.com")

        comm_a = make_communicator(user_a)
        await comm_a.connect()

        with patch(
            "apps.chat.consumers.ChatConsumer.get_agent_response",
            new_callable=AsyncMock,
            return_value="Hi A",
        ):
            await comm_a.send_json_to({
                "type": "message",
                "content": "Hello from A",
            })
            await comm_a.receive_json_from(timeout=5)

        await comm_a.disconnect()

        b_count = await get_message_count(user_b)
        assert b_count == 0

        a_count = await get_message_count(user_a)
        assert a_count == 2
