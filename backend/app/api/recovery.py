"""
Recovery Policies & Execution History Endpoints (/api/recovery)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.recovery import RecoveryPolicy, RecoveryExecution, ExecutionStatus
from backend.app.models.audit import AuditLog
from backend.app.schemas.recovery import (
    RecoveryPolicyResponse,
    RecoveryPolicyUpdate,
    RecoveryExecutionResponse,
    RecoveryHistoryResponse,
)
from backend.app.security.auth import require_admin
from backend.app.models.user import User

router = APIRouter(prefix="/recovery", tags=["Recovery & Policies"])


@router.get("/history", response_model=RecoveryHistoryResponse)
def get_recovery_history(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve history of all automated and manual recovery executions."""
    total = db.query(RecoveryExecution).count()
    successful = db.query(RecoveryExecution).filter(RecoveryExecution.status == ExecutionStatus.SUCCEEDED).count()
    rate = round((successful / total * 100), 1) if total > 0 else 100.0

    executions = (
        db.query(RecoveryExecution)
        .order_by(RecoveryExecution.started_at.desc())
        .limit(limit)
        .all()
    )

    for ex in executions:
        if ex.service:
            ex.service_name = ex.service.name

    return {
        "total": total,
        "success_rate_percent": rate,
        "executions": executions
    }


@router.get("/policies", response_model=List[RecoveryPolicyResponse])
def get_recovery_policies(db: Session = Depends(get_db)):
    """List all configured autonomic recovery policies."""
    return db.query(RecoveryPolicy).order_by(RecoveryPolicy.id.asc()).all()


@router.patch("/policies/{policy_id}", response_model=RecoveryPolicyResponse)
def update_recovery_policy(
    policy_id: int,
    policy_update: RecoveryPolicyUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Update recovery policy settings (Requires Administrator)."""
    policy = db.query(RecoveryPolicy).filter(RecoveryPolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found.")

    update_data = policy_update.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(policy, key, val)

    audit = AuditLog(
        user_id=admin_user.id,
        action="POLICY_UPDATED",
        entity_type="recovery_policy",
        entity_id=str(policy.id),
        details={"name": policy.name, "updates": update_data}
    )
    db.add(audit)

    db.commit()
    db.refresh(policy)
    return policy
