"""
Cloud Service Telemetry Simulator & Fault Injector
Generates realistic telemetry and handles safe simulated failure injections.
"""

import random
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.metric import MetricSample
from backend.app.schemas.simulation import FailureType


class TelemetrySimulator:
    def __init__(self):
        # In-memory failure injection state: { service_id: { "type": FailureType, "expires_at": datetime, "intensity": float } }
        self._active_faults: Dict[int, Dict[str, Any]] = {}

    def inject_fault(self, service_id: int, failure_type: FailureType, duration_seconds: int = 45, intensity: float = 95.0):
        """Inject a simulated failure into a service for testing self-healing automation."""
        if failure_type == FailureType.NORMAL:
            self.clear_fault(service_id)
            return

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
        self._active_faults[service_id] = {
            "type": failure_type,
            "expires_at": expires_at,
            "intensity": intensity
        }

    def clear_fault(self, service_id: int):
        """Clear active simulated fault (called when recovery executes successfully)."""
        if service_id in self._active_faults:
            del self._active_faults[service_id]

    def get_active_fault(self, service_id: int) -> Optional[FailureType]:
        fault = self._active_faults.get(service_id)
        if not fault:
            return None
        if datetime.now(timezone.utc) > fault["expires_at"]:
            del self._active_faults[service_id]
            return None
        return fault["type"]

    def generate_metric_sample(self, service: Service) -> Dict[str, Any]:
        """Generate a realistic metric sample for the given service based on its state and active fault."""
        fault_type = self.get_active_fault(service.id)
        
        # Baseline healthy metrics
        base_cpu = random.uniform(20.0, 48.0)
        base_mem = random.uniform(35.0, 62.0)
        base_lat = random.uniform(35.0, 110.0)
        base_err = random.uniform(0.0, 0.8)
        base_reqs = random.randint(45, 220)
        is_healthy = True

        if service.status == ServiceStatus.STOPPED or fault_type == FailureType.CONTAINER_CRASH:
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "latency_ms": 3000.0, # Timeout
                "error_rate_percent": 100.0,
                "request_count": 0,
                "is_healthy": False
            }

        if fault_type == FailureType.CPU_OVERLOAD:
            base_cpu = random.uniform(91.0, 99.2)
            base_lat = random.uniform(450.0, 1200.0)
            base_err = random.uniform(8.0, 24.0)
            is_healthy = False

        elif fault_type == FailureType.MEMORY_PRESSURE:
            base_mem = random.uniform(92.0, 98.5)
            base_lat = random.uniform(380.0, 950.0)
            base_err = random.uniform(6.0, 18.0)
            is_healthy = False

        elif fault_type == FailureType.HIGH_LATENCY:
            base_lat = random.uniform(650.0, 1800.0)
            base_cpu = random.uniform(45.0, 70.0)
            base_err = random.uniform(4.0, 12.0)
            is_healthy = False

        elif fault_type == FailureType.HTTP_500_ERRORS:
            base_err = random.uniform(35.0, 85.0)
            base_lat = random.uniform(150.0, 450.0)
            is_healthy = False

        # Status degradation if thresholds are crossed
        if (base_cpu > service.cpu_threshold_percent or 
            base_mem > service.memory_threshold_percent or 
            base_lat > service.latency_threshold_ms or 
            base_err > service.error_rate_threshold_percent):
            is_healthy = False

        return {
            "cpu_percent": round(base_cpu, 1),
            "memory_percent": round(base_mem, 1),
            "latency_ms": round(base_lat, 1),
            "error_rate_percent": round(base_err, 1),
            "request_count": base_reqs,
            "is_healthy": is_healthy
        }


simulator = TelemetrySimulator()
