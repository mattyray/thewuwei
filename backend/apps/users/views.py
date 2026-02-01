from rest_framework import generics, permissions

from .models import User
from .serializers import UserSerializer


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH the current authenticated user's profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user
