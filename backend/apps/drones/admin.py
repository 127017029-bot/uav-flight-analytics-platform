from django.contrib import admin
from .models import Drone, ComponentHealth, BatteryProfile


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ['name', 'serial_number', 'model', 'manufacturer', 'drone_type', 'status', 'total_flight_hours']
    list_filter = ['status', 'drone_type', 'manufacturer']
    search_fields = ['name', 'serial_number', 'model']


@admin.register(ComponentHealth)
class ComponentHealthAdmin(admin.ModelAdmin):
    list_display = ['drone', 'component_type', 'health_score', 'status', 'cycles_count']
    list_filter = ['component_type', 'status']


@admin.register(BatteryProfile)
class BatteryProfileAdmin(admin.ModelAdmin):
    list_display = ['drone', 'chemistry', 'state_of_health', 'cycle_count', 'estimated_rul_cycles']
    list_filter = ['chemistry']
