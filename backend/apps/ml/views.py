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

    Reads latest telemetry, runs model inference, and stores the prediction.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.telemetry.models import TelemetryData
        latest_telem = TelemetryData.objects.filter(flight__drone_id=drone_id).order_by('-timestamp').first()

        if not latest_telem:
            return Response({'error': 'No telemetry data found for this drone.'}, status=status.HTTP_404_NOT_FOUND)

        # Build features dict matching the trained GBR model schema
        voltage = latest_telem.battery_voltage or 15.0
        current = latest_telem.battery_current or 10.0
        temp = latest_telem.battery_temperature or 25.0
        battery_pct = latest_telem.battery_percentage or 100.0

        features = {
            'cycle': latest_telem.flight_id * 12,
            'capacity_measured': (battery_pct / 100.0) * 5000.0,
            'state_of_health': 98.0,
            'internal_resistance': 0.06,
            'voltage_max': max(16.8, voltage),
            'voltage_min': 12.8,
            'voltage_mean': voltage,
            'voltage_std': 0.15,
            'current_mean': current,
            'current_std': 1.2,
            'current_max': current + 2.0,
            'temperature_mean': temp,
            'temperature_max': temp + 3.0,
            'temperature_std': 0.8,
            'charge_duration_min': 45.0,
            'discharge_duration_min': 25.0,
            'energy_charged_wh': 80.0,
            'energy_discharged_wh': 72.0,
            'coulombic_efficiency': 90.0,
            'degradation_rate': 0.05,
            'capacity_measured_rolling_10': (battery_pct / 100.0) * 5000.0,
            'capacity_measured_rolling_diff': -1.2,
            'voltage_mean_rolling_10': voltage,
            'voltage_mean_rolling_diff': -0.01,
            'temperature_mean_rolling_10': temp,
            'temperature_mean_rolling_diff': 0.05
        }

        from .predictor import MLPredictor
        res = MLPredictor.predict_battery_rul(features)

        active_model = MLModel.objects.filter(model_type='battery_rul', is_active=True).first()
        pred = MLPrediction.objects.create(
            drone_id=drone_id,
            flight=latest_telem.flight,
            model=active_model,
            prediction_type='battery_rul',
            input_summary={
                'battery_voltage': voltage,
                'battery_current': current,
                'battery_percentage': battery_pct,
                'battery_temperature': temp
            },
            prediction_value=float(res.get('predicted_rul_cycles', 150)),
            prediction_label=f"{res.get('predicted_rul_cycles', 150)} cycles",
            confidence_score=float(res.get('confidence', 0.9)),
            explanation={
                'top_features': ['state_of_health', 'degradation_rate', 'cycle'],
                'cycle': features['cycle'],
                'state_of_health': features['state_of_health']
            }
        )

        return Response({
            'id': pred.id,
            'drone_id': drone_id,
            'prediction_type': 'battery_rul',
            'predicted_rul_cycles': res.get('predicted_rul_cycles'),
            'predicted_rul_hours': res.get('predicted_rul_hours'),
            'confidence': res.get('confidence'),
            'model': active_model.name if active_model else 'battery_rul_gbr_v1',
            'explanation': pred.explanation
        })


