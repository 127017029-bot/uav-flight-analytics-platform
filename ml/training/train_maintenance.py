"""
Predictive Maintenance Urgency Classifier
===========================================
Random Forest classifier for predicting maintenance urgency
(low/medium/high/critical) based on component health metrics.
"""

import numpy as np
import pandas as pd
import os
import json
import joblib
import argparse
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score


FEATURE_COLS = [
    'total_hours', 'cycles_since_maintenance', 'avg_vibration',
    'avg_temperature', 'anomaly_frequency', 'last_maintenance_days_ago',
    'health_score', 'degradation_rate', 'component_age_days',
    'max_temperature_recorded', 'rpm_variance_avg',
]

URGENCY_LABELS = ['low', 'medium', 'high', 'critical']


def generate_maintenance_data(n_samples: int = 20000,
                              output_dir: str = None) -> pd.DataFrame:
    """Generate synthetic component maintenance data."""
    records = []

    for _ in range(n_samples):
        hours = np.random.exponential(200)
        cycles = int(hours * np.random.uniform(1, 4))
        vibration = np.random.exponential(0.5)
        temp = np.random.normal(45, 10)
        anomaly_freq = np.random.exponential(0.1)
        maint_days = np.random.exponential(45)
        health = np.clip(100 - hours * 0.05 - vibration * 10 + np.random.normal(0, 5), 0, 100)
        deg_rate = max(0, 0.01 + 0.0001 * hours + np.random.normal(0, 0.005))
        age_days = int(hours / np.random.uniform(2, 8))
        max_temp = temp + np.random.uniform(10, 30)
        rpm_var = np.random.exponential(50)

        # Urgency label based on rule combination
        score = 0
        score += max(0, 70 - health) * 1.0
        score += max(0, maint_days - 60) * 0.3
        score += vibration * 5
        score += anomaly_freq * 20
        score += max(0, temp - 60) * 1.0
        score += deg_rate * 100

        if score < 15:
            urgency = 'low'
        elif score < 35:
            urgency = 'medium'
        elif score < 60:
            urgency = 'high'
        else:
            urgency = 'critical'

        records.append({
            'total_hours': round(hours, 1),
            'cycles_since_maintenance': cycles,
            'avg_vibration': round(vibration, 3),
            'avg_temperature': round(temp, 1),
            'anomaly_frequency': round(anomaly_freq, 3),
            'last_maintenance_days_ago': round(maint_days, 1),
            'health_score': round(health, 1),
            'degradation_rate': round(deg_rate, 4),
            'component_age_days': age_days,
            'max_temperature_recorded': round(max_temp, 1),
            'rpm_variance_avg': round(rpm_var, 1),
            'urgency': urgency,
        })

    df = pd.DataFrame(records)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(os.path.join(output_dir, 'maintenance_data.csv'), index=False)
        print(f"[OK] Generated {len(df)} maintenance records")
        print(f"  Distribution: {df['urgency'].value_counts().to_dict()}")
    return df


def train_maintenance_model(data_path: str = None,
                            output_dir: str = 'ml/models') -> dict:
    """Train predictive maintenance urgency classifier."""
    print("\n" + "=" * 60)
    print("  Predictive Maintenance Model Training")
    print("=" * 60)

    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        df = generate_maintenance_data(20000, 'ml/data')

    X = df[FEATURE_COLS].values
    le = LabelEncoder()
    le.fit(URGENCY_LABELS)
    y = le.transform(df['urgency'].values)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=200, max_depth=12, min_samples_split=5,
        class_weight='balanced', random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, target_names=URGENCY_LABELS, output_dict=True)
    weighted_f1 = f1_score(y_test, y_pred, average='weighted')

    metrics = {
        'model_name': 'predictive_maintenance_rf',
        'model_type': 'predictive_maintenance',
        'version': '1.0.0',
        'algorithm': 'RandomForestClassifier',
        'weighted_f1': round(weighted_f1, 4),
        'accuracy': round(report['accuracy'], 4),
        'per_class': {
            label: {
                'precision': round(report[label]['precision'], 4),
                'recall': round(report[label]['recall'], 4),
                'f1': round(report[label]['f1-score'], 4),
            } for label in URGENCY_LABELS
        },
        'feature_names': FEATURE_COLS,
        'trained_at': datetime.now().isoformat(),
        'top_features': {
            k: round(v, 4) for k, v in sorted(
                zip(FEATURE_COLS, model.feature_importances_),
                key=lambda x: -x[1])[:8]
        },
    }

    print(f"\n[RESULTS] Weighted F1: {metrics['weighted_f1']} | Accuracy: {metrics['accuracy']}")
    print(classification_report(y_test, y_pred, target_names=URGENCY_LABELS))

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(model, os.path.join(output_dir, 'maintenance_model.pkl'))
    joblib.dump(scaler, os.path.join(output_dir, 'maintenance_scaler.pkl'))
    joblib.dump(le, os.path.join(output_dir, 'maintenance_label_encoder.pkl'))
    with open(os.path.join(output_dir, 'maintenance_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics


def predict_maintenance_urgency(features: dict, model_dir: str = 'ml/models') -> dict:
    """Predict maintenance urgency for a component."""
    model = joblib.load(os.path.join(model_dir, 'maintenance_model.pkl'))
    scaler = joblib.load(os.path.join(model_dir, 'maintenance_scaler.pkl'))
    le = joblib.load(os.path.join(model_dir, 'maintenance_label_encoder.pkl'))

    vec = [features.get(col, 0) for col in FEATURE_COLS]
    X = scaler.transform([vec])
    pred_class = model.predict(X)[0]
    pred_proba = model.predict_proba(X)[0]

    urgency = le.inverse_transform([pred_class])[0]
    confidence = float(pred_proba.max())

    return {
        'urgency': urgency,
        'confidence': round(confidence, 3),
        'probabilities': {
            label: round(float(prob), 4)
            for label, prob in zip(URGENCY_LABELS, pred_proba)
        },
        'model_version': '1.0.0',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Predictive Maintenance Model')
    parser.add_argument('--data', default=None)
    parser.add_argument('--output', default='ml/models')
    args = parser.parse_args()
    train_maintenance_model(args.data, args.output)
