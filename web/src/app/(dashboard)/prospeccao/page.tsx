"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import Link from "next/link";
import {
  TrendingUp,
  Search,
  Loader2,
  MapPin,
  Pickaxe,
  Target,
  BarChart3,
  Building2,
  ChevronDown,
  ChevronUp,
  Info,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { MultiSelect } from "@/components/multi-select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatCard } from "@/components/stat-card";
import {
  fetchOpportunities,
  fetchEmpresaPortfolios,
  fetchMunicipioConcentration,
  fetchConcessoesFilters,
  fetchEmpresaConcessoes,
  fetchRalTopSubstancias,
  fmtNumber,
  type ProspeccaoResponse,
  type ProspeccaoOpportunity,
  type EmpresaPortfolio,
  type MunicipioConcentration,
  type ConcessoesFilterOptions,
  type EmpresaConcessao,
} from "@/lib/api";
import { fmtBR, fmtHa, fmtReais, fmtPct } from "@/lib/format";

function ScoreBadge({ score }: { score: number }) {
  const variant = score >= 70 ? "default" : score >= 40 ? "secondary" : "outline";
  const color =
    score >= 70
      ? "bg-success text-white"
      : score >= 40
        ? "bg-warning text-white"
        : "";
  return (
    <Badge variant={variant} className={`text-[10px] font-tabular ${color}`}>
      {score}
    </Badge>
  );
}

export default function ProspeccaoPage() {
  const [filterOptions, setFilterOptions] = useState<ConcessoesFilterOptions | null>(null);

  // Opportunities tab
  const [oppData, setOppData] = useState<ProspeccaoResponse | null>(null);
  const [oppLoading, setOppLoading] = useState(false);
  const [oppPage, setOppPage] = useState(0);
  const [minScore, setMinScore] = useState(30);
  const [regime, setRegime] = useState<string[]>([]);
  const [categoria, setCategoria] = useState<string[]>([]);
  const [estrategicoOnly, setEstrategicoOnly] = useState(false);

  // Empresas tab
  const [empresas, setEmpresas] = useState<EmpresaPortfolio[] | null>(null);
  const [empresasLoading, setEmpresasLoading] = useState(false);
  const [expandedEmpresa, setExpandedEmpresa] = useState<string | null>(null);
  const [empresaConcessoes, setEmpresaConcessoes] = useState<EmpresaConcessao[]>([]);
  const [empConcessoesLoading, setEmpConcessoesLoading] = useState(false);

  // Municipios tab
  const [municipios, setMunicipios] = useState<MunicipioConcentration[] | null>(null);
  const [municipiosLoading, setMunicipiosLoading] = useState(false);

  // RAL context
  const [ralSubstancias, setRalSubstancias] = useState<{ substancia: string; n: number }[] | null>(null);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchConcessoesFilters().then(setFilterOptions).catch((e) => { console.error("filters:", e); });
    fetchRalTopSubstancias().then((res) => setRalSubstancias(res.rows)).catch((e) => { console.error("ral:", e); });
  }, []);

  // Load empresa concessões when expanded
  useEffect(() => {
    if (!expandedEmpresa) { setEmpresaConcessoes([]); return; }
    setEmpConcessoesLoading(true);
    fetchEmpresaConcessoes(expandedEmpresa)
      .then((res) => setEmpresaConcessoes(res.rows))
      .catch(() => setEmpresaConcessoes([]))
      .finally(() => setEmpConcessoesLoading(false));
  }, [expandedEmpresa]);

  const loadOpportunities = useCallback(
    (pg: number) => {
      setOppLoading(true);
      setError(null);
      fetchOpportunities({
        min_score: minScore,
        regime: regime.length > 0 ? regime : undefined,
        categoria: categoria.length > 0 ? categoria : undefined,
        estrategico: estrategicoOnly || undefined,
        limit: 200,
        offset: pg * 200,
      })
        .then(setOppData)
        .catch((e) => setError(e.message))
        .finally(() => setOppLoading(false));
    },
    [minScore, regime, categoria, estrategicoOnly]
  );

  useEffect(() => {
    loadOpportunities(oppPage);
  }, [oppPage, loadOpportunities]);

  const loadEmpresas = () => {
    if (empresas) return;
    setEmpresasLoading(true);
    fetchEmpresaPortfolios()
      .then((res) => setEmpresas(res.rows))
      .catch((e) => { console.error("empresas:", e); })
      .finally(() => setEmpresasLoading(false));
  };

  const loadMunicipios = () => {
    if (municipios) return;
    setMunicipiosLoading(true);
    fetchMunicipioConcentration()
      .then((res) => setMunicipios(res.rows))
      .catch((e) => { console.error("municipios:", e); })
      .finally(() => setMunicipiosLoading(false));
  };

  const regimeLabels = filterOptions?.regime_labels ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Prospecção
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Identificação de oportunidades em concessões minerárias — ranking por score de potencial
        </p>
      </div>

      {error && (
        <Card className="border-destructive/30">
          <CardContent className="p-4 text-sm text-destructive">
            Erro: {error}
          </CardContent>
        </Card>
      )}

      {/* KPIs */}
      {oppData?.stats ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Oportunidades"
            value={fmtBR(oppData.stats.total)}
            subtitle={`score ≥ ${minScore}`}
            icon={Target}
          />
          <StatCard
            label="Score Médio"
            value={String(oppData.stats.avg_score)}
            icon={TrendingUp}
            accentClass="bg-brand-teal"
          />
          <StatCard
            label="Minerais Estratégicos"
            value={fmtBR(oppData.stats.strategic_count)}
            icon={Pickaxe}
            accentClass="bg-brand-gold"
          />
          <StatCard
            label="Área Total"
            value={fmtHa(oppData.stats.total_area)}
            icon={MapPin}
            accentClass="bg-brand-orange"
          />
        </div>
      ) : !error ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-5">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}

      <Tabs
        defaultValue="opportunities"
        className="space-y-4"
        onValueChange={(v) => {
          if (v === "empresas") loadEmpresas();
          if (v === "municipios") loadMunicipios();
        }}
      >
        <TabsList>
          <TabsTrigger value="opportunities">Top Oportunidades</TabsTrigger>
          <TabsTrigger value="empresas">Por Empresa</TabsTrigger>
          <TabsTrigger value="municipios">Por Município</TabsTrigger>
        </TabsList>

        {/* Tab 1: Opportunities */}
        <TabsContent value="opportunities">
          {/* Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 items-end">
                <div>
                  <label className="mb-1 block text-xs font-medium text-muted-foreground">
                    Score mínimo
                  </label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={minScore}
                      min={0}
                      max={100}
                      onChange={(e) => { setMinScore(Number(e.target.value)); setOppPage(0); }}
                    />
                    <button type="button" className="group relative" aria-label="Detalhes do score">
                      <Info className="h-3.5 w-3.5 text-muted-foreground/50 cursor-help" />
                      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block group-focus:block w-56 rounded-md border bg-popover p-2.5 text-[10px] leading-relaxed text-popover-foreground shadow-md z-50">
                        <strong className="block mb-1">Composição do Score (0-100):</strong>
                        CFEM inativa: 30 pts<br />
                        Mineral estratégico: 25 pts<br />
                        Área (ha): 8-15 pts<br />
                        Sem receita CFEM: 15 pts<br />
                        Categoria alta: 8-15 pts
                      </span>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-muted-foreground">
                    Regime
                  </label>
                  <MultiSelect
                    options={filterOptions?.regimes ?? []}
                    selected={regime}
                    onChange={(v) => { setRegime(v); setOppPage(0); }}
                    placeholder="Todos"
                    labels={regimeLabels}
                  />
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-muted-foreground">
                    Categoria
                  </label>
                  <MultiSelect
                    options={filterOptions?.categorias ?? []}
                    selected={categoria}
                    onChange={(v) => { setCategoria(v); setOppPage(0); }}
                    placeholder="Todas"
                  />
                </div>

                <div className="flex items-center gap-2 pb-2">
                  <Checkbox
                    id="estrategico"
                    checked={estrategicoOnly}
                    onCheckedChange={(v) => { setEstrategicoOnly(!!v); setOppPage(0); }}
                  />
                  <label htmlFor="estrategico" className="text-xs cursor-pointer">
                    Apenas estratégicos
                  </label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Opportunities table */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="flex items-center gap-2 font-heading text-base">
                <Target className="h-4 w-4 text-brand-orange" />
                Ranking de Oportunidades
                {oppData && (
                  <Badge variant="secondary" className="ml-2 tabular-nums">
                    {fmtNumber(oppData.total)}
                  </Badge>
                )}
              </CardTitle>
              {oppLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            </CardHeader>
            <CardContent>
              {oppData && oppData.rows.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-muted/50">
                        <TableHead className="text-xs">Score</TableHead>
                        <TableHead className="text-xs">Processo</TableHead>
                        <TableHead className="text-xs">Titular</TableHead>
                        <TableHead className="text-xs">Substância</TableHead>
                        <TableHead className="text-xs">Categoria</TableHead>
                        <TableHead className="text-xs">Regime</TableHead>
                        <TableHead className="text-xs text-right">Área</TableHead>
                        <TableHead className="text-xs">Motivo</TableHead>
                        <TableHead className="text-xs w-8"></TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {oppData.rows.map((opp, i) => (
                        <TableRow key={i}>
                          <TableCell>
                            <ScoreBadge score={opp.score} />
                          </TableCell>
                          <TableCell className="font-mono text-xs">
                            <Link
                              href={`/concessoes?search=${encodeURIComponent(opp.processo_norm)}`}
                              className="text-brand-teal hover:underline"
                              title="Ver no Concessões"
                            >
                              {opp.processo_norm}
                            </Link>
                          </TableCell>
                          <TableCell className="text-xs max-w-[200px] truncate" title={opp.titular}>
                            {opp.titular}
                          </TableCell>
                          <TableCell className="text-xs">
                            {opp.substancia_principal}
                          </TableCell>
                          <TableCell className="text-xs">
                            {opp.categoria}
                          </TableCell>
                          <TableCell className="text-xs">
                            {regimeLabels[opp.regime] ?? opp.regime}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {opp.AREA_HA != null ? fmtHa(opp.AREA_HA) : "—"}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground max-w-[200px] truncate" title={opp.motivo}>
                            {opp.motivo}
                          </TableCell>
                          <TableCell>
                            <Link
                              href={`/mapa?search=${encodeURIComponent(opp.processo_norm)}`}
                              className="text-muted-foreground hover:text-brand-teal"
                              title="Ver no Mapa"
                            >
                              <MapPin className="h-3.5 w-3.5" />
                            </Link>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : !oppLoading ? (
                <div className="flex flex-col items-center justify-center py-16">
                  <Target className="h-10 w-10 text-muted-foreground/30" />
                  <p className="mt-3 text-sm text-muted-foreground">
                    Nenhuma oportunidade encontrada com score ≥ {minScore}
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <Skeleton key={i} className="h-8 w-full" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Score methodology */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-sm font-heading">
                <Info className="h-4 w-4 text-muted-foreground" />
                Metodologia do Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="rounded-lg border p-2">
                  <p className="font-medium">Inativo (sem CFEM)</p>
                  <p className="text-muted-foreground">+30 pts</p>
                </div>
                <div className="rounded-lg border p-2">
                  <p className="font-medium">Mineral estratégico</p>
                  <p className="text-muted-foreground">+25 pts</p>
                </div>
                <div className="rounded-lg border p-2">
                  <p className="font-medium">Alto valor (preciosos/estr.)</p>
                  <p className="text-muted-foreground">+15 pts</p>
                </div>
                <div className="rounded-lg border p-2">
                  <p className="font-medium">Área {">"} 500 ha</p>
                  <p className="text-muted-foreground">+15 pts</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Empresas */}
        <TabsContent value="empresas">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="flex items-center gap-2 font-heading text-base">
                <Building2 className="h-4 w-4 text-brand-teal" />
                Portfólio por Empresa
                {empresas && (
                  <Badge variant="secondary" className="ml-2 tabular-nums">
                    {empresas.length} empresas
                  </Badge>
                )}
              </CardTitle>
              {empresasLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            </CardHeader>
            <CardContent>
              {empresas ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-muted/50">
                        <TableHead className="text-xs">Titular</TableHead>
                        <TableHead className="text-xs text-right">Concessões</TableHead>
                        <TableHead className="text-xs text-right">Substâncias</TableHead>
                        <TableHead className="text-xs text-right">CFEM Ativas</TableHead>
                        <TableHead className="text-xs text-right">Inativas</TableHead>
                        <TableHead className="text-xs text-right">CFEM Total</TableHead>
                        <TableHead className="text-xs text-right">Área Total</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {empresas.map((emp, i) => (
                        <>
                        <TableRow key={i} className="cursor-pointer hover:bg-muted/50" onClick={() => setExpandedEmpresa(expandedEmpresa === emp.titular ? null : emp.titular)}>
                          <TableCell className="text-xs max-w-[250px] truncate font-medium" title={emp.titular}>
                            {expandedEmpresa === emp.titular ? (
                              <ChevronUp className="inline mr-1 h-3 w-3" />
                            ) : (
                              <ChevronDown className="inline mr-1 h-3 w-3" />
                            )}
                            {emp.titular}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtBR(emp.total_concessoes)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {emp.substancias_distintas}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtBR(emp.ativas_cfem)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            <span className={emp.inativas > 0 ? "text-danger font-medium" : ""}>
                              {fmtBR(emp.inativas)}
                            </span>
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtReais(emp.cfem_total)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtHa(emp.area_total)}
                          </TableCell>
                        </TableRow>
                        {expandedEmpresa === emp.titular && (
                          <TableRow key={`${i}-detail`}>
                            <TableCell colSpan={7} className="bg-muted/30 p-0">
                              {empConcessoesLoading ? (
                                <div className="flex items-center gap-2 p-4 text-xs text-muted-foreground">
                                  <Loader2 className="h-3 w-3 animate-spin" /> Carregando concessões...
                                </div>
                              ) : empresaConcessoes.length > 0 ? (
                                <div className="overflow-x-auto">
                                  <Table>
                                    <TableHeader>
                                      <TableRow className="text-[10px]">
                                        <TableHead>Processo</TableHead>
                                        <TableHead>Regime</TableHead>
                                        <TableHead>Substância</TableHead>
                                        <TableHead>Município</TableHead>
                                        <TableHead className="text-right">Área</TableHead>
                                        <TableHead className="text-right">CFEM</TableHead>
                                        <TableHead>Status</TableHead>
                                      </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                      {empresaConcessoes.map((c, j) => (
                                        <TableRow key={j} className="text-[11px]">
                                          <TableCell className="font-mono">
                                            <Link
                                              href={`/concessoes?search=${encodeURIComponent(c.processo_norm)}`}
                                              className="text-brand-teal hover:underline"
                                            >
                                              {c.processo_norm}
                                            </Link>
                                          </TableCell>
                                          <TableCell>{c.regime}</TableCell>
                                          <TableCell>{c.substancia_principal}</TableCell>
                                          <TableCell>{c.municipio_principal}</TableCell>
                                          <TableCell className="text-right tabular-nums">
                                            {c.AREA_HA != null ? fmtHa(c.AREA_HA) : "—"}
                                          </TableCell>
                                          <TableCell className="text-right tabular-nums">
                                            {c.cfem_total != null ? fmtReais(c.cfem_total) : "—"}
                                          </TableCell>
                                          <TableCell>
                                            <Badge variant={c.ativo_cfem ? "default" : "secondary"} className={`text-[9px] ${c.ativo_cfem ? "bg-success" : ""}`}>
                                              {c.ativo_cfem ? "Ativa" : "Inativa"}
                                            </Badge>
                                          </TableCell>
                                        </TableRow>
                                      ))}
                                    </TableBody>
                                  </Table>
                                </div>
                              ) : (
                                <p className="p-4 text-xs text-muted-foreground">Nenhuma concessão encontrada</p>
                              )}
                            </TableCell>
                          </TableRow>
                        )}
                        </>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : empresasLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <Skeleton key={i} className="h-8 w-full" />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16">
                  <Building2 className="h-10 w-10 text-muted-foreground/30" />
                  <p className="mt-3 text-sm text-muted-foreground">
                    Selecione esta aba para carregar dados
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Municipios */}
        <TabsContent value="municipios">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="flex items-center gap-2 font-heading text-base">
                <MapPin className="h-4 w-4 text-brand-orange" />
                Concentração por Município
                {municipios && (
                  <Badge variant="secondary" className="ml-2 tabular-nums">
                    {municipios.length} registros
                  </Badge>
                )}
              </CardTitle>
              {municipiosLoading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            </CardHeader>
            <CardContent>
              {municipios ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-muted/50">
                        <TableHead className="text-xs">Município</TableHead>
                        <TableHead className="text-xs">Substância</TableHead>
                        <TableHead className="text-xs text-right">Concessões</TableHead>
                        <TableHead className="text-xs text-right">Ativas</TableHead>
                        <TableHead className="text-xs text-right">Área Total</TableHead>
                        <TableHead className="text-xs text-right">CFEM Total</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {municipios.slice(0, 100).map((m, i) => (
                        <TableRow key={i}>
                          <TableCell className="text-xs font-medium">
                            {m.municipio}
                          </TableCell>
                          <TableCell className="text-xs">
                            {m.substancia}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtBR(m.concessoes)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtBR(m.ativas)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtHa(m.area_total)}
                          </TableCell>
                          <TableCell className="text-xs text-right tabular-nums">
                            {fmtReais(m.cfem_total)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : municipiosLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <Skeleton key={i} className="h-8 w-full" />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-16">
                  <MapPin className="h-10 w-10 text-muted-foreground/30" />
                  <p className="mt-3 text-sm text-muted-foreground">
                    Selecione esta aba para carregar dados
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* RAL Context Section */}
      {ralSubstancias && ralSubstancias.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-heading">
              <BarChart3 className="h-4 w-4 text-brand-teal" />
              Contexto de Produção Mineral — MG (RAL)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-3 text-xs text-muted-foreground">
              Principais substâncias por registros no Relatório Anual de Lavra (ANM/RAL)
            </p>
            <div className="flex flex-wrap gap-2">
              {ralSubstancias.map((s) => (
                <Badge key={s.substancia} variant="outline" className="text-xs font-normal">
                  {s.substancia} <span className="ml-1 text-muted-foreground tabular-nums">({fmtNumber(s.n)})</span>
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
