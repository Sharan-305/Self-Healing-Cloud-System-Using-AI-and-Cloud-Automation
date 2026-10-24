"""
Initial Seed Data Generator
Populates baseline users, demo cloud microservices, and autonomic recovery policies.
"""

from sqlalchemy.orm import Session
from backend.app.models.user import User, UserRole
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.recovery import RecoveryPolicy, TriggerCondition, RecoveryActionType
from backend.app.security.auth import get_password_hash


def seed_initial_data(db: Session):
    """Ensure baseline users, services, and policies exist in database."""
    
    # 1. Seed Users
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@selfhealing.cloud",
            hashed_password=get_password_hash("AdminSecure2026!"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)

    viewer_user = db.query(User).filter(User.username == "viewer").first()
    if not viewer_user:
        viewer_user = User(
            username="viewer",
            email="viewer@selfhealing.cloud",
            hashed_password=get_password_hash("ViewerPass2026!"),
            role=UserRole.VIEWER,
            is_active=True
        )
        db.add(viewer_user)

    db.commit()

    # 2. Seed Monitored Cloud Services
    default_services = [
        {
            "name": "api-gateway",
            "service_type": "api-gateway",
            "description": "Primary ingress proxy and rate limiter",
            "container_id": "cnt-gateway-01",
            "target_endpoint": "http://localhost:8080/health",
            "cpu_threshold_percent": 80.0,
            "memory_threshold_percent": 85.0,
            "latency_threshold_ms": 300.0,
            "error_rate_threshold_percent": 10.0,
        },
        {
            "name": "auth-service",
            "service_type": "microservice",
            "description": "Identity provider, OAuth2 and JWT token broker",
            "container_id": "cnt-auth-01",
            "target_endpoint": "http://localhost:8081/health",
            "cpu_threshold_percent": 85.0,
            "memory_threshold_percent": 80.0,
            "latency_threshold_ms": 250.0,
            "error_rate_threshold_percent": 8.0,
        },
        {
            "name": "payment-service",
            "service_type": "microservice",
            "description": "Payment transactions and gateway integration",
            "container_id": "cnt-payment-01",
            "target_endpoint": "http://localhost:8082/health",
            "cpu_threshold_percent": 80.0,
            "memory_threshold_percent": 85.0,
            "latency_threshold_ms": 400.0,
            "error_rate_threshold_percent": 5.0,
        },
        {
            "name": "inventory-service",
            "service_type": "microservice",
            "description": "Real-time stock reservation and catalog engine",
            "container_id": "cnt-inventory-01",
            "target_endpoint": "http://localhost:8083/health",
            "cpu_threshold_percent": 85.0,
            "memory_threshold_percent": 85.0,
            "latency_threshold_ms": 450.0,
            "error_rate_threshold_percent": 12.0,
        },
        {
            "name": "notification-worker",
            "service_type": "background-worker",
            "description": "Asynchronous event queues and email delivery worker",
            "container_id": "cnt-notif-01",
            "target_endpoint": "http://localhost:8084/health",
            "cpu_threshold_percent": 90.0,
            "memory_threshold_percent": 90.0,
            "latency_threshold_ms": 600.0,
            "error_rate_threshold_percent": 15.0,
        }
    ]

    for s_data in default_services:
        existing = db.query(Service).filter(Service.name == s_data["name"]).first()
        if not existing:
            service = Service(
                name=s_data["name"],
                service_type=s_data["service_type"],
                description=s_data["description"],
                container_id=s_data["container_id"],
                target_endpoint=s_data["target_endpoint"],
                status=ServiceStatus.HEALTHY,
                uptime_seconds=3600,
                cpu_threshold_percent=s_data["cpu_threshold_percent"],
                memory_threshold_percent=s_data["memory_threshold_percent"],
                latency_threshold_ms=s_data["latency_threshold_ms"],
                error_rate_threshold_percent=s_data["error_rate_threshold_percent"],
                auto_recovery_enabled=True,
                max_recovery_attempts=3
            )
            db.add(service)

    db.commit()

    # 3. Seed Autonomic Recovery Policies
    default_policies = [
        {
            "name": "Container Crash Auto-Restart Policy",
            "description": "Automatically restarts container when health probes fail consecutively.",
            "trigger_condition": TriggerCondition.CONTAINER_DOWN,
            "action_type": RecoveryActionType.RESTART,
            "max_retries": 3,
            "cooldown_seconds": 45,
            "is_enabled": True,
            "requires_admin_approval": False
        },
        {
            "name": "CPU Pressure Mitigation Policy",
            "description": "Spins up replica or requests thread scale-up when CPU exceeds threshold.",
            "trigger_condition": TriggerCondition.HIGH_CPU,
            "action_type": RecoveryActionType.SCALE_UP,
            "max_retries": 2,
            "cooldown_seconds": 60,
            "is_enabled": True,
            "requires_admin_approval": False
        },
        {
            "name": "Memory Leak Cache Purge Policy",
            "description": "Frees memory buffers and purges cached pools when RAM approaches limit.",
            "trigger_condition": TriggerCondition.HIGH_MEMORY,
            "action_type": RecoveryActionType.CLEAR_CACHE,
            "max_retries": 3,
            "cooldown_seconds": 60,
            "is_enabled": True,
            "requires_admin_approval": False
        },
        {
            "name": "High Latency Service Cycle Policy",
            "description": "Gracefully recycles lagging service process to drain hanging threads.",
            "trigger_condition": TriggerCondition.HIGH_LATENCY,
            "action_type": RecoveryActionType.RESTART,
            "max_retries": 2,
            "cooldown_seconds": 90,
            "is_enabled": True,
            "requires_admin_approval": False
        },
        {
            "name": "HTTP 5xx Error Drain Policy",
            "description": "Drains traffic and recreates unhealthy container instances.",
            "trigger_condition": TriggerCondition.REPEATED_5XX,
            "action_type": RecoveryActionType.DRAIN_AND_RECREATE,
            "max_retries": 2,
            "cooldown_seconds": 120,
            "is_enabled": True,
            "requires_admin_approval": False
        },
        {
            "name": "AI Anomaly Fast Mitigation Policy",
            "description": "Initiates fast health verification and proactive recycling on multivariate anomaly.",
            "trigger_condition": TriggerCondition.ANOMALY_DETECTED,
            "action_type": RecoveryActionType.RESTART,
            "max_retries": 2,
            "cooldown_seconds": 60,
            "is_enabled": True,
            "requires_admin_approval": False
        }
    ]

    for p_data in default_policies:
        existing_pol = db.query(RecoveryPolicy).filter(
            RecoveryPolicy.trigger_condition == p_data["trigger_condition"]
        ).first()
        if not existing_pol:
            pol = RecoveryPolicy(**p_data)
            db.add(pol)

    db.commit()
