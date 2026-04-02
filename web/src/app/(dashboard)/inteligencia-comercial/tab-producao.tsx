"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchCfemTimeSeries,
  fetchCfemTopMunicipios,
  fetchCfemTopSubstancias,
  fetchRalTopSubstanciasValue,
  fetchIbamaInfracoesTrend,
  fetchSemadLicensingTrend,
  type CfemTimeRow,
} from "@/lib/api";
import { MetricChart } from "./metric-chart";
import { PRODUCAO_PRESETS } from "./chart-helpers";

interface ProducaoTabProps {
  activeMetric: string;
  onMetricChange: (id: string) => void;
}

export function ProducaoTab({ activeMetric, onMetricChange }: ProducaoTabProps) {
  const [cfemTime, setCfemTime] = useState<Record<string, unknown>[] | null>(null);
  const [cfemMun, setCfemMun] = useState<Record<string, unknown>[] | null>(null);
  const [cfemSub, setCfemSub] = useState<Record<string, unknown>[] | null>(null);
  const [ralValue, setRalValue] = useState<Record<string, unknown>[] | null>(null);
  const [ibamaInfracoes, setIbamaInfracoes] = useState<Record<string, unknown>[] | null>(null);
  const [semadTrend, setSemadTrend] = useState<Record<string, unknown>[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchCfemTimeSeries().then((r) => {
        setCfemTime(
          r.rows.map((row: CfemTimeRow) => ({
            ...row,
            periodo: `${row.ano}-${String(row.mes).padStart(2, "0")}`,
          }))
        );
      }),
      fetchCfemTopMunicipios().then((r) => setCfemMun(r.rows)),
      fetchCfemTopSubstancias().then((r) => setCfemSub(r.rows)),
      fetchRalTopSubstanciasValue().then((r) => setRalValue(r.rows)),
      fetchIbamaInfracoesTrend()
        .then((r) => setIbamaInfracoes(r.rows))
        .catch(() => setIbamaInfracoes([])),
      fetchSemadLicensingTrend()
        .then((r) => setSemadTrend(r.rows))
        .catch(() => setSemadTrend([])),
    ])
      .catch((e) => console.error("producao:", e))
      .finally(() => setLoading(false));
  }, []);

  const chartData = useCallback((): Record<string, unknown>[] | null => {
    switch (activeMetric) {
      case "cfem-mensal":
        return cfemTime;
      case "cfem-municipio":
        return cfemMun;
      case "cfem-substancia":
        return cfemSub;
      case "ral-producao":
        return ralValue;
      case "ibama-infracoes":
        return ibamaInfracoes;
      case "semad-licenciamento":
        return semadTrend;
      default:
        return null;
    }
  }, [activeMetric, cfemTime, cfemMun, cfemSub, ralValue, ibamaInfracoes, semadTrend]);

  return (
    <MetricChart
      presets={PRODUCAO_PRESETS}
      activePreset={activeMetric}
      onPresetChange={onMetricChange}
      data={chartData()}
      loading={loading}
    />
  );
}