class MotorAnomalyPredictView(APIView):
    """Detect motor anomalies for a drone.

    Reads latest telemetry, runs model inference, and stores the prediction.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.telemetry.models import TelemetryData
        latest_telem = TelemetryData.objects.filter(flight__drone_id=drone_id).order_by('-timestamp').first()

        if not latest_telem:
            return Response({'error': 'No telemetry data found for this drone.'}, status=status.HTTP_404_NOT_FOUND)

        features = {
            'motor_rpm_1': latest_telem.motor_rpm_1 or 0.0,
            'motor_rpm_2': latest_telem.motor_rpm_2 or 0.0,
            'motor_rpm_3': latest_telem.motor_rpm_3 or 0.0,
            'motor_rpm_4': latest_telem.motor_rpm_4 or 0.0,
            'motor_temp_1': latest_telem.motor_temp_1 or 25.0,
            'motor_temp_2': latest_telem.motor_temp_2 or 25.0,
            'motor_temp_3': latest_telem.motor_temp_3 or 25.0,
            'motor_temp_4': latest_telem.motor_temp_4 or 25.0,
            'vibration_x': latest_telem.vibration_x or 0.0,
            'vibration_y': latest_telem.vibration_y or 0.0,
            'vibration_z': latest_telem.vibration_z or 0.0,
        }

        from .predictor import MLPredictor
        res = MLPredictor.predict_motor_anomaly(features)

        active_model = MLModel.objects.filter(model_type='motor_anomaly', is_active=True).first()
        pred = MLPrediction.objects.create(
            drone_id=drone_id,
            flight=latest_telem.flight,
            model=active_model,
            prediction_type='motor_anomaly',
            input_summary=features,
            prediction_value=1.0 if res.get('is_anomaly') else 0.0,
            prediction_label='anomaly' if res.get('is_anomaly') else 'normal',
            confidence_score=float(res.get('confidence', 0.90)),
            explanation={
                'anomaly_score': res.get('anomaly_score'),
                'is_anomaly': res.get('is_anomaly')
            }
        )

        # Trigger a system Alert if an anomaly is detected
        if res.get('is_anomaly'):
            from apps.alerts.models import Alert
            Alert.objects.create(
                drone_id=drone_id,
                flight=latest_telem.flight,
                alert_type='motor_anomaly',
                severity='critical' if res.get('anomaly_score', 0) > 0.8 else 'warning',
                title=f"Motor vibration anomaly on {latest_telem.flight.drone.name}",
                message=f"Isolation Forest flagged motor operations with anomaly score {res.get('anomaly_score')}. Inspect bearing balance.",
                ai_generated=True,
                model_name=active_model.name if active_model else 'motor_anomaly_iforest_v1',
                confidence=res.get('confidence')
            )

        return Response({
            'id': pred.id,
            'drone_id': drone_id,
            'prediction_type': 'motor_anomaly',
            'is_anomaly': res.get('is_anomaly'),
            'anomaly_score': res.get('anomaly_score'),
            'confidence': res.get('confidence'),
            'model': active_model.name if active_model else 'motor_anomaly_iforest_v1',
        })


class FlightAnomalyPredictView(APIView):
    """Detect anomalies in flight telemetry data."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        flight_id = request.data.get('flight_id')
        if not flight_id:
            return Response({'error': 'flight_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.telemetry.models import TelemetryData
        telemetry_points = TelemetryData.objects.filter(flight_id=flight_id)

        if not telemetry_points.exists():
            return Response({'error': 'No telemetry data found for this flight.'}, status=status.HTTP_404_NOT_FOUND)

        anomalies = []
        from .predictor import MLPredictor

        # Sample points to avoid scanning thousands on each HTTP request
        sample_rate = max(1, telemetry_points.count() // 50)
        sampled_points = telemetry_points.order_by('timestamp')[::sample_rate]

        for pt in sampled_points:
            features = {
                'motor_rpm_1': pt.motor_rpm_1, 'motor_rpm_2': pt.motor_rpm_2,
                'motor_rpm_3': pt.motor_rpm_3, 'motor_rpm_4': pt.motor_rpm_4,
                'motor_temp_1': pt.motor_temp_1, 'motor_temp_2': pt.motor_temp_2,
                'motor_temp_3': pt.motor_temp_3, 'motor_temp_4': pt.motor_temp_4,
                'vibration_x': pt.vibration_x, 'vibration_y': pt.vibration_y,
                'vibration_z': pt.vibration_z
            }
            res = MLPredictor.predict_motor_anomaly(features)
            if res.get('is_anomaly'):
                anomalies.append({
                    'timestamp_offset_s': int((pt.timestamp - telemetry_points[0].timestamp).total_seconds()),
                    'type': 'motor_anomaly',
                    'severity': 'medium' if res.get('anomaly_score', 0) < 0.8 else 'high',
                    'score': res.get('anomaly_score'),
                })

        risk_score = len(anomalies) / max(1, len(sampled_points))
        risk_score = round(min(1.0, risk_score * 2.0), 3)

        return Response({
            'flight_id': flight_id,
            'prediction_type': 'flight_anomaly',
            'total_anomalies': len(anomalies),
            'risk_score': risk_score,
            'anomalies': anomalies[:10],
            'confidence': 0.95,
            'model': 'flight_anomaly_analyzer_v1',
        })


class MissionRiskPredictView(APIView):
    """Assess risk for a planned mission."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mission_id = request.data.get('mission_id')
        if not mission_id:
            return Response({'error': 'mission_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.missions.models import Mission
        mission = Mission.objects.filter(id=mission_id).first()
        if not mission:
            return Response({'error': 'Mission not found.'}, status=status.HTTP_404_NOT_FOUND)

        drone = mission.assigned_drone
        if drone:
            from django.db import models
            drone_hours = drone.flights.aggregate(total_hours=models.Sum('distance'))['total_hours'] or 12.5
            drone_flights = drone.flights.count()

            from apps.telemetry.models import TelemetryData
            latest_telem = TelemetryData.objects.filter(flight__drone=drone).order_by('-timestamp').first()
            battery_soh = latest_telem.battery_percentage if latest_telem else 96.0
            comp_health_avg = 95.0
        else:
            drone_hours = 0.0
            drone_flights = 0
            battery_soh = 100.0
            comp_health_avg = 100.0

        features = {
            'distance_total_km': mission.estimated_distance_km or 2.5,
            'max_altitude_planned': mission.max_altitude_m or 120.0,
            'waypoint_count': mission.waypoints.count() or 4,
            'weather_wind_speed': 4.5,
            'weather_visibility_km': 15.0,
            'weather_temperature': 28.0,
            'battery_soh': battery_soh,
            'drone_total_hours': float(drone_hours),
            'drone_total_flights': drone_flights,
            'time_of_day_hour': 14.0,
            'payload_weight_ratio': 0.15,
            'estimated_duration_min': mission.estimated_duration_min or 15.0,
            'terrain_complexity': 2.0,
            'days_since_maintenance': 8.0,
            'component_health_avg': comp_health_avg,
        }

        from .predictor import MLPredictor
        res = MLPredictor.predict_mission_risk(features)

        active_model = MLModel.objects.filter(model_type='mission_risk', is_active=True).first()
        pred = MLPrediction.objects.create(
            drone=drone,
            model=active_model,
            prediction_type='mission_risk',
            input_summary=features,
            prediction_value=float(res.get('risk_score', 0)),
            prediction_label=res.get('risk_level', 'low'),
            confidence_score=float(res.get('confidence', 0.90)),
            explanation=res.get('risk_factors', {})
        )

        mission.risk_score = res.get('risk_score')
        mission.save()

        return Response({
            'id': pred.id,
            'mission_id': mission_id,
            'prediction_type': 'mission_risk',
            'risk_score': res.get('risk_score'),
            'risk_level': res.get('risk_level'),
            'risk_factors': res.get('risk_factors'),
            'confidence': res.get('confidence'),
            'model': active_model.name if active_model else 'mission_risk_gbr_v1',
        })


class MaintenancePredictView(APIView):
    """Predict maintenance needs for a drone."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        drone_id = request.data.get('drone_id')
        if not drone_id:
            return Response({'error': 'drone_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from apps.drones.models import Drone
        drone = Drone.objects.filter(id=drone_id).first()
        if not drone:
            return Response({'error': 'Drone not found.'}, status=status.HTTP_404_NOT_FOUND)

        from django.db import models
        total_hours = drone.flights.aggregate(total_hours=models.Sum('distance'))['total_hours'] or 15.0
        flights_count = drone.flights.count()

        components = ['motor_1', 'motor_2', 'motor_3', 'motor_4', 'battery', 'esc', 'gps', 'imu']
        predictions = []

        from .predictor import MLPredictor
        active_model = MLModel.objects.filter(model_type='predictive_maintenance', is_active=True).first()

        overall_health = 100.0
        critical_count = 0

        for comp in components:
            from apps.telemetry.models import TelemetryData
            latest_telem = TelemetryData.objects.filter(flight__drone_id=drone_id).order_by('-timestamp').first()

            avg_vib = 0.35
            avg_temp = 35.0
            if latest_telem:
                avg_vib = (latest_telem.vibration_x + latest_telem.vibration_y + latest_telem.vibration_z) / 3.0
                if 'motor' in comp:
                    idx = comp.split('_')[-1]
                    avg_temp = getattr(latest_telem, f'motor_temp_{idx}', 35.0) or 35.0
                elif comp == 'battery':
                    avg_temp = latest_telem.battery_temperature or 30.0

            # Simulate lower health for motor_3 to demonstrate anomaly triggers
            health_base = 68.0 if comp == 'motor_3' else 95.0
            features = {
                'total_hours': float(total_hours),
                'cycles_since_maintenance': flights_count,
                'avg_vibration': float(avg_vib),
                'avg_temperature': float(avg_temp),
                'anomaly_frequency': 0.05 if comp != 'motor_3' else 0.22,
                'last_maintenance_days_ago': 14.0,
                'health_score': health_base,
                'degradation_rate': 0.02 if comp != 'motor_3' else 0.12,
                'component_age_days': 45.0,
                'max_temperature_recorded': float(avg_temp) + 5.0,
                'rpm_variance_avg': 120.0
            }

            res = MLPredictor.predict_maintenance_urgency(features)

            if res.get('urgency') in ['high', 'critical']:
                critical_count += 1

            overall_health -= (100 - features['health_score']) / len(components)

            predictions.append({
                'component': comp,
                'needs_maintenance': res.get('urgency') in ['high', 'critical'],
                'urgency': res.get('urgency'),
                'confidence': res.get('confidence'),
                'recommended_action': res.get('recommended_action'),
            })

            MLPrediction.objects.create(
                drone_id=drone_id,
                model=active_model,
                prediction_type='predictive_maintenance',
                input_summary=features,
                prediction_value=1.0 if res.get('urgency') in ['high', 'critical'] else 0.0,
                prediction_label=f"{comp}: {res.get('urgency')}",
                confidence_score=res.get('confidence'),
                explanation=res.get('probabilities')
            )

        if critical_count > 0:
            drone.status = 'maintenance'
            drone.save()

            # Trigger alert for maintenance needed
            from apps.alerts.models import Alert
            Alert.objects.create(
                drone_id=drone_id,
                alert_type='maintenance_due',
                severity='warning',
                title=f"Maintenance alert triggered for drone {drone.name}",
                message=f"Predictive maintenance models indicate critical wear in components. Current health score: {overall_health:.1f}%",
                ai_generated=True,
                model_name=active_model.name if active_model else 'maintenance_rf_v1',
                confidence=0.92
            )

        return Response({
            'drone_id': drone_id,
            'prediction_type': 'predictive_maintenance',
            'components': predictions,
            'overall_health_score': round(max(0.0, overall_health), 1),
            'model': active_model.name if active_model else 'maintenance_rf_v1',
        })
