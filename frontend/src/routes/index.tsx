import { createFileRoute } from "@tanstack/react-router";
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
import {
  SERVICE_LABELS,
  getServiceTrend,
  listAlerts,
  listServices,
  listWindowMetrics,
} from "@/lib/api/placeholder-data";

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
  const alerts = listAlerts();
  const latest = listWindowMetrics();
  const services = listServices();

  const totalAlerts = alerts.length;
  const criticalAlerts = alerts.filter((a) => a.priority === "Critical").length;
  const servicesMonitored = services.length;
  const avgRisk =
    latest.reduce((sum, w) => sum + w.final_score, 0) / latest.length;

  // Aggregate anomaly trend = mean final_score across services per bucket.
  const buckets = getServiceTrend(services[0]).map((w, i) => {
    const ts = w.window_start;
    const mean =
      services.reduce(
        (acc, s) => acc + (getServiceTrend(s)[i]?.final_score ?? 0),
        0,
      ) / services.length;
    return {
      id: i,
      service: "aggregate",
      window_start: ts,
      window_end: w.window_end,
      record_count: 0,
      latency_mean: 0,
      latency_max: 0,
      cpu_mean: 0,
      cpu_max: 0,
      memory_mean: 0,
      queue_lag_mean: 0,
      queue_lag_max: 0,
      error_count: 0,
      ml_score: 0,
      statistical_score: 0,
      final_score: mean,
      prediction: 0,
      priority: "Low" as const,
    };
  });

  const recent = alerts.slice(0, 6);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Total Alerts"
          value={totalAlerts}
          icon={AlertOctagon}
          hint="Across all services"
        />
        <KpiCard
          label="Critical Alerts"
          value={criticalAlerts}
          icon={AlertOctagon}
          accent="danger"
          hint="Requires immediate action"
        />
        <KpiCard
          label="Services Monitored"
          value={servicesMonitored}
          icon={ServerCog}
          hint="Reporting telemetry"
        />
        <KpiCard
          label="Average Risk Score"
          value={avgRisk.toFixed(2)}
          icon={Gauge}
          accent={avgRisk > 0.6 ? "danger" : avgRisk > 0.4 ? "warning" : "success"}
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
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {latest.map((w) => (
              <HealthTile
                key={w.service}
                service={SERVICE_LABELS[w.service] ?? w.service}
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
            data={buckets}
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
                    <TableCell className="text-xs">
                      {SERVICE_LABELS[a.service] ?? a.service}
                    </TableCell>
                    <TableCell>
                      <PriorityBadge priority={a.priority} />
                    </TableCell>
                    <TableCell>
                      <StatusPill status={a.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
