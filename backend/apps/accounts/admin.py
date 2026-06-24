"""
Accounts admin configuration.

Registers User and Pilot models with appropriate display fields,
filters, and search capabilities.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Pilot, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'organization', 'is_active', 'date_joined',
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'organization']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'organization']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('UAV Platform', {
            'fields': ('role', 'organization', 'phone', 'avatar'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('UAV Platform', {
            'fields': ('role', 'organization', 'phone'),
        }),
    )


@admin.register(Pilot)
class PilotAdmin(admin.ModelAdmin):
    """Admin configuration for the Pilot model."""

    list_display = [
        'user', 'license_number', 'certification_level',
        'total_flight_hours', 'rating', 'is_active_pilot', 'created_at',
    ]
    list_filter = ['certification_level', 'is_active_pilot']
    search_fields = [
        'user__username', 'user__email', 'license_number',
    ]
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
