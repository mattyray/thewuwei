"""
TDD: User/Auth API Tests

Tests for the /api/auth/me/ endpoint.
"""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestMeEndpoint:

    def test_get_current_user(self, auth_client, user):
        response = auth_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email
        assert response.data["timezone"] == "America/New_York"

    def test_update_timezone(self, auth_client, user):
        response = auth_client.patch("/api/auth/me/", {
            "timezone": "Europe/London",
        })
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.timezone == "Europe/London"

    def test_update_reminder_settings(self, auth_client, user):
        response = auth_client.patch("/api/auth/me/", {
            "reminder_enabled": False,
        })
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.reminder_enabled is False

    def test_cannot_set_arbitrary_fields(self, auth_client, user):
        """Users can't make themselves superusers via the API."""
        response = auth_client.patch("/api/auth/me/", {
            "is_superuser": True,
        })
        user.refresh_from_db()
        assert user.is_superuser is False
