# UAV Digital Twin & Predictive Maintenance Platform

A full-stack, low-latency telemetry streaming and predictive maintenance platform for UAV fleets. This system integrates real-time WebSockets, WebGL-based 3D digital twin rendering, interactive geospatial flight planning, and multiple machine learning models (degradation regression, anomaly isolation, and wear classification) into a unified dashboard.

---

## Technical Stack & Systems Architecture

```
                                  [ UAV Telemetry Source ]
                                             │
                                     (10Hz WebSockets)
                                             │
                                             ▼
                                   [ Nginx Reverse Proxy ]
                                   /                     \
                      (HTTP API)  /                       \  (WS /ws/)
                                 ▼                         ▼
                           [ Django WSGI ]           [ Channels ASGI ]
                           (Gunicorn Web)            (Uvicorn Stream)
                                 │                          │
                                 +───────────┬──────────────+
                                             │
                                             ▼
                                     [ Redis Broker ] <────> [ Celery Workers ]
                                             │               (Retrains & Scans)
                                             ▼
                              [ PostgreSQL + TimescaleDB ]
```

* **Backend (Django Rest Framework & Channels)**: Handles REST API endpoints, real-time ASGI routing, and WebSockets telemetry broadcast (10Hz) via Redis channel layers.
* **Frontend (React, Vite, Zustand)**: Built with dynamic components, featuring real-time charting via Recharts and global state synchronization.
* **3D Digital Twin Viewport (React Three Fiber & Drei)**: Renders a 3D drone mesh inside a WebGL Canvas. The model rotates dynamically using Euler angles (roll, pitch, yaw) streamed via WebSockets, and overlays component-level health status in real-time.
* **Geospatial Mission Planner (React-Leaflet)**: Plots waypoints interactively on dark cartographic tiles, displaying home base anchors, circular geofence boundaries, and polyline flight paths.
* **Data Layer (PostgreSQL + TimescaleDB)**: Partitioned using hypertables to handle high-frequency telemetry streams. Includes automated data retention (90 days) and chunk compression policies to optimize storage footprint.
* **Observability (Prometheus Metrics Exporter)**: Custom `/metrics` exporter exposing fleet-wide telemetry, ML prediction frequencies, system alerts, and critical anomalies for Grafana visualization.

---

## Machine Learning Inferences & MLOps

The platform serves four predictive models. Inference weights are loaded and cached in memory at Django startup, routing execution dynamically through the **ONNX Runtime** engine for optimized C++ graph execution if `.onnx` binaries are available:

1. **Battery Remaining Useful Life (RUL)**: Gradient Boosting Regressor predicting remaining cycles before degradation capacity drops below safety threshold (Test $R^2$: `0.996`).
2. **Motor Vibration Anomaly Detection**: Isolation Forest classifier isolating bearing faults, prop imbalance, or structural vibrations from high-frequency telemetry inputs (AUC-ROC: `0.960`).
3. **Pre-flight Mission Risk Scorer**: Gradient Boosting Regressor scoring flight safety (0-100) based on weather factors, payload ratio, waypoint count, and historical drone airworthiness metrics (Test $R^2$: `0.910`).
4. **Predictive Maintenance Urgency**: Random Forest Classifier evaluating component wear into low/medium/high/critical categories, automatically setting drone status to `maintenance` and logging system alerts (Weighted F1: `0.956`).

---

## Getting Started

### 1. Backend Setup (SQLite / PostgreSQL)
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Activate your virtual environment and install requirements:
   ```bash
   .venv\Scripts\activate      # On Windows
   source .venv/bin/activate   # On macOS/Linux
   pip install -r requirements.txt
   ```
3. Initialize Pre-trained Model Weights:
   ```bash
   python ml/download_models.py
   ```
4. Run database migrations:
   ```bash
   python manage.py migrate
   ```
5. Seed mock fleet data:
   ```bash
   python manage.py seed_data
   ```
6. Start the development server (ASGI):
   ```bash
   python manage.py runserver
   ```

### 2. Frontend Setup (React / Vite)
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install node modules and start Vite:
   ```bash
   npm install
   npm run dev
   ```
   *The frontend dashboard will run at `http://localhost:5173/`.*

### 3. Asynchronous Workers (Celery & Redis)
Ensure Redis is running locally on port `6379`, then start the worker processes:
```bash
# Terminal 1: Start tasks worker
celery -A config worker --loglevel=info

# Terminal 2: Start scheduler beat
celery -A config beat --loglevel=info
```

---

## Database Optimization

To configure the telemetry table for production-scale write loads, execute the following SQL script on your PostgreSQL instance:
```bash
psql -h <db_host> -U <db_user> -d <db_name> -f migrate_timescaledb.sql
```
This migrates the telemetry storage to a **TimescaleDB hypertable**, enabling automatic 7-day chunk partitioning, segmenting compression by `flight_id` (compressing records older than 14 days), and dropping chunks older than 90 days.