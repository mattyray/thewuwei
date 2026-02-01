"""
TDD: API Authentication Tests

Every endpoint requires authentication. These tests prove it.
Unauthenticated requests get 401/403.
"""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestAuthRequired:
    """Every API endpoint rejects unauthenticated requests."""

    endpoints = [
        ("get", "/api/journal/"),
        ("post", "/api/journal/"),
        ("get", "/api/checkins/today/"),
        ("post", "/api/checkins/meditation/"),
        ("get", "/api/gratitude/"),
        ("post", "/api/gratitude/"),
        ("get", "/api/todos/"),
        ("post", "/api/todos/"),
        ("get", "/api/mantras/"),
        ("post", "/api/mantras/"),
        ("get", "/api/auth/me/"),
    ]

    @pytest.mark.parametrize("method,url", endpoints)
    def test_unauthenticated_rejected(self, api_client, method, url):
        response = getattr(api_client, method)(url)
        assert response.status_code in (401, 403)
