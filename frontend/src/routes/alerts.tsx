import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { formatDistanceToNow } from "date-fns";

import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
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
import { api } from "@/lib/api/client";
import { SERVICE_LABELS } from "@/lib/api/placeholder-data";
import type { Alert, AlertStatus, Priority, ServiceCount } from "@/lib/api/types";

export const Route = createFileRoute("/alerts")({
  head: () => ({
    meta: [
      { title: "Alerts Center — SentinelIQ" },
      {
        name: "description",
        content: "Triage and filter active anomaly alerts across services.",
      },
    ],
  }),
  component: AlertsPage,
});

const PRIORITIES: Priority[] = ["Critical", "High", "Medium"];
const STATUSES: AlertStatus[] = ["OPEN", "ACKNOWLEDGED", "RESOLVED"];
/** Visible page length for the details table; header counts still use full fetch. */
const TABLE_PAGE_SIZE = 20;

function AlertsPage() {
  const [all, setAll] = useState<Alert[]>([]);
  const [services, setServices] = useState<ServiceCount[]>([]);
  const [q, setQ] = useState("");
  const [priority, setPriority] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [service, setService] = useState<string>("all");

  useEffect(() => {
    api.listAlerts()
      .then((data) => setAll(Array.isArray(data) ? data : data?.data ?? []))
      .catch((err) => console.error("Failed to fetch alerts:", err));

    api.listServices()
      .then((data) => setServices(Array.isArray(data) ? data : data?.data ?? []))
      .catch((err) => console.error("Failed to fetch services:", err));
  }, []);

  const filtered = useMemo(() => {
    return all.filter((a) => {
      if (priority !== "all" && a.priority !== priority) return false;
      if (status !== "all" && a.status !== status) return false;
      if (service !== "all" && a.service !== service) return false;
      if (q) {
        const needle = q.toLowerCase();
        if (
          !String(a.id).includes(needle) &&
          !a.service.toLowerCase().includes(needle)
        )
          return false;
      }
      return true;
    });
  }, [all, priority, status, service, q]);

  const visible = useMemo(
    () => filtered.slice(0, TABLE_PAGE_SIZE),
    [filtered],
  );

  const counts = [
    { p: "Critical", n: all.filter((a) => a.priority === "Critical").length },
    { p: "High", n: all.filter((a) => a.priority === "High").length },
    { p: "Medium", n: all.filter((a) => a.priority === "Medium").length },
    { p: "Open", n: all.filter((a) => a.status === "OPEN").length },
  ];

  return (
    <div className="space-y-6">
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

      <Card>
        <CardContent className="p-3">
          <div className="flex flex-wrap items-center gap-2">
            <Input
              placeholder="Search id or service…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              className="h-9 w-full sm:w-64"
            />
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
            <Select value={service} onValueChange={(val) => setService(val)}>
              <SelectTrigger className="h-9 w-48">
                <SelectValue placeholder="Service" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All services</SelectItem>
                {services.map((s) => (
                  <SelectItem key={s.service} value={s.service}>
                    {SERVICE_LABELS[s.service] ?? s.service} ({s.count})
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

      <Card>
        <CardContent className="p-0">
          <Table className="table-fixed w-full">
            <TableHeader>
              <TableRow>
                <TableHead className="w-[8%]">ID</TableHead>
                <TableHead className="w-[20%]">Service</TableHead>
                <TableHead className="w-[12%]">Priority</TableHead>
                <TableHead className="w-[12%]">Final Score</TableHead>
                <TableHead className="w-[14%]">Status</TableHead>
                <TableHead className="w-[22%] text-right">Created</TableHead>
                <TableHead className="w-[12%] text-center">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {visible.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-mono text-xs">#{a.id}</TableCell>
                  <TableCell className="text-sm">
                    {SERVICE_LABELS[a.service] ?? a.service}
                  </TableCell>
                  <TableCell>
                    <PriorityBadge priority={a.priority} />
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {a.final_score.toFixed(3)}
                  </TableCell>
                  <TableCell className="w-[14%]">
                    <StatusPill status={a.status} />
                  </TableCell>
                  <TableCell
                    className="w-[22%] text-right text-xs text-muted-foreground whitespace-nowrap"
                    title={a.created_at}
                  >
                    {formatDistanceToNow(new Date(a.created_at), {
                      addSuffix: true,
                    })}
                  </TableCell>
                  <TableCell className="w-[12%] text-center">
                    <IncidentDetailsDialog item={a} />
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    className="py-10 text-center text-sm text-muted-foreground"
                  >
                    No alerts match the current filters.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {filtered.length > 0 && (
            <p className="border-t border-border px-4 py-2 text-xs text-muted-foreground">
              Showing {visible.length} of {filtered.length} matching alerts
              {filtered.length > TABLE_PAGE_SIZE
                ? ` (page limit ${TABLE_PAGE_SIZE})`
                : ""}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
