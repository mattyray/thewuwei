"""
TDD: Mantra Model Tests

Tests that drive the Mantra model design.
"""

import pytest


class TestMantra:
    """Tests that drive the Mantra model design."""

    def test_create_mantra(self, user):
        from apps.mantras.models import Mantra

        mantra = Mantra.objects.create(
            user=user,
            content="Intrusive thoughts are mud in a glass of water. Let it settle.",
        )
        assert "Intrusive thoughts" in mantra.content
        assert mantra.user == user

    def test_mantra_default_order(self, user):
        """Mantras have an order field, defaulting to 0."""
        from apps.mantras.models import Mantra

        mantra = Mantra.objects.create(user=user, content="Test")
        assert mantra.order == 0

    def test_mantra_ordering(self, user):
        """Mantras are ordered by order field, then created_at."""
        from apps.mantras.models import Mantra

        second = Mantra.objects.create(user=user, content="Second", order=2)
        first = Mantra.objects.create(user=user, content="First", order=1)

        mantras = list(Mantra.objects.filter(user=user))
        assert mantras[0] == first
        assert mantras[1] == second

    def test_mantra_reorder(self, user):
        """Can reorder mantras by updating order field."""
        from apps.mantras.models import Mantra

        a = Mantra.objects.create(user=user, content="A", order=1)
        b = Mantra.objects.create(user=user, content="B", order=2)

        # Swap order
        a.order = 2
        b.order = 1
        a.save()
        b.save()

        mantras = list(Mantra.objects.filter(user=user))
        assert mantras[0].content == "B"
        assert mantras[1].content == "A"

    def test_mantra_str(self, user):
        from apps.mantras.models import Mantra

        mantra = Mantra.objects.create(user=user, content="Be like water")
        assert "Be like water" in str(mantra)

    def test_mantra_timestamps(self, user):
        from apps.mantras.models import Mantra

        mantra = Mantra.objects.create(user=user, content="Test")
        assert mantra.created_at is not None


class TestMantraMultiTenancy:
    """Multi-tenancy tests for mantras."""

    def test_users_have_separate_mantras(self, user, other_user):
        from apps.mantras.models import Mantra

        Mantra.objects.create(user=user, content="User A mantra")
        Mantra.objects.create(user=other_user, content="User B mantra")

        user_mantras = Mantra.objects.filter(user=user)
        assert user_mantras.count() == 1
        assert user_mantras.first().content == "User A mantra"
