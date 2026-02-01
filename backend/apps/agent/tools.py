"""
Agent tools — pure business logic functions called by the LangGraph agent.

Each tool takes a user and arguments, performs database operations,
and returns a dict result. Tools are testable independently of the LLM.
"""

from datetime import date, timedelta
from typing import Optional

from django.db.models import Q
from django.utils import timezone

from apps.journal.models import DailyCheckin, GratitudeEntry, JournalEntry
from apps.mantras.models import Mantra
from apps.todos.models import Todo


def _get_or_create_checkin(user) -> DailyCheckin:
    """Get or create today's checkin for a user."""
    checkin, _ = DailyCheckin.objects.get_or_create(
        user=user, date=date.today()
    )
    return checkin


def log_meditation(
    user, duration_minutes: Optional[int] = None
) -> dict:
    """Log that the user completed their meditation."""
    checkin = _get_or_create_checkin(user)
    checkin.meditation_completed = True
    checkin.meditation_duration = duration_minutes
    checkin.meditation_completed_at = timezone.now()
    checkin.save()

    return {
        "logged": True,
        "duration": duration_minutes,
        "date": str(date.today()),
    }


def save_gratitude_list(user, items: list[str]) -> dict:
    """Save the user's gratitude list for today."""
    entry, created = GratitudeEntry.objects.update_or_create(
        user=user,
        date=date.today(),
        defaults={"items": items},
    )

    checkin = _get_or_create_checkin(user)
    checkin.gratitude_completed = True
    checkin.gratitude_completed_at = timezone.now()
    checkin.save()

    return {
        "saved": True,
        "count": len(items),
        "items": items,
    }


def save_journal_entry(user, content: str) -> dict:
    """Save a journal entry for today. Appends if one already exists."""
    try:
        entry = JournalEntry.objects.get(user=user, date=date.today())
        entry.content = f"{entry.content}\n\n{content}"
        entry.save()
    except JournalEntry.DoesNotExist:
        entry = JournalEntry.objects.create(
            user=user, date=date.today(), content=content
        )

    checkin = _get_or_create_checkin(user)
    checkin.journal_completed = True
    checkin.journal_completed_at = timezone.now()
    checkin.save()

    return {
        "saved": True,
        "date": str(date.today()),
        "content_length": len(entry.content),
    }


def _parse_due_date(due_date: Optional[str]) -> Optional[date]:
    """Parse a due date string into a date object."""
    if due_date is None:
        return None
    due_date_lower = due_date.strip().lower()
    if due_date_lower == "today":
        return date.today()
    if due_date_lower == "tomorrow":
        return date.today() + timedelta(days=1)
    return date.fromisoformat(due_date)


def create_todo(
    user, task: str, due_date: Optional[str] = None
) -> dict:
    """Create a new todo item."""
    parsed_date = _parse_due_date(due_date)
    todo = Todo.objects.create(
        user=user, task=task, due_date=parsed_date
    )
    return {
        "created": True,
        "task": todo.task,
        "due_date": str(todo.due_date) if todo.due_date else None,
    }


def complete_todo(user, search: str) -> dict:
    """Mark a todo as complete by searching for it."""
    search_lower = search.lower()
    todos = Todo.objects.filter(user=user, completed=False)

    # Try exact match first
    exact = todos.filter(task__iexact=search)
    if exact.count() == 1:
        todo = exact.first()
        todo.completed = True
        todo.completed_at = timezone.now()
        todo.save()
        return {"completed": True, "task": todo.task}

    # Try partial match — check if all search words appear in the task
    search_words = search_lower.split()
    matches = []
    for todo in todos:
        task_lower = todo.task.lower()
        if all(word in task_lower for word in search_words):
            matches.append(todo)

    if len(matches) == 1:
        todo = matches[0]
        todo.completed = True
        todo.completed_at = timezone.now()
        todo.save()
        return {"completed": True, "task": todo.task}

    if len(matches) > 1:
        return {
            "completed": False,
            "message": "Multiple matches found",
            "matches": [{"id": t.pk, "task": t.task} for t in matches],
        }

    return {
        "completed": False,
        "message": "Todo not found",
    }


def get_todos(user, include_completed: bool = False) -> dict:
    """Get the user's todo list."""
    qs = Todo.objects.filter(user=user)
    if not include_completed:
        qs = qs.filter(completed=False)

    todos = [
        {
            "id": t.pk,
            "task": t.task,
            "due_date": str(t.due_date) if t.due_date else None,
            "completed": t.completed,
        }
        for t in qs
    ]
    return {"todos": todos}


def get_recent_entries(user, days: int = 7) -> dict:
    """Get recent journal entries."""
    cutoff = date.today() - timedelta(days=days)
    entries = JournalEntry.objects.filter(
        user=user, date__gte=cutoff
    )
    return {
        "entries": [
            {
                "date": str(e.date),
                "content": e.content,
                "reflection": e.reflection,
            }
            for e in entries
        ]
    }


def get_mantras(user) -> dict:
    """Get the user's mantras."""
    mantras = Mantra.objects.filter(user=user)
    return {
        "mantras": [
            {"id": m.pk, "content": m.content}
            for m in mantras
        ]
    }


def add_mantra(user, content: str) -> dict:
    """Add a new mantra."""
    mantra = Mantra.objects.create(user=user, content=content)
    return {"added": True, "id": mantra.pk, "content": mantra.content}


def get_todays_status(user) -> dict:
    """Get today's check-in status."""
    checkin = _get_or_create_checkin(user)
    return {
        "date": str(date.today()),
        "meditation": checkin.meditation_completed,
        "meditation_duration": checkin.meditation_duration,
        "gratitude": checkin.gratitude_completed,
        "journal": checkin.journal_completed,
    }
