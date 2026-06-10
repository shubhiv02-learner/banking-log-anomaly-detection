import type { Priority } from "./api/types";

export type HealthStatus = "Healthy" | "Medium" | "High" | "Critical";

export function priorityToHealth(p: Priority): HealthStatus {
  if (p === "Low") return "Healthy";
  return p;
}

export const HEALTH_STYLES: Record<
  HealthStatus,
  { bg: string; text: string; dot: string; label: string }
> = {
  Healthy: {
    bg: "bg-emerald-500/10 border-emerald-500/30",
    text: "text-emerald-600 dark:text-emerald-400",
    dot: "bg-emerald-500",
    label: "Healthy",
  },
  Medium: {
    bg: "bg-amber-500/10 border-amber-500/30",
    text: "text-amber-600 dark:text-amber-400",
    dot: "bg-amber-500",
    label: "Medium",
  },
  High: {
    bg: "bg-orange-500/10 border-orange-500/30",
    text: "text-orange-600 dark:text-orange-400",
    dot: "bg-orange-500",
    label: "High",
  },
  Critical: {
    bg: "bg-red-500/10 border-red-500/40",
    text: "text-red-600 dark:text-red-400",
    dot: "bg-red-500",
    label: "Critical",
  },
};

export const PRIORITY_STYLES: Record<Priority, string> = {
  Critical:
    "bg-red-500/15 text-red-700 dark:text-red-300 border border-red-500/30",
  High: "bg-orange-500/15 text-orange-700 dark:text-orange-300 border border-orange-500/30",
  Medium:
    "bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30",
  Low: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30",
};
