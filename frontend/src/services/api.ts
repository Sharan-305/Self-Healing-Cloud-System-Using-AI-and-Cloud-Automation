import { DashboardSummary, Service, MetricSample, Incident, RecoveryPolicy, RecoveryExecution, User } from '../types';

const API_BASE = '/api';

class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('selfhealing_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('selfhealing_token', token);
    } else {
      localStorage.removeItem('selfhealing_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || 'An unexpected error occurred');
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(res.access_token);
    return res;
  }

  async register(username: string, email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  // Dashboard Summary
  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>('/dashboard/summary');
  }

  // Services
  async getServices(): Promise<{ total: number; services: Service[] }> {
    return this.request<{ total: number; services: Service[] }>('/services');
  }

  async getService(id: number): Promise<Service> {
    return this.request<Service>(`/services/${id}`);
  }

  async executeServiceAction(serviceId: number, action: string): Promise<Service> {
    return this.request<Service>(`/services/${serviceId}/action`, {
      method: 'POST',
      body: JSON.stringify({ action })
    });
  }

  async getServiceMetrics(serviceId: number, limit = 30): Promise<{ service_id: number; service_name: string; samples: MetricSample[] }> {
    return this.request<{ service_id: number; service_name: string; samples: MetricSample[] }>(`/services/${serviceId}/metrics?limit=${limit}`);
  }

  // Incidents
  async getIncidents(): Promise<{ total: number; active_count: number; incidents: Incident[] }> {
    return this.request<{ total: number; active_count: number; incidents: Incident[] }>('/incidents');
  }

  async resolveIncident(incidentId: number): Promise<Incident> {
    return this.request<Incident>(`/incidents/${incidentId}/resolve`, {
      method: 'PATCH'
    });
  }

  // Recovery
  async getRecoveryHistory(): Promise<{ total: number; success_rate_percent: number; executions: RecoveryExecution[] }> {
    return this.request<{ total: number; success_rate_percent: number; executions: RecoveryExecution[] }>('/recovery/history');
  }

  async getRecoveryPolicies(): Promise<RecoveryPolicy[]> {
    return this.request<RecoveryPolicy[]>('/recovery/policies');
  }

  // Simulations
  async injectFault(serviceId: number, failureType: string, durationSeconds = 45): Promise<any> {
    return this.request('/simulations/inject', {
      method: 'POST',
      body: JSON.stringify({
        service_id: serviceId,
        failure_type: failureType,
        duration_seconds: durationSeconds
      })
    });
  }

  async resetSimulation(serviceId: number): Promise<any> {
    return this.request(`/simulations/${serviceId}/reset`, {
      method: 'POST'
    });
  }

  // Audit Logs
  async getAuditLogs(): Promise<{ total: number; logs: any[] }> {
    return this.request<{ total: number; logs: any[] }>('/audit-logs');
  }
}

export const api = new ApiService();
