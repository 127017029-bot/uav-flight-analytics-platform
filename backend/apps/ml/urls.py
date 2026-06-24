from django.urls import path
from .views import (
    MLModelListView, PredictionHistoryView,
    BatteryRULPredictView, MotorAnomalyPredictView,
    FlightAnomalyPredictView, MissionRiskPredictView,
    MaintenancePredictView,
)

app_name = 'ml'

urlpatterns = [
    path('models/', MLModelListView.as_view(), name='ml-models'),
    path('predictions/', PredictionHistoryView.as_view(), name='ml-predictions'),
    path('predict/battery-rul/', BatteryRULPredictView.as_view(), name='predict-battery-rul'),
    path('predict/motor-anomaly/', MotorAnomalyPredictView.as_view(), name='predict-motor-anomaly'),
    path('predict/flight-anomaly/', FlightAnomalyPredictView.as_view(), name='predict-flight-anomaly'),
    path('predict/mission-risk/', MissionRiskPredictView.as_view(), name='predict-mission-risk'),
    path('predict/maintenance/', MaintenancePredictView.as_view(), name='predict-maintenance'),
]
