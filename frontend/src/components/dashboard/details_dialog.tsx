// src/components/dashboard/details_dialog.tsx
//import React from "react";
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
import type { Ticket, Alert } from "@/lib/api/types";

// This allows the component to accept either an Alert model or a Ticket model safely
interface IncidentDetailsDialogProps {
  item: Alert | Ticket;
}

export function IncidentDetailsDialog({ item }: IncidentDetailsDialogProps) {
  // TypeScript Type Guard: Check if it's an Alert by evaluating if 'final_score' exists
  const isAlert = "final_score" in item;
  const isTicket = "ticket_id" in item;
  return (
    <Dialog>
      {/* Clickable Icon Trigger Row Link */}
      <DialogTrigger asChild>
        <button 
          className="p-2 text-muted-foreground hover:text-primary hover:bg-muted rounded-md transition-colors cursor-pointer flex items-center justify-center" 
          title="Open Details View"
        >
          <Eye className="w-4 h-4" />
        </button>
      </DialogTrigger>

      {/* Modal Popup Body Layout */}
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
          <DialogDescription className="font-mono text-xs text-muted-foreground">
            {isAlert ? "Real-time infrastructure performance score metrics." : "System configuration and tracking ticket metrics."}
          </DialogDescription>
        </DialogHeader>

        {/* Structured Meta Grid */}
        <div className="grid grid-cols-2 gap-4 border-y border-border py-4 text-sm">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Target Domain Service</p>
              <p className="font-medium">
                {SERVICE_LABELS[item.service] ?? item.service}
              </p>
            </div>
          </div>

          {isAlert ? (
            /* ALERT SPECIFIC FIELDS */
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
              <div>
                <p className="text-xs text-muted-foreground">Anomaly Engine Score</p>
                <p className="font-mono font-semibold text-amber-500">
                  {(item as Alert).final_score.toFixed(3)}
                </p>
              </div>
            </div>
          ) : (
            /* TICKET/INCIDENT SPECIFIC FIELDS */
            <>
              <div className="flex items-center gap-2">
                <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Ticket Reference</p>
                  <p className="font-mono font-medium">{(item as Ticket).ticket_id || "N/A"}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Alert Source ID</p>
                  <p className="font-mono font-medium">{(item as Ticket).alert_id || "None"}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">Assigned Analyst</p>
                  <p className="font-medium">{(item as Ticket).assignee || "Unassigned"}</p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Logs Payload Section */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="w-3.5 h-3.5" />
            <span>
              Detected {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
            </span>
          </div>
          
          <div className="bg-muted p-3 rounded-lg border text-xs font-mono whitespace-pre-wrap leading-relaxed">
            <span className="text-muted-foreground flex items-center gap-1 mb-1 font-sans font-semibold">
              <FileText className="w-3 h-3" /> // Telemetry Diagnostic Payload
            </span>
            {(!isAlert && (item as Ticket).priority) || 
              `Anomalous threshold breach flags identified on network node: ${item.service}. Core system telemetry reports anomalous activity behavior score index value at ${(isAlert ? (item as Alert).final_score : 1.0).toFixed(3)}.`
            }
            {(!isTicket  || 
             `[SYSTEM CORRELATION]
          An incident workflow state has been initialized targeting the "${SERVICE_LABELS[item.service] ?? item.service}" service layer. 

• Alert Context ID : ${item.alert_id || "None linked"}
• Assigned Analyst  : ${item.assignee || "Unassigned (Triage Required)"}
• Dispatch Status   : Notification sent ${item.notification_time ? formatDistanceToNow(new Date(item.notification_time), { addSuffix: true }) : "Pending"}

No manual engineering notes have been appended to Ticket Reference #${item.ticket_id || item.id} yet.`
  )}
</div>
        </div>
      </DialogContent>
    </Dialog>
  );
}