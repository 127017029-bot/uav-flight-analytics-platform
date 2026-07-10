import os
import urllib.request
import zipfile
import sys

def download_progress(block_num, block_size, total_size):
    """Draws a professional CLI progress bar for file downloads."""
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100, int(downloaded * 100 / total_size))
        bar_length = 40
        filled_length = int(bar_length * percent / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[MLOps] Downloading model weights: |{bar}| {percent}% ({downloaded / (1024*1024):.1f} MB)")
        sys.stdout.flush()

def main():
    print("============================================================")
    print("  Pretrained ML Models Initialization Utility")
    print("============================================================")
    
    # 1. Define paths and target URLs
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(project_root, 'ml', 'models')
    zip_path = os.path.join(models_dir, 'models.zip')
    
    # Target release asset URL on GitHub
    repo_url = "https://github.com/127017029-bot/uav-flight-analytics-platform"
    release_tag = "v1.0.0"
    download_url = f"{repo_url}/releases/download/{release_tag}/models.zip"
    
    # 2. Ensure destination directories exist
    os.makedirs(models_dir, exist_ok=True)
    
    # 3. Download the zipped weights archive
    print(f"[MLOps] Target Release: {release_tag}")
    print(f"[MLOps] Remote URL: {download_url}")
    print("[MLOps] Executing network fetch...")
    
    try:
        urllib.request.urlretrieve(download_url, zip_path, download_progress)
        print("\n[MLOps] Download completed successfully.")
    except Exception as e:
        print(f"\n[ERROR] Failed to download model archive: {e}")
        print("[ERROR] Please verify your internet connection or check if the release asset exists.")
        sys.exit(1)
        
    # 4. Extract archive
    print(f"[MLOps] Extracting files to: {models_dir}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        print("[MLOps] Extraction complete.")
    except Exception as e:
        print(f"[ERROR] Failed to extract weights archive: {e}")
        sys.exit(1)
        
    # 5. Clean up zip file
    try:
        os.remove(zip_path)
    except OSError:
        pass
        
    # 6. Verify outputs
    required_files = [
        'battery_rul_model.pkl', 'battery_rul_model.onnx',
        'motor_anomaly_model.pkl', 'motor_anomaly_model.onnx',
        'mission_risk_model.pkl', 'mission_risk_model.onnx',
        'maintenance_model.pkl', 'maintenance_model.onnx'
    ]
    
    missing = []
    for f in required_files:
        path = os.path.join(models_dir, f)
        if not os.path.exists(path):
            missing.append(f)
            
    if missing:
        print(f"[WARNING] Verification failed. Missing models: {missing}")
    else:
        print("[SUCCESS] All model weights verified. Platform is ready for inference.")

if __name__ == '__main__':
    main()
