from rest_framework import viewsets, permissions
from .models import MaintenanceRecord
from .serializers import MaintenanceRecordSerializer


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """CRUD operations for maintenance work orders.

    Supports filtering by status, type, priority, drone, and component.
    """
    queryset = MaintenanceRecord.objects.select_related('drone', 'created_by').all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['status', 'maintenance_type', 'priority', 'drone', 'component']
    search_fields = ['title', 'description', 'technician_notes']
    ordering_fields = ['created_at', 'scheduled_date', 'priority']
