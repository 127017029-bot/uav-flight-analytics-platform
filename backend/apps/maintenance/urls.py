from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaintenanceRecordViewSet

app_name = 'maintenance'

router = DefaultRouter()
router.register(r'', MaintenanceRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
