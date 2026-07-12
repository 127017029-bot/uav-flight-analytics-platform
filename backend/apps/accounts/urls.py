"""
Accounts URL configuration.

Routes for user registration, profile, JWT token management, and pilot CRUD.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

app_name = 'accounts'

router = DefaultRouter()
router.register(r'pilots', views.PilotViewSet, basename='pilot')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('register', views.RegisterView.as_view(), name='register-no-slash'),
    
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile', views.UserProfileView.as_view(), name='profile-no-slash'),
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend client compatibility URL mapping
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login', TokenObtainPairView.as_view(), name='login-no-slash'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('refresh', TokenRefreshView.as_view(), name='refresh-no-slash'),
    
    path('', include(router.urls)),
]
