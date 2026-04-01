"use client";

import { useEffect, useState } from "react";
import {
  BarChart3,
  FileWarning,
  Landmark,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/stat-card";
import {
  fetchOverviewStats,
  fetchOverviewTrend,
  fmtNumber,
  fmtPct,
  type OverviewStats,
  type TrendPoint,
} from "@/lib/api";
import { TrendChart } from "./trend-chart";

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [trend, setTrend] = useState<TrendPoint[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverviewStats().then(setStats).catch((e) => setError(e.message));
    fetchOverviewTrend().then(setTrend).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Visão Geral
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Panorama consolidado do licenciamento ambiental minerário em Minas Gerais
        </p>
      </div>

      {/* Error state */}
      {error && (
        <Card className="border-destructive/30">
          <CardContent className="p-6 text-sm text-destructive">
            Erro ao carregar dados: {error}.
            <span className="text-muted-foreground"> Verifique se a API está rodando.</span>
          </CardContent>
        </Card>
      )}

      {/* KPI cards */}
      {stats ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Total Decisões"
            value={fmtNumber(stats.total_decisoes)}
            subtitle="processos analisados"
            icon={BarChart3}
          />
          <StatCard
            label="Aprovação Mineração"
            value={fmtPct(stats.taxa_aprovacao_mineracao)}
            subtitle={`${fmtNumber(stats.total_decisoes_mineracao)} decisões minerárias`}
            icon={TrendingUp}
            accentClass="bg-brand-teal"
          />
          <StatCard
            label="Licenças IBAMA"
            value={fmtNumber(stats.total_infracoes)}
            subtitle="licenças emitidas"
            icon={FileWarning}
            accentClass="bg-brand-orange"
          />
          <StatCard
            label="Processos ANM"
            value={fmtNumber(stats.total_processos_anm)}
            subtitle="títulos minerários"
            icon={Landmark}
          />
        </div>
      ) : !error ? (
        <KPISkeleton />
      ) : null}

      {/* Trend chart */}
      {trend ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-heading">
              <TrendingUp className="h-4 w-4 text-brand-teal" />
              Tendência Anual de Decisões
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TrendChart data={trend} />
          </CardContent>
        </Card>
      ) : !error ? (
        <Card>
          <CardHeader>
            <CardTitle>Tendência Anual</CardTitle>
          </CardHeader>
          <CardContent>
            <Skeleton className="h-64 w-full" />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function KPISkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i}>
          <CardContent className="flex items-start gap-4 p-5">
            <Skeleton className="h-10 w-10 rounded-lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="h-7 w-24" />
              <Skeleton className="h-3 w-32" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
