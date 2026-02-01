import pytest
from apps.users.models import User


@pytest.fixture
def user(db) -> User:
    """Create a standard test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def other_user(db) -> User:
    """Create a second user for multi-tenancy tests."""
    return User.objects.create_user(
        email="other@example.com",
        password="testpass123",
    )
