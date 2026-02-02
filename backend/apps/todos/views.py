from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Todo.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get("date")
        if date_param:
            qs = qs.filter(created_at__date=date_param)
        return qs

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        todo = self.get_object()
        todo.completed = True
        todo.completed_at = timezone.now()
        todo.save()
        serializer = self.get_serializer(todo)
        return Response(serializer.data)
