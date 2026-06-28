// src/routes/analytics.tsx

import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { 
  ResponsiveContainer, 
  AreaChart, 
  LineChart, 
  ComposedChart,
  Line, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  Label
} from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PriorityBadge } from "@/components/dashboard/priority-badge";
import { api, serviceLabel } from "@/lib/api/client";

export const Route = createFileRoute("/analytics")({
  head: () => ({
    meta: [
      { title: "Service Analytics — SentinelIQ" },
      {
        name: "description",
        content: "Complete 3-tier multi-variable diagnostics engine.",
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
 
  const formatXAxis = (tickItem: string) => {
    if (!tickItem) return "";
    try {
      const d = new Date(tickItem);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return tickItem;
    }
  };
 
  console.log("sample metric for chart ###", slice[0]);
  return (
    <div className="space-y-6">
      {/* GLOBAL CONTROLS HEADER CARD */}
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 p-3">
          <Select value={service} onValueChange={setService}>
            <SelectTrigger className="h-9 w-56">
              <SelectValue placeholder="Select service" />
            </SelectTrigger>
            <SelectContent>
              {services.map((s) => (
                <SelectItem key={s.service} value={s.service}>
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
              <Stat label="Prediction Status" value={`State [${latest.prediction}]`} mono />
              <Stat label="Total Records" value={latest.record_count.toLocaleString()} mono />
              <Stat label="Error Count" value={latest.error_count} mono />
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

      {/* THREE TIER AUDITED DASHBOARD LAYOUT */}
      <div className="space-y-6">
        
        {/* CHART 1: INFRASTRUCTURE CORE HARDWARE LAYER (DYNAMICALLY NORMALIZED) */}
          {/* CHART 1 */}
        {slice.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold tracking-tight">
                Unified Resource Footprint Overlays (Normalized Variance)
              </CardTitle>
              <p className="text-xs text-muted-foreground">
                Metrics are scaled relatively (0-100%) to maximize micro-variation visibility across 1-minute synthetic windows.
              </p>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="h-[340px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart 
                    data={(() => {
                      if (!slice.length) return [];
                      const latencies = slice.map(r => Number(r.latency_mean ?? 0));
                      const ewmas = slice.map(r => Number(r.ewma ?? 0));
                      const cpus = slice.map(r => Number(r.cpu_mean ?? 0));
                      const mems = slice.map(r => Number(r.memory_mean ?? 0));
                      const lags = slice.map(r => Number(r.queue_lag_mean ?? 0));

                      const maxLat = Math.max(...latencies, 1); const minLat = Math.min(...latencies, 0);
                      const maxEwma = Math.max(...ewmas, 1);   const minEwma = Math.min(...ewmas, 0);
                      const maxCpu = Math.max(...cpus, 1);     const minCpu = Math.min(...cpus, 0);
                      const maxMem = Math.max(...mems, 1);     const minMem = Math.min(...mems, 0);
                      const maxLag = Math.max(...lags, 1);     const minLag = Math.min(...lags, 0);

                    // Helper function to transform values to a clean 0 - 100 range
                      const norm = (val: number, min: number, max: number) => {
                        if (max === min) return 50;
                        return ((val - min) / (max - min)) * 100;
                      };

                      return slice.map((row) => ({
                        ...row,
                        raw_latency: Number(row.latency_mean ?? 0),
                        raw_ewma: Number(row.ewma ?? 0),
                        raw_cpu: Number(row.cpu_mean ?? 0),
                        raw_mem: Number(row.memory_mean ?? 0),
                        raw_lag: Number(row.queue_lag_mean ?? 0),

                        norm_latency: norm(Number(row.latency_mean ?? 0), minLat, maxLat),
                        norm_ewma: norm(Number(row.ewma ?? 0), minEwma, maxEwma),
                        norm_cpu: norm(Number(row.cpu_mean ?? 0), minCpu, maxCpu),
                        norm_mem: norm(Number(row.memory_mean ?? 0), minMem, maxMem),
                        norm_lag: norm(Number(row.queue_lag_mean ?? 0), minLag, maxLag),
                      }));
                    })()}
                  margin={{ top: 10, right: 15, left: -5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted/40" />
                  <XAxis dataKey="window_end" tickFormatter={formatXAxis} className="text-[10px] fill-muted-foreground" />
                  
                  {/* Universal scale wrapper representing relative operational bounds */}
                  <YAxis domain={[0, 100]} className="text-[10px] fill-muted-foreground" unit="m" />
                  
                  <Tooltip 
                    contentStyle={{ backgroundColor: "var(--background)", borderColor: "var(--border)", borderRadius: "8px" }}
                    labelStyle={{ fontSize: "12px", fontFamily: "monospace", fontWeight: "bold", color: "var(--foreground)" }}
                    itemStyle={{ fontSize: "12px", padding: "2px 0" }}
                    /* 💡 INTERCEPT HOVER AND RESTORE RAW METRIC SCALE LABELS */
                    formatter={(value: any, name: string, props: any) => {
                      const payload = props.payload;
                      switch (name) {
                        case "Latency (Mean)":
                          return [`${payload.raw_latency.toFixed(1)} ms`, name];
                        case "EWMA Latency":
                          return [`${payload.raw_ewma.toFixed(1)} ms`, name];
                        case "CPU Utilization":
                          return [`${payload.raw_cpu.toFixed(1)}m`, name];
                        case "Memory Utilization":
                          return [`${payload.raw_mem.toFixed(1)}MiB`, name];
                        case "Queue Lag":
                          return [`${payload.raw_lag.toFixed(2)} items`, name];
                        default:
                          return [value, name];
                      }
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  
                  {/* Performance Paths mapped to normalized variance variables */}
                  <Line type="monotone" dataKey="norm_latency" name="Latency (Mean)" stroke="#3b82f6" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="norm_ewma" name="EWMA Latency" stroke="#f97316" strokeWidth={1.5} strokeDasharray="4 4" dot={false} connectNulls />
                  <Line type="monotone" dataKey="norm_lag" name="Queue Lag (items)" stroke="#eab308" strokeWidth={1.5} strokeDasharray="2 2" dot={false} connectNulls />
                  <Line type="monotone" dataKey="norm_cpu" name="CPU Utilization " stroke="#ef4444" strokeWidth={2} dot={false} connectNulls />
                  <Line type="monotone" dataKey="norm_mem" name="Memory Utilization " stroke="#10b981" strokeWidth={2} dot={false} connectNulls />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>)}
        {/* CHART 2: MATHEMATICAL ACCUMULATORS & WEIGHT INDEXES */}
        {slice.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold tracking-tight">
              Statistical Indicators (CUSUM Volume & Persistence Signal)
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              CUSUM as a soft background volume with the Persistence threshold tracking on top.
            </p>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={slice.map((row) => {
                              const rawCusum = parseFloat(row.cusum ?? 0);
                              const rawPersistence = parseFloat(row.persistence_score ?? 0);

                              return {
                                ...row,
                                norm_cusum: isNaN(rawCusum) ? 0 : rawCusum / 1000,
                                norm_persistence: isNaN(rawPersistence) ? 0 : (rawPersistence * 100) / 1000
                              };
                            })}
                            margin={{ top: 10, right: 15, left: 15, bottom: 5 }} >
                   <defs>
                    <linearGradient id="cusumAreaGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f1f5f9" stopOpacity={0.5}/> 
                      <stop offset="95%" stopColor="#f1f5f9" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="window_end" tickFormatter={formatXAxis} />
                  <YAxis />

                  <Tooltip />
                  <Legend />

                  {/* Filled area */}
                  <Area 
                    type="monotone" 
                    dataKey="norm_cusum" 
                    name="CUSUM Accumulator Volume" 
                    stroke="#64748b"
                    strokeWidth={1}
                    fill="url(#cusumAreaGrad)" 
                    //fillOpacity={1}
                    connectNulls
                  />

                  {/* Overlay line */}
                  <Line 
                    type="monotone" 
                    dataKey="norm_persistence" 
                    name="Persistence Index Signal" 
                    stroke="#f43f5e"
                    strokeWidth={2} 
                    dot={false}
                    connectNulls
                  />
                </ComposedChart>
            </ResponsiveContainer>

            </div>
          </CardContent>
        </Card>)}

       {/* ======================================================================= */}
        {/* CHART 3: BOUNDED PROBABILITIES & COMPOSITE VECTORS (0.0 - 1.0)          */}
        {/* ======================================================================= */}
         {/* CHART 3: PROBABILITIES & COMPOSITE VECTORS */}
         {slice.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold tracking-tight">
                Statistical Threat Models & Composite Vectors
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="h-[320px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart 
                    data={slice.map((row) => {
                      const parsedStatistical = row.statistical_score ?? 0;
                      const parsedProbability = row.incident_probability ?? 0;
                      const parsedML = row.ml_score ?? 0;
                      const parsedFinal = row.final_score ?? 0;

                      return {
                        ...row,
                        display_statistical: isNaN(parsedStatistical) ? 0 : parsedStatistical,
                        display_probability: isNaN(parsedProbability) ? 0 : parsedProbability,
                        display_ml: isNaN(parsedML) ? 0 : parsedML,
                        display_final: isNaN(parsedFinal) ? 0 : parsedFinal,
                      };
                    })}
                    margin={{ top: 10, right: 15, left: -10, bottom: 5 }}
                  >
                    <defs>
                      <linearGradient id="finalScoreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.15}/>
                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-muted/40" />
                    <XAxis dataKey="window_end" tickFormatter={formatXAxis} className="text-[10px] fill-muted-foreground" />
                    <YAxis domain={[0.0, 1.0]} className="text-[10px] fill-muted-foreground" tickFormatter={(v) => Number(v).toFixed(1)} />
                    
                    <Tooltip 
                      contentStyle={{ backgroundColor: "var(--background)", borderColor: "var(--border)", borderRadius: "8px" }}
                      labelStyle={{ fontSize: "12px", fontFamily: "monospace", fontWeight: "bold", color: "var(--foreground)" }}
                      itemStyle={{ fontSize: "12px", padding: "2px 0" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />

                    {/* 🍇 1. FIRST LAYER: Background Composite Area Shading with Gradient Fill Enabled */}
                    <Area 
                      type="monotone" 
                      dataKey="display_final" 
                      name="Composite Threat Vector (Final Weight)" 
                      stroke="#a855f7" 
                      strokeWidth={2.5} 
                      fillOpacity={1} 
                      fill="url(#finalScoreGrad)" 
                      connectNulls 
                    />

                    {/* 🔷 2. SECOND LAYER: Foreground Statistical Line */}
                    <Line 
                      type="monotone" 
                      dataKey="display_statistical" 
                      name="Statistical Score" 
                      stroke="#0ea5e9" 
                      strokeWidth={2} 
                      dot={false} 
                      connectNulls 
                    />

                    {/* 🔴 3. THIRD LAYER: Foreground Incident Probability Line */}
                    <Line 
                      type="monotone" 
                      dataKey="display_probability" 
                      name="Incident Probability" 
                      stroke="#f43f5e" 
                      strokeWidth={2} 
                      dot={false} 
                      connectNulls 
                    />

                    {/* 🟢 4. FOURTH LAYER: Foreground Machine Learning Line */}
                    <Line 
                      type="monotone" 
                      dataKey="display_ml" 
                      name="Machine Learning Threat Score" 
                      stroke="#10b981" 
                      strokeWidth={2} 
                      dot={false} 
                      connectNulls 
                    />
                    
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

      </div>
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
      <span className={`text-sm ${mono ? "font-mono font-semibold text-primary" : ""}`}>{value}</span>
    </div>
  );
}