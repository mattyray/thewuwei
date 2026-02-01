from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Mantra
from .serializers import MantraSerializer, ReorderSerializer


class MantraViewSet(viewsets.ModelViewSet):
    serializer_class = MantraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Mantra.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        serializer = ReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["order"]
        mantras = Mantra.objects.filter(user=request.user, pk__in=ids)

        # Build a map of pk -> mantra
        mantra_map = {m.pk: m for m in mantras}

        for index, pk in enumerate(ids):
            if pk in mantra_map:
                mantra_map[pk].order = index
                mantra_map[pk].save(update_fields=["order"])

        return Response({"status": "reordered"})
