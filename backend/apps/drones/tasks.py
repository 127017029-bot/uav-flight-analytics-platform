from celery import shared_task
from .models import Drone
from django.utils import timezone
from datetime import timedelta

@shared_task
def check_drone_heartbeats():
    """Verify that active drones have sent telemetry recently, marking them offline if stale."""
    print("[Celery Drones] Checking active drone heartbeats...")
    # Stub: updates drone status based on telemetry freshness
    return "Heartbeat check complete."
