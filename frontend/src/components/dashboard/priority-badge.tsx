import { PRIORITY_STYLES } from "@/lib/health";
import type { Priority } from "@/lib/api/types";

export function PriorityBadge({ priority }: { priority: Priority }) {
  return (
    <span
      className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium ${PRIORITY_STYLES[priority]}`}
    >
      {priority}
    </span>
  );
}
