// src/components/dashboard/details_dialog.tsx
import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Eye, ShieldAlert, User, Server, Hash, Activity } from "lucide-react";
import { PriorityBadge } from "./priority-badge";
import { StatusPill } from "./status-pill";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api/client";
import type { Ticket, Alert, WindowMetric, WindowMetricFull } from "@/lib/api/types";
import { JsonRecordsView, JsonRawView, PayloadSummaryView } from "@/lib/json-display";

type ExtensibleItem = (Alert | Ticket) & {
  notification_time?: string | null;
  window_metric_id?: number;
};

interface IncidentDetailsDialogProps {
  item: ExtensibleItem;
}

const PANEL =
  "h-[min(420px,50vh)] rounded-lg border border-border bg-card text-card-foreground";
const TAB_TRIGGER =
  "data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=inactive]:text-muted-foreground";

export function IncidentDetailsDialog({ item }: IncidentDetailsDialogProps) {
  const isAlert = "final_score" in item;

  const [isOpen, setIsOpen] = useState(false);
  const [metrics, setMetrics] = useState<(WindowMetric & Partial<WindowMetricFull>) | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && isAlert && item.window_metric_id) {
      setIsLoading(true);

      Promise.all([
        api.listWindowMetrics(),
        api.get_window_metric_details_by_id(item.window_metric_id),
      ])
        .then(([listData, detailsData]) => {
          const metricList: WindowMetric[] = Array.isArray(listData)
            ? listData
            : ((listData as { data?: WindowMetric[] })?.data ?? []);

          const matchedMetric = metricList.find((m) => m.id === item.window_metric_id);

          if (matchedMetric && detailsData) {
            setMetrics({
              ...matchedMetric,
              ...detailsData,
            });
          } else {
            setMetrics(matchedMetric || null);
          }
        })
        .catch((err) => {
          console.error("Failed to fetch combined window metrics:", err);
        })
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, isAlert, item.window_metric_id]);

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return `${formatDistanceToNow(new Date(dateStr), { addSuffix: true })} (${dateStr})`;
    } catch {
      return dateStr;
    }
  };

  const alertOverview = (
    <ScrollArea className={PANEL}>
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed text-foreground">
        {isLoading
          ? "Loading evaluation window metrics…"
          : `--- SentinelIQ Real-Time Alert Stream ---
[Target Node]     : ${item.service.toUpperCase()}
[Breach Severity] : ${item.priority.toUpperCase()}
[Log Event Time]  : ${item.created_at}

=== Evaluation Window Timeframe ===
• Window Start    : ${metrics?.window_start ? formatTime(metrics.window_start) : "No window tracking start timestamp linked"}
• Window End      : ${metrics?.window_end ? formatTime(metrics.window_end) : "No window tracking end timestamp linked"}

=== Metric Engine Aggregations ===
• Record Count    : ${metrics?.record_count ?? "N/A"} records evaluated
• Latency Profile : Mean: ${metrics?.latency_mean?.toFixed(2) ?? "N/A"}ms | Max: ${metrics?.latency_max?.toFixed(2) ?? "N/A"}ms
• Compute Load    : CPU Mean: ${metrics?.cpu_mean?.toFixed(1) ?? "N/A"}% | CPU Max: ${metrics?.cpu_max?.toFixed(1) ?? "N/A"}%
• Memory Profile  : Mean Usage: ${metrics?.memory_mean?.toFixed(1) ?? "N/A"}%
• Queue Backlog   : Mean Lag: ${metrics?.queue_lag_mean ?? "N/A"} | Max Lag: ${metrics?.queue_lag_max ?? "N/A"}
• Error Count     : ${metrics?.error_count ?? 0} errors logged in window

=== Engine Vector Analysis ===
• ML Model Score          : ${metrics?.ml_score?.toFixed(4) ?? "N/A"}
• Final Statistical Score : ${metrics?.statistical_score?.toFixed(4) ?? "N/A"}
• Final Weighted Score    : ${metrics?.final_score?.toFixed(4) ?? "N/A"}
• Prediction Flag         : State Code [${metrics?.prediction ?? "0"}]`}
      </pre>
    </ScrollArea>
  );

  const ticketOverview = (
    <ScrollArea className={PANEL}>
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed text-foreground">
        {`[SYSTEM CORRELATION]
An incident workflow state has been initialized targeting the "${SERVICE_LABELS[item.service] ?? item.service}" service layer.

• Alert Context ID  : ${"alert_id" in item ? item.alert_id || "None linked" : "None linked"}
• Assigned Analyst  : ${"assignee" in item ? item.assignee || "Unassigned (Triage Required)" : "Unassigned"}
• Dispatch Status   : Notification sent ${item.notification_time ? formatTime(item.notification_time) : "Pending"}
• Ticket Reference  : #${"ticket_id" in item ? item.ticket_id || item.id : item.id}

No manual engineering notes have been appended yet.`}
      </pre>
    </ScrollArea>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button
          className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-md transition-colors cursor-pointer flex items-center justify-center"
          title="Open Diagnostics Pane"
        >
          <Eye className="w-4 h-4" />
        </button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-3xl max-h-[85vh] overflow-y-auto gap-5 bg-background text-foreground">
        <DialogHeader className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <PriorityBadge priority={item.priority} />
            <StatusPill status={item.status} />
          </div>
          <DialogTitle className="text-xl font-semibold tracking-tight flex items-center gap-2">
            {isAlert ? (
              <Activity className="w-5 h-5 text-amber-500" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-red-500" />
            )}
            {isAlert ? "Alert Threat Telemetry" : "Incident Ticket Logs"}: #{item.id}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4 border-y border-border py-4 text-sm">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Target Domain Service</p>
              <p className="font-medium text-foreground">
                {SERVICE_LABELS[item.service] ?? item.service}
              </p>
            </div>
          </div>

          {isAlert ? (
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
              <div>
                <p className="text-xs text-muted-foreground">Anomaly Engine Score</p>
                <p className="font-mono font-semibold text-amber-500">
                  {item.final_score.toFixed(3)}
                </p>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Ticket Reference</p>
                  <p className="font-mono font-medium text-foreground">
                    {"ticket_id" in item ? item.ticket_id || "N/A" : "N/A"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 col-span-2 sm:col-span-1">
                <User className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Assigned Analyst</p>
                  <p className="font-medium text-foreground">
                    {"assignee" in item ? item.assignee || "Unassigned" : "Unassigned"}
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {isAlert ? (
          <Tabs defaultValue="overview" className="w-full min-w-0">
            <TabsList className="grid w-full grid-cols-4 h-auto gap-1 bg-muted/80 p-1">
              <TabsTrigger value="overview" className={TAB_TRIGGER}>
                Overview
              </TabsTrigger>
              <TabsTrigger value="summary" className={TAB_TRIGGER}>
                Summary
              </TabsTrigger>
              <TabsTrigger value="records" className={TAB_TRIGGER}>
                Records
              </TabsTrigger>
              <TabsTrigger value="raw" className={`${TAB_TRIGGER} text-[11px] sm:text-sm px-1 sm:px-3`}>
                Telemetry Details
              </TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="mt-3">
              {alertOverview}
            </TabsContent>
            <TabsContent value="summary" className="mt-3">
              <ScrollArea className={`${PANEL} pr-3`}>
                <div className="p-3">
                  {isLoading ? (
                    <p className="text-sm text-muted-foreground py-6 text-center">Loading summary…</p>
                  ) : (
                    <PayloadSummaryView
                      value={metrics?.payload_summary}
                      emptyLabel="No telemetry summary linked"
                    />
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="records" className="mt-3">
              <ScrollArea className={`${PANEL} pr-3`}>
                <div className="p-3">
                  {isLoading ? (
                    <p className="text-sm text-muted-foreground py-6 text-center">Loading records…</p>
                  ) : (
                    <JsonRecordsView value={metrics?.payload_json} />
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="raw" className="mt-3 space-y-3">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                  Payload Summary
                </h4>
                <JsonRawView value={metrics?.payload_summary} />
              </div>
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
                  Payload JSON
                </h4>
                <JsonRawView value={metrics?.payload_json} />
              </div>
            </TabsContent>
          </Tabs>
        ) : (
          <Tabs defaultValue="overview" className="w-full min-w-0">
            <TabsList className="grid w-full grid-cols-3 h-auto gap-1 bg-muted/80 p-1">
              <TabsTrigger value="overview" className={TAB_TRIGGER}>
                Overview
              </TabsTrigger>
              <TabsTrigger value="summary" className={TAB_TRIGGER}>
                Summary
              </TabsTrigger>
              <TabsTrigger value="raw" className={`${TAB_TRIGGER} text-[11px] sm:text-sm px-1 sm:px-3`}>
                Telemetry Details
              </TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="mt-3">
              {ticketOverview}
            </TabsContent>
            <TabsContent value="summary" className="mt-3">
              <ScrollArea className={`${PANEL} pr-3`}>
                <div className="p-3">
                  <PayloadSummaryView
                    value={"incident_summary" in item ? item.incident_summary : null}
                    emptyLabel="No incident summary linked"
                  />
                </div>
              </ScrollArea>
            </TabsContent>
            <TabsContent value="raw" className="mt-3">
              <JsonRawView
                value={"incident_summary" in item ? item.incident_summary : null}
              />
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
