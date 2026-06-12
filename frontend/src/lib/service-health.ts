import type { Alert, Priority } from "./api/types";

export function getServiceHealth(
  service: string,
  alerts: Alert[],
  priority: Priority
): Priority {

  const openAlerts = alerts.filter(
    a => a.service === service && a.status === "OPEN"
  );

  if (openAlerts.some(a => a.priority === "Critical"))
    return "Critical";

  if (openAlerts.some(a => a.priority === "High"))
    return "High";

  if (openAlerts.some(a => a.priority === "Medium"))
    return "Medium";

  return priority;
}