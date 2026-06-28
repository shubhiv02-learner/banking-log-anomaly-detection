// src/components/dashboard/details_dialog.tsx
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Eye, ShieldAlert, Clock, User, Server, Hash, FileText, Activity } from "lucide-react";
import { PriorityBadge } from "./priority-badge";
import { StatusPill } from "./status-pill";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import { formatDistanceToNow } from "date-fns";
import { api } from "@/lib/api/client"; // 👈 IMPORT THE API INSTANCE
import type { Ticket, Alert, WindowMetric } from "@/lib/api/types";

type ExtensibleItem = (Alert | Ticket) & {
  notification_time?: string;
  window_metric_id?: number; // Ensure this relation key is visible
};

interface IncidentDetailsDialogProps {
  item: ExtensibleItem;
}

export function IncidentDetailsDialog({ item }: IncidentDetailsDialogProps) {
  const isAlert = "final_score" in item;
  
  // Local state to manage dialog open state and local metric fetching
  const [isOpen, setIsOpen] = useState(false);
  const [metrics, setMetrics] = useState<WindowMetric | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Only fetch metrics if the dialog is open, it's an alert, and we have a target id
    if (isOpen && isAlert && item.window_metric_id) {
      setIsLoading(true);
      api.listWindowMetrics()
        .then((data) => {
          const metricList: WindowMetric[] = Array.isArray(data) ? data : (data as any)?.data ?? [];
          // Find the single metric node where id matches your alert's foreign key reference
          const matchedMetric = metricList.find((m) => m.id === item.window_metric_id);
          setMetrics(matchedMetric || null);
        })
        .catch((err) => console.error("Failed to map window metrics reference:", err))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen, isAlert, item.window_metric_id]);

  const formatTime = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return `${formatDistanceToNow(new Date(dateStr), { addSuffix: true })} (${dateStr})`;
    } catch (e) {
      return dateStr;
    }
  };

  return (
    /* Bind controlled open attributes to sync local lifecycle checks */
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <button 
          className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-md transition-colors cursor-pointer flex items-center justify-center" 
          title="Open Diagnostics Pane"
        >
          <Eye className="w-4 h-4" />
        </button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[550px] gap-6">
        <DialogHeader className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <PriorityBadge priority={item.priority} />
            <StatusPill status={item.status} />
          </div>
          <DialogTitle className="text-xl font-semibold tracking-tight flex items-center gap-2">
            {isAlert ? <Activity className="w-5 h-5 text-amber-500" /> : <ShieldAlert className="w-5 h-5 text-red-500" />}
            {isAlert ? "Alert Threat Telemetry" : "Incident Ticket Logs"}: #{item.id}
          </DialogTitle>
        </DialogHeader>

        {/* Structural Info Grid */}
        <div className="grid grid-cols-2 gap-4 border-y border-border py-4 text-sm">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Target Domain Service</p>
              <p className="font-medium">{SERVICE_LABELS[item.service] ?? item.service}</p>
            </div>
          </div>

          {isAlert ? (
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
              <div>
                <p className="text-xs text-muted-foreground">Anomaly Engine Score</p>
                <p className="font-mono font-semibold text-amber-500">{item.final_score.toFixed(3)}</p>
              </div>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Ticket Reference</p>
                  <p className="font-mono font-medium">{item.ticket_id || "N/A"}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Assigned Analyst</p>
                  <p className="font-medium">{item.assignee || "Unassigned"}</p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Telemetry Output Display Area */}
        <div className="space-y-2">
          <div className="bg-muted p-4 rounded-lg border text-xs font-mono whitespace-pre-wrap leading-relaxed max-h-[320px] overflow-y-auto">
            <span className="text-muted-foreground flex items-center gap-1 mb-2 font-sans font-semibold">
              <FileText className="w-3 h-3" /> // Telemetry Diagnostic Notes
            </span>
            
            {isAlert ? (
              /* DYNAMIC ALERT RENDERING BLOCK */
              isLoading ? (
                "⏳ Rebuilding evaluation timeframe vectors from listWindowMetrics()..."
              ) : (
`--- SentinelIQ Real-Time Alert Stream ---
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
• Error Count : ${metrics?.error_count ?? 0} errors logged in window

=== Engine Vector Analysis ===
• ML Model Score  : ${metrics?.ml_score?.toFixed(4) ?? "N/A"}
• Final Statistical Score : ${metrics?.statistical_score?.toFixed(4) ?? "N/A"}
• Final Weighted Score : ${metrics?.final_score?.toFixed(4) ?? "N/A"}
• Prediction Flag : State Code [${metrics?.prediction ?? "0"}]

=== Linked Raw Telemetry Summary===
${metrics?.payload_summary ? JSON.stringify(metrics.payload_summary, null, 2) : "None linked"}

=== Linked Raw Telemetry ===
${metrics?.payload_json ? JSON.stringify(metrics.payload_json, null, 2) : "None linked"}`
              )
            ) : (
              /* DYNAMIC INCIDENT RENDERING BLOCK */
              `[SYSTEM CORRELATION]
An incident workflow state has been initialized targeting the "${SERVICE_LABELS[item.service] ?? item.service}" service layer. 

• Alert Context ID : ${item.alert_id || "None linked"}
• Assigned Analyst  : ${item.assignee || "Unassigned (Triage Required)"}
• Dispatch Status   : Notification sent ${item.notification_time ? formatTime(item.notification_time) : "Pending"}
• Operational Summary : ${item?.incident_summary ? JSON.stringify(item.incident_summary, null, 2) : "None linked"}
No manual engineering notes have been appended to Ticket Reference #${item.ticket_id || item.id} yet.`
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}