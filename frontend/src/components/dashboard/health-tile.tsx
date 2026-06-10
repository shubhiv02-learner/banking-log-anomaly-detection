import { HEALTH_STYLES, priorityToHealth } from "@/lib/health";
import type { Priority } from "@/lib/api/types";

export function HealthTile({
  service,
  priority,
  score,
}: {
  service: string;
  priority: Priority;
  score: number;
}) {
  const status = priorityToHealth(priority);
  const s = HEALTH_STYLES[status];
  return (
    <div
      className={`flex items-center justify-between rounded-md border p-3 ${s.bg}`}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <span className={`h-2 w-2 shrink-0 rounded-full ${s.dot}`} />
        <div className="min-w-0">
          <p className="truncate text-sm font-medium">{service}</p>
          <p className="font-mono text-[10px] text-muted-foreground">
            score {score.toFixed(2)}
          </p>
        </div>
      </div>
      <span className={`text-xs font-semibold ${s.text}`}>{s.label}</span>
    </div>
  );
}
