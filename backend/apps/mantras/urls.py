from rest_framework.routers import DefaultRouter

from .views import MantraViewSet

router = DefaultRouter()
router.register("mantras", MantraViewSet, basename="mantras")

urlpatterns = router.urls
