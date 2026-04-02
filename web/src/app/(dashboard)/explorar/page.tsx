"use client";

import { Suspense, useEffect, useState, useCallback, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { type ColumnDef } from "@tanstack/react-table";
import {
  FileSearch,
  Search,
  Loader2,
  Download,
  Filter,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { DataTable, columnsFromKeys } from "@/components/data-table";
import { RecordDetail } from "@/components/record-detail";
import { FilterChips } from "@/components/filter-chips";
import {
  fetchExplorerDatasets,
  fetchExplorerData,
  explorerExportUrl,
  fmtNumber,
  type ExplorerResponse,
  type ExplorerFilters,
} from "@/lib/api";

const PAGE_SIZE = 50;

const SOURCE_ATTRIBUTION: Record<string, string> = {
  v_mg_semad: "Fonte: Secretaria de Meio Ambiente e Desenvolvimento Sustentável de Minas Gerais (SEMAD/MG)",
  v_ibama: "Fonte: Instituto Brasileiro do Meio Ambiente (IBAMA) — SISLIC",
  v_ibama_infracoes: "Fonte: Instituto Brasileiro do Meio Ambiente (IBAMA) — Autos de Infração",
  v_anm: "Fonte: Agência Nacional de Mineração (ANM) — SIGMINE",
  v_cfem: "Fonte: Agência Nacional de Mineração (ANM) — CFEM",
  v_ral: "Fonte: Agência Nacional de Mineração (ANM) — Relatório Anual de Lavra",
  v_scm: "Fonte: Agência Nacional de Mineração (ANM) — SCM Concessões",
  v_cnpj_empresas: "Fonte: Receita Federal — Cadastro CNPJ",
  v_copam_deliberacoes: "Fonte: COPAM/MG — Câmara de Atividades Minerárias",
};

// Columns to hide by default (heavy or low-value in list view)
const HIDDEN_COLUMNS = new Set([
  "texto_documentos",
  "documentos_pdf",
  "documents_str",
  "detail_id",
]);

// Per-dataset column formatting and display names
const COLUMN_CONFIG: Record<string, Record<string, { label?: string; mono?: boolean; currency?: boolean; date?: boolean; badge?: boolean; maxW?: number }>> = {
  v_mg_semad: {
    processo: { mono: true },
    decisao: { badge: true },
    data_decisao: { date: true, label: "Data Decisão" },
    cnpj_cpf: { mono: true, label: "CNPJ/CPF" },
    atividade: { maxW: 180 },
  },
  v_ibama: {
    licenca: { label: "Licença", mono: true },
    empreendimento: { maxW: 250 },
    tipo_licenca: { label: "Tipo" },
    data_emissao: { date: true, label: "Emissão" },
    data_validade: { date: true, label: "Validade" },
  },
  v_anm: {
    processo_norm: { label: "Processo", mono: true },
    FASE: { label: "Fase" },
    SUBS: { label: "Substância" },
    AREA_HA: { label: "Área (ha)" },
    UF: { label: "UF" },
  },
  v_cfem: {
    cnpj: { mono: true, label: "CNPJ" },
    substancia: { label: "Substância" },
    valor_recolhido: { currency: true, label: "Valor (R$)" },
    ano_referencia: { label: "Ano" },
    mes_referencia: { label: "Mês" },
  },
  v_ibama_infracoes: {
    data_infracao: { date: true, label: "Data" },
    municipio: { label: "Município" },
    descricao: { maxW: 300, label: "Descrição" },
    cpf_cnpj: { mono: true, label: "CPF/CNPJ" },
  },
};

export default function ExploradorPage() {
  return (
    <Suspense>
      <ExploradorContent />
    </Suspense>
  );
}

function ExploradorContent() {
  const params = useSearchParams();
  const [datasets, setDatasets] = useState<Record<string, string> | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [data, setData] = useState<ExplorerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);

  // Filters — pre-fill from URL search params (cross-page nav)
  const [search, setSearch] = useState(params.get("search") ?? "");
  const [searchInput, setSearchInput] = useState(params.get("search") ?? "");
  const [decisao, setDecisao] = useState<string>("");
  const [classe, setClasse] = useState<string>("");
  const [anoMin, setAnoMin] = useState<string>("");
  const [anoMax, setAnoMax] = useState<string>("");
  const [miningOnly, setMiningOnly] = useState(false);
  const [uf, setUf] = useState<string>("");

  // Detail panel
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);

  // Load datasets on mount — select from URL param if provided
  const urlDataset = params.get("dataset");
  useEffect(() => {
    fetchExplorerDatasets()
      .then((ds) => {
        setDatasets(ds);
        const entries = Object.entries(ds);
        // Try URL param first (e.g. ?dataset=mg_semad → v_mg_semad)
        const match = urlDataset
          ? Object.values(ds).find((v) => v === urlDataset || v === `v_${urlDataset}`)
          : null;
        if (match) {
          setSelectedDataset(match);
        } else if (entries.length > 0) {
          setSelectedDataset(entries[0][1]);
        }
      })
      .catch((e) => setError(e.message));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const filters: ExplorerFilters = useMemo(
    () => ({
      search: search || undefined,
      decisao: decisao || undefined,
      classe: classe ? Number(classe) : undefined,
      ano_min: anoMin ? Number(anoMin) : undefined,
      ano_max: anoMax ? Number(anoMax) : undefined,
      mining_only: miningOnly || undefined,
      uf: uf || undefined,
    }),
    [search, decisao, classe, anoMin, anoMax, miningOnly, uf]
  );

  const loadData = useCallback(
    (ds: string, pg: number) => {
      if (!ds) return;
      setLoading(true);
      setError(null);
      fetchExplorerData(ds, {
        ...filters,
        limit: PAGE_SIZE,
        offset: pg * PAGE_SIZE,
      })
        .then(setData)
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    },
    [filters]
  );

  useEffect(() => {
    if (selectedDataset) loadData(selectedDataset, page);
  }, [selectedDataset, page, loadData]);

  const handleDatasetChange = (ds: string) => {
    setSelectedDataset(ds);
    setPage(0);
    setSelectedRecordId(null);
    clearFilters();
  };

  const handleSearch = () => {
    setSearch(searchInput);
    setPage(0);
  };

  const clearFilters = () => {
    setSearch("");
    setSearchInput("");
    setDecisao("");
    setClasse("");
    setAnoMin("");
    setAnoMax("");
    setMiningOnly(false);
    setUf("");
    setPage(0);
  };

  const hasActiveFilters = !!(search || decisao || classe || anoMin || anoMax || miningOnly || uf);
  const isSemad = selectedDataset === "v_mg_semad";

  // Build columns from first row keys with per-dataset formatting
  const columns: ColumnDef<Record<string, unknown>, unknown>[] = useMemo(() => {
    if (!data?.rows?.[0]) return [];
    const keys = Object.keys(data.rows[0]).filter((k) => !HIDDEN_COLUMNS.has(k));
    const colConfig = COLUMN_CONFIG[selectedDataset] ?? {};

    return keys.map((key) => {
      const cfg = colConfig[key];
      return {
        accessorKey: key,
        header: cfg?.label ?? key,
        cell: ({ getValue }: { getValue: () => unknown }) => {
          const value = getValue();

          // Badge for decision columns
          if (cfg?.badge && typeof value === "string") {
            return (
              <Badge
                variant={
                  value.startsWith("Def") ? "default" : value.startsWith("Ind") ? "destructive" : "secondary"
                }
                className="text-[10px]"
              >
                {value}
              </Badge>
            );
          }

          // Currency formatting
          if (cfg?.currency && value != null) {
            return (
              <span className="font-tabular">
                {Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
              </span>
            );
          }

          // Monospace for codes/IDs
          if (cfg?.mono && value != null) {
            return <span className="font-mono text-xs">{String(value)}</span>;
          }

          // Max width with truncation
          if (cfg?.maxW && value != null) {
            return (
              <span className="block truncate" style={{ maxWidth: cfg.maxW }} title={String(value)}>
                {String(value)}
              </span>
            );
          }

          return formatCell(value);
        },
      };
    });
  }, [data, selectedDataset]);

  const handleRowClick = (row: Record<string, unknown>) => {
    if (isSemad && row.detail_id) {
      setSelectedRecordId(String(row.detail_id));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Explorador de Dados
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Consulta direta aos datasets — SEMAD, IBAMA, ANM, CFEM e mais
        </p>
      </div>

      {error && (
        <Card className="border-destructive/30">
          <CardContent className="p-4 text-sm text-destructive">
            Erro: {error}
          </CardContent>
        </Card>
      )}

      {/* Controls */}
      <Card>
        <CardContent className="space-y-4 p-4">
          {/* Row 1: Dataset + Search */}
          <div className="flex flex-wrap items-end gap-3">
            <div className="min-w-[200px] flex-1">
              <label className="mb-1 block text-xs font-medium text-muted-foreground">
                Dataset
              </label>
              {datasets ? (
                <Select value={selectedDataset} onValueChange={handleDatasetChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione um dataset" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(datasets).map(([label, view]) => (
                      <SelectItem key={view} value={view}>
                        {label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Skeleton className="h-10 w-full" />
              )}
            </div>

            <div className="flex flex-1 min-w-[200px] gap-2">
              <div className="flex-1">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Busca
                </label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    placeholder="Buscar em campos de texto..."
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
          </div>

          {/* Row 2: Dataset-specific filters */}
          {isSemad && (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:flex md:flex-wrap md:items-end">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Decisão
                </label>
                <Select value={decisao || "all"} onValueChange={(v) => { setDecisao(v === "all" ? "" : v); setPage(0); }}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas</SelectItem>
                    <SelectItem value="Deferido">Deferido</SelectItem>
                    <SelectItem value="Indeferido">Indeferido</SelectItem>
                    <SelectItem value="Arquivamento">Arquivamento</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Classe
                </label>
                <Select value={classe || "all"} onValueChange={(v) => { setClasse(v === "all" ? "" : v); setPage(0); }}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas</SelectItem>
                    {[1, 2, 3, 4, 5, 6].map((c) => (
                      <SelectItem key={c} value={String(c)}>
                        {c}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Ano mín.
                </label>
                <Input
                  type="number"
                  placeholder="2010"
                  min={2000}
                  max={2030}
                  value={anoMin}
                  onChange={(e) => { setAnoMin(e.target.value); setPage(0); }}
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Ano máx.
                </label>
                <Input
                  type="number"
                  placeholder="2025"
                  min={2000}
                  max={2030}
                  value={anoMax}
                  onChange={(e) => { setAnoMax(e.target.value); setPage(0); }}
                />
              </div>

              <div className="flex items-center gap-2 col-span-2 sm:col-span-1 md:pb-2">
                <Checkbox
                  id="mining-only"
                  checked={miningOnly}
                  onCheckedChange={(v) => { setMiningOnly(!!v); setPage(0); }}
                />
                <label htmlFor="mining-only" className="text-xs cursor-pointer">
                  Apenas mineração
                </label>
              </div>
            </div>
          )}

          {/* IBAMA-specific UF filter */}
          {(selectedDataset === "v_ibama_infracoes" || selectedDataset === "v_anm") && (
            <div className="flex items-end gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  UF
                </label>
                <Select value={uf || "all"} onValueChange={(v) => { setUf(v === "all" ? "" : v); setPage(0); }}>
                  <SelectTrigger className="w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos</SelectItem>
                    <SelectItem value="MG">MG</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          {hasActiveFilters && (
            <Button variant="ghost" size="sm" onClick={clearFilters}>
              <X className="mr-1 h-3 w-3" />
              Limpar filtros
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Active filter chips */}
      <FilterChips
        chips={[
          ...(search ? [{ label: "Busca", value: search, onRemove: () => { setSearch(""); setSearchInput(""); setPage(0); } }] : []),
          ...(decisao ? [{ label: "Decisão", value: decisao, onRemove: () => { setDecisao(""); setPage(0); } }] : []),
          ...(classe ? [{ label: "Classe", value: classe, onRemove: () => { setClasse(""); setPage(0); } }] : []),
          ...(anoMin ? [{ label: "Ano mín", value: anoMin, onRemove: () => { setAnoMin(""); setPage(0); } }] : []),
          ...(anoMax ? [{ label: "Ano máx", value: anoMax, onRemove: () => { setAnoMax(""); setPage(0); } }] : []),
          ...(miningOnly ? [{ label: "Mineração", value: "Sim", onRemove: () => { setMiningOnly(false); setPage(0); } }] : []),
          ...(uf ? [{ label: "UF", value: uf, onRemove: () => { setUf(""); setPage(0); } }] : []),
        ]}
        onClearAll={clearFilters}
      />

      {/* Data table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 font-heading text-base">
            <FileSearch className="h-4 w-4 text-brand-teal" />
            {selectedDataset || "—"}
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
              onRowClick={isSemad ? handleRowClick : undefined}
              exportUrl={explorerExportUrl(selectedDataset, filters)}
              loading={loading}
            />
          ) : !loading && !error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <FileSearch className="h-10 w-10 text-muted-foreground/30" />
              <p className="mt-3 text-sm text-muted-foreground">
                Selecione um dataset acima para explorar os dados
              </p>
              <p className="mt-1 text-xs text-muted-foreground/60">
                Mg Semad = decisões de licenciamento · IBAMA = licenças federais · ANM = concessões minerárias
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

      {/* Source attribution */}
      {selectedDataset && SOURCE_ATTRIBUTION[selectedDataset] && (
        <p className="text-[10px] text-muted-foreground/60">
          {SOURCE_ATTRIBUTION[selectedDataset]}
        </p>
      )}

      {/* Detail panel */}
      <RecordDetail
        dataset={selectedDataset}
        recordId={selectedRecordId}
        onClose={() => setSelectedRecordId(null)}
      />
    </div>
  );
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (typeof value === "number") {
    return value % 1 === 0
      ? value.toLocaleString("pt-BR")
      : value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  }
  if (typeof value === "boolean") return value ? "Sim" : "Não";
  const s = String(value);
  return s.length > 80 ? s.slice(0, 80) + "\u2026" : s;
}
