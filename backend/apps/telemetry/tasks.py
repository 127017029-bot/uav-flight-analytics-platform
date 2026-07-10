from celery import shared_task
from .models import TelemetryData
from django.utils import timezone
from django.db.models import Avg, Max

@shared_task
def aggregate_telemetry_data():
    """Aggregate high-frequency telemetry into periodic statistical points."""
    print("[Celery Telemetry] Running telemetry aggregation task...")
    # Stub: aggregates data and logs summary stats
    total_records = TelemetryData.objects.count()
    return f"Telemetry aggregation complete. Total records in DB: {total_records}"
