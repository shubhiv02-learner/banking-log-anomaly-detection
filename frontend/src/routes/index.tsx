import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertOctagon, Gauge, ServerCog } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { HealthTile } from "@/components/dashboard/health-tile";
import { PriorityBadge } from "@/components/dashboard/priority-badge";
import { StatusPill } from "@/components/dashboard/status-pill";
import { TrendChart } from "@/components/dashboard/trend-chart";
import { api, serviceLabel } from "@/lib/api/client";
import type { WindowMetric } from "@/lib/api/types";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Executive Dashboard — SentinelIQ" },
      {
        name: "description",
        content:
          "Top-line observability KPIs, system health overview, and recent alerts.",
      },
    ],
  }),
  component: Dashboard,
});

function Dashboard() {
  const summaryQ = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: api.dashboardSummary,
  });
  const latestQ = useQuery({
    queryKey: ["window-metrics", "latest"],
    queryFn: api.listWindowMetrics,
  });
  const recentAlertsQ = useQuery({
    queryKey: ["alerts", "recent"],
    queryFn: api.recentAlerts,
  });

  const latest: WindowMetric[] = latestQ.data ?? [];
  const recent = (recentAlertsQ.data ?? []).slice(0, 6);
  const summary = summaryQ.data;

  const uniqueLatest = Array.from(
    new Map(
      latest.map(item => [item.service, item])
      ).values()
   );

  // Aggregate trend across services: align by index of each service's trend.
  // Derived from `latest` to avoid extra fan-out queries on the dashboard.
  const aggregateBuckets: WindowMetric[] =
    latest.length > 0
      ? latest.map((w, i) => ({
          ...w,
          id: i,
          service: "aggregate",
          final_score:
            latest.reduce((acc, s) => acc + s.final_score, 0) / latest.length,
        }))
      : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Total Alerts"
          value={summary?.total_alerts ?? "—"}
          icon={AlertOctagon}
          hint="Across all services"
        />
        <KpiCard
          label="Critical Alerts"
          value={summary?.critical_alerts ?? "—"}
          icon={AlertOctagon}
          accent="danger"
          hint="Requires immediate action"
        />
        <KpiCard
          label="Services Monitored"
          value={summary?.services_monitored ?? "—"}
          icon={ServerCog}
          hint="Reporting telemetry"
        />
        <KpiCard
          label="Average Risk Score"
          value={summary?.avg_risk_score ? summary.avg_risk_score.toFixed(2): "0.00"}
          icon={Gauge}
          accent={
            summary && summary.avg_risk_score > 0.6
              ? "danger"
              : summary && summary.avg_risk_score > 0.4
                ? "warning"
                : "success"
          }
          hint="Mean final_score, latest window"
        />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold">
            System Health Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          {latestQ.isError && (
            <p className="text-sm text-destructive">
              Failed to load services: {(latestQ.error as Error).message}
            </p>
          )}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
  {uniqueLatest.map((w) => (
  	  <HealthTile
      		key={w.service}
      		service={serviceLabel(w.service)}
      		priority={w.priority}
      		score={w.final_score}
    	  />
  	))}
      </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TrendChart
            title="Anomaly Score Trend — All Services"
            data={aggregateBuckets}
            dataKey="final_score"
            domain={[0, 1]}
            format={(v) => v.toFixed(2)}
            color="var(--color-chart-1)"
          />
        </div>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4" /> Recent Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-xs">Service</TableHead>
                  <TableHead className="text-xs">Priority</TableHead>
                  <TableHead className="text-xs">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recent.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="text-xs">{serviceLabel(a.service)}</TableCell>
                    <TableCell>
                      <PriorityBadge priority={a.priority} />
                    </TableCell>
                    <TableCell>
                      <StatusPill status={a.status} />
                    </TableCell>
                  </TableRow>
                ))}
                {recentAlertsQ.isLoading && (
                  <TableRow>
                    <TableCell colSpan={3} className="py-6 text-center text-xs text-muted-foreground">
                      Loading…
                    </TableCell>
                  </TableRow>
                )}
                {recentAlertsQ.isError && (
                  <TableRow>
                    <TableCell colSpan={3} className="py-6 text-center text-xs text-destructive">
                      Failed to load alerts.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
