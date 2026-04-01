"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { TrendPoint } from "@/lib/api";

export function TrendChart({ data }: { data: TrendPoint[] }) {
  if (!data.length) {
    return (
      <p className="py-12 text-center text-sm text-muted-foreground">
        Sem dados de tendência disponíveis.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="gradTotal" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.2} />
            <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="gradDeferidos" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="var(--chart-4)" stopOpacity={0.2} />
            <stop offset="95%" stopColor="var(--chart-4)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="ano"
          tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
          axisLine={{ stroke: "var(--border)" }}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
          axisLine={{ stroke: "var(--border)" }}
        />
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            fontSize: 13,
          }}
          formatter={(value, name) => [
            Number(value).toLocaleString("pt-BR"),
            String(name),
          ]}
        />
        <Area
          type="monotone"
          dataKey="total"
          name="Total"
          stroke="var(--chart-1)"
          fill="url(#gradTotal)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="deferidos"
          name="Deferidos"
          stroke="var(--chart-4)"
          fill="url(#gradDeferidos)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
