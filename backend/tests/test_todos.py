"""
TDD: Todo Model Tests

Tests that drive the Todo model design.
"""

from datetime import date

import pytest
from django.db import IntegrityError
from django.utils import timezone


class TestTodo:
    """Tests that drive the Todo model design."""

    def test_create_todo(self, user):
        from apps.todos.models import Todo

        todo = Todo.objects.create(user=user, task="Call the doctor")
        assert todo.task == "Call the doctor"
        assert todo.user == user

    def test_todo_defaults(self, user):
        """New todos are incomplete with no due date."""
        from apps.todos.models import Todo

        todo = Todo.objects.create(user=user, task="Test")
        assert todo.completed is False
        assert todo.completed_at is None
        assert todo.due_date is None

    def test_todo_with_due_date(self, user):
        from apps.todos.models import Todo

        tomorrow = date(2026, 2, 2)
        todo = Todo.objects.create(
            user=user, task="Buy groceries", due_date=tomorrow
        )
        assert todo.due_date == tomorrow

    def test_complete_todo(self, user):
        from apps.todos.models import Todo

        todo = Todo.objects.create(user=user, task="Test")
        todo.completed = True
        todo.completed_at = timezone.now()
        todo.save()

        todo.refresh_from_db()
        assert todo.completed is True
        assert todo.completed_at is not None

    def test_todo_ordering(self, user):
        """Incomplete first, then by due date, then by newest."""
        from apps.todos.models import Todo

        completed = Todo.objects.create(user=user, task="Done")
        completed.completed = True
        completed.save()

        no_date = Todo.objects.create(user=user, task="No date")
        with_date = Todo.objects.create(
            user=user, task="Has date", due_date=date(2026, 2, 5)
        )

        todos = list(Todo.objects.filter(user=user))
        # Incomplete before completed
        assert todos[-1] == completed

    def test_todo_str(self, user):
        from apps.todos.models import Todo

        todo = Todo.objects.create(user=user, task="Call the doctor")
        assert "Call the doctor" in str(todo)

    def test_todo_timestamps(self, user):
        from apps.todos.models import Todo

        todo = Todo.objects.create(user=user, task="Test")
        assert todo.created_at is not None


class TestTodoMultiTenancy:
    """Multi-tenancy tests for todos."""

    def test_users_have_separate_todos(self, user, other_user):
        from apps.todos.models import Todo

        Todo.objects.create(user=user, task="User A task")
        Todo.objects.create(user=other_user, task="User B task")

        user_todos = Todo.objects.filter(user=user)
        assert user_todos.count() == 1
        assert user_todos.first().task == "User A task"

        other_todos = Todo.objects.filter(user=other_user)
        assert other_todos.count() == 1
        assert other_todos.first().task == "User B task"
