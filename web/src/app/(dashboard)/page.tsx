"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Building2,
  Database,
  ExternalLink,
  FileSearch,
  Globe,
  Info,
  Landmark,
  Map,
  RotateCcw,
  ShieldCheck,
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
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/stat-card";
import {
  fetchOverviewStats,
  fetchMetaSources,
  fmtNumber,
  fmtPct,
  type OverviewStats,
  type SourceMeta,
} from "@/lib/api";

/* ── Platform map data ── */

const PLATFORM_MAP = [
  {
    section: "Análise & Pesquisa",
    subtitle: "Investigue empresas, decisões e dados brutos do licenciamento ambiental",
    color: "text-brand-orange",
    borderColor: "border-brand-orange/20",
    items: [
      { href: "/empresa", icon: Building2, label: "Consulta Empresa", desc: "Dossier completo por CNPJ ou CPF" },
      { href: "/explorar", icon: Database, label: "Explorador", desc: "Acesso direto a 16+ bases de dados públicas" },
      { href: "/decisoes", icon: BarChart3, label: "Análise de Decisões", desc: "Tendências, fatores de risco, padrões regionais" },
    ],
  },
  {
    section: "Direitos Minerários",
    subtitle: "Explore títulos minerários, mapeie concessões e identifique oportunidades",
    color: "text-brand-teal",
    borderColor: "border-brand-teal/20",
    items: [
      { href: "/mapa", icon: Map, label: "Mapa Interativo", desc: "Concessões, UCs e Terras Indígenas em camadas" },
      { href: "/concessoes", icon: FileSearch, label: "Concessões", desc: "Base pesquisável com filtros e exportação CSV" },
      { href: "/prospeccao", icon: TrendingUp, label: "Prospecção Mineral", desc: "Scoring de oportunidades por potencial" },
    ],
  },
  {
    section: "Mercado & Conformidade",
    subtitle: "Acompanhe indicadores de mercado e avalie a aderência regulatória",
    color: "text-brand-gold",
    borderColor: "border-brand-gold/20",
    items: [
      { href: "/inteligencia-comercial", icon: Globe, label: "Inteligência Comercial", desc: "Câmbio, comércio exterior, CFEM, cotações" },
      { href: "/due-diligence", icon: ShieldCheck, label: "Due Diligence", desc: "Avaliação estruturada de conformidade ambiental" },
    ],
  },
];

/* ── Page ── */

function relativeTime(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    const diffMs = Date.now() - d.getTime();
    const diffH = Math.floor(diffMs / 3_600_000);
    if (diffH < 1) return "agora";
    if (diffH < 24) return `${diffH}h atrás`;
    const diffD = Math.floor(diffH / 24);
    if (diffD === 1) return "ontem";
    if (diffD < 30) return `${diffD}d atrás`;
    return dateStr;
  } catch { return dateStr; }
}

export default function HomePage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [sources, setSources] = useState<SourceMeta[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(() => {
    setError(null);
    fetchOverviewStats().then(setStats).catch((e) => setError(e.message));
    fetchMetaSources().then(setSources).catch((e) => { console.error("sources:", e); });
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Summo Quartile
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Inteligência ambiental e mineral para mineração no Brasil
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Link
            href="/empresa"
            className="inline-flex items-center gap-2 rounded-lg bg-brand-orange px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-orange/90"
          >
            <Building2 className="h-4 w-4" />
            Consultar Empresa
          </Link>
          <Link
            href="/mapa"
            className="inline-flex items-center gap-2 rounded-lg border border-brand-teal/30 bg-brand-teal/5 px-4 py-2.5 text-sm font-medium text-brand-teal transition-colors hover:bg-brand-teal/10"
          >
            <Map className="h-4 w-4" />
            Explorar Mapa
          </Link>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <Card className="border-destructive/30">
          <CardContent className="flex items-center justify-between gap-4 p-6">
            <p className="text-sm text-destructive">
              Erro ao carregar dados: {error}.
              <span className="text-muted-foreground"> Verifique se a API está rodando.</span>
            </p>
            <Button variant="outline" size="sm" onClick={loadData}>
              <RotateCcw className="mr-2 h-3.5 w-3.5" />
              Tentar novamente
            </Button>
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
            label="Infrações IBAMA"
            value={fmtNumber(stats.total_infracoes)}
            subtitle="infrações ambientais · Fonte: IBAMA"
            icon={ShieldCheck}
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

      {/* Platform map — walkthrough */}
      <div>
        <h2 className="font-heading text-lg font-semibold tracking-tight">
          Mapa da Plataforma
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Explore as ferramentas disponíveis por área de atuação
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {PLATFORM_MAP.map((group) => (
            <Card key={group.section} className={`border ${group.borderColor} transition-shadow hover:shadow-md`}>
              <CardHeader className="pb-3">
                <CardTitle className={`text-sm font-semibold uppercase tracking-wide ${group.color}`}>
                  {group.section}
                </CardTitle>
                <p className="text-xs text-muted-foreground">{group.subtitle}</p>
              </CardHeader>
              <CardContent className="space-y-1 pt-0">
                {group.items.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="group flex items-start gap-3 rounded-lg px-2 py-2.5 transition-colors hover:bg-muted/50"
                  >
                    <item.icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground group-hover:text-foreground" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium group-hover:text-foreground">
                        {item.label}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {item.desc}
                      </p>
                    </div>
                    <ArrowRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground/0 transition-all group-hover:text-muted-foreground/60 group-hover:translate-x-0.5" />
                  </Link>
                ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Data sources — ALWAYS VISIBLE */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 font-heading text-base">
            <Database className="h-4 w-4 text-brand-teal" />
            Fontes de Dados
          </CardTitle>
        </CardHeader>
        <CardContent>
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
                      <td className="py-2 pr-4 text-muted-foreground tabular-nums" title={src.last_collected ?? undefined}>
                        {src.last_collected ? relativeTime(src.last_collected) : "—"}
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
        </CardContent>
      </Card>

      {/* Methodology — expandable */}
      <Accordion type="single" collapsible>
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
