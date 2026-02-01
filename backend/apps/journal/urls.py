from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CheckinViewSet, GratitudeViewSet, JournalViewSet

router = DefaultRouter()
router.register("journal", JournalViewSet, basename="journal")
router.register("checkins", CheckinViewSet, basename="checkins")
router.register("gratitude", GratitudeViewSet, basename="gratitude")

urlpatterns = router.urls
