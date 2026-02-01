"""
TDD: User Model Tests

These tests drive the design of the custom User model.
They establish:
1. Email-based auth (no username)
2. Default field values
3. User creation via manager
4. Superuser creation
5. Multi-tenancy foundation (two users can coexist)
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class TestUserModel:
    """Tests that drive the User model schema design."""

    def test_user_model_is_custom(self):
        """AUTH_USER_MODEL points to our custom model, not Django's default."""
        assert User.__name__ == "User"
        assert User._meta.app_label == "users"

    def test_create_user_with_email(self, db):
        """Users authenticate with email, not username."""
        user = User.objects.create_user(
            email="matt@thewuwei.com",
            password="testpass123",
        )
        assert user.email == "matt@thewuwei.com"
        assert user.check_password("testpass123")
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_requires_email(self, db):
        """Email is mandatory — can't create a user without it."""
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="testpass123")

    def test_email_is_unique(self, user):
        """Two users can't share the same email."""
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email="test@example.com",
                password="different",
            )

    def test_email_is_normalized(self, db):
        """Email domain is lowercased."""
        user = User.objects.create_user(
            email="Matt@THEWUWEI.COM",
            password="testpass123",
        )
        assert user.email == "Matt@thewuwei.com"

    def test_no_username_field(self, db):
        """Username field is removed — email is the identifier."""
        assert User.USERNAME_FIELD == "email"
        assert not hasattr(User, "username") or User.username is None

    def test_str_returns_email(self, user):
        """String representation is the email."""
        assert str(user) == "test@example.com"


class TestUserDefaults:
    """Tests that drive default field values."""

    def test_default_timezone(self, user):
        assert user.timezone == "America/New_York"

    def test_default_reminder_time(self, user):
        from datetime import time

        assert user.daily_reminder_time == time(20, 0)

    def test_default_reminder_enabled(self, user):
        assert user.reminder_enabled is True

    def test_default_reflections_today(self, user):
        assert user.reflections_today == 0

    def test_default_api_key_empty(self, user):
        """API key starts empty — users can add their own later."""
        assert user.anthropic_api_key == ""


class TestSuperuserCreation:
    """Tests that drive the superuser manager method."""

    def test_create_superuser(self, db):
        admin = User.objects.create_superuser(
            email="admin@thewuwei.com",
            password="adminpass123",
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True


class TestMultiTenancyFoundation:
    """Tests that establish the multi-tenancy pattern from day one."""

    def test_two_users_exist_independently(self, user, other_user):
        """Multiple users can coexist — foundation for data scoping."""
        assert User.objects.count() == 2
        assert user.email != other_user.email
        assert user.pk != other_user.pk
