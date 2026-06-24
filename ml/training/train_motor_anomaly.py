"""
Motor Anomaly Detection Model
===============================
Isolation Forest + Autoencoder hybrid approach for detecting
anomalous motor behavior in UAV quadcopter systems.

Detects: bearing wear, prop imbalance, ESC faults, overheating.
"""

import numpy as np
import pandas as pd
import os
import json
import joblib
import argparse
from datetime import datetime

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, f1_score, roc_auc_score


FEATURE_COLS = [
    'motor_rpm_1', 'motor_rpm_2', 'motor_rpm_3', 'motor_rpm_4',
    'motor_temp_1', 'motor_temp_2', 'motor_temp_3', 'motor_temp_4',
    'vibration_x', 'vibration_y', 'vibration_z',
    'rpm_mean', 'rpm_std', 'rpm_imbalance',
    'temp_mean', 'temp_std', 'temp_max_delta',
    'vibration_rms',
]


def generate_motor_data(n_normal: int = 10000, n_anomaly: int = 500,
                        output_dir: str = None) -> pd.DataFrame:
    """Generate synthetic motor telemetry with normal and anomalous samples."""
    records = []

    # Normal operation data
    for i in range(n_normal):
        base_rpm = np.random.uniform(4000, 6000)
        rpms = [int(base_rpm + np.random.normal(0, 50)) for _ in range(4)]
        base_temp = np.random.uniform(30, 55)
        temps = [round(base_temp + np.random.normal(0, 2), 1) for _ in range(4)]
        vib = [round(np.random.normal(0, 0.5), 3) for _ in range(3)]

        rpm_arr = np.array(rpms)
        temp_arr = np.array(temps)
        records.append({
            'motor_rpm_1': rpms[0], 'motor_rpm_2': rpms[1],
            'motor_rpm_3': rpms[2], 'motor_rpm_4': rpms[3],
            'motor_temp_1': temps[0], 'motor_temp_2': temps[1],
            'motor_temp_3': temps[2], 'motor_temp_4': temps[3],
            'vibration_x': vib[0], 'vibration_y': vib[1], 'vibration_z': vib[2],
            'rpm_mean': rpm_arr.mean(), 'rpm_std': rpm_arr.std(),
            'rpm_imbalance': rpm_arr.max() - rpm_arr.min(),
            'temp_mean': temp_arr.mean(), 'temp_std': temp_arr.std(),
            'temp_max_delta': temp_arr.max() - temp_arr.min(),
            'vibration_rms': np.sqrt(np.mean(np.array(vib) ** 2)),
            'is_anomaly': 0,
        })

    # Anomalous data — various fault types
    fault_types = ['rpm_drop', 'temp_spike', 'high_vibration', 'imbalance']
    for i in range(n_anomaly):
        fault = np.random.choice(fault_types)
        base_rpm = np.random.uniform(4000, 6000)
        rpms = [int(base_rpm + np.random.normal(0, 50)) for _ in range(4)]
        base_temp = np.random.uniform(30, 55)
        temps = [round(base_temp + np.random.normal(0, 2), 1) for _ in range(4)]
        vib = [round(np.random.normal(0, 0.5), 3) for _ in range(3)]

        if fault == 'rpm_drop':
            idx = np.random.randint(0, 4)
            rpms[idx] = int(rpms[idx] * np.random.uniform(0.5, 0.75))
        elif fault == 'temp_spike':
            idx = np.random.randint(0, 4)
            temps[idx] = round(temps[idx] + np.random.uniform(20, 40), 1)
        elif fault == 'high_vibration':
            vib = [round(np.random.normal(0, 2.5), 3) for _ in range(3)]
        elif fault == 'imbalance':
            rpms[0] = int(rpms[0] * 1.3)
            rpms[2] = int(rpms[2] * 0.7)

        rpm_arr = np.array(rpms)
        temp_arr = np.array(temps)
        records.append({
            'motor_rpm_1': rpms[0], 'motor_rpm_2': rpms[1],
            'motor_rpm_3': rpms[2], 'motor_rpm_4': rpms[3],
            'motor_temp_1': temps[0], 'motor_temp_2': temps[1],
            'motor_temp_3': temps[2], 'motor_temp_4': temps[3],
            'vibration_x': vib[0], 'vibration_y': vib[1], 'vibration_z': vib[2],
            'rpm_mean': rpm_arr.mean(), 'rpm_std': rpm_arr.std(),
            'rpm_imbalance': rpm_arr.max() - rpm_arr.min(),
            'temp_mean': temp_arr.mean(), 'temp_std': temp_arr.std(),
            'temp_max_delta': temp_arr.max() - temp_arr.min(),
            'vibration_rms': np.sqrt(np.mean(np.array(vib) ** 2)),
            'is_anomaly': 1,
        })

    df = pd.DataFrame(records)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(os.path.join(output_dir, 'motor_telemetry.csv'), index=False)
        print(f"[OK] Generated {len(df)} motor records ({n_normal} normal, {n_anomaly} anomalous)")
    return df


