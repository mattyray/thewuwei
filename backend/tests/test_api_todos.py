"""
TDD: Todos API Tests

Tests for todo CRUD and multi-tenancy at the API level.
"""

from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.todos.models import Todo


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


class TestTodoAPI:

    def test_create_todo(self, auth_client, user):
        response = auth_client.post("/api/todos/", {
            "task": "Call the doctor",
        })
        assert response.status_code == 201
        assert response.data["task"] == "Call the doctor"
        assert Todo.objects.filter(user=user).count() == 1

    def test_create_todo_with_due_date(self, auth_client):
        response = auth_client.post("/api/todos/", {
            "task": "Buy groceries",
            "due_date": "2026-02-05",
        })
        assert response.status_code == 201
        assert response.data["due_date"] == "2026-02-05"

    def test_list_todos(self, auth_client, user):
        Todo.objects.create(user=user, task="Task 1")
        Todo.objects.create(user=user, task="Task 2")
        response = auth_client.get("/api/todos/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2

    def test_update_todo(self, auth_client, user):
        todo = Todo.objects.create(user=user, task="Original")
        response = auth_client.patch(f"/api/todos/{todo.pk}/", {
            "task": "Updated task",
        })
        assert response.status_code == 200
        todo.refresh_from_db()
        assert todo.task == "Updated task"

    def test_complete_todo(self, auth_client, user):
        todo = Todo.objects.create(user=user, task="Do thing")
        response = auth_client.post(f"/api/todos/{todo.pk}/complete/")
        assert response.status_code == 200
        todo.refresh_from_db()
        assert todo.completed is True
        assert todo.completed_at is not None

    def test_delete_todo(self, auth_client, user):
        todo = Todo.objects.create(user=user, task="Delete me")
        response = auth_client.delete(f"/api/todos/{todo.pk}/")
        assert response.status_code == 204
        assert Todo.objects.filter(pk=todo.pk).count() == 0


class TestTodoMultiTenancy:

    def test_user_cannot_list_other_users_todos(self, auth_client, other_user):
        Todo.objects.create(user=other_user, task="Secret task")
        response = auth_client.get("/api/todos/")
        assert len(response.data["results"]) == 0

    def test_user_cannot_complete_other_users_todo(self, auth_client, other_user):
        todo = Todo.objects.create(user=other_user, task="Secret task")
        response = auth_client.post(f"/api/todos/{todo.pk}/complete/")
        assert response.status_code == 404

    def test_user_cannot_delete_other_users_todo(self, auth_client, other_user):
        todo = Todo.objects.create(user=other_user, task="Secret task")
        response = auth_client.delete(f"/api/todos/{todo.pk}/")
        assert response.status_code == 404
