# back-end/users/views.py

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer

class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    GET /api/users/me/ and PUT /api/users/me/
    """
    queryset = User.objects.all()      # needed for schema generation
    serializer_class   = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
