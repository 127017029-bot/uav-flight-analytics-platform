"""
Accounts views for the UAV Digital Twin Platform.

Provides endpoints for user registration, profile management,
and pilot CRUD operations.
"""
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Pilot
from .serializers import (
    PilotSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(CreateAPIView):
    """
    User registration endpoint.

    POST /api/accounts/register/
    Creates a new user account with hashed password.
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Create user and return profile data (excluding password)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(RetrieveUpdateAPIView):
    """
    Authenticated user profile endpoint.

    GET  /api/accounts/profile/ — retrieve current user's profile
    PUT  /api/accounts/profile/ — update current user's profile
    PATCH /api/accounts/profile/ — partial update
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user


class PilotViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Pilot profiles.

    Supports list, create, retrieve, update, and delete.
    Filterable by certification_level and is_active_pilot.
    """

    queryset = Pilot.objects.select_related('user').all()
    serializer_class = PilotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Apply optional filters for certification level and active status."""
        qs = super().get_queryset()
        certification = self.request.query_params.get('certification_level')
        if certification:
            qs = qs.filter(certification_level=certification)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active_pilot=is_active.lower() == 'true')
        return qs
