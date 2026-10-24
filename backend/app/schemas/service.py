"""
Service & Container Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from backend.app.models.service import ServiceStatus


class ServiceBase(BaseModel):
    name: str
    service_type: str = "microservice"
    description: Optional[str] = ""
    target_endpoint: Optional[str] = None
    container_id: Optional[str] = None
    
    health_check_interval_seconds: int = 5
    max_consecutive_failures: int = 3
    cpu_threshold_percent: float = 85.0
    memory_threshold_percent: float = 85.0
    latency_threshold_ms: float = 500.0
    error_rate_threshold_percent: float = 15.0
    auto_recovery_enabled: bool = True
    max_recovery_attempts: int = 3


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_endpoint: Optional[str] = None
    cpu_threshold_percent: Optional[float] = None
    memory_threshold_percent: Optional[float] = None
    latency_threshold_ms: Optional[float] = None
    error_rate_threshold_percent: Optional[float] = None
    auto_recovery_enabled: Optional[bool] = None
    max_recovery_attempts: Optional[int] = None


class ServiceActionRequest(BaseModel):
    action: str # "restart", "stop", "start", "scale_up", "clear_cache"


class ServiceResponse(ServiceBase):
    id: int
    status: ServiceStatus
    uptime_seconds: int
    consecutive_failures: int
    active_recovery_attempts: int
    last_health_check: Optional[datetime] = None
    in_cooldown_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    total: int
    services: List[ServiceResponse]
