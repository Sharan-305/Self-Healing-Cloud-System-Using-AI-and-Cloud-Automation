# Self-Healing Cloud System Using AI and Cloud Automation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Isolation%20Forest-F7931E.svg?logo=scikit-learn)](https://scikit-learn.org)

An autonomic closed-loop cloud operations platform that continuously monitors cloud microservices, detects anomalies and operational failures, matches pre-configured recovery policies, and safely executes autonomous remediation with before-and-after health verification, anti-flapping protection, and an immutable audit trail.

---

## 1. System Architecture

```mermaid
flowchart TD
    subgraph UI ["Layer 1: Presentation & Real-Time Operations"]
        FE["React + Vite + TypeScript Dashboard"]
        WS["WebSocket Telemetry & Alerts Channel"]
        SimLab["Simulation Lab (Fault Injector)"]
    end

    subgraph API ["Layer 2: API & Gateway Layer (FastAPI)"]
        Auth["JWT Auth & Role-Based Access (Admin/Viewer)"]
        REST["REST API Endpoints (/api/...)"]
        WSManager["WebSocket Connection Manager"]
    end

    subgraph Engine ["Layer 3: Monitoring & Decision Engines"]
        Collector["Health Monitoring Engine (Periodic Poller)"]
        ML["AI Anomaly Detection (Isolation Forest)"]
        RuleBase["Rule-Based Threshold Validator"]
        Orchestrator["Self-Healing Orchestrator (State Machine)"]
    end

    subgraph Adapters ["Layer 4: Cloud & Service Adapters"]
        LocalAdapter["Local Process & Simulated Container Adapter"]
        DockerAdapter["Docker Engine Adapter (docker-py)"]
        CloudAdapter["Cloud Adapter Interface (AWS / Azure)"]
    end

    subgraph Storage ["Layer 5: Data & Telemetry"]
        PG[("PostgreSQL / SQLite Database")]
        Prom["Prometheus Telemetry Scraper"]
        Graf["Grafana Dashboard Visualizer"]
        Audit[("Immutable Audit Trail")]
    end

    FE <-->|REST & WebSocket| API
    API --> Engine
    Collector -->|Collects CPU, Mem, Latency, Errors| Adapters
    Collector -->|Telemetry Samples| PG
    Collector -->|Feature Vector| ML
    Collector -->|Consecutive Failures| RuleBase
    ML -->|Anomaly Score & Evidence| Orchestrator
    RuleBase -->|Trigger Signals| Orchestrator
    Orchestrator -->|Match Policy & Validate Cooldown| PG
    Orchestrator -->|Execute Recovery (Restart, Scale, Cache Purge)| Adapters
    Orchestrator -->|Record Audit & Update Incident| Audit
    Orchestrator -->|Broadcast Event| WSManager
    WSManager --> WS
    Prom -->|Scrape /metrics| API
    Graf -->|Query| Prom
```

---

## 2. Key Features

1. **Continuous Real-Time Telemetry & WebSocket Streams:**
   - Background poller sampling CPU, Memory, Latency, Error Rate, and Request Count every 5 seconds.
   - Live WebSocket channel (`/ws/monitoring`) streaming immediate telemetry updates without page refresh.

2. **Rule-Based Health & Consecutive Failure Checks:**
   - Multi-check anti-flapping barrier: Requires consecutive threshold breaches (`consecutive_failures >= max_consecutive_failures`) to prevent transient spikes from triggering unintended restarts.
   - Condition triggers: `CONTAINER_DOWN`, `HIGH_CPU`, `HIGH_MEMORY`, `HIGH_LATENCY`, `REPEATED_5XX`.

3. **AI Anomaly Detection Pipeline (Isolation Forest):**
   - Multidimensional vector scaling with Scikit-learn's `StandardScaler` and `IsolationForest`.
   - Returns continuous anomaly decision score with clear threshold boundaries.
   - Differentiates statistical anomaly alerts from confirmed system failures.

4. **Autonomic Self-Healing Orchestration (State Machine):**
   - 9-Step Autonomic Cycle:
     1. Detect failure or anomaly.
     2. Validate consecutive failure count.
     3. Identify affected service.
     4. Match active recovery policy.
     5. Safety guard checks: Cooldown validation (`in_cooldown_until`) and retry limit guard (`active_recovery_attempts < max_retries`).
     6. Execute remediation action (`restart`, `scale_up`, `clear_cache`, `drain_and_recreate`).
     7. Post-health verification check.
     8. Record immutable audit log entry.
     9. Broadcast success/failure notification to dashboard.
   - **Anti-Flapping Protection:** If retries exceed limit (e.g. 3 attempts), auto-recovery immediately halts and escalates the incident to `MANUAL_INTERVENTION_REQUIRED`.

5. **Simulation & Chaos Engineering Lab:**
   - In-app sandbox allowing operators to inject deterministic failures:
     - `CPU Overload (95%+)`
     - `Memory Pressure (95%+)`
     - `High Latency (1200ms+)`
     - `HTTP 500 Failure Storm (60%+)`
     - `Dead Container Crash (SIGKILL / 0% CPU)`
   - Safe observation: Telemetry reflects injected failure, triggers self-healing, restores healthy baseline, and clears active fault.

