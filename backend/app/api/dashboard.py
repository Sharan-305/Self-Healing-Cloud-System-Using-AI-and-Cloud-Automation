"""
Dashboard Analytics & Aggregation Endpoint (/api/dashboard/summary)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.metric import MetricSample
from backend.app.models.incident import Incident, IncidentStatus
from backend.app.models.recovery import RecoveryExecution, ExecutionStatus
from backend.app.schemas.dashboard import (
    DashboardSummaryResponse,
    ServiceHealthBreakdown,
    ClusterMetricsOverview,
)
from backend.app.config import settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve holistic cluster health, metrics overview, and recent actions."""
    services = db.query(Service).all()
    total_services = len(services)

    # Health Breakdown
    breakdown = ServiceHealthBreakdown()
    for s in services:
        if s.status == ServiceStatus.HEALTHY:
            breakdown.healthy += 1
        elif s.status == ServiceStatus.DEGRADED:
            breakdown.degraded += 1
        elif s.status == ServiceStatus.UNHEALTHY:
            breakdown.unhealthy += 1
        elif s.status == ServiceStatus.RECOVERING:
            breakdown.recovering += 1
        elif s.status == ServiceStatus.STOPPED:
            breakdown.stopped += 1

    # Compute cluster averages from most recent metric sample per service
    cluster_metrics = ClusterMetricsOverview()
    if services:
        cpu_sum = 0.0
        mem_sum = 0.0
        lat_sum = 0.0
        err_sum = 0.0
        req_sum = 0
        counted = 0

        for s in services:
            latest = (
                db.query(MetricSample)
                .filter(MetricSample.service_id == s.id)
                .order_by(MetricSample.timestamp.desc())
                .first()
            )
            if latest:
                cpu_sum += latest.cpu_percent
                mem_sum += latest.memory_percent
                lat_sum += latest.latency_ms
                err_sum += latest.error_rate_percent
                req_sum += latest.request_count
                counted += 1

        if counted > 0:
            cluster_metrics.average_cpu_percent = round(cpu_sum / counted, 1)
            cluster_metrics.average_memory_percent = round(mem_sum / counted, 1)
            cluster_metrics.average_latency_ms = round(lat_sum / counted, 1)
            cluster_metrics.overall_error_rate_percent = round(err_sum / counted, 1)
            cluster_metrics.total_active_requests = req_sum

    # Active Incidents
    active_incidents = (
        db.query(Incident)
        .filter(Incident.status.in_([IncidentStatus.DETECTED, IncidentStatus.MITIGATING, IncidentStatus.ESCALATED, IncidentStatus.MANUAL_INTERVENTION_REQUIRED]))
        .order_by(Incident.created_at.desc())
        .all()
    )

    # Recovery Stats
    total_recoveries = db.query(RecoveryExecution).count()
    successful_recoveries = db.query(RecoveryExecution).filter(RecoveryExecution.status == ExecutionStatus.SUCCEEDED).count()
    success_rate = round((successful_recoveries / total_recoveries * 100), 1) if total_recoveries > 0 else 100.0

    # Recent recovery executions
    recent_actions = (
        db.query(RecoveryExecution)
        .order_by(RecoveryExecution.started_at.desc())
        .limit(5)
        .all()
    )

    # Attach service names for readability
    for inc in active_incidents[:5]:
        if inc.service:
            inc.service_name = inc.service.name

    for act in recent_actions:
        if act.service:
            act.service_name = act.service.name

    return {
        "total_services": total_services,
        "health_breakdown": breakdown,
        "cluster_metrics": cluster_metrics,
        "active_incidents_count": len(active_incidents),
        "total_recoveries_count": total_recoveries,
        "recovery_success_rate_percent": success_rate,
        "auto_recovery_enabled": settings.AUTO_RECOVERY_GLOBAL_ENABLED,
        "simulation_mode": settings.SIMULATION_MODE_DEFAULT,
        "recent_incidents": active_incidents[:5],
        "recent_recovery_actions": recent_actions
    }
