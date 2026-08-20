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
import { IncidentDetailsDialog } from "@/components/dashboard/details_dialog";
import { IncidentActionDialog } from "@/components/dashboard/incident-action-dialog";
import { Button } from "@/components/ui/button";
import { api, type DashboardUser, type IncidentAction } from "@/lib/api/client";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import { useAuth } from "@/lib/auth";

import type { Ticket, AlertStatus, Priority } from "@/lib/api/types";

export const Route = createFileRoute("/incidents")({
  head: () => ({
    meta: [
      { title: "Incidents Center — SentryyIQ" },
      {
        name: "description",
        content: "Triage and filter active anomaly alerts across services.",
      },
    ],
  }),
  component: IncidentsPage,
});

const PRIORITIES: Priority[] = ["Critical", "High", "Medium"];
const STATUSES: AlertStatus[] = ["OPEN", "ASSIGNED", "RESOLVED", "CLOSED"];
/** Visible page length for the details table; header counts still use full fetch. */
const TABLE_PAGE_SIZE = 15;

function nextAction(status: AlertStatus): IncidentAction | null {
  if (status === "OPEN") return "ASSIGNED";
  if (status === "ASSIGNED") return "RESOLVED";
  if (status === "RESOLVED") return "CLOSED";
  return null;
}

function actionLabel(action: IncidentAction): string {
  if (action === "ASSIGNED") return "Assign";
  if (action === "RESOLVED") return "Resolve";
  return "Close";
}

function IncidentsPage() {
  const { user } = useAuth();
  const [all, setAll] = useState<Ticket[]>([]);
  const [users, setUsers] = useState<DashboardUser[]>([]);
  const [priority, setPriority] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [actionTicket, setActionTicket] = useState<Ticket | null>(null);
  const [pendingAction, setPendingAction] = useState<IncidentAction | null>(null);

  function loadIncidents() {
    api.listTickets()
      .then((data) => setAll(Array.isArray(data) ? data : []))
      .catch((err) => console.error("Failed to fetch incidents:", err));
  }

  useEffect(() => {
    loadIncidents();
    api.listUsers()
      .then((data) => setUsers(Array.isArray(data) ? data : []))
      .catch((err) => console.error("Failed to fetch users:", err));
  }, []);

  const filtered = useMemo(() => {
    return all.filter((a) => {
      if (priority !== "all" && a.priority !== priority) return false;
      if (status !== "all" && a.status !== status) return false;
      return true;
    });
  }, [all, priority, status]);

  const visible = useMemo(
    () => filtered.slice(0, TABLE_PAGE_SIZE),
    [filtered],
  );

  const counts = [
    { p: "Open", n: all.filter((a) => a.status === "OPEN").length },
    {
      p: "Assigned",
      n: all.filter((a) => a.status === "ASSIGNED").length,
      statusPill: "ASSIGNED" as AlertStatus,
    },
    { p: "Resolved", n: all.filter((a) => a.status === "RESOLVED").length },
    { p: "Closed", n: all.filter((a) => a.status === "CLOSED").length },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {counts.map(({ p, n, statusPill }) => (
          <Card key={p}>
            <CardContent className="p-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">
                {p}
              </p>
              <div className="mt-2 flex items-center justify-between">
                <span className="font-mono text-2xl font-semibold">{n}</span>
                {statusPill ? (
                  <StatusPill status={statusPill} />
                ) : p === "Open" ? (
                  <StatusPill status="OPEN" />
                ) : p === "Resolved" ? (
                  <StatusPill status="RESOLVED" />
                ) : (
                  <StatusPill status="CLOSED" />
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

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
              {filtered.length} of {all.length} incidents
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table className="table-fixed w-full">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[7%]">ID</TableHead>
                <TableHead className="w-[8%]">Alert Id</TableHead>
                <TableHead className="w-[12%]">Ticket Id</TableHead>
                <TableHead className="w-[14%]">Service</TableHead>
                <TableHead className="w-[12%]">Assigned To</TableHead>
                <TableHead className="w-[10%]">Priority</TableHead>
                <TableHead className="w-[12%]">Status</TableHead>
                <TableHead className="w-[15%] text-right">Assigned On</TableHead>
                <TableHead className="w-[16%] text-center align-middle">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visible.map((a) => {
                const action = nextAction(a.status);
                return (
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
                  <TableCell className="w-[12%]">
                    <StatusPill status={a.status} />
                  </TableCell>
                  <TableCell
                    className="w-[15%] text-right text-xs text-muted-foreground whitespace-nowrap"
                    title={a.created_at}
                  >
                    {formatDistanceToNow(new Date(a.created_at), {
                      addSuffix: true,
                    })}
                  </TableCell>
                  <TableCell className="w-[16%] text-center align-middle">
                    <div className="flex items-center justify-center gap-1">
                      <IncidentDetailsDialog item={a} />
                      {action ? (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setActionTicket(a);
                            setPendingAction(action);
                          }}
                        >
                          {actionLabel(action)}
                        </Button>
                      ) : null}
                    </div>
                  </TableCell>
                </TableRow>
                );
              })}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={9}
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    No incidents match the current filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {filtered.length > 0 && (
            <p className="border-t border-border px-4 py-2 text-xs text-muted-foreground">
              Showing {visible.length} of {filtered.length} matching incidents
              {filtered.length > TABLE_PAGE_SIZE
                ? ` (page limit ${TABLE_PAGE_SIZE})`
                : ""}
            </p>
          )}
        </CardContent>
      </Card>

      <IncidentActionDialog
        ticket={actionTicket}
        action={pendingAction}
        users={users}
        currentUserName={user?.name ?? ""}
        onClose={() => {
          setActionTicket(null);
          setPendingAction(null);
        }}
        onSuccess={loadIncidents}
      />
    </div>
  );
}
