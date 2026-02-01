from datetime import date

from django.utils import timezone
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
        return GratitudeEntry.objects.filter(user=self.request.user)

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
