import type { AlertStatus } from "@/lib/api/types";

const STYLES: Record<AlertStatus, string> = {
  OPEN: "bg-red-500/15 text-red-700 dark:text-red-300",
  ACKNOWLEDGED: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  RESOLVED: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
};

export function StatusPill({
  status,
  label,
}: {
  status: AlertStatus;
  /** Optional display override (e.g. ASSIGNED for ACKNOWLEDGED on incidents). */
  label?: string;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide ${STYLES[status]}`}
    >
      {label ?? status}
    </span>
  );
}

export function statusDisplayLabel(
  status: AlertStatus,
  mode: "alerts" | "incidents" = "alerts",
): string {
  if (mode === "incidents" && status === "ACKNOWLEDGED") return "ASSIGNED";
  return status;
}
