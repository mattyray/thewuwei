from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.journal.urls")),
    path("api/", include("apps.todos.urls")),
    path("api/", include("apps.mantras.urls")),
]
