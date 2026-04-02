"use client";

import { useEffect, useState } from "react";
import {
  BarChart3,
  Database,
  ExternalLink,
  FileWarning,
  Info,
  Landmark,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/stat-card";
import {
  fetchOverviewStats,
  fetchOverviewTrend,
  fetchOverviewInsights,
  fetchMetaSources,
  fmtNumber,
  fmtPct,
  type OverviewStats,
  type TrendPoint,
  type Insight,
  type SourceMeta,
} from "@/lib/api";
import { TrendChart } from "./trend-chart";

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [trend, setTrend] = useState<TrendPoint[] | null>(null);
  const [insights, setInsights] = useState<Insight[] | null>(null);
  const [sources, setSources] = useState<SourceMeta[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverviewStats().then(setStats).catch((e) => setError(e.message));
    fetchOverviewTrend().then(setTrend).catch((e) => { console.error("trend:", e); });
    fetchOverviewInsights().then(setInsights).catch((e) => { console.error("insights:", e); });
    fetchMetaSources().then(setSources).catch((e) => { console.error("sources:", e); });
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
        <p className="mt-0.5 text-xs text-muted-foreground/60">
          Fontes: SEMAD/MG, IBAMA, ANM/SIGMINE, CFEM, COPAM
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
            subtitle="processos analisados · Fonte: SEMAD MG"
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
            subtitle="licenças emitidas · Fonte: IBAMA SISLIC"
            icon={FileWarning}
            accentClass="bg-brand-orange"
          />
          <StatCard
            label="Processos ANM"
            value={fmtNumber(stats.total_processos_anm)}
            subtitle="títulos minerários · Fonte: ANM SIGMINE"
            icon={Landmark}
          />
        </div>
      ) : !error ? (
        <KPISkeleton />
      ) : null}

      {/* Insights panel alongside trend chart */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Trend chart (2 cols) */}
        <div className="lg:col-span-2">
          {trend ? (
            <Card className="h-full">
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

        {/* Insights sidebar (1 col) */}
        {insights ? (
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading text-base">
                <Info className="h-4 w-4 text-brand-orange" />
                Insights Chave
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {insights.map((ins, i) => (
                <InsightCard key={i} tone={ins.tone} title={ins.title} value={ins.value} detail={ins.detail} />
              ))}
            </CardContent>
          </Card>
        ) : stats ? (
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading text-base">
                <Info className="h-4 w-4 text-brand-orange" />
                Insights Chave
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </CardContent>
          </Card>
        ) : null}
      </div>

      {/* Data sources + methodology */}
      <Accordion type="multiple" className="space-y-3">
        <AccordionItem value="sources" className="rounded-xl border bg-card shadow-sm">
          <AccordionTrigger className="px-6 py-4 hover:no-underline">
            <div className="flex items-center gap-2 font-heading text-base">
              <Database className="h-4 w-4 text-brand-teal" />
              Fontes de Dados
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-6 pb-4">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Fonte</th>
                    <th className="pb-2 pr-4 text-right font-medium">Registros</th>
                    <th className="pb-2 pr-4 font-medium">Atualização</th>
                    <th className="pb-2 font-medium">Link</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {(sources ?? FALLBACK_SOURCES).map((src) => {
                    const isFresh = !!src.last_collected;
                    return (
                      <tr key={src.key ?? src.name}>
                        <td className="py-2 pr-4 font-medium">
                          <span
                            className="mr-2 inline-block h-1.5 w-1.5 rounded-full align-middle"
                            style={{ background: isFresh ? "var(--success)" : "var(--danger)" }}
                          />
                          {src.name}
                        </td>
                        <td className="py-2 pr-4 text-right tabular-nums">
                          {src.records != null ? fmtNumber(src.records) : <span className="text-muted-foreground">—</span>}
                        </td>
                        <td className="py-2 pr-4 text-muted-foreground tabular-nums">
                          {src.last_collected ?? "—"}
                        </td>
                        <td className="py-2">
                          {src.url ? (
                            <a
                              href={src.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-brand-teal hover:underline"
                            >
                              verificar <ExternalLink className="h-3 w-3" />
                            </a>
                          ) : null}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="methodology" className="rounded-xl border bg-card shadow-sm">
          <AccordionTrigger className="px-6 py-4 hover:no-underline">
            <div className="flex items-center gap-2 font-heading text-base">
              <Info className="h-4 w-4 text-brand-orange" />
              Sobre / Metodologia
            </div>
          </AccordionTrigger>
          <AccordionContent className="px-6 pb-4">
            <div className="space-y-2 text-sm text-muted-foreground leading-relaxed">
              <p>
                O Sistema Integrado Summo Quartile consolida dados de múltiplas fontes públicas
                oficiais para oferecer inteligência ambiental, mineral e operacional.
              </p>
              <p>
                <strong>Decisões SEMAD:</strong> Extraídas do portal de licenciamento ambiental do
                estado de Minas Gerais. Incluem decisões de deferimento, indeferimento e arquivamento
                classificadas por atividade (DN COPAM 217/2017), classe de impacto (1-6) e regional.
              </p>
              <p>
                <strong>ANM/SIGMINE:</strong> Dados de títulos minerários via ArcGIS REST API. Inclui
                processos de concessão de lavra, licenciamento, pesquisa e lavra garimpeira.
              </p>
              <p>
                <strong>CFEM:</strong> Compensação Financeira pela Exploração de Recursos Minerais,
                com dados de pagamentos por município e substância mineral.
              </p>
              <p>
                <strong>Auditabilidade:</strong> Todo registro no sistema é rastreável à URL da fonte
                original. Dados processados em formato Parquet e consultados via DuckDB.
              </p>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

const FALLBACK_SOURCES: SourceMeta[] = [
  { key: "mg_semad", name: "MG SEMAD Decisões", records: null, last_collected: null, url: "https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca" },
  { key: "ibama_licencas", name: "IBAMA Licenças Federais", records: null, last_collected: null, url: "https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json" },
  { key: "anm_processos", name: "ANM SIGMINE Processos", records: null, last_collected: null, url: "https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0" },
  { key: "ibama_infracoes", name: "IBAMA Infrações Ambientais", records: null, last_collected: null, url: "https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao" },
  { key: "anm_cfem", name: "ANM CFEM Royalties", records: null, last_collected: null, url: "https://app.anm.gov.br/dadosabertos/ARRECADACAO/" },
  { key: "anm_ral", name: "ANM RAL Produção", records: null, last_collected: null, url: "https://app.anm.gov.br/dadosabertos/AMB/" },
  { key: "receita_federal_cnpj", name: "Receita Federal CNPJ", records: null, last_collected: null, url: "https://brasilapi.com.br/api/cnpj/v1/" },
  { key: "copam_cmi", name: "COPAM CMI Reuniões", records: null, last_collected: null, url: "https://sistemas.meioambiente.mg.gov.br/reunioes/reuniao-copam/index-externo" },
  { key: "icmbio_ucs", name: "ICMBio Unidades Conservação", records: null, last_collected: null, url: "https://www.gov.br/icmbio/pt-br/assuntos/dados_geoespaciais/" },
];

function InsightCard({ tone, title, value, detail }: {
  tone: "positive" | "neutral" | "negative";
  title?: string;
  value?: string;
  detail?: string;
}) {
  const toneClasses = {
    positive: "border-l-success bg-success/5",
    neutral: "border-l-muted-foreground bg-muted/30",
    negative: "border-l-danger bg-danger/5",
  };

  return (
    <div className={`rounded-r-md border-l-2 px-3 py-2.5 ${toneClasses[tone]}`}>
      {title && <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">{title}</p>}
      {value && <p className="text-sm font-semibold">{value}</p>}
      {detail && <p className="text-xs text-muted-foreground">{detail}</p>}
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
