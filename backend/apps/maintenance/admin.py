from django.contrib import admin
from .models import MaintenanceRecord


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    """Admin configuration for MaintenanceRecord."""
    list_display = [
        'title', 'drone', 'maintenance_type', 'component',
        'status', 'priority', 'scheduled_date', 'created_at',
    ]
    list_filter = ['status', 'maintenance_type', 'priority', 'component']
    search_fields = ['title', 'description', 'technician_notes']
    date_hierarchy = 'created_at'
