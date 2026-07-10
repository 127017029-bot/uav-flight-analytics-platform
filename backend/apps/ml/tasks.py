from celery import shared_task
import os
import subprocess
from django.conf import settings

@shared_task
def retrain_models():
    """Retrain all machine learning models weekly."""
    print("[Celery ML] Starting weekly ML models retraining...")
    project_root = settings.BASE_DIR.parent
    python_exe = os.path.join(settings.BASE_DIR, '.venv', 'Scripts', 'python')
    if not os.path.exists(python_exe):
        python_exe = 'python'

    scripts = [
        ('ml/data/generate_battery_data.py', ['--output', 'ml/data']),
        ('ml/training/train_battery_rul.py', ['--data', 'ml/data/battery_degradation.csv', '--output', 'ml/models']),
        ('ml/training/train_motor_anomaly.py', ['--output', 'ml/models']),
        ('ml/training/train_mission_risk.py', ['--output', 'ml/models']),
        ('ml/training/train_maintenance.py', ['--output', 'ml/models']),
    ]

    for script, args in scripts:
        script_path = os.path.join(project_root, script)
        if os.path.exists(script_path):
            print(f"[Celery ML] Running retraining script: {script}")
            try:
                cmd = [python_exe, script_path] + args
                res = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
                if res.returncode == 0:
                    print(f"[Celery ML] Finished {script} successfully.")
                else:
                    print(f"[Celery ML] Retraining failed for {script}: {res.stderr}")
            except Exception as e:
                print(f"[Celery ML] Error executing {script}: {e}")
        else:
            print(f"[Celery ML] Retraining script not found: {script_path}")
