"use client";

import { useEffect, useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  fetchPtax,
  fetchCommodities,
  fetchComexYearly,
  fetchComexByUF,
  fetchComexByCountry,
  type PtaxResponse,
  type CommodityResponse,
} from "@/lib/api";
import { MetricChart } from "./metric-chart";
import { MERCADO_PRESETS } from "./chart-helpers";

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchPtax().then(setPtax),
      fetchCommodities().then(setCommodities).catch(() => {}),
      fetchComexYearly().then((r) => {
        // Pivot by year
        const pivot: Record<number, Record<string, unknown>> = {};
        for (const row of r.rows) {
          if (!pivot[row.ano]) pivot[row.ano] = { ano: row.ano };
          pivot[row.ano][row.fluxo] = row.valor_fob_usd;
        }
        setComexYearly(Object.values(pivot).sort((a, b) => (a.ano as number) - (b.ano as number)));
      }),
      fetchComexByUF().then((r) => setComexByUF(r.rows)),
      fetchComexByCountry().then((r) => setComexByCountry(r.rows)),
    ])
      .catch((e) => console.error("mercado:", e))
      .finally(() => setLoading(false));
  }, []);

  // Select the right data based on active preset
  const chartData = useCallback((): Record<string, unknown>[] | null => {
    switch (activeMetric) {
      case "cambio": {
        if (!ptax) return null;
        const step = Math.max(1, Math.floor(ptax.rows.length / 200));
        return ptax.rows
          .filter((_, i) => i % step === 0 || i === ptax.rows.length - 1)
          .map((r) => ({ data: r.data, valor: Number(r.cotacao_venda) }));
      }
      case "comex-anual":
        return comexYearly;
      case "comex-pais":
        return comexByCountry as Record<string, unknown>[] | null;
      case "comex-uf":
        return comexByUF as Record<string, unknown>[] | null;
      default:
        return null;
    }
  }, [activeMetric, ptax, comexYearly, comexByCountry, comexByUF]);

  return (
    <div className="space-y-4">
      <MetricChart
        presets={MERCADO_PRESETS}
        activePreset={activeMetric}
        onPresetChange={onMetricChange}
        data={chartData()}
        loading={loading}
      />

      {/* Commodity price cards */}
      {commodities && commodities.latest && Object.keys(commodities.latest).length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Cotações de Minerais</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(commodities.latest).map(([mineral, data]) => (
                <div key={mineral} className="rounded-lg border p-3">
                  <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
                    {mineral}
                  </p>
                  <p className="mt-1 text-lg font-bold tabular-nums">
                    {data.preco_usd ?? "—"}
                  </p>
                  {data.unidade && (
                    <p className="text-[10px] text-muted-foreground">{data.unidade}</p>
                  )}
                </div>
              ))}
            </div>
            <p className="mt-3 text-[10px] text-muted-foreground/60">
              Fonte: commodity_prices.csv (referência manual — dados 2024)
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