def train_motor_anomaly_model(data_path: str = None, output_dir: str = 'ml/models') -> dict:
    """Train Isolation Forest motor anomaly detection model."""
    print("\n" + "=" * 60)
    print("  Motor Anomaly Detection Model Training")
    print("=" * 60)

    if data_path and os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        print("[DATA] Generating synthetic motor data...")
        df = generate_motor_data(10000, 500, 'ml/data')
        data_path = 'ml/data/motor_telemetry.csv'

    X = df[FEATURE_COLS].values
    y_true = df['is_anomaly'].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train only on normal data (unsupervised)
    X_normal = X_scaled[y_true == 0]
    print(f"[TRAIN] Training on {len(X_normal)} normal samples...")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples='auto',
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_normal)

    # Predict on all data
    y_pred_raw = model.predict(X_scaled)
    y_pred = (y_pred_raw == -1).astype(int)  # -1 = anomaly in sklearn

    # Anomaly scores (lower = more anomalous)
    scores = model.decision_function(X_scaled)
    anomaly_scores = 1 - (scores - scores.min()) / (scores.max() - scores.min())

    # Metrics
    f1 = f1_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True)
    try:
        auc = roc_auc_score(y_true, anomaly_scores)
    except ValueError:
        auc = 0.0

    metrics = {
        'model_name': 'motor_anomaly_iforest',
        'model_type': 'motor_anomaly',
        'version': '1.0.0',
        'algorithm': 'IsolationForest',
        'f1_score': round(f1, 4),
        'precision': round(report['1']['precision'], 4),
        'recall': round(report['1']['recall'], 4),
        'auc_roc': round(auc, 4),
        'accuracy': round(report['accuracy'], 4),
        'n_features': len(FEATURE_COLS),
        'feature_names': FEATURE_COLS,
        'trained_at': datetime.now().isoformat(),
        'contamination': 0.05,
    }

    print(f"\n[RESULTS]")
    print(f"  F1-Score:  {metrics['f1_score']}")
    print(f"  Precision: {metrics['precision']}")
    print(f"  Recall:    {metrics['recall']}")
    print(f"  AUC-ROC:   {metrics['auc_roc']}")

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(model, os.path.join(output_dir, 'motor_anomaly_model.pkl'))
    joblib.dump(scaler, os.path.join(output_dir, 'motor_anomaly_scaler.pkl'))
    with open(os.path.join(output_dir, 'motor_anomaly_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"[SAVED] Model artifacts → {output_dir}")
    return metrics


def predict_motor_anomaly(features: dict, model_dir: str = 'ml/models') -> dict:
    """Predict motor anomaly score for a telemetry packet."""
    model = joblib.load(os.path.join(model_dir, 'motor_anomaly_model.pkl'))
    scaler = joblib.load(os.path.join(model_dir, 'motor_anomaly_scaler.pkl'))

    feature_vector = [features.get(col, 0) for col in FEATURE_COLS]
    X = scaler.transform([feature_vector])

    raw_score = model.decision_function(X)[0]
    prediction = model.predict(X)[0]
    is_anomaly = prediction == -1
    anomaly_score = max(0, min(1, 0.5 - raw_score))

    return {
        'is_anomaly': bool(is_anomaly),
        'anomaly_score': round(anomaly_score, 4),
        'confidence': round(abs(raw_score) * 0.5, 3),
        'model_version': '1.0.0',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Motor Anomaly Model')
    parser.add_argument('--data', default=None, help='Path to motor data CSV')
    parser.add_argument('--output', default='ml/models')
    args = parser.parse_args()
    train_motor_anomaly_model(args.data, args.output)
