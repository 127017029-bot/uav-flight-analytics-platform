from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for Alert records."""
    list_display = [
        'title', 'drone', 'alert_type', 'severity',
        'ai_generated', 'acknowledged', 'resolved', 'created_at',
    ]
    list_filter = ['alert_type', 'severity', 'acknowledged', 'resolved', 'ai_generated']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
