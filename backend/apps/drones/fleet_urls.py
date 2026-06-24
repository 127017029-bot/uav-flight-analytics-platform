from django.urls import path
from .views import FleetOverviewView, FleetStatusView

urlpatterns = [
    path('overview/', FleetOverviewView.as_view(), name='fleet-overview'),
    path('status/', FleetStatusView.as_view(), name='fleet-status'),
]
