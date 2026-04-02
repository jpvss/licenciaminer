"use client";

import { useMemo } from "react";
import {
  ComposedChart,
  BarChart,
  Bar,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Globe } from "lucide-react";
import { fmtCompact } from "@/lib/format";
import type { PresetConfig } from "./chart-helpers";
import { CHART_TOOLTIP_STYLE, COLORS } from "./chart-helpers";

interface MetricChartProps {
  presets: PresetConfig[];
  activePreset: string;
  onPresetChange: (id: string) => void;
  data: Record<string, unknown>[] | null;
  loading?: boolean;
  height?: number;
}

export function MetricChart({
  presets,
  activePreset,
  onPresetChange,
  data,
  loading,
  height = 360,
}: MetricChartProps) {
  const preset = useMemo(
    () => presets.find((p) => p.id === activePreset) ?? presets[0],
    [presets, activePreset]
  );

  if (loading) {
    return (
      <Card>
        <CardContent className="p-5">
          <Skeleton className="h-8 w-48 mb-4" />
          <Skeleton className="w-full" style={{ height }} />
        </CardContent>
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">{preset.label}</CardTitle>
          <PresetSelector presets={presets} value={activePreset} onChange={onPresetChange} />
        </CardHeader>
        <CardContent className="flex flex-col items-center py-12 text-sm text-muted-foreground">
          <Globe className="h-8 w-8 text-muted-foreground/30 mb-2" />
          Dados não disponíveis para esta visualização.
        </CardContent>
      </Card>
    );
  }

  const needsRightAxis = preset.series.some((s) => s.yAxisId === "right");

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{preset.label}</CardTitle>
        <PresetSelector presets={presets} value={activePreset} onChange={onPresetChange} />
      </CardHeader>
      <CardContent>
        {preset.mode === "bar-h" ? (
          <HorizontalBarChart data={data} preset={preset} height={height} />
        ) : (
          <ComposedChartView
            data={data}
            preset={preset}
            height={height}
            needsRightAxis={needsRightAxis}
          />
        )}
        <p className="mt-2 text-[10px] text-muted-foreground/60">{preset.fonte}</p>
      </CardContent>
    </Card>
  );
}

/* ── Preset Selector ── */

function PresetSelector({
  presets,
  value,
  onChange,
}: {
  presets: PresetConfig[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[200px] h-8 text-xs">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {presets.map((p) => (
          <SelectItem key={p.id} value={p.id} className="text-xs">
            {p.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

/* ── ComposedChart (line + bar) ── */

function ComposedChartView({
  data,
  preset,
  height,
  needsRightAxis,
}: {
  data: Record<string, unknown>[];
  preset: PresetConfig;
  height: number;
  needsRightAxis: boolean;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={data} margin={{ top: 5, right: needsRightAxis ? 60 : 20, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis
          dataKey={preset.xKey}
          tick={{ fontSize: 10 }}
          stroke={COLORS.muted}
        />
        <YAxis
          yAxisId="left"
          tick={{ fontSize: 10 }}
          stroke={COLORS.muted}
          tickFormatter={(v: number) => fmtCompact(v)}
        />
        {needsRightAxis && (
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 10 }}
            stroke={COLORS.muted}
            tickFormatter={(v: number) => fmtCompact(v)}
          />
        )}
        <Tooltip
          contentStyle={CHART_TOOLTIP_STYLE}
          formatter={(value, name) => {
            const cfg = preset.series.find((s) => s.label === name);
            return [cfg ? cfg.format(Number(value)) : String(value), name];
          }}
        />
        <Legend />

        {preset.series.map((s) => {
          if (s.type === "bar") {
            return (
              <Bar
                key={s.key}
                yAxisId={s.yAxisId}
                dataKey={s.key}
                name={s.label}
                fill={s.color}
                fillOpacity={0.8}
                radius={[3, 3, 0, 0]}
              />
            );
          }
          if (s.type === "area") {
            return (
              <Area
                key={s.key}
                yAxisId={s.yAxisId}
                type="monotone"
                dataKey={s.key}
                name={s.label}
                stroke={s.color}
                fill={s.color}
                fillOpacity={0.1}
                strokeWidth={2}
              />
            );
          }
          return (
            <Line
              key={s.key}
              yAxisId={s.yAxisId}
              type="monotone"
              dataKey={s.key}
              name={s.label}
              stroke={s.color}
              strokeWidth={2}
              dot={false}
            />
          );
        })}
      </ComposedChart>
    </ResponsiveContainer>
  );
}

/* ── Horizontal BarChart ── */

function HorizontalBarChart({
  data,
  preset,
  height,
}: {
  data: Record<string, unknown>[];
  preset: PresetConfig;
  height: number;
}) {
  const mainSeries = preset.series[0];
  const yWidth = Math.min(120, Math.max(60, (preset.yKey?.length ?? 8) * 7));

  return (
    <ResponsiveContainer width="100%" height={Math.max(height, data.length * 28 + 40)}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: yWidth, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={COLORS.border} />
        <XAxis
          type="number"
          tick={{ fontSize: 10 }}
          stroke={COLORS.muted}
          tickFormatter={(v: number) => fmtCompact(v)}
        />
        <YAxis
          type="category"
          dataKey={preset.yKey}
          tick={{ fontSize: 9 }}
          stroke={COLORS.muted}
          width={yWidth}
        />
        <Tooltip
          contentStyle={CHART_TOOLTIP_STYLE}
          formatter={(v) => [mainSeries.format(Number(v)), mainSeries.label]}
        />
        <Bar
          dataKey={mainSeries.key}
          fill={mainSeries.color}
          radius={[0, 4, 4, 0]}
          name={mainSeries.label}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
