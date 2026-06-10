import type { Alert, WindowMetric } from "./types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "";

async function http<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText} — ${path}`);
  }
  return res.json() as Promise<T>;
}

export interface DashboardSummary {
  total_alerts: number;
  critical_alerts: number;
  services_monitored: number;
  avg_risk_score: number;
}
export interface ServiceCount {
  service: string;
  count: number;
}
export const api = {
  health: () => http<{ status: string }>("/health"),
  dashboardSummary: () => http<DashboardSummary>("/dashboard/summary"),
  listAlerts: () => http<Alert[]>("/alerts"),
  recentAlerts: () => http<Alert[]>("/alerts/recent"),
  getAlert: (id: number) => http<Alert>(`/alerts/${id}`),
  listServices: () => http<ServiceCount[]>("/analytics/services"),
  listWindowMetrics: () => http<WindowMetric[]>("/window-metrics"),
  recentWindowMetrics: () => http<WindowMetric[]>("/window-metrics/recent"),
  serviceTrend: (service: string) =>
    http<WindowMetric[]>(`/window-metrics/service/${encodeURIComponent(service)}`),
  getWindowMetric: (id: number) => http<WindowMetric>(`/window-metrics/${id}`),
};

export function serviceLabel(service: string): string {
  return service
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
