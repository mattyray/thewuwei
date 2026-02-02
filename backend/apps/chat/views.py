from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ChatMessage
from .serializers import ChatMessageSerializer


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<msg_date>\d{4}-\d{2}-\d{2})",
    )
    def by_date(self, request, msg_date=None):
        """Get all chat messages for a specific date."""
        messages = ChatMessage.objects.filter(
            user=request.user,
            created_at__date=msg_date,
        )
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
