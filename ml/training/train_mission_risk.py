"""
Mission Risk Scoring Model
============================
XGBoost-based model for pre-flight mission risk assessment.
Scores missions 0-100 based on environmental, drone health,
and mission complexity factors.
"""

import numpy as np
import pandas as pd
import os
import json
import joblib
import argparse
from datetime import datetime

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


FEATURE_COLS = [
    'distance_total_km', 'max_altitude_planned', 'waypoint_count',
    'weather_wind_speed', 'weather_visibility_km', 'weather_temperature',
    'battery_soh', 'drone_total_hours', 'drone_total_flights',
    'time_of_day_hour', 'payload_weight_ratio',
    'estimated_duration_min', 'terrain_complexity',
    'days_since_maintenance', 'component_health_avg',
]


def generate_mission_data(n_samples: int = 10000, output_dir: str = None) -> pd.DataFrame:
    """Generate synthetic mission profiles with risk labels."""
    records = []

    for _ in range(n_samples):
        # Mission parameters
        distance = np.random.exponential(5) + 0.5
        max_alt = np.random.uniform(20, 150)
        waypoints = np.random.randint(2, 20)
        wind = np.random.exponential(3)
        visibility = np.random.uniform(1, 20)
        temperature = np.random.normal(25, 10)
        battery_soh = np.random.uniform(60, 100)
        drone_hours = np.random.exponential(100)
        drone_flights = int(drone_hours * np.random.uniform(1.5, 3))
        time_hour = np.random.uniform(0, 24)
        payload_ratio = np.random.uniform(0, 0.9)
        duration = distance * np.random.uniform(3, 8)
        terrain = np.random.uniform(0, 1)
        days_maintenance = np.random.exponential(30)
        health_avg = np.random.uniform(50, 100)

        # Risk scoring formula (complex, nonlinear)
        risk = 10  # base
        risk += max(0, wind - 8) * 4  # high wind
        risk += max(0, 120 - max_alt) * -0.05  # altitude risk
        risk += max(0, max_alt - 120) * 0.5  # above legal limit
        risk += max(0, 80 - battery_soh) * 1.5  # battery degradation
        risk += max(0, days_maintenance - 60) * 0.3  # overdue maintenance
        risk += max(0, 80 - health_avg) * 0.8  # poor health
        risk += payload_ratio * 15  # heavy payload
        risk += max(0, distance - 10) * 2  # long distance
        risk += max(0, 5 - visibility) * 5  # poor visibility
        risk += (1 if time_hour < 6 or time_hour > 20 else 0) * 10  # night ops
        risk += terrain * 10  # complex terrain
        risk += np.random.normal(0, 5)  # noise

        risk = np.clip(risk, 0, 100)

        records.append({
            'distance_total_km': round(distance, 2),
            'max_altitude_planned': round(max_alt, 1),
            'waypoint_count': waypoints,
            'weather_wind_speed': round(wind, 1),
            'weather_visibility_km': round(visibility, 1),
            'weather_temperature': round(temperature, 1),
            'battery_soh': round(battery_soh, 1),
            'drone_total_hours': round(drone_hours, 1),
            'drone_total_flights': drone_flights,
            'time_of_day_hour': round(time_hour, 1),
            'payload_weight_ratio': round(payload_ratio, 2),
            'estimated_duration_min': round(duration, 1),
            'terrain_complexity': round(terrain, 2),
            'days_since_maintenance': round(days_maintenance, 1),
            'component_health_avg': round(health_avg, 1),
            'risk_score': round(risk, 1),
        })

    df = pd.DataFrame(records)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(os.path.join(output_dir, 'mission_profiles.csv'), index=False)
        print(f"[OK] Generated {len(df)} mission profiles")
    return df


def train_mission_risk_model(data_path: str = None, output_dir: str = 'ml/models') -> dict:
    """Train mission risk scoring model."""
    print("\n" + "=" * 60)
    print("  Mission Risk Scoring Model Training")
    print("=" * 60)

    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_mission_data(10000, 'ml/data')

    X = df[FEATURE_COLS].values
    y = df['risk_score'].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=200, max_depth=5, learning_rate=0.1,
        subsample=0.8, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    metrics = {
        'model_name': 'mission_risk_gbr',
        'model_type': 'mission_risk',
        'version': '1.0.0',
        'algorithm': 'GradientBoostingRegressor',
        'test_rmse': round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        'test_mae': round(mean_absolute_error(y_test, y_pred), 2),
        'test_r2': round(r2_score(y_test, y_pred), 4),
        'trained_at': datetime.now().isoformat(),
        'feature_names': FEATURE_COLS,
        'top_features': {
            k: round(v, 4)
            for k, v in sorted(zip(FEATURE_COLS, model.feature_importances_),
                               key=lambda x: -x[1])[:8]
        },
    }

    print(f"\n[RESULTS] RMSE: {metrics['test_rmse']} | MAE: {metrics['test_mae']} | R²: {metrics['test_r2']}")

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(model, os.path.join(output_dir, 'mission_risk_model.pkl'))
    joblib.dump(scaler, os.path.join(output_dir, 'mission_risk_scaler.pkl'))
    with open(os.path.join(output_dir, 'mission_risk_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics


def predict_mission_risk(features: dict, model_dir: str = 'ml/models') -> dict:
    """Score mission risk 0-100."""
    model = joblib.load(os.path.join(model_dir, 'mission_risk_model.pkl'))
    scaler = joblib.load(os.path.join(model_dir, 'mission_risk_scaler.pkl'))

    vec = [features.get(col, 0) for col in FEATURE_COLS]
    X = scaler.transform([vec])
    score = model.predict(X)[0]

    risk_level = 'low' if score < 30 else 'medium' if score < 60 else 'high' if score < 80 else 'critical'

    return {
        'risk_score': round(np.clip(score, 0, 100), 1),
        'risk_level': risk_level,
        'confidence': 0.85,
        'model_version': '1.0.0',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Mission Risk Model')
    parser.add_argument('--data', default=None)
    parser.add_argument('--output', default='ml/models')
    args = parser.parse_args()
    train_mission_risk_model(args.data, args.output)
