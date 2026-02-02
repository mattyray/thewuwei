from datetime import date, timedelta

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chat.models import ChatMessage
from apps.chat.serializers import ChatMessageSerializer
from apps.todos.models import Todo
from apps.todos.serializers import TodoSerializer

from .models import DailyCheckin, GratitudeEntry, JournalEntry
from .serializers import (
    DailyCheckinSerializer,
    GratitudeEntrySerializer,
    JournalEntrySerializer,
)


class JournalViewSet(viewsets.ModelViewSet):
    serializer_class = JournalEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        try:
            entry = JournalEntry.objects.get(
                user=request.user, date=date.today()
            )
        except JournalEntry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(entry)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path=r"(?P<entry_date>\d{4}-\d{2}-\d{2})")
    def by_date(self, request, entry_date=None):
        try:
            entry = JournalEntry.objects.get(
                user=request.user, date=entry_date
            )
        except JournalEntry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(entry)
        return Response(serializer.data)


class CheckinViewSet(viewsets.GenericViewSet):
    serializer_class = DailyCheckinSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyCheckin.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        checkin, _ = DailyCheckin.objects.get_or_create(
            user=request.user, date=date.today()
        )
        serializer = self.get_serializer(checkin)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="meditation")
    def meditation(self, request):
        checkin, _ = DailyCheckin.objects.get_or_create(
            user=request.user, date=date.today()
        )
        checkin.meditation_completed = True
        duration = request.data.get("duration_minutes")
        if duration is not None:
            checkin.meditation_duration = int(duration)
        checkin.meditation_completed_at = timezone.now()
        checkin.save()
        serializer = self.get_serializer(checkin)
        return Response(serializer.data)


class GratitudeViewSet(viewsets.ModelViewSet):
    serializer_class = GratitudeEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = GratitudeEntry.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get("date")
        if date_param:
            qs = qs.filter(date=date_param)
        return qs

    @action(detail=False, methods=["get"], url_path="today")
    def today(self, request):
        try:
            entry = GratitudeEntry.objects.get(
                user=request.user, date=date.today()
            )
        except GratitudeEntry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(entry)
        return Response(serializer.data)


def _build_daily_summary(user, d, include_chat=True):
    """Build a summary dict for a single date."""
    checkin = DailyCheckin.objects.filter(user=user, date=d).first()
    journal = JournalEntry.objects.filter(user=user, date=d).first()
    gratitude = GratitudeEntry.objects.filter(user=user, date=d).first()
    todos = Todo.objects.filter(user=user, created_at__date=d)

    summary = {
        "date": str(d),
        "checkin": DailyCheckinSerializer(checkin).data if checkin else None,
        "journal": JournalEntrySerializer(journal).data if journal else None,
        "gratitude": GratitudeEntrySerializer(gratitude).data if gratitude else None,
        "todos": TodoSerializer(todos, many=True).data,
    }

    if include_chat:
        messages = ChatMessage.objects.filter(user=user, created_at__date=d)
        summary["chat_messages"] = ChatMessageSerializer(messages, many=True).data
    else:
        summary["chat_messages"] = []

    return summary


class DailySummaryView(APIView):
    """Aggregate all data for a single date."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, summary_date):
        if summary_date == "today":
            d = date.today()
        else:
            try:
                d = date.fromisoformat(summary_date)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(_build_daily_summary(request.user, d))


class RecentDailySummariesView(APIView):
    """Return daily summaries for the last N days (chat excluded for performance)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        days = int(request.query_params.get("days", 5))
        days = min(days, 30)  # Cap at 30
        user = request.user
        today_ = date.today()

        summaries = []
        for i in range(1, days + 1):
            d = today_ - timedelta(days=i)
            summary = _build_daily_summary(user, d, include_chat=False)
            # Only include days that have some activity
            has_activity = (
                summary["checkin"] is not None
                or summary["journal"] is not None
                or summary["gratitude"] is not None
                or len(summary["todos"]) > 0
            )
            if has_activity:
                summaries.append(summary)

        return Response(summaries)
