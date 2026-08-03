import type { AlertStatus } from "@/lib/api/types";

const STYLES: Record<AlertStatus, string> = {
  OPEN: "bg-red-500/15 text-red-700 dark:text-red-300",
  ASSIGNED: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  RESOLVED: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  CLOSED: "bg-slate-500/15 text-slate-700 dark:text-slate-300",
};

export function StatusPill({
  status,
  label,
}: {
  status: AlertStatus;
  /** Optional display override. */
  label?: string;
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide ${STYLES[status] ?? STYLES.OPEN}`}
    >
      {label ?? status}
    </span>
  );
}
