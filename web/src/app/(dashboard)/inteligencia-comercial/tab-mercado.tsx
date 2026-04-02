"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchPtax,
  fetchCommodities,
  fetchComexYearly,
  fetchComexByUF,
  fetchComexByCountry,
  fetchCommodityTimeSeries,
  type PtaxResponse,
  type CommodityResponse,
} from "@/lib/api";
import { MetricChart } from "./metric-chart";
import { MERCADO_PRESETS } from "./chart-helpers";

/** Mineral name mapping for filtering commodity time-series by preset ID */
const COMMODITY_MINERAL_MAP: Record<string, string> = {
  "commodity-ferro": "Minerio de Ferro (62% Fe CFR)",
  "commodity-ouro": "Ouro",
  "commodity-cobre": "Cobre (LME)",
  "commodity-litio": "Litio (Li2CO3)",
};

interface MercadoTabProps {
  activeMetric: string;
  onMetricChange: (id: string) => void;
}

export function MercadoTab({ activeMetric, onMetricChange }: MercadoTabProps) {
  const [ptax, setPtax] = useState<PtaxResponse | null>(null);
  const [commodities, setCommodities] = useState<CommodityResponse | null>(null);
  const [comexYearly, setComexYearly] = useState<Record<string, unknown>[] | null>(null);
  const [comexByUF, setComexByUF] = useState<Record<string, unknown>[] | null>(null);
  const [comexByCountry, setComexByCountry] = useState<Record<string, unknown>[] | null>(null);
  const [commodityByMineral, setCommodityByMineral] = useState<
    Record<string, Record<string, unknown>[]>
  >({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch all commodity minerals in parallel
    const mineralFetches = Object.entries(COMMODITY_MINERAL_MAP).map(
      ([presetId, mineralName]) =>
        fetchCommodityTimeSeries(mineralName)
          .then((r) => ({ presetId, rows: r.rows }))
          .catch(() => ({ presetId, rows: [] }))
    );

    Promise.all([
      fetchPtax().then(setPtax),
      fetchCommodities().then(setCommodities).catch(() => {}),
      fetchComexYearly().then((r) => {
        const pivot: Record<number, Record<string, unknown>> = {};
        for (const row of r.rows) {
          if (!pivot[row.ano]) pivot[row.ano] = { ano: row.ano };
          pivot[row.ano][row.fluxo] = row.valor_fob_usd;
        }
        setComexYearly(Object.values(pivot).sort((a, b) => (a.ano as number) - (b.ano as number)));
      }),
      fetchComexByUF().then((r) => setComexByUF(r.rows)),
      fetchComexByCountry().then((r) => setComexByCountry(r.rows)),
      Promise.all(mineralFetches).then((results) => {
        const byMineral: Record<string, Record<string, unknown>[]> = {};
        for (const { presetId, rows } of results) {
          byMineral[presetId] = rows as Record<string, unknown>[];
        }
        setCommodityByMineral(byMineral);
      }),
    ])
      .catch((e) => console.error("mercado:", e))
      .finally(() => setLoading(false));
  }, []);

  const chartData = useCallback((): Record<string, unknown>[] | null => {
    switch (activeMetric) {
      case "cambio": {
        if (!ptax) return null;
        const step = Math.max(1, Math.floor(ptax.rows.length / 200));
        return ptax.rows
          .filter((_, i) => i % step === 0 || i === ptax.rows.length - 1)
          .map((r) => ({ data: r.data, valor: Number(r.cotacao_venda) }));
      }
      case "commodity-ferro":
      case "commodity-ouro":
      case "commodity-cobre":
      case "commodity-litio":
        return commodityByMineral[activeMetric] ?? null;
      case "comex-anual":
        return comexYearly;
      case "comex-pais":
        return comexByCountry as Record<string, unknown>[] | null;
      case "comex-uf":
        return comexByUF as Record<string, unknown>[] | null;
      default:
        return null;
    }
  }, [activeMetric, ptax, commodityByMineral, comexYearly, comexByCountry, comexByUF]);

  return (
    <div className="space-y-4">
      <MetricChart
        presets={MERCADO_PRESETS}
        activePreset={activeMetric}
        onPresetChange={onMetricChange}
        data={chartData()}
        loading={loading}
      />

      {/* Commodity price summary cards */}
      {commodities && commodities.latest && Object.keys(commodities.latest).length > 0 && (
        <div className="grid gap-2 sm:grid-cols-3 lg:grid-cols-6">
          {Object.entries(commodities.latest).map(([mineral, data]) => (
            <div key={mineral} className="rounded-lg border p-2.5">
              <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground truncate">
                {mineral.split("(")[0].trim()}
              </p>
              <p className="mt-0.5 text-sm font-bold tabular-nums">
                {data.preco_usd ?? "—"}
              </p>
              <p className="text-[9px] text-muted-foreground">
                {data.unidade} · {data.data?.slice(0, 7)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
