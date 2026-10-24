"""
Service & Container Management Endpoints (/api/services)
"""

from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.metric import MetricSample
from backend.app.models.recovery import RecoveryExecution, RecoveryActionType, ExecutionStatus
from backend.app.models.audit import AuditLog
from backend.app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ServiceListResponse,
    ServiceActionRequest,
)
from backend.app.schemas.metric import MetricSampleResponse, MetricHistoryResponse
from backend.app.security.auth import get_current_user, require_admin
from backend.app.models.user import User
from backend.app.monitoring.simulator import simulator

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=ServiceListResponse)
def list_services(db: Session = Depends(get_db)):
    """List all registered cloud services and containers."""
    services = db.query(Service).order_by(Service.id.asc()).all()
    return {
        "total": len(services),
        "services": services
    }


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def register_service(
    service_in: ServiceCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Register a new monitored cloud service (Requires Administrator)."""
    existing = db.query(Service).filter(Service.name == service_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service with name '{service_in.name}' is already registered."
        )

    service = Service(
        **service_in.model_dump(),
        status=ServiceStatus.HEALTHY,
        uptime_seconds=0
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # Audit log
    audit = AuditLog(
        user_id=admin_user.id,
        action="SERVICE_REGISTERED",
        entity_type="service",
        entity_id=str(service.id),
        details={"name": service.name, "type": service.service_type}
    )
    db.add(audit)
    db.commit()

    return service


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    """Retrieve details of a specific service."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")
    return service


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service_thresholds(
    service_id: int,
    service_update: ServiceUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Update service alert thresholds and automation flags (Requires Administrator)."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    update_data = service_update.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(service, field, val)

    db.commit()
    db.refresh(service)

    audit = AuditLog(
        user_id=admin_user.id,
        action="SERVICE_CONFIG_UPDATED",
        entity_type="service",
        entity_id=str(service.id),
        details=update_data
    )
    db.add(audit)
    db.commit()

    return service


@router.post("/{service_id}/action", response_model=ServiceResponse)
def execute_service_action(
    service_id: int,
    action_req: ServiceActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute a controlled lifecycle or recovery action (e.g. restart, stop, start, clear_cache)."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    action = action_req.action.lower()
    allowed_actions = ["restart", "stop", "start", "scale_up", "clear_cache"]
    if action not in allowed_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Action '{action}' is not supported. Allowed: {allowed_actions}"
        )

    pre_status = service.status.value
    now = datetime.now(timezone.utc)

    if action == "restart":
        simulator.clear_fault(service.id)
        service.status = ServiceStatus.HEALTHY
        service.consecutive_failures = 0
        service.uptime_seconds = 0
        post_status = "healthy"
        log = f"Container {service.container_id or service.name} cycled successfully. Memory and connection pools refreshed."

    elif action == "stop":
        service.status = ServiceStatus.STOPPED
        post_status = "stopped"
        log = f"Container {service.container_id or service.name} stopped by operator."

    elif action == "start":
        simulator.clear_fault(service.id)
        service.status = ServiceStatus.HEALTHY
        service.consecutive_failures = 0
        post_status = "healthy"
        log = f"Container {service.container_id or service.name} initialized and started."

    elif action == "clear_cache":
        simulator.clear_fault(service.id)
        service.status = ServiceStatus.HEALTHY
        post_status = "healthy"
        log = f"In-memory buffers and Redis cache keys purged for {service.name}."

    elif action == "scale_up":
        simulator.clear_fault(service.id)
        service.status = ServiceStatus.HEALTHY
        post_status = "healthy"
        log = f"Provisioned supplementary worker replica for {service.name}."

    # Record execution history
    exec_record = RecoveryExecution(
        service_id=service.id,
        action=RecoveryActionType.RESTART if action in ["restart", "start"] else RecoveryActionType.CLEAR_CACHE,
        status=ExecutionStatus.SUCCEEDED,
        attempt_number=1,
        executed_by=current_user.username,
        pre_health_status=pre_status,
        post_health_status=post_status,
        execution_log=log,
        started_at=now,
        completed_at=now
    )
    db.add(exec_record)

    # Record audit log
    audit = AuditLog(
        user_id=current_user.id,
        action=f"SERVICE_ACTION_{action.upper()}",
        entity_type="service",
        entity_id=str(service.id),
        details={"action": action, "pre_status": pre_status, "post_status": post_status}
    )
    db.add(audit)

    db.commit()
    db.refresh(service)
    return service


@router.get("/{service_id}/metrics", response_model=MetricHistoryResponse)
def get_service_metrics(
    service_id: int,
    limit: int = Query(default=30, ge=5, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve historical metric telemetry samples for dashboard visualization."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    samples = (
        db.query(MetricSample)
        .filter(MetricSample.service_id == service_id)
        .order_by(MetricSample.timestamp.desc())
        .limit(limit)
        .all()
    )
    # Return chronologically ascending for graphing
    samples.reverse()

    return {
        "service_id": service.id,
        "service_name": service.name,
        "samples": samples
    }
