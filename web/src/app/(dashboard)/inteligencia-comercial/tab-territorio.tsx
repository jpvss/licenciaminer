"use client";

import { useEffect, useState, useCallback } from "react";
import { MapPin } from "lucide-react";
import { StatCard } from "@/components/stat-card";
import {
  fetchAnmByFase,
  fetchAnmBySubstancia,
  fetchAnmStats,
  fetchStrategicMinerals,
} from "@/lib/api";
import { fmtBR } from "@/lib/format";
import { MetricChart } from "./metric-chart";
import { TERRITORIO_PRESETS } from "./chart-helpers";

interface TerritorioTabProps {
  activeMetric: string;
  onMetricChange: (id: string) => void;
}

export function TerritorioTab({ activeMetric, onMetricChange }: TerritorioTabProps) {
  const [byFase, setByFase] = useState<Record<string, unknown>[] | null>(null);
  const [bySubs, setBySubs] = useState<Record<string, unknown>[] | null>(null);
  const [stats, setStats] = useState<{ total_records: number } | null>(null);
  const [strategic, setStrategic] = useState<Record<string, unknown>[] | null>(null);
  const [byCategory, setByCategory] = useState<Record<string, unknown>[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchAnmByFase().then((r) => setByFase(r.rows)),
      fetchAnmBySubstancia().then((r) => setBySubs(r.rows)),
      fetchAnmStats().then(setStats),
      fetchStrategicMinerals().then((r) => {
        // Build strategic minerals view (cross-ref ANM substance data)
        setStrategic(
          r.rows
            .filter((row) => row.estrategico === "true" || row.estrategico === "1")
            .map((row) => ({ substancia: row.substancia, categoria: row.categoria }))
        );

        // Group by category
        const catCount: Record<string, number> = {};
        for (const row of r.rows) {
          catCount[row.categoria] = (catCount[row.categoria] ?? 0) + 1;
        }
        setByCategory(
          Object.entries(catCount)
            .map(([categoria, n]) => ({ categoria, n }))
            .sort((a, b) => b.n - a.n)
        );
      }),
    ])
      .catch((e) => console.error("territorio:", e))
      .finally(() => setLoading(false));
  }, []);

  const chartData = useCallback((): Record<string, unknown>[] | null => {
    switch (activeMetric) {
      case "anm-fase":
        return byFase;
      case "anm-substancia":
        return bySubs;
      case "minerais-estrategicos": {
        if (!bySubs || !strategic) return null;
        // Filter ANM substances to only strategic ones
        const stratSet = new Set(strategic.map((s) => String(s.substancia).toUpperCase()));
        return bySubs.filter((row) => stratSet.has(String(row.substancia).toUpperCase()));
      }
      case "categorias":
        return byCategory;
      default:
        return null;
    }
  }, [activeMetric, byFase, bySubs, strategic, byCategory]);

  return (
    <div className="space-y-4">
      {stats && (
        <StatCard
          label="Processos ANM"
          value={fmtBR(stats.total_records)}
          subtitle="total de processos minerários em MG"
          icon={MapPin}
          accentClass="bg-brand-teal"
        />
      )}
      <MetricChart
        presets={TERRITORIO_PRESETS}
        activePreset={activeMetric}
        onPresetChange={onMetricChange}
        data={chartData()}
        loading={loading}
      />
    </div>
  );
}
