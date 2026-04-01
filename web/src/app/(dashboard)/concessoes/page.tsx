"use client";

import { useEffect, useState, useCallback } from "react";
import {
  FileSearch,
  ChevronLeft,
  ChevronRight,
  Loader2,
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
  fetchExplorerDatasets,
  fetchExplorerData,
  fmtNumber,
  type ExplorerResponse,
} from "@/lib/api";

const PAGE_SIZE = 50;

export default function ConcessoesPage() {
  const [datasets, setDatasets] = useState<Record<string, string> | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [data, setData] = useState<ExplorerResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<{
    decisao?: string;
    classe?: number;
    ano_min?: number;
    ano_max?: number;
  }>({});

  // Load datasets on mount
  useEffect(() => {
    fetchExplorerDatasets()
      .then((ds) => {
        setDatasets(ds);
        // Auto-select first dataset
        const entries = Object.entries(ds);
        if (entries.length > 0) {
          setSelectedDataset(entries[0][1]);
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  const loadData = useCallback(
    (ds: string, pg: number) => {
      if (!ds) return;
      setLoading(true);
      setError(null);
      fetchExplorerData(ds, {
        limit: PAGE_SIZE,
        offset: pg * PAGE_SIZE,
        ...filters,
      })
        .then(setData)
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    },
    [filters]
  );

  // Load data when dataset or page changes
  useEffect(() => {
    if (selectedDataset) loadData(selectedDataset, page);
  }, [selectedDataset, page, loadData]);

  const columns = data?.rows?.[0] ? Object.keys(data.rows[0]) : [];
  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0;

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
          <CardContent className="p-6 text-sm text-destructive">
            Erro: {error}
          </CardContent>
        </Card>
      )}

      {/* Controls */}
      <Card>
        <CardContent className="flex flex-wrap items-end gap-4 p-4">
          {/* Dataset selector */}
          <div className="min-w-[200px] flex-1">
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Dataset
            </label>
            {datasets ? (
              <Select
                value={selectedDataset}
                onValueChange={(v) => {
                  setSelectedDataset(v);
                  setPage(0);
                }}
              >
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

          {/* Filters */}
          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Classe (1-6)
            </label>
            <Select
              value={filters.classe ? String(filters.classe) : "all"}
              onValueChange={(v) => {
                setFilters((f) => ({ ...f, classe: v === "all" ? undefined : Number(v) }));
                setPage(0);
              }}
            >
              <SelectTrigger className="w-[100px]">
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
              className="w-[100px]"
              placeholder="2010"
              min={2000}
              max={2030}
              onChange={(e) => {
                const v = e.target.value ? Number(e.target.value) : undefined;
                setFilters((f) => ({ ...f, ano_min: v }));
                setPage(0);
              }}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-muted-foreground">
              Ano máx.
            </label>
            <Input
              type="number"
              className="w-[100px]"
              placeholder="2025"
              min={2000}
              max={2030}
              onChange={(e) => {
                const v = e.target.value ? Number(e.target.value) : undefined;
                setFilters((f) => ({ ...f, ano_max: v }));
                setPage(0);
              }}
            />
          </div>

          <Button
            variant="outline"
            onClick={() => {
              setFilters({});
              setPage(0);
            }}
          >
            Limpar filtros
          </Button>
        </CardContent>
      </Card>

      {/* Data table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="flex items-center gap-2 font-heading text-base">
            <FileSearch className="h-4 w-4 text-brand-teal" />
            {selectedDataset || "—"}
            {data && (
              <Badge variant="secondary" className="ml-2 font-tabular">
                {fmtNumber(data.total)} registros
              </Badge>
            )}
          </CardTitle>
          {loading && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
        </CardHeader>
        <CardContent>
          {data && columns.length > 0 ? (
            <>
              <div className="overflow-x-auto rounded-md border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      {columns.map((col) => (
                        <th
                          key={col}
                          className="whitespace-nowrap px-3 py-2 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.rows.map((row, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                        {columns.map((col) => (
                          <td key={col} className="whitespace-nowrap px-3 py-2 font-tabular">
                            {formatCell(row[col])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="mt-4 flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  Mostrando {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, data.total)} de{" "}
                  {fmtNumber(data.total)}
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page === 0}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    <ChevronLeft className="mr-1 h-3 w-3" />
                    Anterior
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages - 1}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Próximo
                    <ChevronRight className="ml-1 h-3 w-3" />
                  </Button>
                </div>
              </div>
            </>
          ) : !loading && !error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <FileSearch className="h-10 w-10 text-muted-foreground/30" />
              <p className="mt-3 text-sm text-muted-foreground">
                Selecione um dataset para explorar
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
    </div>
  );
}

function formatCell(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return value % 1 === 0
      ? value.toLocaleString("pt-BR")
      : value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  }
  return String(value);
}
