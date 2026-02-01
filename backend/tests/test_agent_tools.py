"""
TDD: Agent Tool Tests

These tests drive the design of every LangGraph agent tool.
Each tool is a function that takes a user and arguments,
performs a database operation, and returns a dict result.

Tools are tested independently of the LLM — they're pure
business logic functions that the agent calls.
"""

from datetime import date, timedelta

import pytest

from apps.journal.models import (
    DailyCheckin,
    GratitudeEntry,
    JournalEntry,
    WeeklySummary,
)
from apps.mantras.models import Mantra
from apps.todos.models import Todo


class TestLogMeditation:
    """Tests for the log_meditation tool."""

    def test_log_meditation_with_duration(self, user):
        from apps.agent.tools import log_meditation

        result = log_meditation(user=user, duration_minutes=20)
        assert result["logged"] is True
        assert result["duration"] == 20

        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.meditation_completed is True
        assert checkin.meditation_duration == 20
        assert checkin.meditation_completed_at is not None

    def test_log_meditation_without_duration(self, user):
        from apps.agent.tools import log_meditation

        result = log_meditation(user=user)
        assert result["logged"] is True
        assert result["duration"] is None

        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.meditation_completed is True
        assert checkin.meditation_duration is None

    def test_log_meditation_creates_checkin_if_missing(self, user):
        from apps.agent.tools import log_meditation

        assert not DailyCheckin.objects.filter(user=user).exists()
        log_meditation(user=user, duration_minutes=15)
        assert DailyCheckin.objects.filter(user=user, date=date.today()).exists()

    def test_log_meditation_updates_existing_checkin(self, user):
        from apps.agent.tools import log_meditation

        DailyCheckin.objects.create(user=user, date=date.today())
        log_meditation(user=user, duration_minutes=10)
        assert DailyCheckin.objects.filter(user=user, date=date.today()).count() == 1


class TestSaveGratitudeList:
    """Tests for the save_gratitude_list tool."""

    def test_save_gratitude_list(self, user):
        from apps.agent.tools import save_gratitude_list

        result = save_gratitude_list(
            user=user, items=["good sleep", "coffee", "sunshine"]
        )
        assert result["saved"] is True
        assert result["count"] == 3

        entry = GratitudeEntry.objects.get(user=user, date=date.today())
        assert entry.items == ["good sleep", "coffee", "sunshine"]

    def test_save_gratitude_updates_checkin(self, user):
        from apps.agent.tools import save_gratitude_list

        save_gratitude_list(user=user, items=["peace"])
        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.gratitude_completed is True

    def test_save_gratitude_replaces_existing(self, user):
        """If gratitude already exists for today, update it."""
        from apps.agent.tools import save_gratitude_list

        GratitudeEntry.objects.create(
            user=user, date=date.today(), items=["old"]
        )
        save_gratitude_list(user=user, items=["new", "items"])
        entry = GratitudeEntry.objects.get(user=user, date=date.today())
        assert entry.items == ["new", "items"]


class TestSaveJournalEntry:
    """Tests for the save_journal_entry tool."""

    def test_save_journal_entry(self, user):
        from apps.agent.tools import save_journal_entry

        result = save_journal_entry(
            user=user,
            content="Today I practiced being present with my anxiety.",
        )
        assert result["saved"] is True

        entry = JournalEntry.objects.get(user=user, date=date.today())
        assert "being present" in entry.content

    def test_save_journal_updates_checkin(self, user):
        from apps.agent.tools import save_journal_entry

        save_journal_entry(user=user, content="Test entry")
        checkin = DailyCheckin.objects.get(user=user, date=date.today())
        assert checkin.journal_completed is True

    def test_save_journal_appends_to_existing(self, user):
        """If journal already exists for today, append content."""
        from apps.agent.tools import save_journal_entry

        JournalEntry.objects.create(
            user=user, date=date.today(), content="Morning thoughts."
        )
        save_journal_entry(user=user, content="Evening reflection.")
        entry = JournalEntry.objects.get(user=user, date=date.today())
        assert "Morning thoughts." in entry.content
        assert "Evening reflection." in entry.content


class TestCreateTodo:
    """Tests for the create_todo tool."""

    def test_create_todo(self, user):
        from apps.agent.tools import create_todo

        result = create_todo(user=user, task="Call the doctor")
        assert result["created"] is True
        assert result["task"] == "Call the doctor"
        assert Todo.objects.filter(user=user, task="Call the doctor").exists()

    def test_create_todo_with_due_date(self, user):
        from apps.agent.tools import create_todo

        result = create_todo(
            user=user, task="Buy groceries", due_date="2026-02-05"
        )
        todo = Todo.objects.get(user=user, task="Buy groceries")
        assert todo.due_date == date(2026, 2, 5)

    def test_create_todo_with_relative_date_tomorrow(self, user):
        from apps.agent.tools import create_todo

        result = create_todo(user=user, task="Do thing", due_date="tomorrow")
        todo = Todo.objects.get(user=user, task="Do thing")
        assert todo.due_date == date.today() + timedelta(days=1)

    def test_create_todo_with_relative_date_today(self, user):
        from apps.agent.tools import create_todo

        result = create_todo(user=user, task="Do thing", due_date="today")
        todo = Todo.objects.get(user=user, task="Do thing")
        assert todo.due_date == date.today()


