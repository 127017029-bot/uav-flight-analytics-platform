# AI-Powered UAV Digital Twin & Predictive Maintenance Platform
## Setup, Execution, and Deployment Manual

This document details how to run the full-stack system locally in development and how to deploy it in production.

---

## 1. Running the Project Locally (Development)

Open a terminal (e.g., PowerShell on Windows or Bash on Linux/macOS) in the project root directory: `c:\Users\riswa\uav-analytics`.

### A. Start the Backend Server (Django ASGI)
1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```
2. **Activate the Virtual Environment**:
   - On Windows:
     ```powershell
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
3. **Run Database Migrations** (SQLite is used in development):
   ```bash
   python manage.py migrate --settings=config.settings.local
   ```
4. **Start the Development Server** (Runs on `http://127.0.0.1:8000/`):
   ```bash
   python manage.py runserver --settings=config.settings.local
   ```

### B. Start Celery Workers & Beat (For Background ML Tasks)
Open a new terminal window in `c:\Users\riswa\uav-analytics\backend` with active virtual environment:
1. **Run Celery Worker**:
   ```bash
   celery -A config worker --loglevel=info
   ```
2. **Run Celery Beat (Periodic scheduler)** (Open a 3rd terminal):
   ```bash
   celery -A config beat --loglevel=info
   ```
*Note: Make sure Redis is running locally on port `6379` as it acts as the Celery broker and Channels layer.*

### C. Start the Frontend (Vite + React)
Open a new terminal window in the project root `c:\Users\riswa\uav-analytics`:
1. **Navigate to the frontend folder**:
   ```bash
   cd frontend
   ```
2. **Install Dependencies** (if not already done):
   ```bash
   npm install
   ```
3. **Start the Dev Server** (Runs on `http://localhost:5173/`):
   ```bash
   npm run dev
   ```

---

## 2. Re-Running the ML Training Pipeline

If you want to re-train the models using the generated synthetic datasets:
1. Open terminal in the project root:
   ```bash
   cd backend
   .venv\Scripts\activate
   ```
2. **Re-run the training pipeline**:
   ```bash
   python ml/data/generate_battery_data.py --output ml/data
   python ml/training/train_battery_rul.py --data ml/data/battery_degradation.csv --output ml/models
   python ml/training/train_motor_anomaly.py --output ml/models
   python ml/training/train_mission_risk.py --output ml/models
   python ml/training/train_maintenance.py --output ml/models
   python ml/export_onnx.py
   ```
*Note: Django will automatically reload the new weights at startup.*

---

## 3. Production Deployment Architecture

In a production environment, the platform operates on PostgreSQL/TimescaleDB and requires a reliable ASGI web server to handle real-time WebSockets.

### A. Database Migration (TimescaleDB)
1. Provision a PostgreSQL instance.
2. Run database migrations using:
   ```bash
   python manage.py migrate --settings=config.settings.production
   ```
3. Apply TimescaleDB partitioning constraints to speed up high-frequency telemetry lookups:
   ```bash
   psql -h <db_host> -U <db_user> -d <db_name> -f migrate_timescaledb.sql
   ```

### B. Deployment with Docker-Compose (Recommended)
You can deploy the backend, database, Redis, Celery, and frontend using containers. A sample production stack:

#### 1. Backend (Django ASGI + Uvicorn)
Use **Uvicorn** with gunicorn workers to handle WS/HTTP streams:
```bash
gunicorn config.asgi:application -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 2. Frontend (Nginx)
Compile static assets and serve via Nginx:
```bash
cd frontend
npm run build
```
Point Nginx server block to serve the resulting `dist/` directory, proxying `/api` and `/ws` connections to the Backend ASGI container.

#### 3. Prometheus Monitoring Scrapers
Add the scraper job in `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'uav-digital-twin-backend'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['backend-service-ip:8000']
```
Exposed gauges and counters (active drones, cumulative inferences, critical warnings) will stream in real-time to your Grafana analytics dashboards.
