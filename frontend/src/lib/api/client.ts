import type { Alert, WindowMetric,Ticket, WindowMetricFull } from "./types";

const BASE_URL = ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "").trim();

/** Join base + path without producing `//` before the endpoint. */
function joinApiUrl(base: string, path: string): string {
  const normalizedBase = base.replace(/\/+$/, "");
  const normalizedPath = path.replace(/^\/+/, "");
  if (!normalizedBase) return `/${normalizedPath}`;
  return `${normalizedBase}/${normalizedPath}`;
}

async function http<T>(path: string): Promise<T> {
  const res = await fetch(joinApiUrl(BASE_URL, path), {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status} ${res.statusText} — ${path}`);
  }
  return res.json() as Promise<T>;
}

export interface DashboardSummary {
  total_alerts: number;
  critical: number;
  high: number;
  medium: number
  }
export interface IncidentsSummary {
  total_incidents: number;
  critical: number;
  high: number;
  medium: number
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
  listTickets: () => http<Ticket[]>("/tickets"),
  serviceTrend: (service: string) =>
    http<WindowMetric[]>(`/window-metrics/service/${encodeURIComponent(service)}`),
  getWindowMetric: (id: number) => http<WindowMetric>(`/window-metrics/${id}`),
  get_incidents_by_id: (id: number) => http<Ticket>(`/tickets/${id}`),
  get_window_metric_details_by_id: (id: number) => http<WindowMetricFull>(`/window-metrics/details/${id}`),
};

export function serviceLabel(service: string): string {
  return service
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