class TestCompleteTodo:
    """Tests for the complete_todo tool."""

    def test_complete_todo_exact_match(self, user):
        from apps.agent.tools import complete_todo

        Todo.objects.create(user=user, task="Call the doctor")
        result = complete_todo(user=user, search="Call the doctor")
        assert result["completed"] is True

        todo = Todo.objects.get(user=user, task="Call the doctor")
        assert todo.completed is True

    def test_complete_todo_partial_match(self, user):
        """Fuzzy matching: 'call doctor' matches 'Call the doctor tomorrow'."""
        from apps.agent.tools import complete_todo

        Todo.objects.create(user=user, task="Call the doctor tomorrow")
        result = complete_todo(user=user, search="call doctor")
        assert result["completed"] is True

    def test_complete_todo_no_match(self, user):
        from apps.agent.tools import complete_todo

        result = complete_todo(user=user, search="nonexistent task")
        assert result["completed"] is False
        assert "not found" in result["message"].lower()

    def test_complete_todo_ambiguous(self, user):
        """Multiple matches returns options instead of guessing."""
        from apps.agent.tools import complete_todo

        Todo.objects.create(user=user, task="Call the doctor")
        Todo.objects.create(user=user, task="Call mom")
        result = complete_todo(user=user, search="call")
        assert "matches" in result
        assert len(result["matches"]) == 2

    def test_complete_todo_scoped_to_user(self, user, other_user):
        """Can't complete another user's todo."""
        from apps.agent.tools import complete_todo

        Todo.objects.create(user=other_user, task="Secret task")
        result = complete_todo(user=user, search="Secret task")
        assert result["completed"] is False


class TestGetTodos:
    """Tests for the get_todos tool."""

    def test_get_todos(self, user):
        from apps.agent.tools import get_todos

        Todo.objects.create(user=user, task="Task 1")
        Todo.objects.create(user=user, task="Task 2")
        result = get_todos(user=user)
        assert len(result["todos"]) == 2

    def test_get_todos_excludes_completed_by_default(self, user):
        from apps.agent.tools import get_todos

        Todo.objects.create(user=user, task="Active")
        done = Todo.objects.create(user=user, task="Done")
        done.completed = True
        done.save()

        result = get_todos(user=user)
        assert len(result["todos"]) == 1
        assert result["todos"][0]["task"] == "Active"

    def test_get_todos_include_completed(self, user):
        from apps.agent.tools import get_todos

        Todo.objects.create(user=user, task="Active")
        done = Todo.objects.create(user=user, task="Done")
        done.completed = True
        done.save()

        result = get_todos(user=user, include_completed=True)
        assert len(result["todos"]) == 2

    def test_get_todos_scoped_to_user(self, user, other_user):
        from apps.agent.tools import get_todos

        Todo.objects.create(user=user, task="Mine")
        Todo.objects.create(user=other_user, task="Theirs")
        result = get_todos(user=user)
        assert len(result["todos"]) == 1


class TestGetRecentEntries:
    """Tests for the get_recent_entries tool."""

    def test_get_recent_entries(self, user):
        from apps.agent.tools import get_recent_entries

        JournalEntry.objects.create(
            user=user, content="Recent", date=date.today()
        )
        JournalEntry.objects.create(
            user=user, content="Old", date=date.today() - timedelta(days=30)
        )
        result = get_recent_entries(user=user, days=7)
        assert len(result["entries"]) == 1
        assert result["entries"][0]["content"] == "Recent"

    def test_get_recent_entries_scoped(self, user, other_user):
        from apps.agent.tools import get_recent_entries

        JournalEntry.objects.create(
            user=other_user, content="Not mine", date=date.today()
        )
        result = get_recent_entries(user=user, days=7)
        assert len(result["entries"]) == 0


class TestGetMantras:
    """Tests for the get_mantras tool."""

    def test_get_mantras(self, user):
        from apps.agent.tools import get_mantras

        Mantra.objects.create(user=user, content="Be like water", order=1)
        Mantra.objects.create(user=user, content="Let it settle", order=2)
        result = get_mantras(user=user)
        assert len(result["mantras"]) == 2
        assert result["mantras"][0]["content"] == "Be like water"

    def test_get_mantras_scoped(self, user, other_user):
        from apps.agent.tools import get_mantras

        Mantra.objects.create(user=other_user, content="Secret")
        result = get_mantras(user=user)
        assert len(result["mantras"]) == 0


class TestAddMantra:
    """Tests for the add_mantra tool."""

    def test_add_mantra(self, user):
        from apps.agent.tools import add_mantra

        result = add_mantra(user=user, content="Be like water")
        assert result["added"] is True
        assert Mantra.objects.filter(user=user, content="Be like water").exists()


class TestGetTodaysStatus:
    """Tests for the get_todays_status tool."""

    def test_get_status_empty_day(self, user):
        from apps.agent.tools import get_todays_status

        result = get_todays_status(user=user)
        assert result["meditation"] is False
        assert result["gratitude"] is False
        assert result["journal"] is False

    def test_get_status_partial_day(self, user):
        from apps.agent.tools import get_todays_status, log_meditation

        log_meditation(user=user, duration_minutes=15)
        result = get_todays_status(user=user)
        assert result["meditation"] is True
        assert result["gratitude"] is False
        assert result["journal"] is False

    def test_get_status_scoped(self, user, other_user):
        """Other user's completions don't show in my status."""
        from apps.agent.tools import get_todays_status, log_meditation

        log_meditation(user=other_user, duration_minutes=20)
        result = get_todays_status(user=user)
        assert result["meditation"] is False
