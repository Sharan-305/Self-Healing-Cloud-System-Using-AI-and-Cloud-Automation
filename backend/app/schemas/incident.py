"""
Incident Management Schemas
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.incident import IncidentSeverity, IncidentStatus


class IncidentResponse(BaseModel):
    id: int
    service_id: int
    service_name: Optional[str] = None
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    suspected_root_cause: str
    metric_evidence: Dict[str, Any]
    recovery_action_taken: Optional[str] = None
    recovery_attempts: int
    detection_time: datetime
    resolution_time: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    total: int
    active_count: int
    incidents: List[IncidentResponse]
