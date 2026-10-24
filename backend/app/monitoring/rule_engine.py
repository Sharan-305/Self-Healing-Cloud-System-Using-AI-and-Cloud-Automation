"""
Rule-Based Health & Failure Detection Engine
Validates metrics against configurable thresholds and consecutive failure counts.
"""

from typing import Optional, Dict, Any, Tuple
from backend.app.models.service import Service, ServiceStatus
from backend.app.models.recovery import TriggerCondition
from backend.app.models.incident import IncidentSeverity


class RuleBasedDetector:
    """
    Evaluates metric samples and consecutive failure states to determine
    if an autonomic recovery trigger condition has been met.
    """
    def evaluate(
        self,
        service: Service,
        metric: Dict[str, Any]
    ) -> Optional[Tuple[TriggerCondition, IncidentSeverity, str]]:
        """
        Returns (TriggerCondition, IncidentSeverity, reason) if failure criteria is verified,
        otherwise None.
        """
        # Guard: Ignore stopped services
        if service.status == ServiceStatus.STOPPED:
            return None

        # Guard: Require multiple consecutive failures to avoid flapping from transient spikes
        if service.consecutive_failures < service.max_consecutive_failures:
            return None

        # 1. Total Container / Probe Outage
        if metric["error_rate_percent"] >= 95.0 or metric["cpu_percent"] == 0:
            return (
                TriggerCondition.CONTAINER_DOWN,
                IncidentSeverity.CRITICAL,
                f"Container {service.container_id or service.name} failed {service.consecutive_failures} consecutive health checks. Service unreachable."
            )

        # 2. Repeated HTTP 5xx Failure Storm
        if metric["error_rate_percent"] >= service.error_rate_threshold_percent:
            return (
                TriggerCondition.REPEATED_5XX,
                IncidentSeverity.HIGH,
                f"Elevated error rate ({metric['error_rate_percent']}%) exceeds threshold ({service.error_rate_threshold_percent}%)."
            )

        # 3. Sustained CPU Overload
        if metric["cpu_percent"] >= service.cpu_threshold_percent:
            return (
                TriggerCondition.HIGH_CPU,
                IncidentSeverity.HIGH,
                f"Sustained CPU utilization ({metric['cpu_percent']}%) exceeds threshold ({service.cpu_threshold_percent}%)."
            )

        # 4. Sustained Memory Pressure
        if metric["memory_percent"] >= service.memory_threshold_percent:
            return (
                TriggerCondition.HIGH_MEMORY,
                IncidentSeverity.HIGH,
                f"Sustained memory consumption ({metric['memory_percent']}%) exceeds threshold ({service.memory_threshold_percent}%)."
            )

        # 5. Severe Latency Degradation
        if metric["latency_ms"] >= service.latency_threshold_ms:
            return (
                TriggerCondition.HIGH_LATENCY,
                IncidentSeverity.MEDIUM,
                f"Response latency ({metric['latency_ms']}ms) exceeds threshold ({service.latency_threshold_ms}ms)."
            )

        return None


rule_detector = RuleBasedDetector()
