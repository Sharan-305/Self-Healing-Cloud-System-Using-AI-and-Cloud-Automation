"""
Simulation Lab Endpoints (/api/simulations)
Allows safe, observable fault injection on local test microservices.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.service import Service
from backend.app.models.audit import AuditLog
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse, FailureType
from backend.app.monitoring.simulator import simulator
from backend.app.security.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/simulations", tags=["Simulation Lab"])


@router.post("/inject", response_model=SimulationResponse)
def inject_fault(
    req: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Safely inject a simulated failure into a demo service to verify self-healing."""
    service = db.query(Service).filter(Service.id == req.service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    simulator.inject_fault(
        service_id=service.id,
        failure_type=req.failure_type,
        duration_seconds=req.duration_seconds,
        intensity=req.intensity_percent or 95.0
    )

    audit = AuditLog(
        user_id=current_user.id,
        action="SIMULATION_FAULT_INJECTED",
        entity_type="service",
        entity_id=str(service.id),
        details={
            "service_name": service.name,
            "failure_type": req.failure_type.value,
            "duration": req.duration_seconds
        }
    )
    db.add(audit)
    db.commit()

    return {
        "status": "injected",
        "service_id": service.id,
        "service_name": service.name,
        "failure_type": req.failure_type,
        "message": f"Successfully injected {req.failure_type.value} into {service.name} (Duration: {req.duration_seconds}s). Monitoring engine will detect and trigger recovery."
    }


@router.post("/{service_id}/reset", response_model=SimulationResponse)
def reset_simulation(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear any active simulated fault for the service."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

    simulator.clear_fault(service_id)
    return {
        "status": "reset",
        "service_id": service.id,
        "service_name": service.name,
        "failure_type": FailureType.NORMAL,
        "message": f"Active simulation cleared for {service.name}. Telemetry returned to normal baseline."
    }
