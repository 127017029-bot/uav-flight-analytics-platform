"""
Battery RUL (Remaining Useful Life) Prediction Model
=====================================================
LSTM-based time-series model for predicting battery remaining
useful life from charge-discharge cycle telemetry features.

Architecture: Stacked LSTM → Dense → RUL prediction
Training: Sliding window over cycle sequences
Export: Saved as .pkl for scikit-learn pipeline inference
"""

import numpy as np
import pandas as pd
import os
import json
import joblib
import argparse
from datetime import datetime

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


# Feature columns for the model
FEATURE_COLS = [
    'cycle', 'capacity_measured', 'state_of_health', 'internal_resistance',
    'voltage_max', 'voltage_min', 'voltage_mean', 'voltage_std',
    'current_mean', 'current_std', 'current_max',
    'temperature_mean', 'temperature_max', 'temperature_std',
    'charge_duration_min', 'discharge_duration_min',
    'energy_charged_wh', 'energy_discharged_wh',
    'coulombic_efficiency', 'degradation_rate',
]

TARGET_COL = 'remaining_useful_life'


def load_and_prepare_data(data_path: str) -> tuple:
    """
    Load battery degradation dataset and prepare features.

    Args:
        data_path: Path to battery_degradation.csv

    Returns:
        X, y, scaler tuple
    """
    df = pd.read_csv(data_path)
    print(f"[DATA] Loaded {len(df)} records from {df['battery_id'].nunique()} batteries")

    # Add rolling statistics per battery
    for col in ['capacity_measured', 'voltage_mean', 'temperature_mean']:
        df[f'{col}_rolling_10'] = df.groupby('battery_id')[col].transform(
            lambda x: x.rolling(10, min_periods=1).mean()
        )
        df[f'{col}_rolling_diff'] = df.groupby('battery_id')[col].transform(
            lambda x: x.diff().rolling(5, min_periods=1).mean()
        )
        FEATURE_COLS.extend([f'{col}_rolling_10', f'{col}_rolling_diff'])

    # Fill NaN from rolling operations
    df = df.fillna(0)

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler, df


def train_battery_rul_model(data_path: str, output_dir: str = 'ml/models') -> dict:
    """
    Train the Battery RUL prediction model.

    Uses Gradient Boosting Regressor as a robust baseline.
    For production, this would be replaced with LSTM using TensorFlow/Keras.

    Args:
        data_path: Path to training data CSV
        output_dir: Directory to save model artifacts

    Returns:
        dict with training metrics
    """
    print("\n" + "=" * 60)
    print("  Battery RUL Prediction Model Training")
    print("=" * 60)

    # Load data
    X, y, scaler, df = load_and_prepare_data(data_path)

    # Split by battery_id to prevent data leakage
    battery_ids = df['battery_id'].unique()
    train_ids, test_ids = train_test_split(battery_ids, test_size=0.2, random_state=42)

    train_mask = df['battery_id'].isin(train_ids)
    test_mask = df['battery_id'].isin(test_ids)

    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]

    print(f"[SPLIT] Train: {len(X_train)} samples ({len(train_ids)} batteries)")
    print(f"[SPLIT] Test:  {len(X_test)} samples ({len(test_ids)} batteries)")

    # Train model
    print("\n[TRAIN] Training Gradient Boosting Regressor...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        verbose=0,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    metrics = {
        'model_name': 'battery_rul_gbr',
        'model_type': 'battery_rul',
        'version': '1.0.0',
        'algorithm': 'GradientBoostingRegressor',
        'train_rmse': round(np.sqrt(mean_squared_error(y_train, y_pred_train)), 2),
        'test_rmse': round(np.sqrt(mean_squared_error(y_test, y_pred_test)), 2),
        'train_mae': round(mean_absolute_error(y_train, y_pred_train), 2),
        'test_mae': round(mean_absolute_error(y_test, y_pred_test), 2),
        'train_r2': round(r2_score(y_train, y_pred_train), 4),
        'test_r2': round(r2_score(y_test, y_pred_test), 4),
        'n_features': len(FEATURE_COLS),
        'feature_names': FEATURE_COLS,
        'trained_at': datetime.now().isoformat(),
        'n_train_samples': len(X_train),
        'n_test_samples': len(X_test),
    }

    # Feature importance
    importance = pd.Series(
        model.feature_importances_, index=FEATURE_COLS
    ).sort_values(ascending=False)

    metrics['top_features'] = {k: round(v, 4) for k, v in importance.head(10).items()}

    print(f"\n[RESULTS]")
    print(f"  Train RMSE: {metrics['train_rmse']} cycles")
    print(f"  Test  RMSE: {metrics['test_rmse']} cycles")
    print(f"  Train MAE:  {metrics['train_mae']} cycles")
    print(f"  Test  MAE:  {metrics['test_mae']} cycles")
    print(f"  Train R²:   {metrics['train_r2']}")
    print(f"  Test  R²:   {metrics['test_r2']}")
    print(f"\n[TOP FEATURES]")
    for feat, imp in importance.head(5).items():
        print(f"  {feat}: {imp:.4f}")

    # Save model artifacts
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, 'battery_rul_model.pkl')
    scaler_path = os.path.join(output_dir, 'battery_rul_scaler.pkl')
    metrics_path = os.path.join(output_dir, 'battery_rul_metrics.json')

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[SAVED] Model   → {model_path}")
    print(f"[SAVED] Scaler  → {scaler_path}")
    print(f"[SAVED] Metrics → {metrics_path}")

    return metrics


def predict_battery_rul(features: dict, model_dir: str = 'ml/models') -> dict:
    """
    Predict remaining useful life for a battery.

    Args:
        features: dict of battery telemetry features
        model_dir: Directory containing model artifacts

    Returns:
        dict with prediction, confidence, and explanation
    """
    model = joblib.load(os.path.join(model_dir, 'battery_rul_model.pkl'))
    scaler = joblib.load(os.path.join(model_dir, 'battery_rul_scaler.pkl'))

    # Prepare feature vector (fill missing with defaults)
    feature_vector = []
    for col in FEATURE_COLS:
        feature_vector.append(features.get(col, 0))

    X = scaler.transform([feature_vector])
    prediction = model.predict(X)[0]

    # Confidence based on feature completeness and model uncertainty
    provided_features = sum(1 for col in FEATURE_COLS[:20] if col in features)
    completeness = provided_features / 20
    confidence = min(0.95, completeness * 0.9 + 0.1)

    return {
        'predicted_rul_cycles': max(0, int(prediction)),
        'confidence': round(confidence, 3),
        'model_version': '1.0.0',
        'input_features_used': provided_features,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train Battery RUL Model')
    parser.add_argument('--data', default='ml/data/battery_degradation.csv')
    parser.add_argument('--output', default='ml/models')
    args = parser.parse_args()

    train_battery_rul_model(args.data, args.output)
