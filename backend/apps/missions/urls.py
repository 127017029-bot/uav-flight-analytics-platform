from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MissionViewSet, WaypointViewSet

app_name = 'missions'

router = DefaultRouter()
router.register(r'', MissionViewSet)

urlpatterns = [
    path('<int:mission_pk>/waypoints/', WaypointViewSet.as_view({
        'get': 'list', 'post': 'create',
    }), name='mission-waypoints-list'),
    path('<int:mission_pk>/waypoints/<int:pk>/', WaypointViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy',
    }), name='mission-waypoints-detail'),
    path('', include(router.urls)),
]
