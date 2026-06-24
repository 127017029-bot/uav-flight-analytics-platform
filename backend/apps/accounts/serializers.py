"""
Accounts serializers for the UAV Digital Twin Platform.

Provides serialization for User registration, profile management,
and Pilot CRUD operations with proper password hashing.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Pilot

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    Used for profile retrieval and updates. Excludes sensitive
    fields like password.
    """

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'organization', 'phone', 'avatar',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_full_name(self, obj) -> str:
        """Return the user's full name or username as fallback."""
        return obj.get_full_name() or obj.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Accepts password and password_confirm fields, validates they match,
    and hashes the password before saving.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Minimum 8 characters.',
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text='Must match the password field.',
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'organization', 'phone',
        ]
        read_only_fields = ['id']

    def validate(self, attrs: dict) -> dict:
        """Ensure password and password_confirm match."""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {'password_confirm': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        """Create user with hashed password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PilotSerializer(serializers.ModelSerializer):
    """
    Serializer for the Pilot model.

    Includes nested read-only user information for display purposes.
    """

    user_detail = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        help_text='ID of the user account to link this pilot profile to.',
    )

    class Meta:
        model = Pilot
        fields = [
            'id', 'user', 'user_detail', 'license_number',
            'certification_level', 'total_flight_hours', 'rating',
            'is_active_pilot', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
