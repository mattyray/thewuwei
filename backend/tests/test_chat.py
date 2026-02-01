"""
TDD: ChatMessage Model Tests

Tests that drive the ChatMessage model design.
"""

import pytest


class TestChatMessage:
    """Tests that drive the ChatMessage model design."""

    def test_create_user_message(self, user):
        from apps.chat.models import ChatMessage

        msg = ChatMessage.objects.create(
            user=user,
            role="user",
            content="Did my meditation for 20 minutes",
        )
        assert msg.role == "user"
        assert msg.content == "Did my meditation for 20 minutes"

    def test_create_assistant_message(self, user):
        from apps.chat.models import ChatMessage

        msg = ChatMessage.objects.create(
            user=user,
            role="assistant",
            content="Logged. 20 minutes of stillness.",
        )
        assert msg.role == "assistant"

    def test_chat_ordering_chronological(self, user):
        """Messages ordered by created_at (oldest first)."""
        from apps.chat.models import ChatMessage

        first = ChatMessage.objects.create(
            user=user, role="user", content="Hello"
        )
        second = ChatMessage.objects.create(
            user=user, role="assistant", content="Hi there"
        )
        messages = list(ChatMessage.objects.filter(user=user))
        assert messages[0] == first
        assert messages[1] == second

    def test_chat_timestamps(self, user):
        from apps.chat.models import ChatMessage

        msg = ChatMessage.objects.create(
            user=user, role="user", content="Test"
        )
        assert msg.created_at is not None


class TestChatMultiTenancy:
    """Multi-tenancy tests for chat messages."""

    def test_users_have_separate_chat_history(self, user, other_user):
        from apps.chat.models import ChatMessage

        ChatMessage.objects.create(
            user=user, role="user", content="User A message"
        )
        ChatMessage.objects.create(
            user=other_user, role="user", content="User B message"
        )

        user_messages = ChatMessage.objects.filter(user=user)
        assert user_messages.count() == 1
        assert user_messages.first().content == "User A message"
