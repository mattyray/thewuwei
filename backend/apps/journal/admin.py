from django.contrib import admin

from .models import DailyCheckin, GratitudeEntry, JournalEntry, WeeklySummary

admin.site.register(JournalEntry)
admin.site.register(DailyCheckin)
admin.site.register(GratitudeEntry)
admin.site.register(WeeklySummary)
