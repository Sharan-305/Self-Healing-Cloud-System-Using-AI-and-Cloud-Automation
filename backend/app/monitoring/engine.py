"""
Continuous Background Health Monitoring Engine
Periodically polls monitored services, gathers telemetry, and triggers autonomic recovery.
"""

import asyncio
from datetime import datetime, timezone
from backend.app.database import SessionLocal
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.metric import MetricSample
from backend.app.models.anomaly import AnomalyEvent
from backend.app.monitoring.simulator import simulator
from backend.app.monitoring.rule_engine import rule_detector
from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.recovery.orchestrator import orchestrator
from backend.app.api.websocket import ws_manager
from backend.app.config import settings

# Global control flag
is_monitoring_running = False


async def monitoring_cycle():
    """Runs a single monitoring tick across all active services."""
    db = SessionLocal()
    try:
        services = db.query(Service).all()
        now = datetime.now(timezone.utc)
        telemetry_update = []

        for service in services:
            # 1. Generate or collect telemetry sample
            sample_data = simulator.generate_metric_sample(service)
            
            metric = MetricSample(
                service_id=service.id,
                timestamp=now,
                cpu_percent=sample_data["cpu_percent"],
                memory_percent=sample_data["memory_percent"],
                latency_ms=sample_data["latency_ms"],
                error_rate_percent=sample_data["error_rate_percent"],
                request_count=sample_data["request_count"],
                is_healthy=sample_data["is_healthy"]
            )
            db.add(metric)

            # 2. Update service health state
            service.last_health_check = now
            if sample_data["is_healthy"]:
                if service.status != ServiceStatus.RECOVERING:
                    service.status = ServiceStatus.HEALTHY
                    service.consecutive_failures = 0
                    service.uptime_seconds += settings.MONITORING_INTERVAL_SECONDS
            else:
                service.consecutive_failures += 1
                if service.consecutive_failures >= service.max_consecutive_failures:
                    if sample_data["error_rate_percent"] >= 90.0 or sample_data["cpu_percent"] == 0:
                        service.status = ServiceStatus.UNHEALTHY
                    else:
                        service.status = ServiceStatus.DEGRADED

                # Rule-Based Autonomic Failure Detection
                trigger_result = rule_detector.evaluate(service, sample_data)
                if trigger_result:
                    trig_cond, severity, reason = trigger_result
                    await orchestrator.handle_triggered_failure(
                        db=db,
                        service=service,
                        trigger_condition=trig_cond,
                        severity=severity,
                        evidence=sample_data,
                        suspected_cause=reason
                    )

            # AI Anomaly Evaluation (Isolation Forest)
            is_anomaly, score, f_dict = anomaly_detector.detect(sample_data)
            if is_anomaly:
                anom_event = AnomalyEvent(
                    service_id=service.id,
                    timestamp=now,
                    anomaly_score=round(score, 3),
                    threshold=anomaly_detector.threshold,
                    feature_values=f_dict,
                    is_confirmed_failure=not sample_data["is_healthy"],
                    model_version=anomaly_detector.version,
                    notes=f"Multivariate metric deviation detected on {service.name} (Score: {score:.3f})"
                )
                db.add(anom_event)

            telemetry_update.append({
                "service_id": service.id,
                "name": service.name,
                "status": service.status.value,
                "cpu": sample_data["cpu_percent"],
                "memory": sample_data["memory_percent"],
                "latency": sample_data["latency_ms"],
                "error_rate": sample_data["error_rate_percent"],
                "consecutive_failures": service.consecutive_failures,
                "uptime": service.uptime_seconds
            })

        db.commit()

        # 3. Broadcast real-time packet via WebSocket
        if ws_manager.active_connections:
            await ws_manager.broadcast({
                "type": "TELEMETRY_UPDATE",
                "timestamp": now.isoformat(),
                "services": telemetry_update
            })

    except Exception as e:
        db.rollback()
        print(f"[Monitoring Engine] Error in monitoring cycle: {e}")
    finally:
        db.close()


async def start_monitoring_loop():
    """Background task loop that runs every MONITORING_INTERVAL_SECONDS."""
    global is_monitoring_running
    is_monitoring_running = True
    print(f"[Monitoring Engine] Started continuous health polling (Interval: {settings.MONITORING_INTERVAL_SECONDS}s)")
    
    while is_monitoring_running:
        await monitoring_cycle()
        await asyncio.sleep(settings.MONITORING_INTERVAL_SECONDS)


def stop_monitoring_loop():
    global is_monitoring_running
    is_monitoring_running = False
    print("[Monitoring Engine] Stopped health polling.")
