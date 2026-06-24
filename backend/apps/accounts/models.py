"""
Accounts models for the UAV Digital Twin Platform.

Defines the custom User model (extending AbstractUser) and the Pilot profile
model linked via a OneToOneField. Supports role-based access (admin,
fleet_manager, pilot, analyst) and pilot certification tracking.
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Adds role-based access control, organization affiliation, and
    optional profile picture for the UAV platform.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        FLEET_MANAGER = 'fleet_manager', 'Fleet Manager'
        PILOT = 'pilot', 'Pilot'
        ANALYST = 'analyst', 'Analyst'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ANALYST,
        help_text='User role determining platform permissions.',
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Organization or company the user belongs to.',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Contact phone number.',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Profile picture.',
    )

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_fleet_manager(self) -> bool:
        """Check if user has fleet manager role."""
        return self.role == self.Role.FLEET_MANAGER

    @property
    def is_pilot_role(self) -> bool:
        """Check if user has pilot role."""
        return self.role == self.Role.PILOT

    @property
    def is_analyst(self) -> bool:
        """Check if user has analyst role."""
        return self.role == self.Role.ANALYST


class Pilot(models.Model):
    """
    Pilot profile linked to a User account.

    Tracks certification level, flight hours, and operational status.
    A user with role='pilot' should have a corresponding Pilot record.
    """

    class CertificationLevel(models.TextChoices):
        BASIC = 'basic', 'Basic'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pilot_profile',
        help_text='The user account linked to this pilot profile.',
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Official pilot license or certification number.',
    )
    certification_level = models.CharField(
        max_length=20,
        choices=CertificationLevel.choices,
        default=CertificationLevel.BASIC,
        help_text='Current certification level.',
    )
    total_flight_hours = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Cumulative flight hours logged.',
    )
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Performance rating (0-5 scale).',
    )
    is_active_pilot = models.BooleanField(
        default=True,
        help_text='Whether this pilot is currently available for missions.',
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about the pilot.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pilot'
        verbose_name_plural = 'Pilots'

    def __str__(self) -> str:
        return (
            f"Pilot {self.user.get_full_name() or self.user.username} "
            f"({self.license_number})"
        )
