from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/",        include("apps.accounts.urls")),
    path("api/drones/",      include("apps.drones.urls")),
    path("api/flights/",     include("apps.flights.urls")),
    path("api/telemetry/",   include("apps.telemetry.urls")),
    path("api/missions/",    include("apps.missions.urls")),
    path("api/maintenance/", include("apps.maintenance.urls")),
    path("api/alerts/",      include("apps.alerts.urls")),
    path("api/analytics/",   include("apps.analytics.urls")),
    path("api/ml/",          include("apps.ml.urls")),
]
