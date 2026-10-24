"""
Monitored Cloud Service and Container Model
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base, TimestampMixin


class ServiceStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    STOPPED = "stopped"


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    service_type = Column(String(50), default="microservice", nullable=False)
    description = Column(String(255), default="")
    container_id = Column(String(128), nullable=True, index=True)
    target_endpoint = Column(String(255), nullable=True)
    
    status = Column(Enum(ServiceStatus), default=ServiceStatus.HEALTHY, nullable=False, index=True)
    uptime_seconds = Column(Integer, default=0, nullable=False)
    last_health_check = Column(DateTime(timezone=True), nullable=True)
    
    # Thresholds & Configuration
    health_check_interval_seconds = Column(Integer, default=5, nullable=False)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    max_consecutive_failures = Column(Integer, default=3, nullable=False)
    
    cpu_threshold_percent = Column(Float, default=85.0, nullable=False)
    memory_threshold_percent = Column(Float, default=85.0, nullable=False)
    latency_threshold_ms = Column(Float, default=500.0, nullable=False)
    error_rate_threshold_percent = Column(Float, default=15.0, nullable=False)
    
    auto_recovery_enabled = Column(Boolean, default=True, nullable=False)
    in_cooldown_until = Column(DateTime(timezone=True), nullable=True)
    active_recovery_attempts = Column(Integer, default=0, nullable=False)
    max_recovery_attempts = Column(Integer, default=3, nullable=False)

    # Relationships
    metrics = relationship("MetricSample", back_populates="service", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="service", cascade="all, delete-orphan")
    anomalies = relationship("AnomalyEvent", back_populates="service", cascade="all, delete-orphan")
    recovery_executions = relationship("RecoveryExecution", back_populates="service", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Service id={self.id} name='{self.name}' status='{self.status}'>"
