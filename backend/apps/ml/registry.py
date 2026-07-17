import os
import json
from django.conf import settings
from django.utils import timezone
from apps.ml.models import MLModel

def register_models_in_db():
    """Register ML models in database if they don't exist yet."""
    # Resolve models directory (parent in development, base in Docker container)
    models_dir = os.path.join(settings.BASE_DIR.parent, 'ml', 'models')
    if not os.path.exists(models_dir):
        models_dir = os.path.join(settings.BASE_DIR, 'ml', 'models')
    
    model_info = [
        ('battery_rul', 'battery_rul_metrics.json', 'Battery RUL Prediction'),
        ('motor_anomaly', 'motor_anomaly_metrics.json', 'Motor Anomaly Detection'),
        ('mission_risk', 'mission_risk_metrics.json', 'Mission Risk Assessment'),
        ('predictive_maintenance', 'maintenance_metrics.json', 'Predictive Maintenance'),
    ]
    
    for mtype, filename, mname in model_info:
        path = os.path.join(models_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    meta = json.load(f)
                
                acc = meta.get('accuracy')
                if acc is None:
                    acc = meta.get('test_r2')
                    if acc is None:
                        acc = 0.90
                
                trained_at_str = meta.get('trained_at')
                if not trained_at_str:
                    trained_at = timezone.now()
                else:
                    try:
                        trained_at = timezone.datetime.fromisoformat(trained_at_str)
                        if timezone.is_naive(trained_at):
                            trained_at = timezone.make_aware(trained_at)
                    except Exception:
                        trained_at = timezone.now()
                
                MLModel.objects.update_or_create(
                    name=meta.get('model_name', mname),
                    version=meta.get('version', '1.0.0'),
                    defaults={
                        'model_type': mtype,
                        'description': f"Algorithm: {meta.get('algorithm', 'Scikit-Learn')}",
                        'accuracy': float(acc) if acc is not None else 0.90,
                        'f1_score': float(meta.get('f1_score')) if meta.get('f1_score') else None,
                        'is_active': True,
                        'trained_at': trained_at,
                    }
                )
            except Exception as ex:
                print(f"[MLRegistry] Error registering model {mtype}: {ex}")
        else:
            # Create a fallback placeholder model in database so that exists() becomes True
            # and we don't hit the disk / retry registering on every request
            try:
                MLModel.objects.get_or_create(
                    model_type=mtype,
                    defaults={
                        'name': mname,
                        'version': '1.0.0-fallback',
                        'description': 'Placeholder model using default heuristics (model file not found)',
                        'accuracy': 0.90,
                        'is_active': True,
                        'trained_at': timezone.now()
                    }
                )
            except Exception as ex:
                print(f"[MLRegistry] Error registering fallback model {mtype}: {ex}")

def get_active_model(model_type):
    """Retrieve active model of a type, registering models lazily if needed."""
    # Ensure models are registered if none exist in the database for this model_type
    if not MLModel.objects.filter(model_type=model_type).exists():
        register_models_in_db()
    return MLModel.objects.filter(model_type=model_type, is_active=True).first()
