import type { Alert, AlertStatus, Priority, WindowMetric } from "./types";

// Deterministic PRNG so charts/tables are stable between renders.
function mulberry32(seed: number) {
  let a = seed;
  return () => {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const SERVICES = [
  "auth-service",
  "payment-api",
  "fraud-detection",
  "trading-engine",
  "notification-service",
  "ledger-service",
] as const;

export const SERVICE_LABELS: Record<string, string> = {
  "auth-service": "Auth Service",
  "payment-api": "Payment API",
  "fraud-detection": "Fraud Detection",
  "trading-engine": "Trading Engine",
  "notification-service": "Notification Service",
  "ledger-service": "Ledger Service",
};

function scoreToPriority(score: number): Priority {
  if (score >= 0.85) return "Critical";
  if (score >= 0.65) return "High";
  if (score >= 0.4) return "Medium";
  return "Low";
}

// Force a specific health distribution for the demo, so the System Health
// Overview always shows a mix of Healthy / Medium / High / Critical tiles.
const FORCED_LATEST_SCORE: Record<string, number> = {
  "auth-service": 0.18,
  "payment-api": 0.93,
  "fraud-detection": 0.74,
  "trading-engine": 0.52,
  "notification-service": 0.28,
  "ledger-service": 0.81,
};

const NOW = new Date("2026-06-10T12:00:00Z").getTime();
const WINDOW_MS = 5 * 60 * 1000; // 5-minute buckets
const HISTORY_WINDOWS = 48;

function buildTrend(service: string): WindowMetric[] {
  const rand = mulberry32(
    service.split("").reduce((a, c) => a + c.charCodeAt(0), 0),
  );
  const baseLatency = 60 + rand() * 180;
  const baseCpu = 0.25 + rand() * 0.3;
  const baseMem = 0.35 + rand() * 0.3;
  const baseQueue = 50 + rand() * 400;
  const targetLatest = FORCED_LATEST_SCORE[service] ?? rand();

  const out: WindowMetric[] = [];
  for (let i = HISTORY_WINDOWS - 1; i >= 0; i--) {
    const isLatest = i === 0;
    const start = NOW - (i + 1) * WINDOW_MS;
    const end = NOW - i * WINDOW_MS;
    const noise = (rand() - 0.5) * 0.2;

    const latency_mean = Math.max(10, baseLatency + noise * baseLatency);
    const latency_max = latency_mean * (1.3 + rand() * 0.6);
    const cpu_mean = Math.min(1, Math.max(0.02, baseCpu + noise * 0.4));
    const cpu_max = Math.min(1, cpu_mean + rand() * 0.2);
    const memory_mean = Math.min(1, Math.max(0.05, baseMem + noise * 0.3));
    const queue_lag_mean = Math.max(0, baseQueue + noise * baseQueue);
    const queue_lag_max = queue_lag_mean * (1.2 + rand() * 0.8);

    const ml_score = Math.min(
      1,
      Math.max(0, 0.4 + noise + (cpu_mean - 0.5) * 0.4),
    );
    const statistical_score = Math.min(
      1,
      Math.max(0, 0.4 + noise * 0.8 + (memory_mean - 0.5) * 0.4),
    );
    let final_score = (ml_score + statistical_score) / 2;
    if (isLatest) final_score = targetLatest;

    const priority = scoreToPriority(final_score);

    out.push({
      id: i + 1 + service.length * 1000,
      service,
      window_start: new Date(start).toISOString(),
      window_end: new Date(end).toISOString(),
      record_count: Math.floor(800 + rand() * 4000),
      latency_mean: Number(latency_mean.toFixed(2)),
      latency_max: Number(latency_max.toFixed(2)),
      cpu_mean: Number(cpu_mean.toFixed(4)),
      cpu_max: Number(cpu_max.toFixed(4)),
      memory_mean: Number(memory_mean.toFixed(4)),
      queue_lag_mean: Number(queue_lag_mean.toFixed(2)),
      queue_lag_max: Number(queue_lag_max.toFixed(2)),
      error_count: Math.floor(rand() * (final_score > 0.7 ? 80 : 10)),
      ml_score: Number(ml_score.toFixed(4)),
      statistical_score: Number(statistical_score.toFixed(4)),
      final_score: Number(final_score.toFixed(4)),
      prediction: final_score >= 0.6 ? 1 : 0,
      priority,
    });
  }
  // Sort oldest → newest for charts.
  return out.reverse();
}

const TRENDS: Record<string, WindowMetric[]> = Object.fromEntries(
  SERVICES.map((s) => [s, buildTrend(s)]),
);

const ALERTS: Alert[] = (() => {
  const rand = mulberry32(42);
  const statuses: AlertStatus[] = ["OPEN", "ACKNOWLEDGED", "RESOLVED"];
  const items: Alert[] = [];
  let id = 1001;
  for (const service of SERVICES) {
    const trend = TRENDS[service];
    // Promote any window with high score into an alert.
    for (const w of trend) {
      if (w.final_score >= 0.55) {
        items.push({
          id: id++,
          service,
          priority: w.priority,
          final_score: w.final_score,
          status:
            w.priority === "Critical"
              ? "OPEN"
              : statuses[Math.floor(rand() * statuses.length)],
          created_at: w.window_end,
        });
      }
    }
  }
  return items.sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );
})();

// Future API surface — swap to fetch() later, signatures stay identical.

export function listAlerts(): Alert[] {
  return ALERTS;
}

export function listServices(): string[] {
  return [...SERVICES];
}

export function listWindowMetrics(): WindowMetric[] {
  // Latest window per service.
  return SERVICES.map((s) => TRENDS[s][TRENDS[s].length - 1]);
}

export function getServiceTrend(service: string): WindowMetric[] {
  return TRENDS[service] ?? [];
}
