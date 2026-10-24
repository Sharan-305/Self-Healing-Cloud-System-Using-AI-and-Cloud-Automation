"""
Consolidated Pydantic Schemas
"""

from backend.app.schemas.auth import UserCreate, UserLogin, UserResponse, Token, TokenData
from backend.app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    ServiceListResponse,
    ServiceActionRequest,
)
from backend.app.schemas.metric import MetricSampleCreate, MetricSampleResponse, MetricHistoryResponse
from backend.app.schemas.incident import IncidentResponse, IncidentListResponse
from backend.app.schemas.recovery import (
    RecoveryPolicyResponse,
    RecoveryPolicyUpdate,
    RecoveryExecutionResponse,
    RecoveryHistoryResponse,
)
from backend.app.schemas.dashboard import (
    DashboardSummaryResponse,
    ServiceHealthBreakdown,
    ClusterMetricsOverview,
)
from backend.app.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    FailureType,
)

__all__ = [
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceResponse",
    "ServiceListResponse",
    "ServiceActionRequest",
    "MetricSampleCreate",
    "MetricSampleResponse",
    "MetricHistoryResponse",
    "IncidentResponse",
    "IncidentListResponse",
    "RecoveryPolicyResponse",
    "RecoveryPolicyUpdate",
    "RecoveryExecutionResponse",
    "RecoveryHistoryResponse",
    "DashboardSummaryResponse",
    "ServiceHealthBreakdown",
    "ClusterMetricsOverview",
    "SimulationRequest",
    "SimulationResponse",
    "FailureType",
]
