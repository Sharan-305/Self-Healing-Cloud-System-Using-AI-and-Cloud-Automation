"""
Incident Management Endpoints (/api/incidents)
"""

from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity
from backend.app.models.audit import AuditLog
from backend.app.schemas.incident import IncidentResponse, IncidentListResponse
from backend.app.security.auth import get_current_user
from backend.app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    service_id: Optional[int] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List and filter incidents."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if service_id:
        query = query.filter(Incident.service_id == service_id)

    total = query.count()
    active_count = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.DETECTED, IncidentStatus.MITIGATING, IncidentStatus.ESCALATED, IncidentStatus.MANUAL_INTERVENTION_REQUIRED])
    ).count()

    incidents = query.order_by(Incident.created_at.desc()).limit(limit).all()

    for inc in incidents:
        if inc.service:
            inc.service_name = inc.service.name

    return {
        "total": total,
        "active_count": active_count,
        "incidents": incidents
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Retrieve full incident details including metric evidence and root cause."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    if inc.service:
        inc.service_name = inc.service.name
    return inc


@router.patch("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an incident as manually resolved."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found.")

    inc.status = IncidentStatus.RESOLVED
    inc.resolution_time = datetime.now(timezone.utc)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="INCIDENT_MANUALLY_RESOLVED",
        entity_type="incident",
        entity_id=str(inc.id),
        details={"service_id": inc.service_id, "resolved_by": current_user.username}
    )
    db.add(audit)
    db.commit()
    db.refresh(inc)

    if inc.service:
        inc.service_name = inc.service.name
    return inc
