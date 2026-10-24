"""
Metric Samples Model for Continuous Telemetry
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class MetricSample(Base):
    __tablename__ = "metric_samples"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    latency_ms = Column(Float, nullable=False)
    error_rate_percent = Column(Float, default=0.0, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
    is_healthy = Column(Boolean, default=True, nullable=False)
    
    # Relationship
    service = relationship("Service", back_populates="metrics")

    __table_args__ = (
        Index("idx_metric_service_timestamp", "service_id", "timestamp"),
    )

    def __repr__(self):
        return f"<MetricSample service_id={self.service_id} cpu={self.cpu_percent}% mem={self.memory_percent}% lat={self.latency_ms}ms>"
