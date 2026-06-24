"""
Celery application factory for the UAV Digital Twin Platform.

This module configures the Celery distributed task queue, wires it to Django
settings, and defines the periodic beat schedule for recurring maintenance
and analytics jobs.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("uav_analytics")

# Read config from Django settings; the CELERY_ namespace means all
# celery-related config keys must be prefixed with CELERY_.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in every installed app.
app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Celery Beat – Periodic Task Schedule
# ---------------------------------------------------------------------------
app.conf.beat_schedule = {
    # Run predictive maintenance analysis every hour
    "predictive-maintenance-hourly": {
        "task": "apps.maintenance.tasks.run_predictive_maintenance",
        "schedule": crontab(minute=0),
        "options": {"queue": "maintenance"},
    },
    # Aggregate telemetry data every 15 minutes
    "telemetry-aggregation": {
        "task": "apps.telemetry.tasks.aggregate_telemetry_data",
        "schedule": crontab(minute="*/15"),
        "options": {"queue": "analytics"},
    },
    # Check for stale drone connections every 5 minutes
    "drone-heartbeat-check": {
        "task": "apps.drones.tasks.check_drone_heartbeats",
        "schedule": crontab(minute="*/5"),
        "options": {"queue": "default"},
    },
    # Generate daily fleet analytics report at 02:00 UTC
    "daily-fleet-report": {
        "task": "apps.analytics.tasks.generate_daily_fleet_report",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "analytics"},
    },
    # Retrain ML models weekly on Sunday at 03:00 UTC
    "weekly-model-retrain": {
        "task": "apps.ml.tasks.retrain_models",
        "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),
        "options": {"queue": "ml"},
    },
}

app.conf.task_routes = {
    "apps.ml.tasks.*": {"queue": "ml"},
    "apps.maintenance.tasks.*": {"queue": "maintenance"},
    "apps.analytics.tasks.*": {"queue": "analytics"},
    "apps.telemetry.tasks.*": {"queue": "analytics"},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Diagnostic task that prints its own request info."""
    print(f"Request: {self.request!r}")
