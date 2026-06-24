from django.urls import path
from .views import FleetDailyStatsView, FleetTrendsView, FlightComparisonView

app_name = 'analytics'

urlpatterns = [
    path('daily-stats/', FleetDailyStatsView.as_view(), name='fleet-daily-stats'),
    path('trends/', FleetTrendsView.as_view(), name='fleet-trends'),
    path('compare-flights/', FlightComparisonView.as_view(), name='flight-comparison'),
]
