"use client";

import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
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
      <ComposedChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="ano"
          tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
          axisLine={{ stroke: "var(--border)" }}
        />
        <YAxis
          yAxisId="left"
          tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
          axisLine={{ stroke: "var(--border)" }}
          label={{
            value: "Decisões",
            angle: -90,
            position: "insideLeft",
            fontSize: 11,
            fill: "var(--muted-foreground)",
            offset: 0,
          }}
        />
        <YAxis
          yAxisId="right"
          orientation="right"
          unit="%"
          domain={[0, 100]}
          tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
          axisLine={{ stroke: "var(--border)" }}
          label={{
            value: "Aprovação",
            angle: 90,
            position: "insideRight",
            fontSize: 11,
            fill: "var(--muted-foreground)",
            offset: 0,
          }}
        />
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            fontSize: 13,
          }}
          formatter={(value, name) => [
            String(name) === "Aprovação"
              ? `${Number(value).toFixed(1)}%`
              : Number(value).toLocaleString("pt-BR"),
            String(name),
          ]}
        />
        <Legend
          wrapperStyle={{ fontSize: 12 }}
          iconType="rect"
          iconSize={10}
        />
        <Bar
          yAxisId="left"
          dataKey="total"
          name="Total"
          fill="var(--chart-1)"
          fillOpacity={0.3}
          radius={[3, 3, 0, 0]}
        />
        <Bar
          yAxisId="left"
          dataKey="deferidos"
          name="Deferidos"
          fill="var(--chart-4)"
          fillOpacity={0.5}
          radius={[3, 3, 0, 0]}
        />
        <Line
          yAxisId="right"
          type="monotone"
          dataKey="taxa_aprovacao"
          name="Aprovação"
          stroke="var(--brand-teal)"
          strokeWidth={2.5}
          dot={{ r: 3, fill: "var(--brand-teal)" }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
