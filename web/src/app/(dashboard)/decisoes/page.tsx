"use client";

import { useEffect, useState } from "react";
import {
  BarChart3,
  FileWarning,
  TrendingDown,
  MapPin,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  fetchApprovalRates,
  fetchDecisionsByModalidade,
  fetchRejectionTrend,
  fetchRegionalRigor,
  fetchInfractionBands,
  fetchInfractionsVsApproval,
  fmtNumber,
  fmtPct,
  type RejectionTrend,
  type RegionalRigor,
  type InfractionBand,
  type InfractionsVsApproval,
} from "@/lib/api";

const CHART_TOOLTIP_STYLE = {
  background: "var(--card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  fontSize: 13,
};

export default function DecisoesPage() {
  const [rejectionTrend, setRejectionTrend] = useState<RejectionTrend[] | null>(null);
  const [regionalRigor, setRegionalRigor] = useState<RegionalRigor[] | null>(null);
  const [modalidade, setModalidade] = useState<Record<string, unknown>[] | null>(null);
  const [approvalRates, setApprovalRates] = useState<Record<string, unknown>[] | null>(null);
  const [infractionBands, setInfractionBands] = useState<InfractionBand[] | null>(null);
  const [infractionsVsApproval, setInfractionsVsApproval] = useState<InfractionsVsApproval[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRejectionTrend().then(setRejectionTrend).catch((e) => setError(e.message));
    fetchRegionalRigor().then(setRegionalRigor).catch((e) => { console.error("regionalRigor:", e); });
    fetchDecisionsByModalidade().then(setModalidade).catch((e) => { console.error("modalidade:", e); });
    fetchApprovalRates().then(setApprovalRates).catch((e) => { console.error("approvalRates:", e); });
    fetchInfractionBands().then(setInfractionBands).catch((e) => { console.error("infractionBands:", e); });
    fetchInfractionsVsApproval().then(setInfractionsVsApproval).catch((e) => { console.error("infractionsVsApproval:", e); });
  }, []);

  // Aggregate modalidade data for stacked view
  const modalidadeAgg = modalidade
    ? Object.values(
        modalidade.reduce<Record<string, Record<string, unknown>>>((acc, row) => {
          const key = String(row.modalidade);
          if (!acc[key]) acc[key] = { modalidade: key, deferido: 0, indeferido: 0, outros: 0 };
          const decisao = String(row.decisao);
          const n = Number(row.n);
          if (decisao === "deferido") acc[key].deferido = (acc[key].deferido as number) + n;
          else if (decisao === "indeferido") acc[key].indeferido = (acc[key].indeferido as number) + n;
          else acc[key].outros = (acc[key].outros as number) + n;
          return acc;
        }, {})
      )
        .sort((a, b) => {
          const totalA = (a.deferido as number) + (a.indeferido as number) + (a.outros as number);
          const totalB = (b.deferido as number) + (b.indeferido as number) + (b.outros as number);
          return totalB - totalA;
        })
        .slice(0, 10)
    : null;

  // Aggregate approval rates by year
  const yearlyRates = approvalRates
    ? Object.values(
        approvalRates.reduce<Record<number, { ano: number; total: number; deferidos: number }>>(
          (acc, row) => {
            const ano = Number(row.ano);
            if (!acc[ano]) acc[ano] = { ano, total: 0, deferidos: 0 };
            acc[ano].total += Number(row.total);
            acc[ano].deferidos += Number(row.deferidos);
            return acc;
          },
          {}
        )
      )
        .map((r) => ({ ...r, taxa: r.total > 0 ? Math.round((1000 * r.deferidos) / r.total) / 10 : 0 }))
        .sort((a, b) => a.ano - b.ano)
    : null;

  // KPIs from rejection trend
  const latestYear = rejectionTrend?.at(-1);
  const prevYear = rejectionTrend?.at(-2);
  const trendDelta =
    latestYear && prevYear
      ? latestYear.taxa_indeferimento - prevYear.taxa_indeferimento
      : null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Análise de Decisões
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Taxas de aprovação, tendências e análise comparativa por regional e modalidade
        </p>
        <p className="mt-0.5 text-xs text-muted-foreground/60">
          Deferido = aprovado · Indeferido = negado · Arquivamento = processo encerrado sem decisão de mérito · Classes 1-6 por impacto ambiental
        </p>
      </div>

      {error && (
        <Card className="border-destructive/30">
          <CardContent className="p-6 text-sm text-destructive">
            Erro ao carregar dados: {error}
          </CardContent>
        </Card>
      )}

      {/* KPI row */}
      {latestYear ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KPICard
            icon={BarChart3}
            label="Total Decisões (Mineração)"
            value={fmtNumber(latestYear.total)}
            subtitle={`em ${latestYear.ano}`}
          />
          <KPICard
            icon={TrendingDown}
            label="Taxa Indeferimento"
            value={fmtPct(latestYear.taxa_indeferimento)}
            subtitle={
              trendDelta !== null
                ? `${trendDelta > 0 ? "+" : ""}${trendDelta.toFixed(1)}pp vs ${prevYear!.ano}`
                : undefined
            }
            accent={latestYear.taxa_indeferimento > 20 ? "bg-danger" : undefined}
          />
          <KPICard
            icon={Activity}
            label="Arquivamentos"
            value={fmtPct(latestYear.taxa_arquivamento)}
            subtitle={`${fmtNumber(latestYear.arquivamentos)} processos`}
            accent="bg-brand-gold"
          />
          <KPICard
            icon={MapPin}
            label="Regionais"
            value={String(regionalRigor?.length ?? "—")}
            subtitle="com dados suficientes"
          />
        </div>
      ) : !error ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}><CardContent className="p-5"><Skeleton className="h-16 w-full" /></CardContent></Card>
          ))}
        </div>
      ) : null}

      {/* Charts */}
      <Tabs defaultValue="trend" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trend">Tendência Temporal</TabsTrigger>
          <TabsTrigger value="regional">Rigor Regional</TabsTrigger>
          <TabsTrigger value="modalidade">Por Modalidade</TabsTrigger>
          <TabsTrigger value="yearly">Taxa Anual</TabsTrigger>
          <TabsTrigger value="risco">Fatores de Risco</TabsTrigger>
        </TabsList>

        {/* Tab 1: Rejection trend + insights */}
        <TabsContent value="trend">
          <div className="grid gap-4 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading">
                <TrendingDown className="h-4 w-4 text-danger" />
                Tendência de Indeferimentos (Mineração)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {rejectionTrend ? (
                <ResponsiveContainer width="100%" height={360}>
                  <AreaChart data={rejectionTrend}>
                    <defs>
                      <linearGradient id="gradIndef" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--chart-3)" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="var(--chart-3)" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="gradArq" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--chart-5)" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="var(--chart-5)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="ano" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <YAxis unit="%" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v, name) => [`${Number(v).toFixed(1)}%`, String(name)]} />
                    <Area type="monotone" dataKey="taxa_indeferimento" name="Indeferimento" stroke="var(--chart-3)" fill="url(#gradIndef)" strokeWidth={2} />
                    <Area type="monotone" dataKey="taxa_arquivamento" name="Arquivamento" stroke="var(--chart-5)" fill="url(#gradArq)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-[360px] w-full" />
              )}
            </CardContent>
          </Card>

          {/* Insights sidebar */}
          <Card>
            <CardHeader>
              <CardTitle className="font-heading text-base">Insights</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {latestYear && (
                <>
                  <InsightItem
                    tone={latestYear.taxa_indeferimento > 20 ? "negative" : "positive"}
                    text={`Indeferimento ${latestYear.ano}: ${fmtPct(latestYear.taxa_indeferimento)}`}
                  />
                  <InsightItem
                    tone="neutral"
                    text={`Arquivamentos: ${fmtPct(latestYear.taxa_arquivamento)} (${fmtNumber(latestYear.arquivamentos)} processos)`}
                  />
                </>
              )}
              {regionalRigor && regionalRigor.length > 0 && (
                <InsightItem
                  tone="negative"
                  text={`Regional mais rigorosa: ${regionalRigor.reduce((a, b) => a.taxa_indeferimento > b.taxa_indeferimento ? a : b).regional.replace("Unidade Regional de Regularização Ambiental ", "")}`}
                />
              )}
              {infractionBands && infractionBands.length > 0 && (
                <InsightItem
                  tone="neutral"
                  text={`${infractionBands.filter(b => b.faixa_infracoes.includes("6+")).reduce((a, b) => a + b.total, 0)} empresas com 6+ infrações`}
                />
              )}
            </CardContent>
          </Card>
          </div>
        </TabsContent>

        {/* Tab 2: Regional rigor */}
        <TabsContent value="regional">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading">
                <MapPin className="h-4 w-4 text-brand-teal" />
                Rigor por Regional SEMAD
              </CardTitle>
            </CardHeader>
            <CardContent>
              {regionalRigor ? (
                <ResponsiveContainer width="100%" height={Math.max(360, regionalRigor.length * 36)}>
                  <BarChart data={regionalRigor} layout="vertical" margin={{ left: 140 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" unit="%" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <YAxis
                      type="category"
                      dataKey="regional"
                      tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                      width={130}
                    />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => [`${Number(v).toFixed(1)}%`]} />
                    <Bar dataKey="taxa_indeferimento" name="Taxa Indeferimento" radius={[0, 4, 4, 0]}>
                      {regionalRigor.map((entry, i) => (
                        <Cell
                          key={i}
                          fill={
                            entry.taxa_indeferimento > 30
                              ? "var(--danger)"
                              : entry.taxa_indeferimento > 15
                              ? "var(--warning)"
                              : "var(--success)"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-[360px] w-full" />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Modalidade */}
        <TabsContent value="modalidade">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading">
                <BarChart3 className="h-4 w-4 text-brand-orange" />
                Decisões por Modalidade
              </CardTitle>
            </CardHeader>
            <CardContent>
              {modalidadeAgg ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={modalidadeAgg} layout="vertical" margin={{ left: 160 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis type="number" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <YAxis
                      type="category"
                      dataKey="modalidade"
                      tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                      width={150}
                    />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                    <Bar dataKey="deferido" name="Deferido" stackId="a" fill="var(--success)" />
                    <Bar dataKey="indeferido" name="Indeferido" stackId="a" fill="var(--danger)" />
                    <Bar dataKey="outros" name="Outros" stackId="a" fill="var(--muted)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-[400px] w-full" />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: Yearly approval */}
        <TabsContent value="yearly">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 font-heading">
                <Activity className="h-4 w-4 text-brand-teal" />
                Taxa de Aprovação Anual (Todas Atividades)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {yearlyRates ? (
                <ResponsiveContainer width="100%" height={360}>
                  <BarChart data={yearlyRates}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="ano" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <YAxis unit="%" domain={[0, 100]} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                    <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v, name) => [name === "Taxa Aprovação" ? `${Number(v).toFixed(1)}%` : fmtNumber(Number(v)), String(name)]} />
                    <Bar dataKey="taxa" name="Taxa Aprovação" radius={[4, 4, 0, 0]}>
                      {yearlyRates.map((entry, i) => (
                        <Cell
                          key={i}
                          fill={entry.taxa >= 70 ? "var(--success)" : entry.taxa >= 50 ? "var(--warning)" : "var(--danger)"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Skeleton className="h-[360px] w-full" />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 5: Risk Factors */}
        <TabsContent value="risco">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Infraction bands vs approval */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-heading text-sm">
                  <FileWarning className="h-4 w-4 text-danger" />
                  Infrações IBAMA vs. Aprovação
                </CardTitle>
              </CardHeader>
              <CardContent>
                {infractionBands ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={infractionBands}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="faixa_infracoes" tick={{ fontSize: 10, fill: "var(--muted-foreground)" }} />
                      <YAxis unit="%" domain={[0, 100]} tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} />
                      <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => [`${Number(v).toFixed(1)}%`]} />
                      <Bar dataKey="taxa_aprovacao" name="Taxa Aprovação" radius={[4, 4, 0, 0]}>
                        {infractionBands.map((entry, i) => (
                          <Cell
                            key={i}
                            fill={entry.taxa_aprovacao >= 70 ? "var(--success)" : entry.taxa_aprovacao >= 50 ? "var(--warning)" : "var(--danger)"}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Skeleton className="h-[300px] w-full" />
                )}
              </CardContent>
            </Card>

            {/* Infractions scatter */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-heading text-sm">
                  <Activity className="h-4 w-4 text-brand-orange" />
                  Dispersão: Infrações × Aprovação
                </CardTitle>
              </CardHeader>
              <CardContent>
                {infractionsVsApproval ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis
                        type="number"
                        dataKey="total_infracoes"
                        name="Infrações"
                        tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                        label={{ value: "Infrações", position: "bottom", fontSize: 11 }}
                      />
                      <YAxis
                        type="number"
                        dataKey="taxa_aprovacao"
                        name="Aprovação"
                        unit="%"
                        domain={[0, 100]}
                        tick={{ fontSize: 11, fill: "var(--muted-foreground)" }}
                      />
                      <ZAxis type="number" dataKey="total_decisoes" range={[20, 400]} />
                      <Tooltip
                        contentStyle={CHART_TOOLTIP_STYLE}
                        formatter={(v, name) => [
                          name === "Aprovação" ? `${Number(v).toFixed(1)}%` : String(v),
                          String(name),
                        ]}
                      />
                      <Scatter
                        data={infractionsVsApproval}
                        fill="var(--brand-orange)"
                        fillOpacity={0.6}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                ) : (
                  <Skeleton className="h-[300px] w-full" />
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Regional detail table */}
      {regionalRigor && (
        <Card>
          <CardHeader>
            <CardTitle className="font-heading">Detalhamento Regional</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 font-medium">Regional</th>
                    <th className="pb-2 text-right font-medium">Total</th>
                    <th className="pb-2 text-right font-medium">Deferidos</th>
                    <th className="pb-2 text-right font-medium">Indeferidos</th>
                    <th className="pb-2 text-right font-medium">Aprovação</th>
                    <th className="pb-2 text-right font-medium">Indeferimento</th>
                  </tr>
                </thead>
                <tbody>
                  {regionalRigor.map((r) => (
                    <tr key={r.regional} className="border-b border-border/50">
                      <td className="py-2 font-medium">{r.regional}</td>
                      <td className="py-2 text-right font-tabular">{fmtNumber(r.total)}</td>
                      <td className="py-2 text-right font-tabular">{fmtNumber(r.deferidos)}</td>
                      <td className="py-2 text-right font-tabular">{fmtNumber(r.indeferidos)}</td>
                      <td className="py-2 text-right">
                        <Badge variant={r.taxa_aprovacao >= 70 ? "default" : r.taxa_aprovacao >= 50 ? "secondary" : "destructive"}>
                          {fmtPct(r.taxa_aprovacao)}
                        </Badge>
                      </td>
                      <td className="py-2 text-right">
                        <Badge variant={r.taxa_indeferimento > 30 ? "destructive" : r.taxa_indeferimento > 15 ? "secondary" : "outline"}>
                          {fmtPct(r.taxa_indeferimento)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function KPICard({
  icon: Icon,
  label,
  value,
  subtitle,
  accent,
}: {
  icon: typeof BarChart3;
  label: string;
  value: string;
  subtitle?: string;
  accent?: string;
}) {
  return (
    <Card className="relative overflow-hidden">
      {accent && <div className={`absolute inset-y-0 left-0 w-1 ${accent}`} />}
      <CardContent className="flex items-start gap-4 p-5">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
          <Icon className="h-5 w-5 text-muted-foreground" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-bold font-heading font-tabular leading-none">{value}</p>
          {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
      </CardContent>
    </Card>
  );
}

function InsightItem({ tone, text }: { tone: "positive" | "neutral" | "negative"; text: string }) {
  const toneClasses = {
    positive: "border-l-success bg-success/5",
    neutral: "border-l-muted-foreground bg-muted/30",
    negative: "border-l-danger bg-danger/5",
  };
  return (
    <div className={`rounded-r-md border-l-2 px-3 py-2 text-xs ${toneClasses[tone]}`}>
      {text}
    </div>
  );
}
