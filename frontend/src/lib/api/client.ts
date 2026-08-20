import type { Alert, WindowMetric, Ticket, WindowMetricFull } from "./types";
import { clearSession, getAccessToken } from "@/lib/auth-storage";

const BASE_URL = ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "").trim();

/** Join base + path without producing `//` before the endpoint. */
function joinApiUrl(base: string, path: string): string {
  const normalizedBase = base.replace(/\/+$/, "");
  const normalizedPath = path.replace(/^\/+/, "");
  if (!normalizedBase) return `/${normalizedPath}`;
  return `${normalizedBase}/${normalizedPath}`;
}

function authHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return headers;
}

function redirectToLoginIfUnauthorized(status: number, path: string): void {
  if (status !== 401) return;
  if (path === "/auth/login") return;
  clearSession();
  if (typeof window === "undefined") return;
  if (window.location.pathname !== "/login") {
    window.location.assign("/login");
  }
}

async function http<T>(path: string): Promise<T> {
  const res = await fetch(joinApiUrl(BASE_URL, path), {
    headers: authHeaders(),
  });
  if (!res.ok) {
    redirectToLoginIfUnauthorized(res.status, path);
    throw new Error(`API ${res.status} ${res.statusText} — ${path}`);
  }
  return res.json() as Promise<T>;
}

async function httpPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(joinApiUrl(BASE_URL, path), {
    method: "POST",
    headers: authHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    redirectToLoginIfUnauthorized(res.status, path);
    let detail = `${res.status} ${res.statusText}`;
    try {
      const errBody = (await res.json()) as {
        detail?: string | { msg?: string }[];
      };
      if (typeof errBody?.detail === "string") {
        detail = errBody.detail;
      } else if (Array.isArray(errBody?.detail) && errBody.detail[0]?.msg) {
        detail = errBody.detail.map((item) => item.msg).filter(Boolean).join(" ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(
      path === "/auth/login" || path === "/tickets/assign"
        ? detail
        : `API ${detail} — ${path}`,
    );
  }
  return res.json() as Promise<T>;
}

export interface DashboardSummary {
  total_alerts: number;
  critical: number;
  high: number;
  medium: number;
}
export interface IncidentsSummary {
  total_incidents: number;
  critical: number;
  high: number;
  medium: number;
}
export interface ServiceCount {
  service: string;
  count: number;
}

export interface CopilotContext {
  service?: string;
  route?: string;
  ticket_id?: string;
}

export interface EvidenceHit {
  title: string;
  snippet?: string | null;
  score?: number | null;
  source?: string | null;
  document_id?: string | null;
}

export interface CopilotSearchResponse {
  hits: EvidenceHit[];
}

export interface SourceRef {
  title: string;
  snippet?: string | null;
  source?: string | null;
}

export interface CopilotAskResponse {
  answer: string;
  confidence?: string | null;
  sources: SourceRef[];
}

export interface AuthUser {
  user_id: number;
  name: string;
  email: string;
  role: string | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface DashboardUser {
  user_id: number;
  name: string;
  email: string;
  role: string | null;
}

export type IncidentAction = "ASSIGNED" | "RESOLVED" | "CLOSED";

export interface IncidentActionRequest {
  ticket_id: string;
  action: IncidentAction;
  assigned_to?: string;
  remarks?: string;
  closure_remark?: string;
  preventive_action?: string;
}

export interface IncidentActionResponse {
  action: IncidentAction;
  message: string;
  ticket_id: string;
  status: string;
  assignee: string | null;
}

export const api = {
  health: () => http<{ status: string }>("/health"),
  login: (email: string, password: string) =>
    httpPost<LoginResponse>("/auth/login", { email, password }),
  me: () => http<AuthUser>("/auth/me"),
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
  get_window_metric_details_by_id: (id: number) =>
    http<WindowMetricFull>(`/window-metrics/details/${id}`),
  copilotSearch: (question: string, context?: CopilotContext) =>
    httpPost<CopilotSearchResponse>("/copilot/search", { question, context }),
  copilotAsk: (question: string, context?: CopilotContext) =>
    httpPost<CopilotAskResponse>("/copilot/ask", { question, context }),
  listUsers: () => http<DashboardUser[]>("/users"),
  updateIncident: (body: IncidentActionRequest) =>
    httpPost<IncidentActionResponse>("/tickets/assign", body),
};

export function serviceLabel(service: string): string {
  return service
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
