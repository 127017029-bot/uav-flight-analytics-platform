"""ML app configuration."""
from django.apps import AppConfig


class MlConfig(AppConfig):
    """Configuration for the machine learning application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ml'
    verbose_name = 'Machine Learning'

    def ready(self):
        # Import predictor inside ready to avoid early loading problems
        import sys
        # Avoid loading models during migrations or shell commands
        if 'manage.py' in sys.argv and any(cmd in sys.argv for cmd in ['migrate', 'makemigrations', 'collectstatic', 'createsuperuser']):
            return

        import threading

        def load_and_register_async():
            try:
                from .predictor import MLPredictor
                MLPredictor.load_models()
                
                # Register trained models in DB
                from .models import MLModel
                from django.utils import timezone
                import json
                import os
                from django.conf import settings
                
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
                            print(f"[MlConfig] Error registering model {mtype}: {ex}")
            except Exception as thread_ex:
                print(f"[MlConfig] Background loader failed: {thread_ex}")

        threading.Thread(target=load_and_register_async, daemon=True).start()
