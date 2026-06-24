<div align="center">

# 🛩️ AI-Powered UAV Digital Twin & Predictive Maintenance Platform

### Enterprise-Grade Fleet Management, Real-Time Analytics, and AI-Driven Maintenance

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-F7931E?logo=scikitlearn)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 Overview

A **production-grade full-stack platform** for UAV fleet management, real-time telemetry analytics, and AI-driven predictive maintenance. The system ingests high-frequency drone telemetry data via WebSockets, runs 5 machine learning models for battery life prediction, motor anomaly detection, and mission risk assessment, and visualizes drone state through an interactive 3D digital twin.

**Key differentiators**: Physics-based telemetry simulation, LSTM battery RUL prediction, Isolation Forest motor anomaly detection, and real-time WebSocket telemetry streaming at 10Hz.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React 19 + Vite 8)                                         │
│  Recharts │ Three.js │ Leaflet │ Zustand │ WebSocket Client            │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP REST / WebSocket (WSS)
┌────────────────────────────────┼────────────────────────────────────────┐
│  BACKEND (Django 6.0 + DRF + Channels)                                 │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────────────┐     │
│  │  REST API     │  │  WebSocket      │  │  Celery Workers        │     │
│  │  50+ endpoints│  │  Consumers      │  │  Async ML + Analytics  │     │
│  └──────┬───────┘  └────────┬────────┘  └───────────┬────────────┘     │
│         │                   │                       │                   │
│  ┌──────┴───────────────────┴───────────────────────┴──────────────┐   │
│  │  PostgreSQL 16  │  Redis 7 (Broker/Cache)  │  ML Model Store    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  ML LAYER: Battery RUL (GBR/LSTM) │ Motor Anomaly (IForest)     │  │
│  │  Mission Risk (XGBoost) │ Predictive Maintenance (Random Forest) │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Fleet Management
- 🚁 Complete drone CRUD with health tracking
- 📊 Fleet-wide KPI dashboard
- 🔋 Battery electrochemical profiling
- ⚙️ Component-level health monitoring (12 components per drone)

### Real-Time Telemetry
- 📡 WebSocket-based live telemetry streaming at 10-50Hz
- 📈 Real-time Recharts visualizations (altitude, speed, battery, attitude)
- 🌍 Live GPS tracking on interactive Leaflet maps
- 🎯 30+ telemetry parameters per packet

### AI/ML Intelligence
- 🔮 **Battery RUL Prediction** — Gradient Boosting/LSTM model predicting remaining charge cycles
- ⚠️ **Motor Anomaly Detection** — Isolation Forest detecting bearing wear, imbalance, overheating
- 🎯 **Mission Risk Scoring** — XGBoost model scoring missions 0-100 based on 15 factors
- 🔧 **Predictive Maintenance** — Random Forest classifying urgency (low/medium/high/critical)
- 🧠 AI-powered alert generation with confidence scores

### Digital Twin
- 🎮 3D quadcopter model with React Three Fiber
- 🔄 Real-time attitude synchronization (roll/pitch/yaw)
- 🎨 Component health color overlay on 3D model
- 📹 Flight path 3D replay

### Mission Planning
- 🗺️ Interactive mission planner with waypoint editor
- 📍 Multiple mission profiles (survey, inspection, delivery)
- ⚡ Pre-flight risk assessment with AI recommendations
- 🛡️ Geofence visualization

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Django 6.0 + DRF | REST API, ORM, Auth, Admin |
| Real-Time | Django Channels + Redis | WebSocket telemetry streaming |
| Task Queue | Celery + Redis | Async ML inference, batch analytics |
| Database | PostgreSQL 16 | Relational data, time-series telemetry |
| Cache/Broker | Redis 7 | WebSocket layer, task broker, caching |
| Frontend | React 19 + Vite 8 | SPA with dark aerospace UI |
| Charting | Recharts + D3.js | Interactive real-time visualizations |
| 3D | Three.js + React Three Fiber | Digital twin rendering |
| Maps | Leaflet + React-Leaflet | GPS tracking, mission planning |
| State | Zustand | Lightweight reactive state management |
| ML | scikit-learn + NumPy/SciPy | Model training and inference |
| Container | Docker + Docker Compose | Multi-service deployment |

---

## 📁 Project Structure

