"""
Metric Sample Telemetry Schemas
"""

from typing import List
from datetime import datetime
from pydantic import BaseModel


class MetricSampleCreate(BaseModel):
    service_id: int
    cpu_percent: float
    memory_percent: float
    latency_ms: float
    error_rate_percent: float = 0.0
    request_count: int = 0
    is_healthy: bool = True


class MetricSampleResponse(BaseModel):
    id: int
    service_id: int
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    latency_ms: float
    error_rate_percent: float
    request_count: int
    is_healthy: bool

    class Config:
        from_attributes = True


class MetricHistoryResponse(BaseModel):
    service_id: int
    service_name: str
    samples: List[MetricSampleResponse]
