from django.contrib import admin
from .models import Mission, Waypoint


class WaypointInline(admin.TabularInline):
    """Inline admin for managing waypoints within a mission."""
    model = Waypoint
    extra = 1
    ordering = ['sequence_order']


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    """Admin configuration for Mission records."""
    list_display = [
        'name', 'mission_type', 'priority', 'status',
        'assigned_drone', 'planned_start', 'created_at',
    ]
    list_filter = ['status', 'mission_type', 'priority']
    search_fields = ['name', 'description']
    inlines = [WaypointInline]


@admin.register(Waypoint)
class WaypointAdmin(admin.ModelAdmin):
    """Admin configuration for Waypoint records."""
    list_display = [
        'mission', 'sequence_order', 'latitude', 'longitude',
        'altitude_m', 'action_type',
    ]
    list_filter = ['action_type']