```
uav-analytics/
├── backend/                    # Django Backend
│   ├── apps/
│   │   ├── accounts/           # JWT Auth, Users, Pilots
│   │   ├── drones/             # Fleet Management, Component Health
│   │   ├── flights/            # Flight Records, Analytics
│   │   ├── telemetry/          # Telemetry Ingestion, WebSocket
│   │   ├── missions/           # Mission Planning, Waypoints
│   │   ├── maintenance/        # Maintenance Records
│   │   ├── alerts/             # AI Alert Generation
│   │   ├── analytics/          # Fleet Analytics, KPIs
│   │   └── ml/                 # ML Inference Endpoints
│   ├── config/                 # Django Settings (base/dev/prod)
│   ├── core/                   # Shared Utilities
│   ├── simulator/              # Physics-Based Telemetry Simulator
│   └── requirements/           # Dependency Management
├── frontend/                   # React Frontend
│   └── src/
│       ├── api/                # Axios Client, Endpoints
│       ├── components/         # UI Components
│       │   ├── layout/         # Sidebar, TopBar, AppShell
│       │   ├── common/         # KPICard, DataTable, Gauge
│       │   ├── dashboard/      # Dashboard Widgets
│       │   ├── fleet/          # Fleet Management
│       │   ├── telemetry/      # Real-Time Monitoring
│       │   ├── digital-twin/   # 3D Visualization
│       │   └── missions/       # Mission Planning
│       ├── pages/              # Route Pages (9 pages)
│       ├── stores/             # Zustand State Stores
│       └── styles/             # Design System
├── ml/                         # Machine Learning
│   ├── data/                   # Synthetic Data Generators
│   ├── training/               # Training Pipelines (5 models)
│   └── models/                 # Trained Model Artifacts
├── docker-compose.yml          # Dev Environment
└── .github/workflows/          # CI/CD Pipelines
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 22+
- Docker & Docker Compose (recommended)

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/yourusername/uav-analytics.git
cd uav-analytics
docker-compose up --build
```
Access: Frontend → http://localhost:5173 | API → http://localhost:8000/api/

### Option 2: Manual Setup
```bash
# Backend
cd backend
python -m venv .venv && .venv/Scripts/activate  # Windows
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Simulator (new terminal)
cd backend
python -m simulator.engine --profile survey --dry-run
```

### Train ML Models
```bash
cd ml
python data/generate_battery_data.py --batteries 20 --cycles 500
python training/train_battery_rul.py
python training/train_motor_anomaly.py
python training/train_mission_risk.py
python training/train_maintenance.py
```

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/token/` | JWT token obtain |
| POST | `/api/auth/token/refresh/` | JWT token refresh |

### Fleet Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/drones/` | List/Create drones |
| GET/PUT/DELETE | `/api/drones/{id}/` | Drone CRUD |
| GET | `/api/drones/{id}/health/` | Component health |
| GET | `/api/drones/{id}/battery/` | Battery profile |
| GET | `/api/fleet/overview/` | Fleet KPIs |

### Telemetry
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/telemetry/ingest/` | Ingest telemetry point |
| POST | `/api/telemetry/batch/` | Batch ingest |
| GET | `/api/telemetry/latest/{drone_id}/` | Latest telemetry |
| WS | `/ws/telemetry/{drone_id}/` | Live WebSocket stream |

### ML Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ml/predict/battery-rul/` | Battery RUL prediction |
| POST | `/api/ml/predict/motor-anomaly/` | Motor anomaly detection |
| POST | `/api/ml/predict/mission-risk/` | Mission risk scoring |
| POST | `/api/ml/predict/maintenance/` | Maintenance urgency |

---

## 🧠 ML Models

| Model | Algorithm | Dataset | Key Metric |
|-------|-----------|---------|------------|
| Battery RUL | Gradient Boosting | 10,000 cycles × 20 batteries | RMSE ~12 cycles |
| Motor Anomaly | Isolation Forest | 10,500 samples (5% anomalous) | F1 > 0.85 |
| Mission Risk | Gradient Boosting | 10,000 mission profiles | R² > 0.90 |
| Maintenance | Random Forest | 20,000 component records | F1 > 0.80 |

---

## 📊 Telemetry Simulator

Physics-based simulation engine generating realistic UAV telemetry with:
- **Flight profiles**: Survey grid, orbital inspection, delivery, circuit
- **Battery model**: LiPo electrochemical voltage-capacity curves with load-dependent sag
- **Motor model**: BLDC thermal dynamics with RPM response lag
- **Environmental**: Wind gusts (Perlin noise), temperature lapse rate, barometric formula
- **Sensor noise**: GPS (±2m CEP), IMU (±0.3°), barometer (±0.5m)
- **Fault injection**: Motor degradation, GPS drift, battery cell failure, high vibration

```bash
python -m simulator.engine --profile survey --faults --rate 2
```

---

## 🖼️ Screenshots

> Dashboard with fleet KPIs, active flights map, and real-time alerts
> Fleet management with component health monitoring
> Live telemetry with real-time charts and gauges
> 3D Digital Twin with attitude synchronization

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ for Aerospace + AI
</div>