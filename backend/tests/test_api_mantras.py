"""
TDD: Mantras API Tests

Tests for mantra CRUD, reordering, and multi-tenancy.
"""

import pytest
from rest_framework.test import APIClient

from apps.mantras.models import Mantra


@pytest.fixture
def auth_client(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class TestMantraAPI:

    def test_create_mantra(self, auth_client, user):
        response = auth_client.post("/api/mantras/", {
            "content": "Be like water",
        })
        assert response.status_code == 201
        assert response.data["content"] == "Be like water"

    def test_list_mantras(self, auth_client, user):
        Mantra.objects.create(user=user, content="A", order=1)
        Mantra.objects.create(user=user, content="B", order=2)
        response = auth_client.get("/api/mantras/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
        # Should be ordered
        assert response.data["results"][0]["content"] == "A"

    def test_update_mantra(self, auth_client, user):
        mantra = Mantra.objects.create(user=user, content="Original")
        response = auth_client.patch(f"/api/mantras/{mantra.pk}/", {
            "content": "Updated",
        })
        assert response.status_code == 200
        mantra.refresh_from_db()
        assert mantra.content == "Updated"

    def test_delete_mantra(self, auth_client, user):
        mantra = Mantra.objects.create(user=user, content="Delete me")
        response = auth_client.delete(f"/api/mantras/{mantra.pk}/")
        assert response.status_code == 204

    def test_reorder_mantras(self, auth_client, user):
        a = Mantra.objects.create(user=user, content="A", order=1)
        b = Mantra.objects.create(user=user, content="B", order=2)
        c = Mantra.objects.create(user=user, content="C", order=3)

        response = auth_client.post("/api/mantras/reorder/", {
            "order": [c.pk, a.pk, b.pk],
        }, format="json")
        assert response.status_code == 200

        a.refresh_from_db()
        b.refresh_from_db()
        c.refresh_from_db()
        assert c.order < a.order < b.order


class TestMantraMultiTenancy:

    def test_user_cannot_see_other_users_mantras(self, auth_client, other_user):
        Mantra.objects.create(user=other_user, content="Secret mantra")
        response = auth_client.get("/api/mantras/")
        assert len(response.data["results"]) == 0

    def test_user_cannot_delete_other_users_mantra(self, auth_client, other_user):
        mantra = Mantra.objects.create(user=other_user, content="Secret")
        response = auth_client.delete(f"/api/mantras/{mantra.pk}/")
        assert response.status_code == 404
