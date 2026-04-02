"use client";

import { useEffect, useState } from "react";
import {
  Globe,
  DollarSign,
  Ship,
  Coins,
  MapPin,
  Loader2,
} from "lucide-react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/stat-card";
import {
  fetchPtax,
  fetchCommodities,
  fetchComexYearly,
  fetchComexByUF,
  fetchCfemTopMunicipios,
  fetchCfemTopSubstancias,
  fetchRalTopSubstancias,
  fetchAnmByFase,
  fetchAnmBySubstancia,
  fetchAnmStats,
  type PtaxResponse,
  type CommodityResponse,
} from "@/lib/api";
import { fmtBR, fmtReais, fmtCompact } from "@/lib/format";

const CHART_TOOLTIP_STYLE = {
  background: "var(--card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  fontSize: 12,
};

export default function InteligenciaComercialPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-gold">
          <Globe className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
            Inteligência Comercial
          </h1>
          <p className="text-xs text-muted-foreground">
            Mineral Intelligence — 4 pilares: Mercado, Comércio Exterior, Arrecadação, Território
          </p>
        </div>
      </div>

      <Tabs defaultValue="mercado" className="space-y-6">
        <TabsList className="flex flex-wrap h-auto gap-1">
          <TabsTrigger value="mercado" className="gap-1.5 text-xs">
            <DollarSign className="h-3.5 w-3.5" />
            Mercado e Cotações
          </TabsTrigger>
          <TabsTrigger value="comex" className="gap-1.5 text-xs">
            <Ship className="h-3.5 w-3.5" />
            Comércio Exterior
          </TabsTrigger>
          <TabsTrigger value="arrecadacao" className="gap-1.5 text-xs">
            <Coins className="h-3.5 w-3.5" />
            Produção e Arrecadação
          </TabsTrigger>
          <TabsTrigger value="territorio" className="gap-1.5 text-xs">
            <MapPin className="h-3.5 w-3.5" />
            Gestão e Território
          </TabsTrigger>
        </TabsList>

        <TabsContent value="mercado"><MercadoTab /></TabsContent>
        <TabsContent value="comex"><ComexTab /></TabsContent>
        <TabsContent value="arrecadacao"><ArrecadacaoTab /></TabsContent>
        <TabsContent value="territorio"><TerritorioTab /></TabsContent>
      </Tabs>
    </div>
  );
}

/* ── Tab 1: Mercado & Cotações ── */

