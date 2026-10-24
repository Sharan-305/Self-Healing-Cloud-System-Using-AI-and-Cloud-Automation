export type UserRole = 'admin' | 'viewer';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export type ServiceStatus = 'healthy' | 'degraded' | 'unhealthy' | 'recovering' | 'stopped';

export interface Service {
  id: number;
  name: string;
  service_type: string;
  description: string;
  container_id?: string;
  target_endpoint?: string;
  status: ServiceStatus;
  uptime_seconds: number;
  consecutive_failures: number;
  max_consecutive_failures: number;
  cpu_threshold_percent: number;
  memory_threshold_percent: number;
  latency_threshold_ms: number;
  error_rate_threshold_percent: number;
  auto_recovery_enabled: boolean;
  active_recovery_attempts: number;
  max_recovery_attempts: number;
  last_health_check?: string;
  in_cooldown_until?: string;
  created_at: string;
}

export interface MetricSample {
  id: number;
  service_id: number;
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  latency_ms: number;
  error_rate_percent: number;
  request_count: number;
  is_healthy: boolean;
}

export type IncidentSeverity = 'low' | 'medium' | 'high' | 'critical';
export type IncidentStatus = 'detected' | 'mitigating' | 'resolved' | 'escalated' | 'manual_intervention_required';

export interface Incident {
  id: number;
  service_id: number;
  service_name?: string;
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  suspected_root_cause: string;
  metric_evidence: Record<string, any>;
  recovery_action_taken?: string;
  recovery_attempts: number;
  detection_time: string;
  resolution_time?: string;
  created_at: string;
}

export interface RecoveryPolicy {
  id: number;
  name: string;
  description: string;
  trigger_condition: string;
  action_type: string;
  max_retries: number;
  cooldown_seconds: number;
  is_enabled: boolean;
  requires_admin_approval: boolean;
}

export interface RecoveryExecution {
  id: number;
  incident_id?: number;
  service_id: number;
  service_name?: string;
  action: string;
  status: 'pending' | 'executing' | 'succeeded' | 'failed' | 'cancelled';
  attempt_number: number;
  executed_by: string;
  pre_health_status?: string;
  post_health_status?: string;
  execution_log: string;
  diagnostics?: Record<string, any>;
  started_at: string;
  completed_at?: string;
}

export interface DashboardSummary {
  total_services: number;
  health_breakdown: {
    healthy: number;
    degraded: number;
    unhealthy: number;
    recovering: number;
    stopped: number;
  };
  cluster_metrics: {
    average_cpu_percent: number;
    average_memory_percent: number;
    average_latency_ms: number;
    overall_error_rate_percent: number;
    total_active_requests: number;
  };
  active_incidents_count: number;
  total_recoveries_count: number;
  recovery_success_rate_percent: number;
  auto_recovery_enabled: boolean;
  simulation_mode: boolean;
  recent_incidents: Incident[];
  recent_recovery_actions: RecoveryExecution[];
}

export type FailureType = 
  | 'cpu_overload'
  | 'memory_pressure'
  | 'high_latency'
  | 'http_500_errors'
  | 'container_crash'
  | 'normal';
