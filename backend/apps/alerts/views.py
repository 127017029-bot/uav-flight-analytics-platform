from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """CRUD operations and workflow actions for system alerts.

    Includes custom actions to acknowledge and resolve alerts.
    """
    queryset = Alert.objects.select_related('drone', 'flight', 'acknowledged_by').all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['alert_type', 'severity', 'drone', 'acknowledged', 'resolved', 'ai_generated']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'severity']

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Mark an alert as acknowledged."""
        alert = self.get_object()
        if alert.acknowledged:
            return Response(
                {'detail': 'Alert already acknowledged.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alert.acknowledged = True
        alert.acknowledged_at = timezone.now()
        # alert.acknowledged_by = request.user  # Uncomment when auth is enabled
        alert.save(update_fields=['acknowledged', 'acknowledged_at'])
        return Response(AlertSerializer(alert).data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved."""
        alert = self.get_object()
        if alert.resolved:
            return Response(
                {'detail': 'Alert already resolved.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alert.resolved = True
        alert.resolved_at = timezone.now()
        if not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_at = timezone.now()
        alert.save(update_fields=[
            'resolved', 'resolved_at', 'acknowledged', 'acknowledged_at',
        ])
        return Response(AlertSerializer(alert).data)
