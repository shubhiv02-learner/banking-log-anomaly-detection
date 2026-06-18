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
  console.log(slice);
  const formatXAxis = (tickItem: string) => {
    if (!tickItem) return "";
    try {
      const d = new Date(tickItem);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return tickItem;
    }
  };

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
        
        {/* ======================================================================= */}
        {/* CHART 1: INFRASTRUCTURE CORE HARDWARE LAYER                             */}
        {/* ======================================================================= */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold tracking-tight">
              Unified Resource Footprint Overlays
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={slice} margin={{ top: 10, right: 15, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted/40" />
                  <XAxis dataKey="window_end" tickFormatter={formatXAxis} className="text-[10px] fill-muted-foreground" />
                  
                  <YAxis yAxisId="left" orientation="left" className="text-[10px] fill-muted-foreground">
                    <Label value="Latency / EWMA (ms)" angle={-90} position="insideLeft" offset={-5} style={{ textAnchor: "middle", fontSize: "10px", fill: "var(--muted-foreground)" }} />
                  </YAxis>
                  <YAxis yAxisId="right" orientation="right" domain={[0, 100]} className="text-[10px] fill-muted-foreground" unit="%" />
                  
                  <Tooltip 
                    contentStyle={{ backgroundColor: "var(--background)", borderColor: "var(--border)", borderRadius: "8px" }}
                    labelStyle={{ fontSize: "12px", fontFamily: "monospace", fontWeight: "bold", color: "var(--foreground)" }}
                    itemStyle={{ fontSize: "12px", padding: "2px 0" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                  
                  <Line yAxisId="left" type="monotone" dataKey="latency_mean" name="Latency (Mean)" stroke="#3b82f6" strokeWidth={2} dot={false} connectNulls />
                  <Line yAxisId="left" type="monotone" dataKey="ewma" name="EWMA Smoothed Latency" stroke="#f97316" strokeWidth={1.5} strokeDasharray="4 4" dot={false} connectNulls />
                  <Line yAxisId="left" type="monotone" dataKey="queue_lag_mean" name="Queue Lag" stroke="#eab308" strokeWidth={1.5} dot={false} strokeDasharray="2 2" connectNulls />
                  <Line yAxisId="right" type="monotone" dataKey="cpu_mean" name="CPU Utilization" stroke="#ef4444" strokeWidth={2} dot={false} connectNulls />
                  <Line yAxisId="right" type="monotone" dataKey="memory_mean" name="Memory Utilization" stroke="#10b981" strokeWidth={2} dot={false} connectNulls />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* CHART 2: MATHEMATICAL ACCUMULATORS & WEIGHT INDEXES */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold tracking-tight">
              Raw Mathematical Indicators (CUSUM Volume & Persistence Signal)
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              CUSUM rendered as a soft background volume canvas with the Persistence threshold tracking on top.
            </p>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart 
                  data={slice.map((row) => {
                    const rawCusum = parseFloat(row.cusum ?? 0);
                    const rawPersistence = parseFloat(row.persistence_score ?? 0);

                    return {
                      ...row,
                      norm_cusum: isNaN(rawCusum) ? 0 : rawCusum / 100,
                      norm_persistence: isNaN(rawPersistence) ? 0 : (rawPersistence * 100) / 1000
                    };
                  })}
                  margin={{ top: 10, right: 15, left: 15, bottom: 5 }}
                >
                  <defs>
                    {/* 🎨 VISUAL RULES: Softer, premium 12% opacity Slate-Blue gradient canvas */}
                    <linearGradient id="cusumAreaGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#475569" stopOpacity={0.4}/> 
                      <stop offset="95%" stopColor="#475569" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted/30" />
                  <XAxis dataKey="window_end" tickFormatter={formatXAxis} className="text-[10px] fill-muted-foreground" />
                  
                  <YAxis className="text-[10px] fill-muted-foreground">
                    <Label 
                      value="Relative Scale Index (k)" 
                      angle={-90} 
                      position="insideLeft" 
                      offset={-5} 
                      style={{ textAnchor: "middle", fontSize: "10px", fill: "var(--muted-foreground)" }} 
                    />
                  </YAxis>
                  
                  <Tooltip 
                    contentStyle={{ backgroundColor: "var(--background)", borderColor: "var(--border)", borderRadius: "8px" }}
                    labelStyle={{ fontSize: "12px", fontFamily: "monospace", fontWeight: "bold", color: "var(--foreground)" }}
                    itemStyle={{ fontSize: "12px", padding: "2px 0" }}
                    formatter={(value: any, name: string) => {
                      const num = Number(value).toFixed(2);
                      if (name.includes("Persistence")) {
                        return [`${num}k`, "Persistence Index"];
                      }
                      return [`${(Number(value) * 2).toFixed(2)}k (Standardized)`, "CUSUM Volumetric Accumulator"];
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />

                  {/* 🔽 LAYER 1: Muted Background Canvas Fill (Soft Slate Blue) */}
                  <Area 
                    type="monotone" 
                    dataKey="norm_cusum" 
                    name="CUSUM Accumulator Volume" 
                    stroke="#64748b" /* Soft Slate Blue outline */
                    strokeWidth={1}
                    fillOpacity={1} 
                    fill="url(#cusumAreaGrad)" 
                    connectNulls
                  />

                  {/* 🔼 LAYER 2: Crisp Foreground Layer (Deep Charcoal Slate Line) */}
                  <Line 
                    type="monotone" 
                    dataKey="norm_persistence" 
                    name="Persistence Index Signal" 
                    stroke="#f43f5e"   /*  "#334155" /* 🌑 Solid Deep Slate Gray for strong contrast without brightness */
                    strokeWidth={2} 
                    dot={false}
                    connectNulls
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

       {/* ======================================================================= */}
        {/* CHART 3: BOUNDED PROBABILITIES & COMPOSITE VECTORS (0.0 - 1.0)          */}
        {/* ======================================================================= */}
          {/* CHART 3: PROBABILITIES & COMPOSITE VECTORS */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold tracking-tight">
              Statistical Threat Models & Composite Vectors
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="h-[320px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                {/* 🛠️ CHANGED WRAPPER FROM AreaChart TO LineChart FOR BALANCED ELEMENT SUPPORT */}
                <LineChart 
                  data={slice.map((row) => {
                    const parsedStatistical = parseFloat(row.statistical_score ?? row.statisticalScore ?? 0);
                    const parsedProbability = parseFloat(row.incident_probability ?? row.incidentProbability ?? 0);
                    const parsedML = parseFloat(row.ml_score ?? row.mlScore ?? 0);
                    const parsedFinal = parseFloat(row.final_score ?? row.finalScore ?? 0);

                    return {
                      ...row,
                      display_statistical: isNaN(parsedStatistical) ? 0 : parsedStatistical,
                      display_probability: isNaN(parsedProbability) ? 0 : parsedProbability,
                      display_ml: isNaN(parsedML) ? 0 : parsedML,
                      display_final: isNaN(parsedFinal) ? 0 : parsedFinal
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

                  {/* 🍇 Background Layer: Composite Area Shading */}
                  <Area 
                    type="monotone" 
                    dataKey="display_final" 
                    name="Composite Threat Vector (Final Weight)" 
                    stroke="#a855f7" 
                    strokeWidth={3} 
                    fillOpacity={1} 
                    fill="url(#finalScoreGrad)" 
                    connectNulls 
                  />

                  {/* 🔷 Foreground Layer: Crisp Statistical Line */}
                  <Line 
                    type="monotone" 
                    dataKey="display_statistical" 
                    name="Statistical Score" 
                    stroke="#0ea5e9" 
                    strokeWidth={2.5} 
                    dot={false} 
                    connectNulls 
                  />

                  {/* 🔴 Foreground Layer: Incident Probability Line */}
                  <Line 
                    type="monotone" 
                    dataKey="display_probability" 
                    name="Incident Probability" 
                    stroke="#f43f5e" 
                    strokeWidth={2.5} 
                    dot={false} 
                    connectNulls 
                  />

                  {/* 💗 Foreground Layer: Machine Learning Line */}
                  <Line 
                    type="monotone" 
                    dataKey="display_ml" 
                    name="Machine Learning Threat Score" 
                    stroke="#ec4899" 
                    strokeWidth={2.5} 
                    dot={false} 
                    connectNulls 
                  />
                  
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
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