6. **Enterprise Security & Audit Trail:**
   - BCrypt password hashing and JWT token authentication.
   - Role-Based Access Control (`admin` vs `viewer`).
   - Append-only `AuditLog` recording every recovery decision, manual operator intervention, and policy adjustment.

---

## 3. Project Structure

```
F:\Projects\Pro9-CC\
├── backend/
│   ├── app/
│   │   ├── api/                     # REST endpoints & WebSockets
│   │   │   ├── auth.py              # Login, register, me
│   │   │   ├── dashboard.py         # Cluster summary & health breakdown
│   │   │   ├── services.py          # Service management & controlled actions
│   │   │   ├── incidents.py         # Incident list & resolution
│   │   │   ├── recovery.py          # Policies & execution history
│   │   │   ├── simulations.py       # Fault injection lab
│   │   │   ├── anomalies.py         # AI Anomaly endpoints & retrain trigger
│   │   │   ├── audit.py             # Immutable audit trail
│   │   │   └── websocket.py         # Real-time WebSocket connection manager
│   │   ├── models/                  # SQLAlchemy ORM models (All 9 models)
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── services/                # Business logic & initial seed generator
│   │   ├── monitoring/              # Telemetry collector, rule engine & container adapter
│   │   ├── ml/                      # Isolation Forest anomaly detection pipeline
│   │   ├── recovery/                # Autonomic self-healing orchestrator
│   │   ├── security/                # BCrypt password hashing & JWT tokens
│   │   ├── config.py                # Pydantic settings & environment configuration
│   │   ├── database.py              # Engine, SessionLocal & init_db
│   │   └── main.py                  # FastAPI application entry point
│   ├── tests/
│   │   ├── test_self_healing_suite.py # 8-suite automated verification tests
│   │   ├── test_api_endpoints.py    # REST API endpoints verification
│   │   └── verify_models.py         # Database models validation
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, Sidebar, MetricCard, LiveClusterChart, ServiceCard, SimulationModal, AuthModal
│   │   ├── services/                # API client & WebSocket listener
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── App.tsx                  # Main dashboard application shell
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── package.json
├── infrastructure/
│   ├── prometheus/prometheus.yml
│   └── grafana/provisioning/datasources/prometheus.yml
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 4. Quick Start (Local Development)

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ & npm
- PostgreSQL (or automatic local SQLite fallback)

### Step 1: Backend Setup
```bash
cd F:\Projects\Pro9-CC

# Install Python requirements (if not already installed)
python -m pip install -r backend/requirements.txt

# Run the complete automated test suite
python backend/tests/test_self_healing_suite.py
```

### Step 2: Start Backend Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Documentation (Swagger / OpenAPI): [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

### Step 3: Start Frontend Dashboard
In a second terminal window:
```bash
cd F:\Projects\Pro9-CC\frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 5. Seed Accounts & Credentials

The system automatically initializes baseline operator accounts on first launch:

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `AdminSecure2026!` | Full administrative controls, fault injection, manual restarts, policy edits |
| **Viewer** | `viewer` | `ViewerPass2026!` | Read-only access to dashboard telemetry, metrics, and incident history |

---

## 6. End-to-End Failure & Self-Healing Walkthrough

To verify autonomic self-healing in action:

1. Log in as `admin` on the dashboard.
2. Navigate to **Simulation Lab** or click **Simulate Failure** in the top navigation bar.
3. Select target: `payment-service`.
4. Choose fault pattern: `CPU Overload (95%+)` or `Dead Container Crash`.
5. Click **Inject Fault Now**.
6. **Watch the Dashboard in Real Time:**
   - Telemetry graph immediately spikes in CPU utilization (>95%) or latency (>1200ms).
   - Consecutive failure counter on the service card increments: `1 / 3` &rarr; `2 / 3` &rarr; `3 / 3`.
   - Status badge transitions from `Healthy` &rarr; `Degraded` / `Unhealthy`.
   - Active Incident is created: *"Autonomic Incident: payment-service [HIGH_CPU]"*.
   - Self-Healing Orchestrator kicks in: Service badge pulses cyan `Auto-Healing`.
   - Matching policy triggers (`scale_up` or `restart`).
   - Container process cycles and clears memory/compute locks.
   - Post-health verification confirms service is restored to `Healthy`.
   - Incident automatically marked `RESOLVED`.
   - Immutable entry written to **Audit Trail**.

---

## 7. Docker Compose Stack

To deploy the entire stack in containers (PostgreSQL, FastAPI Backend, React Frontend, Prometheus, Grafana):

```bash
cd F:\Projects\Pro9-CC
docker compose up -d --build
```
- Frontend Dashboard: [http://localhost:3000](http://localhost:3000)
- Backend API & Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Prometheus Scraper: [http://localhost:9090](http://localhost:9090)
- Grafana: [http://localhost:3001](http://localhost:3001) (admin/admin)
