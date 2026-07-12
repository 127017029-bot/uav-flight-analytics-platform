from django.urls import path
from .views import FleetDailyStatsView, FleetTrendsView, FlightComparisonView

app_name = 'analytics'

urlpatterns = [
    path('daily-stats/', FleetDailyStatsView.as_view(), name='fleet-daily-stats'),
    path('daily-stats', FleetDailyStatsView.as_view(), name='fleet-daily-stats-no-slash'),
    path('fleet-daily/', FleetDailyStatsView.as_view(), name='fleet-daily-stats-compat'),
    path('fleet-daily', FleetDailyStatsView.as_view(), name='fleet-daily-stats-compat-no-slash'),
    
    path('trends/', FleetTrendsView.as_view(), name='fleet-trends'),
    path('trends', FleetTrendsView.as_view(), name='fleet-trends-no-slash'),
    path('fleet-trends/', FleetTrendsView.as_view(), name='fleet-trends-compat'),
    path('fleet-trends', FleetTrendsView.as_view(), name='fleet-trends-compat-no-slash'),
    
    path('compare-flights/', FlightComparisonView.as_view(), name='flight-comparison'),
    path('compare-flights', FlightComparisonView.as_view(), name='flight-comparison-no-slash'),
    path('comparison/', FlightComparisonView.as_view(), name='flight-comparison-compat'),
    path('comparison', FlightComparisonView.as_view(), name='flight-comparison-compat-no-slash'),
]
