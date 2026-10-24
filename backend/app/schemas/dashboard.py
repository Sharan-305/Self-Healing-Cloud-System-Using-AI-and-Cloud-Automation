"""
Dashboard Metrics & Status Aggregation Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.service import ServiceResponse
from backend.app.schemas.incident import IncidentResponse
from backend.app.schemas.recovery import RecoveryExecutionResponse


class ServiceHealthBreakdown(BaseModel):
    healthy: int = 0
    degraded: int = 0
    unhealthy: int = 0
    recovering: int = 0
    stopped: int = 0


class ClusterMetricsOverview(BaseModel):
    average_cpu_percent: float = 0.0
    average_memory_percent: float = 0.0
    average_latency_ms: float = 0.0
    overall_error_rate_percent: float = 0.0
    total_active_requests: int = 0


class DashboardSummaryResponse(BaseModel):
    total_services: int
    health_breakdown: ServiceHealthBreakdown
    cluster_metrics: ClusterMetricsOverview
    active_incidents_count: int
    total_recoveries_count: int
    recovery_success_rate_percent: float
    auto_recovery_enabled: bool
    simulation_mode: bool
    recent_incidents: List[IncidentResponse]
    recent_recovery_actions: List[RecoveryExecutionResponse]
