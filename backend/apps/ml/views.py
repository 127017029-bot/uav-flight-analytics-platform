import random
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MLModel, MLPrediction
from .serializers import MLModelSerializer, MLPredictionSerializer


class MLModelListView(generics.ListAPIView):
    """List all registered ML models."""
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['model_type', 'is_active']


class PredictionHistoryView(generics.ListAPIView):
    """List prediction history, optionally filtered by drone or type.

    Query params:
    - ``drone_id``: filter by drone
    - ``prediction_type``: filter by prediction type
    """
    serializer_class = MLPredictionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = MLPrediction.objects.select_related('drone', 'model').all()
        drone_id = self.request.query_params.get('drone_id')
        pred_type = self.request.query_params.get('prediction_type')
        if drone_id:
            qs = qs.filter(drone_id=drone_id)
        if pred_type:
            qs = qs.filter(prediction_type=pred_type)
        return qs


# ---------------------------------------------------------------------------
# Placeholder prediction endpoints returning mock data for dev / demo
# ---------------------------------------------------------------------------

class BatteryRULPredictView(APIView):
    """Predict battery remaining useful life for a drone.

    Returns mock prediction data during development.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=400)
        rul_cycles = random.randint(50, 500)
        confidence = round(random.uniform(0.75, 0.98), 3)
        return Response({
            'drone_id': drone_id,
            'prediction_type': 'battery_rul',
            'predicted_rul_cycles': rul_cycles,
            'predicted_rul_hours': round(rul_cycles * 0.5, 1),
            'confidence': confidence,
            'model': 'battery_rul_v1_mock',
            'explanation': {
                'top_features': ['cycle_count', 'state_of_health', 'avg_temperature'],
                'note': 'Mock prediction — replace with real model inference.',
            },
        })


class MotorAnomalyPredictView(APIView):
    """Detect motor anomalies for a drone.

    Returns mock anomaly detection data during development.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=400)
        motors = {}
        for i in range(1, 5):
            is_anomaly = random.random() < 0.15
            motors[f'motor_{i}'] = {
                'is_anomaly': is_anomaly,
                'anomaly_score': round(random.uniform(0.6, 0.99), 3) if is_anomaly else round(random.uniform(0.01, 0.3), 3),
                'predicted_issue': 'bearing_wear' if is_anomaly else 'none',
            }
        return Response({
            'drone_id': drone_id,
            'prediction_type': 'motor_anomaly',
            'motors': motors,
            'confidence': round(random.uniform(0.80, 0.97), 3),
            'model': 'motor_anomaly_v1_mock',
        })


class FlightAnomalyPredictView(APIView):
    """Detect anomalies in flight telemetry data.

    Returns mock flight anomaly data during development.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        flight_id = request.data.get('flight_id')
        if not flight_id:
            return Response({'error': 'flight_id is required.'}, status=400)
        anomaly_count = random.randint(0, 5)
        return Response({
            'flight_id': flight_id,
            'prediction_type': 'flight_anomaly',
            'total_anomalies': anomaly_count,
            'risk_score': round(random.uniform(0, 1), 3),
            'anomalies': [
                {
                    'timestamp_offset_s': random.randint(10, 600),
                    'type': random.choice(['vibration_spike', 'altitude_deviation', 'speed_anomaly']),
                    'severity': random.choice(['low', 'medium', 'high']),
                    'score': round(random.uniform(0.5, 0.99), 3),
                }
                for _ in range(anomaly_count)
            ],
            'confidence': round(random.uniform(0.80, 0.97), 3),
            'model': 'flight_anomaly_v1_mock',
        })


class MissionRiskPredictView(APIView):
    """Assess risk for a planned mission.

    Returns mock risk assessment data during development.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mission_id = request.data.get('mission_id')
        if not mission_id:
            return Response({'error': 'mission_id is required.'}, status=400)
        risk_score = round(random.uniform(0, 1), 3)
        return Response({
            'mission_id': mission_id,
            'prediction_type': 'mission_risk',
            'risk_score': risk_score,
            'risk_level': 'high' if risk_score > 0.7 else ('medium' if risk_score > 0.4 else 'low'),
            'risk_factors': {
                'weather': round(random.uniform(0, 1), 2),
                'battery': round(random.uniform(0, 1), 2),
                'distance': round(random.uniform(0, 1), 2),
                'drone_health': round(random.uniform(0, 1), 2),
            },
            'confidence': round(random.uniform(0.75, 0.95), 3),
            'model': 'mission_risk_v1_mock',
        })


class MaintenancePredictView(APIView):
    """Predict maintenance needs for a drone.

    Returns mock predictive maintenance data during development.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=400)
        components = ['motor_1', 'motor_2', 'motor_3', 'motor_4', 'battery', 'esc', 'gps']
        predictions = []
        for comp in components:
            needs_maintenance = random.random() < 0.25
            predictions.append({
                'component': comp,
                'needs_maintenance': needs_maintenance,
                'predicted_failure_hours': random.randint(10, 200) if needs_maintenance else None,
                'confidence': round(random.uniform(0.70, 0.98), 3),
                'recommended_action': 'inspect_and_replace' if needs_maintenance else 'no_action',
            })
        return Response({
            'drone_id': drone_id,
            'prediction_type': 'predictive_maintenance',
            'components': predictions,
            'overall_health_score': round(random.uniform(60, 100), 1),
            'model': 'predictive_maintenance_v1_mock',
        })
