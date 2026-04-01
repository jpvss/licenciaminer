"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import {
  FileSearch,
  Search,
  Loader2,
  MapPin,
  Coins,
  X,
  Pickaxe,
  Building2,
  ExternalLink,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { DataTable, columnsFromKeys } from "@/components/data-table";
import { StatCard } from "@/components/stat-card";
import {
  fetchConcessoes,
  fetchConcessoesStats,
  fetchConcessoesFilters,
  fetchConcessaoDetail,
  type ConcessoesFilters,
  type ConcessoesStats,
  type ConcessoesFilterOptions,
  type ConcessoesResponse,
  fmtNumber,
} from "@/lib/api";
import { fmtBR, fmtHa, fmtReais } from "@/lib/format";
import type { ColumnDef } from "@tanstack/react-table";

const PAGE_SIZE = 100;

const HIDDEN_COLUMNS = new Set([
  "texto_documentos",
  "documentos_pdf",
  "documents_str",
  "processo_norm",
]);

export default function ConcessoesPage() {
  const [filterOptions, setFilterOptions] = useState<ConcessoesFilterOptions | null>(null);
  const [stats, setStats] = useState<ConcessoesStats | null>(null);
  const [data, setData] = useState<ConcessoesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  // Filters
  const [search, setSearch] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [regime, setRegime] = useState("");
  const [categoria, setCategoria] = useState("");
  const [cfemStatus, setCfemStatus] = useState("");

  // Detail
  const [selectedProcesso, setSelectedProcesso] = useState<string | null>(null);
  const [detailRecord, setDetailRecord] = useState<Record<string, unknown> | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    fetchConcessoesFilters()
      .then(setFilterOptions)
      .catch((e) => setError(e.message));
  }, []);

  const filters: ConcessoesFilters = useMemo(
    () => ({
      search: search || undefined,
      regime: regime ? [regime] : undefined,
      categoria: categoria ? [categoria] : undefined,
      cfem_status: (cfemStatus || undefined) as ConcessoesFilters["cfem_status"],
    }),
    [search, regime, categoria, cfemStatus]
  );

  const loadData = useCallback(
    (pg: number) => {
      setLoading(true);
      setError(null);

      const params: ConcessoesFilters = {
        ...filters,
        limit: PAGE_SIZE,
        offset: pg * PAGE_SIZE,
      };

      Promise.all([
        fetchConcessoes(params),
        fetchConcessoesStats(filters),
      ])
        .then(([concessoesData, statsData]) => {
          setData(concessoesData);
          setStats(statsData);
        })
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    },
    [filters]
  );

  useEffect(() => {
    loadData(page);
  }, [page, loadData]);

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(0);
  };

  const clearFilters = () => {
    setSearch("");
    setSearchInput("");
    setRegime("");
    setCategoria("");
    setCfemStatus("");
    setPage(0);
  };

  const hasActiveFilters = !!(search || regime || categoria || cfemStatus);

  // Detail panel
  useEffect(() => {
    if (!selectedProcesso) {
      setDetailRecord(null);
      return;
    }
    setDetailLoading(true);
    fetchConcessaoDetail(selectedProcesso)
      .then(setDetailRecord)
      .catch(() => setDetailRecord(null))
      .finally(() => setDetailLoading(false));
  }, [selectedProcesso]);

  // Build columns
  const columns: ColumnDef<Record<string, unknown>, unknown>[] = useMemo(() => {
    if (!data?.rows?.[0]) return [];
    const keys = Object.keys(data.rows[0]).filter((k) => !HIDDEN_COLUMNS.has(k));

    return keys.map((key) => ({
      accessorKey: key,
      header: key,
      cell: ({ getValue }: { getValue: () => unknown }) => {
        const value = getValue();
        if (key === "ativo_cfem") {
          return (
            <Badge variant={value === true ? "default" : "secondary"} className="text-[10px]">
              {value === true ? "Ativo" : "Inativo"}
            </Badge>
          );
        }
        if (key === "cfem_total" && typeof value === "number") {
          return fmtReais(value);
        }
        if (key === "AREA_HA" && typeof value === "number") {
          return fmtHa(value);
        }
        return formatCell(value);
      },
    }));
  }, [data]);

  const handleRowClick = (row: Record<string, unknown>) => {
    const processo = row.processo_norm ?? row.processo;
    if (processo) setSelectedProcesso(String(processo));
  };

  const regimeLabels = data?.regime_labels ?? filterOptions?.regime_labels ?? {};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Base de Concessões
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Concessões minerárias ANM — decretos de lavra, licenciamentos e garimpeira
        </p>
      </div>

      {error && (
        <Card className="border-destructive/30">
          <CardContent className="p-4 text-sm text-destructive">
            Erro: {error}
          </CardContent>
        </Card>
      )}

      {/* KPI cards */}
      {stats ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Total Concessões"
            value={fmtBR(stats.total)}
            icon={FileSearch}
          />
          <StatCard
            label="CFEM Ativas"
            value={stats.cfem_ativas != null ? fmtBR(stats.cfem_ativas) : "—"}
            icon={Coins}
            accentClass="bg-success"
          />
          <StatCard
            label="Substâncias"
            value={fmtBR(stats.substancias)}
            icon={Pickaxe}
            accentClass="bg-brand-teal"
          />
          <StatCard
            label="Municípios"
            value={fmtBR(stats.municipios)}
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

      {/* Filters */}
      <Card>
        <CardContent className="space-y-4 p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex flex-1 min-w-[200px] gap-2">
              <div className="flex-1">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Busca
                </label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    placeholder="Processo, titular, substância..."
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  />
                </div>
              </div>
              <div className="flex items-end">
                <Button onClick={handleSearch} size="default">
                  <Search className="mr-1.5 h-3.5 w-3.5" />
                  Buscar
                </Button>
              </div>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Regime
              </label>
              <Select value={regime || "all"} onValueChange={(v) => { setRegime(v === "all" ? "" : v); setPage(0); }}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  {(filterOptions?.regimes ?? []).map((r) => (
                    <SelectItem key={r} value={r}>
                      {regimeLabels[r] ?? r}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Categoria
              </label>
              <Select value={categoria || "all"} onValueChange={(v) => { setCategoria(v === "all" ? "" : v); setPage(0); }}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  {(filterOptions?.categorias ?? []).map((c) => (
                    <SelectItem key={c} value={c}>
                      {c}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                CFEM
              </label>
              <Select value={cfemStatus || "all"} onValueChange={(v) => { setCfemStatus(v === "all" ? "" : v); setPage(0); }}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="ativo">Ativo</SelectItem>
                  <SelectItem value="inativo">Inativo</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters} className="mb-0.5">
                <X className="mr-1 h-3 w-3" />
                Limpar
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Data table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 font-heading text-base">
            <FileSearch className="h-4 w-4 text-brand-teal" />
            Concessões
            {data && (
              <Badge variant="secondary" className="ml-2 tabular-nums">
                {fmtNumber(data.total)} registros
              </Badge>
            )}
          </CardTitle>
          {loading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
        </CardHeader>
        <CardContent>
          {data && columns.length > 0 ? (
            <DataTable
              columns={columns}
              data={data.rows}
              total={data.total}
              pageSize={PAGE_SIZE}
              page={page}
              onPageChange={setPage}
              onRowClick={handleRowClick}
              loading={loading}
            />
          ) : !loading && !error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <FileSearch className="h-10 w-10 text-muted-foreground/30" />
              <p className="mt-3 text-sm text-muted-foreground">
                Nenhuma concessão encontrada
              </p>
            </div>
          ) : !error ? (
            <div className="space-y-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-8 w-full" />
              ))}
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Detail panel */}
      <Sheet open={selectedProcesso !== null} onOpenChange={(v) => !v && setSelectedProcesso(null)}>
        <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
          <SheetHeader>
            <SheetTitle className="font-heading text-base">
              Detalhe da Concessão
            </SheetTitle>
          </SheetHeader>

          {detailLoading && (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          )}

          {detailRecord && !detailLoading && (
            <div className="space-y-4 py-4">
              <div>
                <h3 className="font-medium text-sm">
                  {str(detailRecord.titular)}
                </h3>
                <p className="mt-0.5 text-xs font-mono text-muted-foreground">
                  {str(detailRecord.processo_norm ?? detailRecord.processo)}
                </p>
                {detailRecord.regime != null && (
                  <Badge variant="secondary" className="mt-1">
                    {regimeLabels[str(detailRecord.regime)] ?? str(detailRecord.regime)}
                  </Badge>
                )}
              </div>

              <Separator />

              <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
                <Field label="Substância" value={str(detailRecord.substancia_principal)} />
                <Field label="Categoria" value={str(detailRecord.categoria)} />
                <Field label="Município" value={str(detailRecord.municipio_principal)} />
                <Field label="CNPJ" value={str(detailRecord.cpf_cnpj_do_titular)} mono />
                <Field label="Área" value={detailRecord.AREA_HA != null ? fmtHa(Number(detailRecord.AREA_HA)) : "—"} />
                <Field label="CFEM Total" value={detailRecord.cfem_total != null ? fmtReais(Number(detailRecord.cfem_total)) : "—"} />
                <Field label="CFEM Status" value={detailRecord.ativo_cfem === true ? "Ativo" : "Inativo"} />
                <Field label="Estratégico" value={detailRecord.estrategico === "sim" ? "Sim" : "Não"} />
              </dl>

              {detailRecord.scm_url != null && (
                <>
                  <Separator />
                  <Button variant="outline" size="sm" className="w-full" asChild>
                    <a href={String(detailRecord.scm_url)} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="mr-2 h-3.5 w-3.5" />
                      Pesquisar no SCM/ANM
                    </a>
                  </Button>
                </>
              )}
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  if (!value || value === "—") return null;
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={mono ? "font-mono text-xs" : "text-sm"}>{value}</dd>
    </div>
  );
}

function str(v: unknown): string {
  if (v === null || v === undefined) return "—";
  return String(v);
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return value % 1 === 0
      ? value.toLocaleString("pt-BR")
      : value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  }
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  const s = String(value);
  return s.length > 80 ? s.slice(0, 80) + "…" : s;
}
