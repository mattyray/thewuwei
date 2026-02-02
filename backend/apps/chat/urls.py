from rest_framework.routers import DefaultRouter

from .views import ChatMessageViewSet

router = DefaultRouter()
router.register("chat-messages", ChatMessageViewSet, basename="chat-messages")

urlpatterns = router.urls
