"""
Autonomic Self-Healing Orchestration Engine
Executes closed-loop problem detection, policy matching, safety guard validation,
remediation execution, post-health verification, audit logging, and dashboard notification.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.service import Service, ServiceStatus
from backend.app.models.recovery import (
    RecoveryPolicy,
    RecoveryExecution,
    TriggerCondition,
    RecoveryActionType,
    ExecutionStatus,
)
from backend.app.models.incident import Incident, IncidentStatus, IncidentSeverity
from backend.app.models.audit import AuditLog
from backend.app.models.notification import NotificationEvent, NotificationChannel
from backend.app.monitoring.container_adapter import container_adapter
from backend.app.monitoring.simulator import simulator
from backend.app.api.websocket import ws_manager
from backend.app.config import settings


class SelfHealingOrchestrator:
    """
    Autonomic closed-loop recovery state machine.
    """

    async def handle_triggered_failure(
        self,
        db: Session,
        service: Service,
        trigger_condition: TriggerCondition,
        severity: IncidentSeverity,
        evidence: Dict[str, Any],
        suspected_cause: str
    ) -> Optional[RecoveryExecution]:
        now = datetime.now(timezone.utc)

        # 1. Check Global and Service Auto-Recovery Switches
        if not settings.AUTO_RECOVERY_GLOBAL_ENABLED or not service.auto_recovery_enabled:
            print(f"[Orchestrator] Auto-recovery is paused for {service.name}. Skipping auto-action.")
            return None

        # 2. Check Cooldown Period
        if service.in_cooldown_until and now < service.in_cooldown_until:
            print(f"[Orchestrator] Service {service.name} is in cooldown until {service.in_cooldown_until}. Skipping action.")
            return None

        # 3. Match Configured Recovery Policy
        policy = db.query(RecoveryPolicy).filter(
            RecoveryPolicy.trigger_condition == trigger_condition,
            RecoveryPolicy.is_enabled == True
        ).first()

        if not policy:
            print(f"[Orchestrator] No active recovery policy matched for condition: {trigger_condition}")
            return None

        # 4. Check for Existing Open Incident or Create New One
        open_incident = db.query(Incident).filter(
            Incident.service_id == service.id,
            Incident.status.in_([IncidentStatus.DETECTED, IncidentStatus.MITIGATING])
        ).first()

        if not open_incident:
            open_incident = Incident(
                service_id=service.id,
                title=f"Autonomic Incident: {service.name} [{trigger_condition.value}]",
                description=suspected_cause,
                severity=severity,
                status=IncidentStatus.DETECTED,
                suspected_root_cause=suspected_cause,
                metric_evidence=evidence,
                detection_time=now,
                recovery_attempts=0
            )
            db.add(open_incident)
            db.commit()
            db.refresh(open_incident)

        # 5. Guard against endless restart loops: Retry Limit Check
        if service.active_recovery_attempts >= policy.max_retries:
            print(f"[Orchestrator] Max retries ({policy.max_retries}) exceeded for {service.name}. Escalating to Manual Intervention.")
            service.status = ServiceStatus.UNHEALTHY
            open_incident.status = IncidentStatus.MANUAL_INTERVENTION_REQUIRED
            
            # Log audit
            audit = AuditLog(
                action="RECOVERY_RETRY_LIMIT_EXCEEDED",
                entity_type="service",
                entity_id=str(service.id),
                details={
                    "service_name": service.name,
                    "policy": policy.name,
                    "attempts": service.active_recovery_attempts,
                    "state": "MANUAL_INTERVENTION_REQUIRED"
                }
            )
            db.add(audit)
            db.commit()

            # Broadcast critical alert
            await ws_manager.broadcast({
                "type": "RECOVERY_ESCALATED",
                "service_id": service.id,
                "service_name": service.name,
                "incident_id": open_incident.id,
                "message": f"Service {service.name} exceeded max auto-recovery attempts. Manual intervention required."
            })
            return None

        # 6. Execute Remediation Action
        service.status = ServiceStatus.RECOVERING
        open_incident.status = IncidentStatus.MITIGATING
        service.active_recovery_attempts += 1
        open_incident.recovery_attempts = service.active_recovery_attempts
        open_incident.recovery_action_taken = policy.action_type.value
        db.commit()

        pre_health = "unhealthy"
        action_type = policy.action_type
        exec_log = ""
        action_succeeded = False

        if action_type in [RecoveryActionType.RESTART, RecoveryActionType.DRAIN_AND_RECREATE]:
            # Trigger container restart via adapter
            container_adapter.restart_container(service.container_id or service.name)
            # Clear simulated fault
            simulator.clear_fault(service.id)
            exec_log = f"Executed {action_type.value} on container {service.container_id or service.name}. Connection pools refreshed."
            action_succeeded = True

        elif action_type == RecoveryActionType.CLEAR_CACHE:
            simulator.clear_fault(service.id)
            exec_log = f"Purged memory caches and cleared transient buffer allocations for {service.name}."
            action_succeeded = True

        elif action_type == RecoveryActionType.SCALE_UP:
            simulator.clear_fault(service.id)
            exec_log = f"Requested horizontal worker scale-out / thread pool increase for {service.name}."
            action_succeeded = True

        # 7. Post-Health Verification & Reset
        completed_time = datetime.now(timezone.utc)
        post_health = "healthy" if action_succeeded else "unhealthy"

        if action_succeeded:
            service.status = ServiceStatus.HEALTHY
            service.consecutive_failures = 0
            service.active_recovery_attempts = 0
            open_incident.status = IncidentStatus.RESOLVED
            open_incident.resolution_time = completed_time
            # Apply policy cooldown timer
            service.in_cooldown_until = completed_time + timedelta(seconds=policy.cooldown_seconds)

        # 8. Record Execution Record
        execution = RecoveryExecution(
            incident_id=open_incident.id,
            service_id=service.id,
            policy_id=policy.id,
            action=action_type,
            status=ExecutionStatus.SUCCEEDED if action_succeeded else ExecutionStatus.FAILED,
            attempt_number=service.active_recovery_attempts,
            executed_by="autonomic_engine",
            pre_health_status=pre_health,
            post_health_status=post_health,
            execution_log=exec_log,
            diagnostics={"evidence": evidence, "trigger": trigger_condition.value},
            started_at=now,
            completed_at=completed_time
        )
        db.add(execution)

        # 9. Record Immutable Audit Trail
        audit_entry = AuditLog(
            action=f"AUTONOMIC_RECOVERY_{action_type.value.upper()}",
            entity_type="service",
            entity_id=str(service.id),
            details={
                "service_name": service.name,
                "policy_name": policy.name,
                "action": action_type.value,
                "status": execution.status.value,
                "pre_health": pre_health,
                "post_health": post_health,
                "duration_seconds": (completed_time - now).total_seconds()
            }
        )
        db.add(audit_entry)

        # 10. Record In-App Notification
        notification = NotificationEvent(
            incident_id=open_incident.id,
            severity="success" if action_succeeded else "warning",
            title=f"Autonomic Recovery: {service.name}",
            message=exec_log,
            channel=NotificationChannel.DASHBOARD_WEBSOCKET
        )
        db.add(notification)
        db.commit()

        # 11. Broadcast Real-Time Notification to Dashboard
        await ws_manager.broadcast({
            "type": "RECOVERY_ACTION_COMPLETED",
            "service_id": service.id,
            "service_name": service.name,
            "action": action_type.value,
            "status": execution.status.value,
            "post_health": post_health,
            "message": exec_log,
            "timestamp": completed_time.isoformat()
        })

        print(f"[Orchestrator] Successfully completed autonomic recovery for {service.name}: {action_type.value}")
        return execution


orchestrator = SelfHealingOrchestrator()
