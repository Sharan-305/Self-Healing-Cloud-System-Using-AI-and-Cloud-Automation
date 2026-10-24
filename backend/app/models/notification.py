"""
In-App and WebSocket Notification Models
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import Base


class NotificationChannel(str, enum.Enum):
    DASHBOARD_WEBSOCKET = "dashboard_websocket"
    IN_APP_BANNER = "in_app_banner"
    EMAIL = "email"


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    
    severity = Column(String(20), default="info", nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.DASHBOARD_WEBSOCKET, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    incident = relationship("Incident", back_populates="notifications")

    def __repr__(self):
        return f"<NotificationEvent id={self.id} title='{self.title}' read={self.is_read}>"
