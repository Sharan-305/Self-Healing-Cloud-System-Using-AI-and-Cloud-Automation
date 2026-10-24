"""
Automated Recovery Policies & Execution History Models
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base, TimestampMixin


class TriggerCondition(str, enum.Enum):
    CONTAINER_DOWN = "CONTAINER_DOWN"
    HIGH_CPU = "HIGH_CPU"
    HIGH_MEMORY = "HIGH_MEMORY"
    HIGH_LATENCY = "HIGH_LATENCY"
    REPEATED_5XX = "REPEATED_5XX"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"


class RecoveryActionType(str, enum.Enum):
    RESTART = "restart"
    SCALE_UP = "scale_up"
    CLEAR_CACHE = "clear_cache"
    ROLLBACK = "rollback"
    DRAIN_AND_RECREATE = "drain_and_recreate"
    MANUAL_ESCALATION = "manual_escalation"


class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecoveryPolicy(Base, TimestampMixin):
    __tablename__ = "recovery_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), default="")
    trigger_condition = Column(Enum(TriggerCondition), nullable=False, unique=True, index=True)
    action_type = Column(Enum(RecoveryActionType), nullable=False)
    
    max_retries = Column(Integer, default=3, nullable=False)
    cooldown_seconds = Column(Integer, default=60, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    requires_admin_approval = Column(Boolean, default=False, nullable=False)

    executions = relationship("RecoveryExecution", back_populates="policy")

    def __repr__(self):
        return f"<RecoveryPolicy id={self.id} condition='{self.trigger_condition}' action='{self.action_type}'>"


class RecoveryExecution(Base, TimestampMixin):
    __tablename__ = "recovery_executions"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("recovery_policies.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = Column(Enum(RecoveryActionType), nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False, index=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    executed_by = Column(String(50), default="system_auto", nullable=False)
    
    pre_health_status = Column(String(50), nullable=True)
    post_health_status = Column(String(50), nullable=True)
    execution_log = Column(Text, default="")
    diagnostics = Column(JSON, default=dict)
    
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    service = relationship("Service", back_populates="recovery_executions")
    incident = relationship("Incident", back_populates="recovery_executions")
    policy = relationship("RecoveryPolicy", back_populates="executions")

    def __repr__(self):
        return f"<RecoveryExecution id={self.id} service_id={self.service_id} action='{self.action}' status='{self.status}'>"
