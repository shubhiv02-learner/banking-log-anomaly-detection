import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WindowMetric } from "@/lib/api/types";

export function TrendChart({
  title,
  data,
  dataKey,
  unit,
  domain,
  format,
  color = "var(--color-chart-1)",
}: {
  title: string;
  data: WindowMetric[];
  dataKey: keyof WindowMetric;
  unit?: string;
  domain?: [number | "auto", number | "auto"];
  format?: (v: number) => string;
  color?: string;
}) {
  const fmt = format ?? ((v: number) => `${v.toFixed(1)}${unit ?? ""}`);
  const chartData = data.map((d) => ({
    t: new Date(d.window_start).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    }),
    value: d[dataKey] as number,
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent className="h-56 pl-0">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 8, right: 16, left: 8, bottom: 0 }}>
            <defs>
              <linearGradient id={`g-${String(dataKey)}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
            <XAxis
              dataKey="t"
              tick={{ fontSize: 10, fill: "var(--color-muted-foreground)" }}
              interval="preserveStartEnd"
              minTickGap={32}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "var(--color-muted-foreground)" }}
              tickFormatter={(v) => fmt(v)}
              domain={domain}
              width={56}
            />
            <Tooltip
              contentStyle={{
                background: "var(--color-popover)",
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                fontSize: 12,
              }}
              formatter={(v: number) => [fmt(v), title]}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              fill={`url(#g-${String(dataKey)})`}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
