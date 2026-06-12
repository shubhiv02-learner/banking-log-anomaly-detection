import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TrendChart } from "@/components/dashboard/trend-chart";
import { PriorityBadge } from "@/components/dashboard/priority-badge";
import { api, serviceLabel } from "@/lib/api/client";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Service Analytics — SentinelIQ" },
      {
        name: "description",
        content:
          "Per-service trends: latency, CPU, memory, queue lag, anomaly score.",
      },
    ],
  }),
  component: AnalyticsPage,
});

function AnalyticsPage() {
  
  const servicesQ = useQuery({
      queryKey: ["services"],
      queryFn: api.listServices,
      });

  const services = servicesQ.data ?? [];
  const [service, setService] = useState<string>("");
  const [range, setRange] = useState<"1h" | "24h" | "7d">("24h");

 useEffect(() => {
  if (!service && services.length) {
    setService(services[0].service);
  }
}, [services, service]);
  const trendQ = useQuery({
    queryKey: ["window-metrics", "service", service],
    queryFn: () => api.serviceTrend(service),
    enabled: !!service,
  });

  const full = trendQ.data ?? [];
  const slice = range === "1h" ? full.slice(-12) : full;
  const latest = full[full.length - 1];
  console.log("services =", services);
  console.log("first service =", services[0]);
  console.log("servicesQ", servicesQ);
  console.log("services[0] =", services[0]);
  console.log("typeof services[0] =", typeof services[0]);
  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 p-3">
          <Select value={service} onValueChange={setService}>
            <SelectTrigger className="h-9 w-56">
              <SelectValue placeholder="Select service" />
            </SelectTrigger>
            <SelectContent>
              {services.map((s) => (
                <SelectItem
                  key={s.service}
                      value={s.service}
                  >
                  {serviceLabel(s.service)}
                </SelectItem>
                ))}
            </SelectContent>
          </Select>
          <Tabs value={range} onValueChange={(v) => setRange(v as typeof range)}>
            <TabsList>
              <TabsTrigger value="1h">1h</TabsTrigger>
              <TabsTrigger value="24h">24h</TabsTrigger>
              <TabsTrigger value="7d">7d</TabsTrigger>
            </TabsList>
          </Tabs>

          {latest && (
            <div className="ml-auto flex flex-wrap items-center gap-4 text-xs">
              <Stat label="Latest Score" value={latest.final_score.toFixed(3)} mono />
              <Stat label="Errors" value={latest.error_count} mono />
              <Stat label="Records" value={latest.record_count.toLocaleString()} mono />
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Priority</span>
                <PriorityBadge priority={latest.priority} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {trendQ.isError && (
        <Card>
          <CardContent className="p-4 text-sm text-destructive">
            Failed to load metrics: {(trendQ.error as Error).message}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <TrendChart
          title="Latency Trend"
          data={slice}
          dataKey="latency_mean"
          format={(v) => `${v.toFixed(0)}ms`}
          color="var(--color-chart-1)"
        />
        <TrendChart
          title="CPU Utilization Trend"
          data={slice}
          dataKey="cpu_mean"
          domain={[0, 1]}
          format={(v) => `${(v ).toFixed(0)}%`}
          color="var(--color-chart-2)"
        />
        <TrendChart
          title="Memory Utilization Trend"
          data={slice}
          dataKey="memory_mean"
          domain={[0, 1]}
          format={(v) => `${(v ).toFixed(0)}%`}
          color="var(--color-chart-3)"
        />
        <TrendChart
          title="Queue Lag Trend"
          data={slice}
          dataKey="queue_lag_mean"
          format={(v) => `${v.toFixed(0)}`}
          color="var(--color-chart-4)"
        />
        <div className="xl:col-span-2">
          <TrendChart
            title="Anomaly Score Trend"
            data={slice}
            dataKey="final_score"
            domain={[0, 1]}
            format={(v) => v.toFixed(2)}
            color="var(--color-chart-5)"
          />
        </div>
      </div>

      {latest && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">
              Current Window — {serviceLabel(service)}
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            <Stat label="latency_max" value={`${latest.latency_max.toFixed(0)}ms`} mono />
            <Stat label="cpu_max" value={`${(latest.cpu_max ).toFixed(0)}%`} mono />
            <Stat label="queue_lag_max" value={latest.queue_lag_max.toFixed(0)} mono />
            <Stat label="ml_score" value={latest.ml_score.toFixed(3)} mono />
            <Stat label="statistical_score" value={latest.statistical_score.toFixed(3)} mono />
            <Stat label="prediction" value={latest.prediction} mono />
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Stat({
  label,
  value,
  mono,
}: {
  label: string;
  value: string | number;
  mono?: boolean;
}) {
  return (
    <div className="flex flex-col">
      <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      <span className={`text-sm ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}
