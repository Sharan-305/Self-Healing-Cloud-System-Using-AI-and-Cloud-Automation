"""
AI-Based Anomaly Event Models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    anomaly_score = Column(Float, nullable=False) # e.g. -0.35 where negative = anomalous
    threshold = Column(Float, default=-0.15, nullable=False)
    feature_values = Column(JSON, nullable=False) # {cpu: 94.2, memory: 88.5, latency: 1200, error_rate: 22.0}
    
    is_confirmed_failure = Column(Boolean, default=False, nullable=False)
    model_version = Column(String(50), default="isolation_forest_v1", nullable=False)
    notes = Column(String(255), default="")

    service = relationship("Service", back_populates="anomalies")

    def __repr__(self):
        return f"<AnomalyEvent service_id={self.service_id} score={self.anomaly_score:.3f} timestamp='{self.timestamp}'>"
