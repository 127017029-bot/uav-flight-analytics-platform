import os
import joblib
from django.conf import settings
import numpy as np

try:
    import onnxruntime as ort
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False

class MLPredictor:
    """Class manager for loading ML models and executing live inferences."""
    _models = {}

    @classmethod
    def load_models(cls):
        """Load all model weights from files if they aren't loaded yet."""
        if cls._models:
            return  # Already loaded

        # The models directory is ml/models at the project root
        models_dir = os.path.join(settings.BASE_DIR.parent, 'ml', 'models')
        print(f"[MLPredictor] Loading models from {models_dir}...")

        model_files = {
            'battery_rul': {
                'model': 'battery_rul_model.pkl',
                'scaler': 'battery_rul_scaler.pkl'
            },
            'motor_anomaly': {
                'model': 'motor_anomaly_model.pkl',
                'scaler': 'motor_anomaly_scaler.pkl'
            },
            'mission_risk': {
                'model': 'mission_risk_model.pkl',
                'scaler': 'mission_risk_scaler.pkl'
            },
            'maintenance': {
                'model': 'maintenance_model.pkl',
                'scaler': 'maintenance_scaler.pkl',
                'le': 'maintenance_label_encoder.pkl'
            }
        }

        for model_name, files in model_files.items():
            cls._models[model_name] = {}
            try:
                # Load main model
                model_path = os.path.join(models_dir, files['model'])
                if os.path.exists(model_path):
                    cls._models[model_name]['model'] = joblib.load(model_path)
                    print(f"[MLPredictor] Loaded {model_name} model successfully.")
                else:
                    print(f"[MLPredictor] Warning: {model_name} model not found at {model_path}")

                # Load scaler
                scaler_path = os.path.join(models_dir, files['scaler'])
                if os.path.exists(scaler_path):
                    cls._models[model_name]['scaler'] = joblib.load(scaler_path)
                    print(f"[MLPredictor] Loaded {model_name} scaler successfully.")

                # Load label encoder (for classification)
                if 'le' in files:
                    le_path = os.path.join(models_dir, files['le'])
                    if os.path.exists(le_path):
                        cls._models[model_name]['le'] = joblib.load(le_path)
                        print(f"[MLPredictor] Loaded {model_name} label encoder successfully.")
            except Exception as e:
                print(f"[MLPredictor] Error loading {model_name} model: {e}")

    @classmethod
    def predict_battery_rul(cls, features: dict) -> dict:
        """Predict remaining useful life for a battery."""
        cls.load_models()
        model_info = cls._models.get('battery_rul', {})
        if 'model' not in model_info or 'scaler' not in model_info:
            return {
                'error': 'Battery RUL model is not loaded.',
                'predicted_rul_cycles': 150,
                'confidence': 0.5,
            }

        FEATURE_COLS = [
            'cycle', 'capacity_measured', 'state_of_health', 'internal_resistance',
            'voltage_max', 'voltage_min', 'voltage_mean', 'voltage_std',
            'current_mean', 'current_std', 'current_max',
            'temperature_mean', 'temperature_max', 'temperature_std',
            'charge_duration_min', 'discharge_duration_min',
            'energy_charged_wh', 'energy_discharged_wh',
            'coulombic_efficiency', 'degradation_rate',
            'capacity_measured_rolling_10', 'capacity_measured_rolling_diff',
            'voltage_mean_rolling_10', 'voltage_mean_rolling_diff',
            'temperature_mean_rolling_10', 'temperature_mean_rolling_diff'
        ]

        feature_vector = [features.get(col, 0) for col in FEATURE_COLS]
        try:
            X = model_info['scaler'].transform([feature_vector])
            prediction = model_info['model'].predict(X)[0]
            provided_features = sum(1 for col in FEATURE_COLS[:20] if col in features)
            completeness = provided_features / 20
            confidence = min(0.95, completeness * 0.9 + 0.1)

            return {
                'predicted_rul_cycles': max(0, int(prediction)),
                'predicted_rul_hours': round(max(0, int(prediction)) * 0.5, 1),
                'confidence': round(confidence, 3),
                'model': 'battery_rul_gbr_v1',
            }
        except Exception as e:
            return {
                'error': f'Inference error: {e}',
                'predicted_rul_cycles': 150,
                'confidence': 0.5,
            }

    @classmethod
    def predict_motor_anomaly(cls, features: dict) -> dict:
        """Detect motor anomalies from telemetry features."""
        cls.load_models()
        model_info = cls._models.get('motor_anomaly', {})
        if 'model' not in model_info or 'scaler' not in model_info:
            return {
                'error': 'Motor anomaly model is not loaded.',
                'is_anomaly': False,
                'anomaly_score': 0.05,
                'confidence': 0.5,
            }

        FEATURE_COLS = [
            'motor_rpm_1', 'motor_rpm_2', 'motor_rpm_3', 'motor_rpm_4',
            'motor_temp_1', 'motor_temp_2', 'motor_temp_3', 'motor_temp_4',
            'vibration_x', 'vibration_y', 'vibration_z',
            'rpm_mean', 'rpm_std', 'rpm_imbalance',
            'temp_mean', 'temp_std', 'temp_max_delta',
            'vibration_rms',
        ]

        # Compute summaries if not present
        if 'rpm_mean' not in features:
            rpms = [features.get(f'motor_rpm_{i}', 0) or 0 for i in range(1, 5)]
            features['rpm_mean'] = float(np.mean(rpms))
            features['rpm_std'] = float(np.std(rpms))
            features['rpm_imbalance'] = float(max(rpms) - min(rpms))

        if 'temp_mean' not in features:
            temps = [features.get(f'motor_temp_{i}', 25.0) or 25.0 for i in range(1, 5)]
            features['temp_mean'] = float(np.mean(temps))
            features['temp_std'] = float(np.std(temps))
            features['temp_max_delta'] = float(max(temps) - min(temps))

        if 'vibration_rms' not in features:
            vibs = [features.get('vibration_x', 0) or 0, features.get('vibration_y', 0) or 0, features.get('vibration_z', 0) or 0]
            features['vibration_rms'] = float(np.sqrt(np.mean(np.array(vibs) ** 2)))

        feature_vector = [features.get(col, 0) for col in FEATURE_COLS]
        try:
            X = model_info['scaler'].transform([feature_vector])
            raw_score = model_info['model'].decision_function(X)[0]
            prediction = model_info['model'].predict(X)[0]
            is_anomaly = prediction == -1
            anomaly_score = max(0.0, min(1.0, 0.5 - raw_score))

            return {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': round(anomaly_score, 4),
                'confidence': round(abs(raw_score) * 0.5 + 0.5, 3),
                'model': 'motor_anomaly_iforest_v1',
            }
        except Exception as e:
            return {
                'error': f'Inference error: {e}',
                'is_anomaly': False,
                'anomaly_score': 0.05,
                'confidence': 0.5,
            }

    @classmethod
    def predict_mission_risk(cls, features: dict) -> dict:
        """Score pre-flight mission risk."""
        cls.load_models()
        model_info = cls._models.get('mission_risk', {})
        if 'model' not in model_info or 'scaler' not in model_info:
            return {
                'error': 'Mission risk model is not loaded.',
                'risk_score': 35.0,
                'risk_level': 'low',
                'confidence': 0.5,
            }

        FEATURE_COLS = [
            'distance_total_km', 'max_altitude_planned', 'waypoint_count',
            'weather_wind_speed', 'weather_visibility_km', 'weather_temperature',
            'battery_soh', 'drone_total_hours', 'drone_total_flights',
            'time_of_day_hour', 'payload_weight_ratio',
            'estimated_duration_min', 'terrain_complexity',
            'days_since_maintenance', 'component_health_avg',
        ]

        feature_vector = [features.get(col, 0) for col in FEATURE_COLS]
        try:
            X = model_info['scaler'].transform([feature_vector])
            risk_score = model_info['model'].predict(X)[0]
            risk_score = max(0.0, min(100.0, float(risk_score)))
            
            risk_level = 'high' if risk_score > 70 else ('medium' if risk_score > 40 else 'low')

            risk_factors = {
                'weather': round(features.get('weather_wind_speed', 0) / 15.0, 2),
                'battery': round((100 - features.get('battery_soh', 100)) / 40.0, 2),
                'distance': round(features.get('distance_total_km', 0) / 10.0, 2),
                'drone_health': round((100 - features.get('component_health_avg', 100)) / 40.0, 2),
            }

            return {
                'risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'confidence': 0.90,
                'model': 'mission_risk_gbr_v1',
            }
        except Exception as e:
            return {
                'error': f'Inference error: {e}',
                'risk_score': 35.0,
                'risk_level': 'low',
                'confidence': 0.5,
            }

    @classmethod
    def predict_maintenance_urgency(cls, features: dict) -> dict:
        """Classify component maintenance urgency."""
        cls.load_models()
        model_info = cls._models.get('maintenance', {})
        if 'model' not in model_info or 'scaler' not in model_info or 'le' not in model_info:
            return {
                'error': 'Maintenance model is not loaded.',
                'urgency': 'low',
                'confidence': 0.5,
                'recommended_action': 'no_action',
            }

        FEATURE_COLS = [
            'total_hours', 'cycles_since_maintenance', 'avg_vibration',
            'avg_temperature', 'anomaly_frequency', 'last_maintenance_days_ago',
            'health_score', 'degradation_rate', 'component_age_days',
            'max_temperature_recorded', 'rpm_variance_avg',
        ]

        feature_vector = [features.get(col, 0) for col in FEATURE_COLS]
        try:
            X = model_info['scaler'].transform([feature_vector])
            pred_class = model_info['model'].predict(X)[0]
            pred_proba = model_info['model'].predict_proba(X)[0]

            urgency = model_info['le'].inverse_transform([pred_class])[0]
            confidence = float(pred_proba.max())

            actions = {
                'low': 'no_action',
                'medium': 'inspect_at_next_cycle',
                'high': 'inspect_immediately',
                'critical': 'inspect_and_replace'
            }

            return {
                'urgency': urgency,
                'confidence': round(confidence, 3),
                'recommended_action': actions.get(urgency, 'no_action'),
                'probabilities': {
                    label: round(float(prob), 4)
                    for label, prob in zip(model_info['le'].classes_, pred_proba)
                },
                'model': 'maintenance_rf_v1',
            }
        except Exception as e:
            return {
                'error': f'Inference error: {e}',
                'urgency': 'low',
                'confidence': 0.5,
                'recommended_action': 'no_action',
            }
