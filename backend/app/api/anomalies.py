"""
AI Anomaly Detection Endpoints (/api/anomalies)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.anomaly import AnomalyEvent
from backend.app.ml.anomaly_detector import anomaly_detector
from backend.app.security.auth import require_admin
from backend.app.models.user import User

router = APIRouter(prefix="/anomalies", tags=["AI Anomaly Detection"])


class AnomalyEventResponse(BaseModel):
    id: int
    service_id: int
    service_name: Optional[str] = None
    timestamp: datetime
    anomaly_score: float
    threshold: float
    feature_values: Dict[str, Any]
    is_confirmed_failure: bool
    model_version: str
    notes: str

    class Config:
        from_attributes = True


class AnomalyListResponse(BaseModel):
    total: int
    model_trained: bool
    model_version: str
    anomalies: List[AnomalyEventResponse]


@router.get("", response_model=AnomalyListResponse)
def list_anomalies(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List detected multidimensional metric anomalies."""
    total = db.query(AnomalyEvent).count()
    events = db.query(AnomalyEvent).order_by(AnomalyEvent.timestamp.desc()).limit(limit).all()

    for ev in events:
        if ev.service:
            ev.service_name = ev.service.name

    return {
        "total": total,
        "model_trained": anomaly_detector.is_trained,
        "model_version": anomaly_detector.version,
        "anomalies": events
    }


@router.post("/train")
def train_anomaly_model(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """Trigger retrain of the Isolation Forest model on historical metric samples."""
    success = anomaly_detector.train_on_history(db)
    return {
        "status": "success" if success else "failed",
        "message": "Isolation Forest model retrained successfully on historical cluster baseline vectors."
    }
