"""
API Integration & Lifecycle Verification Test
"""

import sys
import os

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.services.seed import seed_initial_data

def run_api_tests():
    print("Testing Backend API Startup & Endpoints...")
    init_db()
    db = SessionLocal()
    seed_initial_data(db)
    db.close()

    client = TestClient(app)

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Healthcheck failed: {res.text}"
    assert res.json()["status"] == "healthy"
    print("  [PASS] GET /health: OK")

    # 2. Login with seeded admin
    login_res = client.post("/api/auth/login", json={"username": "admin", "password": "AdminSecure2026!"})
    assert login_res.status_code == 200, f"Admin login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  [PASS] POST /api/auth/login: Authenticated successfully as Admin")

    # 3. GET /api/auth/me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "admin"
    print("  [PASS] GET /api/auth/me: OK")

    # 4. GET /api/dashboard/summary
    dash_res = client.get("/api/dashboard/summary")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_services"] >= 5
    print(f"  [PASS] GET /api/dashboard/summary: Monitored Services = {dash_data['total_services']}")

    # 5. GET /api/services
    services_res = client.get("/api/services")
    assert services_res.status_code == 200
    assert services_res.json()["total"] >= 5
    service_id = services_res.json()["services"][0]["id"]
    print(f"  [PASS] GET /api/services: {services_res.json()['total']} microservices registered")

    # 6. GET /api/recovery/policies
    pol_res = client.get("/api/recovery/policies")
    assert pol_res.status_code == 200
    assert len(pol_res.json()) >= 6
    print(f"  [PASS] GET /api/recovery/policies: {len(pol_res.json())} autonomic policies configured")

    # 7. POST /api/simulations/inject (Test failure injection)
    sim_res = client.post(
        "/api/simulations/inject",
        json={"service_id": service_id, "failure_type": "cpu_overload", "duration_seconds": 30},
        headers=headers
    )
    assert sim_res.status_code == 200
    assert sim_res.json()["status"] == "injected"
    print("  [PASS] POST /api/simulations/inject: Injected CPU overload fault successfully")

    # 8. POST /api/services/{id}/action (Test manual recovery action)
    action_res = client.post(
        f"/api/services/{service_id}/action",
        json={"action": "restart"},
        headers=headers
    )
    assert action_res.status_code == 200
    assert action_res.json()["status"] == "healthy"
    print("  [PASS] POST /api/services/{id}/action: Restart executed and service verified healthy")

    print("\nAll Backend API Endpoints Verified Successfully!")

if __name__ == "__main__":
    run_api_tests()
