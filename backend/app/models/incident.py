"""
Incident Management Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base, TimestampMixin


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    DETECTED = "detected"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    MANUAL_INTERVENTION_REQUIRED = "manual_intervention_required"


class Incident(Base, TimestampMixin):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM, nullable=False, index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.DETECTED, nullable=False, index=True)
    
    suspected_root_cause = Column(String(255), default="Unknown")
    metric_evidence = Column(JSON, default=dict)
    
    recovery_action_taken = Column(String(100), nullable=True)
    recovery_attempts = Column(Integer, default=0, nullable=False)
    
    detection_time = Column(DateTime(timezone=True), nullable=False)
    resolution_time = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    service = relationship("Service", back_populates="incidents")
    recovery_executions = relationship("RecoveryExecution", back_populates="incident", cascade="all, delete-orphan")
    notifications = relationship("NotificationEvent", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident id={self.id} service_id={self.service_id} severity='{self.severity}' status='{self.status}'>"
