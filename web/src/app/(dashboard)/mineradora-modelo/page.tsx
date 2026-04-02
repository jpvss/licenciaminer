"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Factory,
  Loader2,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import {
  fetchSimSetores,
  fetchSimSetor,
  type SimSetoresResponse,
  type SimSetorResponse,
  type SimKPI,
} from "@/lib/api";
import { fmtBR } from "@/lib/format";

const CHART_TOOLTIP_STYLE = {
  background: "var(--card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  fontSize: 12,
};

export default function MineradoraModeloPage() {
  const [setores, setSetores] = useState<SimSetoresResponse | null>(null);
  const [activeSetor, setActiveSetor] = useState<string>("");
  const [setorData, setSetorData] = useState<SimSetorResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [setorLoading, setSetorLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [setorError, setSetorError] = useState<string | null>(null);

  useEffect(() => {
    fetchSimSetores()
      .then((data) => {
        setSetores(data);
        const keys = Object.keys(data.setores);
        if (keys.length > 0) {
          setActiveSetor(keys[0]);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!activeSetor) return;
    setSetorLoading(true);
    setSetorError(null);
    fetchSimSetor(activeSetor)
      .then(setSetorData)
      .catch((e) => { setSetorError(e.message ?? "Erro ao carregar setor"); })
      .finally(() => setSetorLoading(false));
  }, [activeSetor]);

  if (loading) return <PageSkeleton />;
  if (error) {
    return (
      <div className="space-y-6">
        <PageHeader />
        <Card className="border-destructive/30">
          <CardContent className="p-6 text-sm text-destructive">
            Erro ao carregar: {error}
          </CardContent>
        </Card>
      </div>
    );
  }

  const setorKeys = setores ? Object.keys(setores.setores) : [];

  return (
    <div className="space-y-6">
      <PageHeader />

      {/* Warning banner */}
      <div className="flex items-center gap-3 rounded-lg border border-warning/30 bg-warning/5 px-4 py-3">
        <AlertTriangle className="h-5 w-5 shrink-0 text-warning" />
        <p className="text-sm">
          <span className="font-semibold">Dados 100% simulados</span>
          {" "}— operação fictícia de 5.0 MTPA de minério de ferro. Para demonstração comercial.
        </p>
      </div>

      {/* Sector tabs */}
      {setorKeys.length > 0 && (
        <Tabs value={activeSetor} onValueChange={setActiveSetor}>
          <TabsList className="flex flex-wrap h-auto gap-1">
            {setorKeys.map((s) => (
              <TabsTrigger key={s} value={s} className="text-xs whitespace-nowrap">
                {s}
              </TabsTrigger>
            ))}
          </TabsList>

          {setorKeys.map((s) => (
            <TabsContent key={s} value={s} className="space-y-4 mt-4">
              <div className="flex items-center gap-2 rounded-md bg-muted/50 px-3 py-2 text-xs text-muted-foreground">
                <AlertTriangle className="h-3.5 w-3.5 text-warning" />
                DADOS SIMULADOS — {s}
              </div>

              {setorError && !setorLoading ? (
                <Card className="border-destructive/30">
                  <CardContent className="p-6 text-sm text-destructive">
                    Erro ao carregar dados do setor: {setorError}
                  </CardContent>
                </Card>
              ) : setorData?.setor === s && !setorLoading ? (
                <div className="space-y-6">
                  {/* KPI cards grid */}
                  <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    {setorData.kpis.map((kpi) => (
                      <KPICard key={kpi.nome} kpi={kpi} />
                    ))}
                  </div>

                  {/* Trend charts */}
                  {setorData.kpis.map((kpi) => (
                    <KPIChart key={kpi.nome} kpi={kpi} />
                  ))}
                </div>
              ) : (
                <KPISkeleton />
              )}
            </TabsContent>
          ))}
        </Tabs>
      )}

      {/* Model parameters footer */}
      <Card>
        <CardContent className="p-4">
          <div className="grid gap-4 text-xs text-muted-foreground sm:grid-cols-3">
            <div>
              <p className="font-medium text-foreground">Produção</p>
              <p>5.0 MTPA Fe · ROM ~45% Fe · Concentrado ~65% Fe</p>
            </div>
            <div>
              <p className="font-medium text-foreground">Método</p>
              <p>Disposição em pilha seca · Recuperação 85% · Disponibilidade 88%</p>
            </div>
            <div>
              <p className="font-medium text-foreground">Simulação</p>
              <p>24 meses · {setorKeys.length} setores · Seed fixa (determinístico)</p>
            </div>
          </div>
          <p className="mt-3 text-[10px] text-muted-foreground/60">
            Todos os dados são fictícios, gerados com base em benchmarks da indústria para fins de demonstração comercial.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-teal">
          <Factory className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
            Mineradora Modelo (IA)
          </h1>
          <p className="text-xs text-muted-foreground">
            SQ Solutions — Dashboard operacional de mineradora modelo 5.0 MTPA
          </p>
        </div>
      </div>
    </div>
  );
}

// KPIs where lower is better (costs, times) — delta color should be inverted
const INVERTED_DELTA = new Set([
  "Ciclo de Transporte",
  "Consumo de Diesel",
  "MTTR",
  "Custo por Tonelada",
  "Lead Time Médio",
  "Demurrage",
  "TRIFR",
  "Volume Disposto",
  "REM (Relação Estéril/Minério)",
]);

function KPICard({ kpi }: { kpi: SimKPI }) {
  const isPositive = kpi.delta >= 0;
  const inverted = INVERTED_DELTA.has(kpi.nome);
  const isGood = inverted ? !isPositive : isPositive;
  const DeltaIcon = isPositive ? ArrowUp : ArrowDown;
  const deltaColor = isGood ? "text-success" : "text-danger";

  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {kpi.nome}
        </p>
        <div className="mt-2 flex items-baseline gap-2">
          <p className="font-heading text-2xl font-bold tabular-nums">
            {fmtBR(kpi.current, kpi.unidade === "%" ? 1 : 2)}
          </p>
          <span className="text-xs text-muted-foreground">{kpi.unidade}</span>
        </div>
        <div className={`mt-1 flex items-center gap-1 text-xs ${deltaColor}`}>
          <DeltaIcon className="h-3 w-3" />
          {isPositive ? "+" : ""}{fmtBR(kpi.delta, 2)} vs. mês anterior
        </div>
        <p className="mt-1.5 text-[10px] text-muted-foreground/60">
          Meta: {fmtBR(kpi.target, 1)} | Mín: {fmtBR(kpi.min_val, 1)} | Máx: {fmtBR(kpi.max_val, 1)}
        </p>
      </CardContent>
    </Card>
  );
}

function KPIChart({ kpi }: { kpi: SimKPI }) {
  const chartData = kpi.series.data.map((d, i) => ({
    month: d.slice(0, 7), // YYYY-MM
    valor: kpi.series.valor[i],
  }));

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          {kpi.nome} ({kpi.unidade})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id={`grad-${kpi.nome}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--brand-teal)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--brand-teal)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 10 }}
              stroke="var(--muted-foreground)"
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10 }}
              stroke="var(--muted-foreground)"
              tickLine={false}
              axisLine={false}
              width={50}
            />
            <Tooltip contentStyle={CHART_TOOLTIP_STYLE} />
            <ReferenceArea
              y1={kpi.min_val}
              y2={kpi.max_val}
              fill="rgba(196,91,82,0.06)"
              stroke="rgba(196,91,82,0.2)"
              strokeDasharray="3 3"
            />
            <ReferenceLine
              y={kpi.target}
              stroke="var(--brand-orange)"
              strokeDasharray="4 4"
              label={{
                value: `Meta: ${kpi.target}`,
                position: "insideTopRight",
                fontSize: 10,
                fill: "var(--brand-orange)",
              }}
            />
            <Area
              type="monotone"
              dataKey="valor"
              stroke="var(--brand-teal)"
              strokeWidth={2}
              fill={`url(#grad-${kpi.nome})`}
              name="Realizado"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

function PageSkeleton() {
  return (
    <div className="space-y-6">
      <PageHeader />
      <Skeleton className="h-12 w-full" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="mt-2 h-8 w-20" />
              <Skeleton className="mt-1 h-3 w-40" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function KPISkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={i}>
          <CardContent className="p-4">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="mt-2 h-8 w-20" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
