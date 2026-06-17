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
import { Eye, ShieldAlert, Clock, User, Server, Hash, FileText } from "lucide-react";
import { PriorityBadge } from "./priority-badge";
import { StatusPill } from "./status-pill";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import { formatDistanceToNow } from "date-fns";
import type { Ticket } from "@/lib/api/types";

interface IncidentDetailsDialogProps {
  ticket: Ticket;
}

export function IncidentDetailsDialog({ ticket }: IncidentDetailsDialogProps) {
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

      {/* Modal Popup Body layout */}
      <DialogContent className="sm:max-w-[550px] gap-6">
        <DialogHeader className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <PriorityBadge priority={ticket.priority} />
            <StatusPill status={ticket.status} />
          </div>
          <DialogTitle className="text-xl font-semibold tracking-tight">
            Incident Logs: #{ticket.id}
          </DialogTitle>
          <DialogDescription className="font-mono text-xs text-muted-foreground">
            System metrics configuration and target service metrics mapping.
          </DialogDescription>
        </DialogHeader>

        {/* Structured Node Attributes Meta Grid */}
        <div className="grid grid-cols-2 gap-4 border-y border-border py-4 text-sm">
          <div className="flex items-center gap-2">
            <Hash className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Ticket Reference</p>
              <p className="font-mono font-medium">{ticket.ticket_id || "None Provided"}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Alert Source ID</p>
              <p className="font-mono font-medium">{ticket.alert_id || "None"}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Target Domain Service</p>
              <p className="font-medium">
                {SERVICE_LABELS[ticket.service] ?? ticket.service}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-muted-foreground shrink-0" />
            <div>
              <p className="text-xs text-muted-foreground">Assigned Analyst</p>
              <p className="font-medium">{ticket.assignee || "Unassigned"}</p>
            </div>
          </div>
        </div>

        {/* Description / Metadata text container */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="w-3.5 h-3.5" />
            <span>
              Logged {formatDistanceToNow(new Date(ticket.created_at), { addSuffix: true })}
            </span>
          </div>
          
          <div className="bg-muted p-3 rounded-lg border text-xs font-mono whitespace-pre-wrap leading-relaxed">
            <span className="text-muted-foreground flex items-center gap-1 mb-1 font-sans font-semibold">
              <FileText className="w-3 h-3" /> // Telemetry Description Payload
            </span>
            {ticket.description || `No alternative detailed message string attached. Examine server groups matching alert system reference key: ${ticket.alert_id}.`}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
