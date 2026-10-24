"""
Simulation Lab Request and Response Schemas
"""

from typing import Optional
import enum
from pydantic import BaseModel


class FailureType(str, enum.Enum):
    CPU_OVERLOAD = "cpu_overload"
    MEMORY_PRESSURE = "memory_pressure"
    HIGH_LATENCY = "high_latency"
    HTTP_500_ERRORS = "http_500_errors"
    CONTAINER_CRASH = "container_crash"
    NORMAL = "normal"


class SimulationRequest(BaseModel):
    service_id: int
    failure_type: FailureType
    duration_seconds: int = 45
    intensity_percent: Optional[float] = 95.0


class SimulationResponse(BaseModel):
    status: str
    service_id: int
    service_name: str
    failure_type: FailureType
    message: str
