"""
Recovery Policies & Executions Schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.recovery import TriggerCondition, RecoveryActionType, ExecutionStatus


class RecoveryPolicyResponse(BaseModel):
    id: int
    name: str
    description: str
    trigger_condition: TriggerCondition
    action_type: RecoveryActionType
    max_retries: int
    cooldown_seconds: int
    is_enabled: bool
    requires_admin_approval: bool

    class Config:
        from_attributes = True


class RecoveryPolicyUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    max_retries: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    requires_admin_approval: Optional[bool] = None


class RecoveryExecutionResponse(BaseModel):
    id: int
    incident_id: Optional[int] = None
    service_id: int
    service_name: Optional[str] = None
    policy_id: Optional[int] = None
    action: RecoveryActionType
    status: ExecutionStatus
    attempt_number: int
    executed_by: str
    pre_health_status: Optional[str] = None
    post_health_status: Optional[str] = None
    execution_log: str
    diagnostics: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecoveryHistoryResponse(BaseModel):
    total: int
    success_rate_percent: float
    executions: List[RecoveryExecutionResponse]
