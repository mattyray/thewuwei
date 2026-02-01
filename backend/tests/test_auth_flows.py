"""
TDD: Auth Flow Tests

Tests for registration, login, logout, CSRF handling,
and allauth headless configuration for Google OAuth.
"""

import pytest
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# --- Registration ---


class TestRegister:
    """POST /api/auth/register/ — email/password signup."""

    def test_register_creates_user(self, api_client, db):
        response = api_client.post("/api/auth/register/", {
            "email": "new@example.com",
            "password": "strongpass123!",
            "password_confirm": "strongpass123!",
        })
        assert response.status_code == 201
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_returns_user_data(self, api_client, db):
        response = api_client.post("/api/auth/register/", {
            "email": "new@example.com",
            "password": "strongpass123!",
            "password_confirm": "strongpass123!",
        })
        assert response.data["email"] == "new@example.com"
        assert "password" not in response.data
        assert "id" in response.data

    def test_register_logs_in_user(self, api_client, db):
        """After registration, the session is set — user is authenticated."""
        api_client.post("/api/auth/register/", {
            "email": "new@example.com",
            "password": "strongpass123!",
            "password_confirm": "strongpass123!",
        })
        # Subsequent request should be authenticated
        response = api_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == "new@example.com"

    def test_register_duplicate_email(self, api_client, user):
        """Can't register with an email that already exists."""
        response = api_client.post("/api/auth/register/", {
            "email": user.email,
            "password": "strongpass123!",
            "password_confirm": "strongpass123!",
        })
        assert response.status_code == 400

    def test_register_password_mismatch(self, api_client, db):
        response = api_client.post("/api/auth/register/", {
            "email": "new@example.com",
            "password": "strongpass123!",
            "password_confirm": "differentpass456!",
        })
        assert response.status_code == 400

    def test_register_weak_password(self, api_client, db):
        """Django password validators reject weak passwords."""
        response = api_client.post("/api/auth/register/", {
            "email": "new@example.com",
            "password": "123",
            "password_confirm": "123",
        })
        assert response.status_code == 400

    def test_register_missing_email(self, api_client, db):
        response = api_client.post("/api/auth/register/", {
            "password": "strongpass123!",
            "password_confirm": "strongpass123!",
        })
        assert response.status_code == 400

    def test_register_missing_password(self, api_client, db):
        response = api_client.post("/api/auth/register/", {
            "email": "new@example.com",
        })
        assert response.status_code == 400


# --- Login ---


class TestLogin:
    """POST /api/auth/login/ — session-based login."""

    def test_login_valid_credentials(self, api_client, user):
        response = api_client.post("/api/auth/login/", {
            "email": user.email,
            "password": "testpass123",
        })
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_login_sets_session(self, api_client, user):
        """After login, subsequent requests are authenticated."""
        api_client.post("/api/auth/login/", {
            "email": user.email,
            "password": "testpass123",
        })
        response = api_client.get("/api/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == user.email

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post("/api/auth/login/", {
            "email": user.email,
            "password": "wrongpassword",
        })
        assert response.status_code == 400

    def test_login_nonexistent_user(self, api_client, db):
        response = api_client.post("/api/auth/login/", {
            "email": "nobody@example.com",
            "password": "testpass123",
        })
        assert response.status_code == 400

    def test_login_missing_fields(self, api_client, db):
        response = api_client.post("/api/auth/login/", {})
        assert response.status_code == 400


# --- Logout ---


class TestLogout:
    """POST /api/auth/logout/ — session clear."""

    def test_logout_clears_session(self, api_client, user):
        """After logout, requests are no longer authenticated."""
        # Login first
        api_client.post("/api/auth/login/", {
            "email": user.email,
            "password": "testpass123",
        })
        # Confirm authenticated
        assert api_client.get("/api/auth/me/").status_code == 200

        # Logout
        response = api_client.post("/api/auth/logout/")
        assert response.status_code == 200

        # Confirm unauthenticated
        assert api_client.get("/api/auth/me/").status_code in (401, 403)

    def test_logout_unauthenticated_still_200(self, api_client, db):
        """Logout is idempotent — calling it when not logged in is fine."""
        response = api_client.post("/api/auth/logout/")
        assert response.status_code == 200


# --- CSRF ---


class TestCSRF:
    """GET /api/auth/csrf/ — provides CSRF token for SPA."""

    def test_csrf_endpoint_returns_token(self, api_client, db):
        response = api_client.get("/api/auth/csrf/")
        assert response.status_code == 200
        assert "csrftoken" in response.cookies or "csrfToken" in response.data


# --- Allauth Headless ---


class TestAllAuthHeadless:
    """allauth headless endpoints are available for Google OAuth."""

    def test_headless_config_endpoint(self, api_client, db):
        """The allauth headless config endpoint is reachable."""
        response = api_client.get(
            "/_allauth/app/v1/config",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        data = response.json()
        assert "socialaccount" in data["data"]

    def test_google_provider_listed(self, api_client, db):
        """Google is listed as an available social provider."""
        response = api_client.get(
            "/_allauth/app/v1/config",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        providers = data["data"]["socialaccount"]["providers"]
        provider_ids = [p["id"] for p in providers]
        assert "google" in provider_ids
