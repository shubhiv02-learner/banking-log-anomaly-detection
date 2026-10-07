// src/components/dashboard/details_dialog.tsx
import { useState, useEffect, useMemo } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  /** Latest incident rows. When set, the open dialog follows this list by id. */
  tickets?: Ticket[];
}

function ticketNotes(ticket: Ticket): string {
  const lines: string[] = [];
  if (ticket.resolution?.trim()) {
    lines.push(`• Resolution        : ${ticket.resolution.trim()}`);
  }
  if (ticket.preventive_action?.trim()) {
    lines.push(`• Preventive Action : ${ticket.preventive_action.trim()}`);
  }
  if (lines.length === 0) {
    return "No manual engineering notes have been appended yet.";
  }
  return lines.join("\n");
}

const PANEL =
  "h-[min(420px,50vh)] overflow-auto rounded-lg border border-border bg-card text-card-foreground [scrollbar-gutter:stable_both-edges] [scrollbar-width:thin]";
const TAB_TRIGGER =
  "data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=inactive]:text-muted-foreground";

export function IncidentDetailsDialog({ item, tickets }: IncidentDetailsDialogProps) {
  const displayItem = useMemo(() => {
    if (!tickets) return item;
    return tickets.find((ticket) => ticket.id === item.id) ?? item;
  }, [item, tickets]);
  const isAlert = "final_score" in displayItem;

  const [isOpen, setIsOpen] = useState(false);
  const [metrics, setMetrics] = useState<(WindowMetric & Partial<WindowMetricFull>) | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen && isAlert && displayItem.window_metric_id) {
      setIsLoading(true);

      Promise.all([
        api.listWindowMetrics(),
        api.get_window_metric_details_by_id(displayItem.window_metric_id),
      ])
        .then(([listData, detailsData]) => {
          const metricList: WindowMetric[] = Array.isArray(listData)
            ? listData
            : ((listData as { data?: WindowMetric[] })?.data ?? []);

          const matchedMetric = metricList.find((m) => m.id === displayItem.window_metric_id);

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
  }, [isOpen, isAlert, displayItem.window_metric_id]);

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return `${formatDistanceToNow(new Date(dateStr), { addSuffix: true })} (${dateStr})`;
    } catch {
      return dateStr;
    }
  };

  const alertOverview = (
    <div className={PANEL}>
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed text-foreground">
        {isLoading
          ? "Loading evaluation window metrics…"
          : `--- SentinelIQ Real-Time Alert Stream ---
[Target Node]     : ${displayItem.service.toUpperCase()}
[Breach Severity] : ${displayItem.priority.toUpperCase()}
[Log Event Time]  : ${displayItem.created_at}

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
    </div>
  );

  const ticketOverview = (
    <div className={PANEL}>
      <pre className="p-4 text-xs font-mono whitespace-pre-wrap leading-relaxed text-foreground">
        {`[SYSTEM CORRELATION]
An incident workflow state has been initialized targeting the "${SERVICE_LABELS[displayItem.service] ?? displayItem.service}" service layer.

• Alert Context ID  : ${"alert_id" in displayItem ? displayItem.alert_id || "None linked" : "None linked"}
• Assigned Analyst  : ${"assignee" in displayItem ? displayItem.assignee || "Unassigned (Triage Required)" : "Unassigned"}
• Workflow Status   : ${displayItem.status}
• Dispatch Status   : Notification sent ${displayItem.notification_time ? formatTime(displayItem.notification_time) : "Pending"}
• Ticket Reference  : #${"ticket_id" in displayItem ? displayItem.ticket_id || displayItem.id : displayItem.id}

${"resolution" in displayItem ? ticketNotes(displayItem) : "No manual engineering notes have been appended yet."}`}
      </pre>
    </div>
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

      <DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-y-auto gap-5 bg-background text-foreground border-2 border-primary/40 shadow-2xl ring-2 ring-foreground/25">
        <DialogHeader className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <PriorityBadge priority={displayItem.priority} />
            <StatusPill status={displayItem.status} />
          </div>
          <DialogTitle className="text-xl font-semibold tracking-tight flex items-center gap-2">
            {isAlert ? (
              <Activity className="w-5 h-5 text-amber-500" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-red-500" />
            )}
            {isAlert ? "Alert Threat Telemetry" : "Incident Ticket Logs"}: #{displayItem.id}
          </DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4 border-y border-border py-4 text-sm">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Target Domain Service</p>
              <p className="font-medium text-foreground">
                {SERVICE_LABELS[displayItem.service] ?? displayItem.service}
              </p>
            </div>
          </div>

          {isAlert ? (
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
              <div>
                <p className="text-xs text-muted-foreground">Anomaly Engine Score</p>
                <p className="font-mono font-semibold text-amber-500">
                  {displayItem.final_score.toFixed(3)}
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
                    {"ticket_id" in displayItem ? displayItem.ticket_id || "N/A" : "N/A"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 col-span-2 sm:col-span-1">
                <User className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Assigned Analyst</p>
                  <p className="font-medium text-foreground">
                    {"assignee" in displayItem ? displayItem.assignee || "Unassigned" : "Unassigned"}
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
              <div className={`${PANEL} pr-1`}>
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
              </div>
            </TabsContent>
            <TabsContent value="records" className="mt-3">
              <div className={`${PANEL} pr-1`}>
                <div className="p-3">
                  {isLoading ? (
                    <p className="text-sm text-muted-foreground py-6 text-center">Loading records…</p>
                  ) : (
                    <JsonRecordsView value={metrics?.payload_json} />
                  )}
                </div>
              </div>
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
              <div className={`${PANEL} pr-1`}>
                <div className="p-3">
                  <PayloadSummaryView
                    value={"incident_summary" in displayItem ? displayItem.incident_summary : null}
                    emptyLabel="No incident summary linked"
                  />
                </div>
              </div>
            </TabsContent>
            <TabsContent value="raw" className="mt-3">
              <JsonRawView
                value={"incident_summary" in displayItem ? displayItem.incident_summary : null}
              />
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}
