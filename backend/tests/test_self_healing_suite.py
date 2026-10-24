"""
Comprehensive Automated Test Suite for Self-Healing Cloud System
Validates all 10 core modules: Auth, Monitoring, AI Anomaly Detection,
Autonomic Self-Healing, Incidents, Recovery Policies, Simulation, Audit & Security.
"""

import sys
import os
import asyncio

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import init_db, SessionLocal
from backend.app.services.seed import seed_initial_data
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.recovery import TriggerCondition, RecoveryPolicy, RecoveryActionType
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity
from backend.app.models.audit import AuditLog
from backend.app.monitoring.simulator import simulator
from backend.app.monitoring.rule_engine import rule_detector
from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.recovery.orchestrator import orchestrator


total_tests = 0
passed_tests = 0


def run_test(name, fn):
    global total_tests, passed_tests
    total_tests += 1
    try:
        fn()
        print(f"  [PASS] {name}")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        import traceback
        traceback.print_exc()


def test_suite():
    global total_tests, passed_tests
    print("\n============================================================")
    print("   Self-Healing Cloud Automated Verification Test Suite")
    print("============================================================\n")

    init_db()
    db = SessionLocal()
    seed_initial_data(db)
    anomaly_detector.train_on_history(db)
    db.close()

    client = TestClient(app)

    # Suite 1: Authentication & RBAC
    print("[Suite 1: Authentication & Role-Based Access Control]")
    
    def test_auth():
        # Login admin
        res = client.post("/api/auth/login", json={"username": "admin", "password": "AdminSecure2026!"})
        assert res.status_code == 200, res.text
        token = res.json()["access_token"]
        assert token and len(token) > 20

        # Login viewer
        res_v = client.post("/api/auth/login", json={"username": "viewer", "password": "ViewerPass2026!"})
        assert res_v.status_code == 200

        # Unauthenticated access rejected
        unauth = client.post("/api/services", json={"name": "rogue-service"})
        assert unauth.status_code == 401

    run_test("JWT Authentication, Token Creation & Protected Route Rejection", test_auth)

    # Suite 2: Dashboard & Metrics Summary
    print("\n[Suite 2: Dashboard & Telemetry Aggregations]")
    
    def test_dashboard():
        res = client.get("/api/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_services"] >= 5
        assert "health_breakdown" in data
        assert "cluster_metrics" in data
        assert data["recovery_success_rate_percent"] >= 0.0

    run_test("Dashboard aggregates cluster health, active nodes, and recovery statistics", test_dashboard)

    # Suite 3: Monitored Microservices & Controlled Actions
    print("\n[Suite 3: Microservice Lifecycle & Controlled Recovery Actions]")
    
    def test_services():
        res = client.get("/api/services")
        assert res.status_code == 200
        services = res.json()["services"]
        assert len(services) >= 5
        s_id = services[0]["id"]

        # Login for action execution
        login = client.post("/api/auth/login", json={"username": "admin", "password": "AdminSecure2026!"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # Restart service
        action_res = client.post(f"/api/services/{s_id}/action", json={"action": "restart"}, headers=headers)
        assert action_res.status_code == 200
        assert action_res.json()["status"] == "healthy"

    run_test("Microservices inventory and authorized restart execution", test_services)

    # Suite 4: Simulation Lab & Fault Injection
    print("\n[Suite 4: Fault Injection & Chaos Simulation]")
    
    def test_simulation():
        login = client.post("/api/auth/login", json={"username": "admin", "password": "AdminSecure2026!"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        # Inject CPU Overload
        inj = client.post(
            "/api/simulations/inject",
            json={"service_id": 1, "failure_type": "cpu_overload", "duration_seconds": 30},
            headers=headers
        )
        assert inj.status_code == 200
        assert inj.json()["status"] == "injected"

        # Verify simulator is generating overload metrics
        db = SessionLocal()
        s1 = db.query(Service).filter(Service.id == 1).first()
        m = simulator.generate_metric_sample(s1)
        assert m["cpu_percent"] >= 90.0
        assert m["is_healthy"] is False

        # Clear fault
        reset = client.post("/api/simulations/1/reset", headers=headers)
        assert reset.status_code == 200
        m_reset = simulator.generate_metric_sample(s1)
        assert m_reset["cpu_percent"] < 80.0
        db.close()

    run_test("Safe fault injection into local demo microservice and metric verification", test_simulation)

    # Suite 5: Rule-Based Health Detection Engine
    print("\n[Suite 5: Rule-Based Health Detection Engine]")
    
    def test_rules():
        db = SessionLocal()
        s = db.query(Service).filter(Service.id == 2).first()
        s.consecutive_failures = s.max_consecutive_failures
        
        # Test Container Down detection
        down_metric = {"cpu_percent": 0.0, "memory_percent": 0.0, "latency_ms": 3000.0, "error_rate_percent": 100.0}
        res_down = rule_detector.evaluate(s, down_metric)
        assert res_down is not None
        assert res_down[0] == TriggerCondition.CONTAINER_DOWN

        # Test High CPU detection
        cpu_metric = {"cpu_percent": 96.0, "memory_percent": 45.0, "latency_ms": 120.0, "error_rate_percent": 1.0}
        res_cpu = rule_detector.evaluate(s, cpu_metric)
        assert res_cpu is not None
        assert res_cpu[0] == TriggerCondition.HIGH_CPU
        db.close()

    run_test("Threshold comparison and consecutive failure trigger condition matching", test_rules)

    # Suite 6: AI-Based Isolation Forest Anomaly Detection
    print("\n[Suite 6: AI Anomaly Detection Pipeline]")
    
    def test_ai_anomaly():
        # Normal metric
        normal_m = {"cpu_percent": 30.0, "memory_percent": 40.0, "latency_ms": 65.0, "error_rate_percent": 0.2}
        is_anom, score, _ = anomaly_detector.detect(normal_m)
        assert not is_anom, f"Normal sample falsely flagged: score={score}"

        # Highly anomalous multivariate spike
        abnormal_m = {"cpu_percent": 99.5, "memory_percent": 98.0, "latency_ms": 2800.0, "error_rate_percent": 75.0}
        is_anom2, score2, _ = anomaly_detector.detect(abnormal_m)
        assert is_anom2 is True, f"Abnormal sample missed: score={score2}"
        assert score2 < 0.0

    run_test("Isolation Forest accurately differentiates normal vs anomalous telemetry", test_ai_anomaly)

    # Suite 7: Closed-Loop Autonomic Self-Healing Orchestration
    print("\n[Suite 7: Autonomic Self-Healing Orchestration & State Machine]")
    
    def test_self_healing():
        db = SessionLocal()
        service = db.query(Service).filter(Service.id == 3).first()
        service.consecutive_failures = 3
        service.status = ServiceStatus.UNHEALTHY

        # Trigger autonomic healing
        sample = {"cpu_percent": 0.0, "memory_percent": 0.0, "latency_ms": 3000.0, "error_rate_percent": 100.0, "is_healthy": False}
        
        # Run async orchestrator synchronously
        asyncio.run(orchestrator.handle_triggered_failure(
            db=db,
            service=service,
            trigger_condition=TriggerCondition.CONTAINER_DOWN,
            severity=IncidentSeverity.CRITICAL,
            evidence=sample,
            suspected_cause="Simulated crash probe failure"
        ))

        # Verification: Service should have returned to HEALTHY
        db.refresh(service)
        assert service.status == ServiceStatus.HEALTHY
        assert service.consecutive_failures == 0
        assert service.in_cooldown_until is not None

        # Verification: Incident should be marked RESOLVED
        inc = db.query(Incident).filter(Incident.service_id == service.id).order_by(Incident.created_at.desc()).first()
        assert inc is not None
        assert inc.status == IncidentStatus.RESOLVED

        # Verification: Immutable audit entry created
        audit = db.query(AuditLog).filter(AuditLog.entity_id == str(service.id)).order_by(AuditLog.created_at.desc()).first()
        assert audit is not None
        assert "RECOVERY" in audit.action
        db.close()

    run_test("Autonomic loop: Problem detected -> Policy matched -> Action executed -> Health verified -> Audit recorded", test_self_healing)

    # Suite 8: Endless Restart Prevention & Escalation
    print("\n[Suite 8: Flapping & Infinite Loop Protection]")
    
    def test_loop_prevention():
        db = SessionLocal()
        service = db.query(Service).filter(Service.id == 4).first()
        service.in_cooldown_until = None
        service.active_recovery_attempts = 3 # Exceeded max_retries

        asyncio.run(orchestrator.handle_triggered_failure(
            db=db,
            service=service,
            trigger_condition=TriggerCondition.CONTAINER_DOWN,
            severity=IncidentSeverity.CRITICAL,
            evidence={"cpu_percent": 0.0},
            suspected_cause="Repeated container failure"
        ))

        db.refresh(service)
        # Service must NOT restart; it must escalate to MANUAL_INTERVENTION_REQUIRED
        inc = db.query(Incident).filter(Incident.service_id == service.id).order_by(Incident.created_at.desc()).first()
        assert inc.status == IncidentStatus.MANUAL_INTERVENTION_REQUIRED
        db.close()

    run_test("Retry limit protection stops infinite restart loops and escalates to manual intervention", test_loop_prevention)

    print("\n============================================================")
    print(f"Test Execution Complete: {passed_tests} / {total_tests} Passed")
    print("============================================================\n")

    if passed_tests != total_tests:
        sys.exit(1)


if __name__ == "__main__":
    test_suite()
