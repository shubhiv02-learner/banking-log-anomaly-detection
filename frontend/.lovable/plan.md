
## SentinelIQ — Observability Dashboard

React + TypeScript + Tailwind observability platform. Placeholder data layer is shaped 1:1 against the future FastAPI schema so integration is a swap of the data source, not a refactor.

### Design direction
- Operations-center aesthetic: dense, data-forward, restrained
- Neutral slate palette + single accent
- Semantic colors for priority (Critical / High / Medium / Low) and health status
- Light + dark themes via existing CSS tokens; toggle persisted to `localStorage`
- Inter for UI, JetBrains Mono for numbers

### Layout
Shared shell rendered by pathless layout `_app.tsx`:
- **Sidebar** (collapsible): brand, primary nav, user block at bottom
- **Topbar**: page title, global search, env badge, notifications, theme toggle, user menu
- **Content**: `<Outlet />`; mobile sidebar collapses into a Sheet

### Routes
- `_app.tsx` — layout
- `_app.index.tsx` → `/` Executive Dashboard
- `_app.alerts.tsx` → `/alerts` Alerts Center
- `_app.analytics.tsx` → `/analytics` Service Analytics

### Data contracts (FastAPI-aligned)

`src/lib/api/types.ts` — single source of truth, reused by mocks today and the HTTP client tomorrow:

```ts
export type Priority = "Critical" | "High" | "Medium" | "Low";

export type AlertStatus = "OPEN" | "ACKNOWLEDGED" | "RESOLVED";

export interface Alert {
  id: number;
  service: string;
  priority: Priority;
  final_score: number;     // 0..1
  status: AlertStatus;
  created_at: string;      // ISO 8601 UTC
}

export interface WindowMetric {
  id: number;
  service: string;
  window_start: string;    // ISO 8601
  window_end: string;      // ISO 8601
  record_count: number;
  latency_mean: number;    // ms
  latency_max: number;     // ms
  cpu_mean: number;        // 0..1
  cpu_max: number;         // 0..1
  memory_mean: number;     // 0..1
  queue_lag_mean: number;
  queue_lag_max: number;
  error_count: number;
  ml_score: number;        // 0..1
  statistical_score: number; // 0..1
  final_score: number;     // 0..1
  prediction: number;      // 0 | 1
  priority: Priority;
}
```

Notes:
- snake_case matches Pydantic; `id: number` matches a SQL PK
- Dates are ISO strings (JSON), not `Date`
- Scores stay 0..1; formatting (%) happens in the UI only

### Mock layer

`src/lib/api/placeholder-data.ts` exposes functions shaped like the future client:
- `listAlerts(): Alert[]`
- `listWindowMetrics(): WindowMetric[]` — latest window per service
- `getServiceTrend(service: string): WindowMetric[]` — time-bucketed history
- `listServices(): string[]`

Later: swap implementations to `fetch("/api/...")` returning the same types — components untouched.

### Health derivation (shared util)

`src/lib/health.ts`:

```ts
export type HealthStatus = "Healthy" | "Medium" | "High" | "Critical";

// Drives the System Health Overview tiles + service grids.
// Uses the latest WindowMetric.priority per service; "Low" → "Healthy".
export function priorityToHealth(p: Priority): HealthStatus;
```

Color tokens per status added to `src/styles.css`:
- `--health-healthy` (green), `--health-medium` (amber), `--health-high` (orange), `--health-critical` (red)

### Pages (placeholder data)

**Executive Dashboard**
- 4 KPI cards:
  - **Total Alerts** — `alerts.length`
  - **Critical Alerts** — count where `priority === "Critical"`
  - **Services Monitored** — distinct services in window metrics
  - **Average Risk Score** — mean of latest `final_score` across services
- **System Health Overview** — colored grid, one tile per service, derived from the latest `WindowMetric.priority` for that service:
  ```text
  Auth Service        Healthy
  Payment API         Critical
  Fraud Detection     High
  Trading Engine      Medium
  ```
  Tile background tinted with the matching health token; status label on the right; latest `final_score` shown small.
- Anomaly score trend chart (aggregate across services, last 24 windows)
- Recent alerts table (top 5 by `created_at`)

**Alerts Center**
- Filter bar: priority, status, service, search by id/service
- Priority summary tiles (Critical / High / Medium / Low counts)
- Alerts table: `id`, `service`, `priority` badge, `final_score`, `status`, `created_at` (relative + tooltip)
- Row click → side drawer with raw JSON

**Service Analytics**
- Service selector + time-range tabs (1h / 24h / 7d)
- Five trend charts driven by `getServiceTrend(service)`, x-axis = `window_start`:
  - **Latency Trend** — `latency_mean`
  - **CPU Utilization Trend** — `cpu_mean`
  - **Memory Utilization Trend** — `memory_mean`
  - **Queue Lag Trend** — `queue_lag_mean`
  - **Anomaly Score Trend** — `final_score`
- Current-window summary card (latest `WindowMetric` for selected service: max values, error count, prediction, priority)

### Reusable components
- `layout/app-sidebar.tsx`, `layout/app-topbar.tsx`, `layout/page-header.tsx`
- `theme/theme-provider.tsx`, `theme/theme-toggle.tsx`
- `dashboard/kpi-card.tsx`
- `dashboard/priority-badge.tsx` (typed on `Priority`)
- `dashboard/status-pill.tsx` (typed on `AlertStatus`)
- `dashboard/health-tile.tsx` (consumes `HealthStatus`)
- `dashboard/score-meter.tsx` (renders 0..1 → colored bar/percent)
- `dashboard/trend-chart.tsx` (reusable line/area, takes `WindowMetric[]` + `dataKey`)
- `dashboard/data-table.tsx` (thin wrapper over shadcn Table)

### Technical notes
- `recharts` already present
- Class-based dark mode (`.dark` on `<html>`); theme persisted to `localStorage("sentineliq-theme")`
- All colors via semantic tokens in `src/styles.css`; new tokens: `--priority-*` and `--health-*`
- No network calls — all data from `placeholder-data.ts` with a deterministic seed
- TanStack file-route naming (`_app.*.tsx`) with `<Outlet />` in layout
