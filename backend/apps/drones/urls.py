from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DroneViewSet, DroneHealthView, DroneBatteryView

app_name = 'drones'

router = DefaultRouter()
router.register(r'', DroneViewSet)

urlpatterns = [
    path('<int:pk>/health/', DroneHealthView.as_view(), name='drone-health'),
    path('<int:drone_id>/battery/', DroneBatteryView.as_view(), name='drone-battery'),
    path('', include(router.urls)),
]
