import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { formatDistanceToNow } from "date-fns";

import { Card, CardContent } from "@/components/ui/card";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { PriorityBadge } from "@/components/dashboard/priority-badge";
import { StatusPill } from "@/components/dashboard/status-pill";
import { IncidentDetailsDialog } from "@/components/dashboard/details_dialog"; // 👈 REGISTER NEW DIALOG COMPONENT INTO ENVIRONMENT
import { api } from "@/lib/api/client";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";

import type { Ticket, AlertStatus, Priority } from "@/lib/api/types";

export const Route = createFileRoute("/incidents")({
  head: () => ({
    meta: [
      { title: "Incidents Center — SentinelIQ" },
      {
        name: "description",
        content: "Triage and filter active anomaly alerts across services.",
      },
    ],
  }),
  component: IncidentsPage,
});

const PRIORITIES: Priority[] = ["Critical", "High", "Medium"];
const STATUSES: AlertStatus[] = ["OPEN", "ACKNOWLEDGED", "RESOLVED"];

function IncidentsPage() {
  const [all, setAll] = useState<Ticket[]>([]);
  const [priority, setPriority] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");

  useEffect(() => {
    api.listTickets()
   .then((data) => setAll(Array.isArray(data) ? data : data?.data ?? []))
      .catch((err) => console.error("Failed to fetch incidents:", err));
  }, []);
 
  useEffect(() => {
    console.log("Incidents count", all.length);

    console.log(
      "critical count",
      all.filter(a => a.priority === "Critical").length
    );

    console.log(
      "high count",
      all.filter(a => a.priority === "High").length
    );

    console.log(
      "medium count",
      all.filter(a => a.priority === "Medium").length
    );
  }, [all]);

  const filtered = useMemo(() => {
    return all.filter((a) => {
      if (priority !== "all" && a.priority !== priority) return false;
      if (status !== "all" && a.status !== status) return false;
      return true;
    });
  }, [all, priority, status]);

  const counts = [
    { p: "Critical Incidents", n: all.filter((a) => a.priority === "Critical" && a.status === "OPEN").length },
    { p: "Acknowledged", n: all.filter((a) => a.status === "ACKNOWLEDGED").length },
    { p: "Resolved", n: all.filter((a) => a.status === "RESOLVED").length },
    { p: "Total Open", n: all.filter((a) => a.status === "OPEN").length },
  ];

  return (
    <div className="space-y-6">
      {/* Priority summary cards */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {counts.map(({ p, n }) => (
          <Card key={p}>
            <CardContent className="p-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">
                {p}
              </p>
              <div className="mt-2 flex items-center justify-between">
                <span className="font-mono text-2xl font-semibold">{n}</span>
                {p === "Open" ? (
                  <StatusPill status="OPEN" />
                ) : (
                  <PriorityBadge priority={p as Priority} />
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-3">
          <div className="flex flex-wrap items-center gap-2">
            <Select value={priority} onValueChange={(val) => setPriority(val)}>
              <SelectTrigger className="h-9 w-36">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All priorities</SelectItem>
                {PRIORITIES.map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={(val) => setStatus(val)}>
              <SelectTrigger className="h-9 w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All statuses</SelectItem>
                {STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="ml-auto text-xs text-muted-foreground">
              {filtered.length} of {all.length} alerts
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Alerts table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">ID</TableHead>
                <TableHead>Alert Id</TableHead>
                <TableHead>Ticket Id</TableHead>
                <TableHead>Service</TableHead>
                <TableHead>Assigned To</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Assigned On</TableHead>
                <TableHead className="w-16 text-center">Actions</TableHead> {/* 👈 ACTIONS HEADER CELL TARGET SETUP */}
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-mono text-xs">#{a.id}</TableCell>
                  <TableCell className="font-mono text-xs">{a.alert_id}</TableCell>
                  <TableCell className="text-sm">{a.ticket_id}</TableCell>
                  <TableCell className="text-sm">
                    {SERVICE_LABELS[a.service] ?? a.service}
                  </TableCell>
                  <TableCell className="text-sm">{a.assignee}</TableCell>
                  <TableCell>
                    <PriorityBadge priority={a.priority} />
                  </TableCell>
                  <TableCell>
                    <StatusPill status={a.status} />
                  </TableCell>
                  <TableCell
                    className="text-right text-xs text-muted-foreground"
                    title={a.created_at}
                  >
                    {formatDistanceToNow(new Date(a.created_at), {
                      addSuffix: true,
                    })}
                  </TableCell>
                  <TableCell className="text-center">
                    {/* 👈 CLICKABLE DIALOG ICON INJECTED PER TICKET ROW */}
                    <IncidentDetailsDialog item={a} />
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={9} // 👈 CORRECTED COLSPAN FROM 6 TO 9 TO MERGE FULL ACTIONS TRACK ROWS SMOOTHLY
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    No incidents match the current filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}