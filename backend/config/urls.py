from django.contrib import admin
from django.urls import include, path

from apps.journal.views import DailySummaryView, RecentDailySummariesView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.journal.urls")),
    path("api/", include("apps.todos.urls")),
    path("api/", include("apps.mantras.urls")),
    path("api/", include("apps.chat.urls")),
    path("api/daily/recent/", RecentDailySummariesView.as_view(), name="daily-recent"),
    path("api/daily/<str:summary_date>/", DailySummaryView.as_view(), name="daily-summary"),
    # allauth (required for OAuth callbacks even in headless mode)
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
]
