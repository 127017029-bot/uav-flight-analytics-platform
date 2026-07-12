from django.urls import path
from .views import FleetOverviewView, FleetStatusView

urlpatterns = [
    path('overview/', FleetOverviewView.as_view(), name='fleet-overview'),
    path('overview', FleetOverviewView.as_view(), name='fleet-overview-no-slash'),
    path('status/', FleetStatusView.as_view(), name='fleet-status'),
    path('status', FleetStatusView.as_view(), name='fleet-status-no-slash'),
]