function MercadoTab() {
  const [ptax, setPtax] = useState<PtaxResponse | null>(null);
  const [commodities, setCommodities] = useState<CommodityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetchPtax().then(setPtax),
      fetchCommodities().then(setCommodities).catch(() => {}),
    ])
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ChartSkeleton />;
  if (error || !ptax) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center py-12 text-sm text-muted-foreground">
          <DollarSign className="h-8 w-8 text-muted-foreground/30 mb-2" />
          {error ? `Erro: ${error}` : "Dados de câmbio ainda não disponíveis."}
        </CardContent>
      </Card>
    );
  }

  // Thin out the chart data for performance (show ~200 points)
  const step = Math.max(1, Math.floor(ptax.rows.length / 200));
  const chartData = ptax.rows
    .filter((_, i) => i % step === 0 || i === ptax.rows.length - 1)
    .map((r) => ({
      data: r.data,
      valor: Number(r.cotacao_venda),
    }));

  return (
    <div className="space-y-4">
      {ptax.latest && (
        <div className="grid gap-4 sm:grid-cols-2">
          <StatCard
            label="USD/BRL (Venda)"
            value={`R$ ${fmtBR(Number(ptax.latest.cotacao_venda), 4)}`}
            subtitle={`Última cotação: ${ptax.latest.data}`}
            icon={DollarSign}
            accentClass="bg-brand-gold"
          />
          <StatCard
            label="Total de Cotações"
            value={fmtBR(ptax.total)}
            subtitle="série histórica BCB PTAX"
            icon={DollarSign}
          />
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Câmbio USD/BRL — Série Histórica
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="data" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
              <YAxis tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" domain={["auto", "auto"]} />
              <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
              <Line type="monotone" dataKey="valor" stroke="var(--brand-gold)" strokeWidth={1.5} dot={false} name="USD/BRL" />
            </LineChart>
          </ResponsiveContainer>
          <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: BCB PTAX</p>
        </CardContent>
      </Card>

      {/* Commodity Prices */}
      {commodities && commodities.latest && Object.keys(commodities.latest).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Cotações de Minerais
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {Object.entries(commodities.latest).map(([mineral, data]) => (
                <div key={mineral} className="rounded-lg border p-3">
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {mineral}
                  </p>
                  <p className="mt-1 text-lg font-bold tabular-nums">
                    {data.preco ?? data.price ?? Object.values(data).find((v) => typeof v === "string" && /[\d.,]/.test(v)) ?? "—"}
                  </p>
                  {(data.unidade ?? data.unit) && (
                    <p className="text-[10px] text-muted-foreground">{data.unidade ?? data.unit}</p>
                  )}
                </div>
              ))}
            </div>
            <p className="mt-3 text-[10px] text-muted-foreground/60">
              Fonte: commodity_prices.csv (referência manual)
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ── Tab 2: Comércio Exterior ── */

function ComexTab() {
  const [yearly, setYearly] = useState<{ ano: number; fluxo: string; valor_fob_usd: number }[] | null>(null);
  const [byUF, setByUF] = useState<{ uf: string; valor_fob_usd: number }[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchComexYearly(), fetchComexByUF()])
      .then(([y, uf]) => {
        setYearly(y.rows);
        setByUF(uf.rows);
      })
      .catch((e) => { console.error("comex:", e); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ChartSkeleton />;

  // Pivot yearly by fluxo
  const yearlyPivot: Record<number, { ano: number; Exportação?: number; Importação?: number }> = {};
  for (const r of yearly ?? []) {
    if (!yearlyPivot[r.ano]) yearlyPivot[r.ano] = { ano: r.ano };
    yearlyPivot[r.ano][r.fluxo as "Exportação" | "Importação"] = r.valor_fob_usd;
  }
  const yearlyChart = Object.values(yearlyPivot).sort((a, b) => a.ano - b.ano);

  return (
    <div className="space-y-4">
      {yearlyChart.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Exportação vs Importação — Mineração (USD FOB)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={yearlyChart} margin={{ top: 5, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="ano" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
                <YAxis tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={(v: number) => fmtCompact(v)} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => fmtReais(Number(v))} />
                <Legend />
                <Bar dataKey="Exportação" fill="var(--brand-teal)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Importação" fill="var(--brand-orange)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: Comex Stat / MDIC — NCM Cap. 26 (Minérios)</p>
          </CardContent>
        </Card>
      )}

      {byUF && byUF.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top 10 UFs por Exportação (USD FOB)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byUF} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={(v: number) => fmtCompact(v)} />
                <YAxis type="category" dataKey="uf" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" width={40} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => fmtReais(Number(v))} />
                <Bar dataKey="valor_fob_usd" fill="var(--brand-teal)" radius={[0, 4, 4, 0]} name="USD FOB" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: Comex Stat / MDIC</p>
          </CardContent>
        </Card>
      )}

      {(!yearly || yearly.length === 0) && (
        <EmptyData message="Dados de comércio exterior ainda não disponíveis." />
      )}
    </div>
  );
}

/* ── Tab 3: Produção & Arrecadação ── */

function ArrecadacaoTab() {
  const [cfemMun, setCfemMun] = useState<{ municipio: string; total: number }[] | null>(null);
  const [cfemSub, setCfemSub] = useState<{ substancia: string; total: number }[] | null>(null);
  const [ralSub, setRalSub] = useState<{ substancia: string; n: number }[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchCfemTopMunicipios(), fetchCfemTopSubstancias(), fetchRalTopSubstancias()])
      .then(([mun, sub, ral]) => {
        setCfemMun(mun.rows);
        setCfemSub(sub.rows);
        setRalSub(ral.rows);
      })
      .catch((e) => { console.error("cfem:", e); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ChartSkeleton />;

  return (
    <div className="space-y-4">
      {cfemMun && cfemMun.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top 15 Municípios por Arrecadação CFEM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={cfemMun} layout="vertical" margin={{ top: 5, right: 20, left: 100, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={(v: number) => fmtCompact(v)} />
                <YAxis type="category" dataKey="municipio" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" width={100} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => fmtReais(Number(v))} />
                <Bar dataKey="total" fill="var(--brand-gold)" radius={[0, 4, 4, 0]} name="CFEM (R$)" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: ANM — CFEM Arrecadação</p>
          </CardContent>
        </Card>
      )}

      {cfemSub && cfemSub.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top 10 Substâncias por Arrecadação CFEM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={cfemSub} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" tickFormatter={(v: number) => fmtCompact(v)} />
                <YAxis type="category" dataKey="substancia" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" width={80} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} formatter={(v) => fmtReais(Number(v))} />
                <Bar dataKey="total" fill="var(--brand-orange)" radius={[0, 4, 4, 0]} name="CFEM (R$)" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: ANM — CFEM Arrecadação</p>
          </CardContent>
        </Card>
      )}

      {ralSub && ralSub.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top 10 Substâncias — Relatório Anual de Lavra (RAL)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ralSub} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
                <YAxis type="category" dataKey="substancia" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" width={80} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="n" fill="var(--brand-teal)" radius={[0, 4, 4, 0]} name="Registros" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: ANM — CFEM + RAL</p>
          </CardContent>
        </Card>
      )}

      {(!cfemMun || cfemMun.length === 0) && (!cfemSub || cfemSub.length === 0) && (
        <EmptyData message="Dados CFEM/RAL ainda não disponíveis." />
      )}
    </div>
  );
}

/* ── Tab 4: Gestão e Território ── */

function TerritorioTab() {
  const [byFase, setByFase] = useState<{ fase: string; n: number }[] | null>(null);
  const [bySubs, setBySubs] = useState<{ substancia: string; n: number }[] | null>(null);
  const [stats, setStats] = useState<{ total_records: number } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchAnmByFase(), fetchAnmBySubstancia(), fetchAnmStats()])
      .then(([fase, subs, st]) => {
        setByFase(fase.rows);
        setBySubs(subs.rows);
        setStats(st);
      })
      .catch((e) => { console.error("territorio:", e); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ChartSkeleton />;

  return (
    <div className="space-y-4">
      {stats && (
        <StatCard
          label="Processos ANM"
          value={fmtBR(stats.total_records)}
          subtitle="total de processos minerários registrados"
          icon={MapPin}
          accentClass="bg-brand-teal"
        />
      )}

      {byFase && byFase.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Processos Minerários por Fase
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byFase} layout="vertical" margin={{ top: 5, right: 20, left: 120, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
                <YAxis type="category" dataKey="fase" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" width={120} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="n" fill="var(--brand-teal)" radius={[0, 4, 4, 0]} name="Processos" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: ANM / SIGMINE</p>
          </CardContent>
        </Card>
      )}

      {bySubs && bySubs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Top 15 Substâncias por Processos ANM
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={bySubs} layout="vertical" margin={{ top: 5, right: 20, left: 100, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} stroke="var(--muted-foreground)" />
                <YAxis type="category" dataKey="substancia" tick={{ fontSize: 9 }} stroke="var(--muted-foreground)" width={100} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
                <Bar dataKey="n" fill="var(--brand-orange)" radius={[0, 4, 4, 0]} name="Processos" />
              </BarChart>
            </ResponsiveContainer>
            <p className="mt-2 text-[10px] text-muted-foreground/60">Fonte: ANM / SIGMINE</p>
          </CardContent>
        </Card>
      )}

      {(!byFase || byFase.length === 0) && (
        <EmptyData message="Dados ANM ainda não disponíveis." />
      )}
    </div>
  );
}

/* ── Shared ── */

function ChartSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

function EmptyData({ message }: { message: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center py-12 text-sm text-muted-foreground">
        <Globe className="h-8 w-8 text-muted-foreground/30 mb-2" />
        {message}
      </CardContent>
    </Card>
  );
}
