"use client";

import { useState } from "react";
import {
  type ColumnDef,
  type SortingState,
  type VisibilityState,
  type ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Columns3,
  Download,
} from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { fmtBR } from "@/lib/format";

interface DataTableProps<TData> {
  columns: ColumnDef<TData, unknown>[];
  data: TData[];
  total: number;
  pageSize: number;
  page: number;
  onPageChange: (page: number) => void;
  onRowClick?: (row: TData) => void;
  exportUrl?: string;
  loading?: boolean;
}

export function DataTable<TData>({
  columns,
  data,
  total,
  pageSize,
  page,
  onPageChange,
  onRowClick,
  exportUrl,
  loading,
}: DataTableProps<TData>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    onColumnVisibilityChange: setColumnVisibility,
    onColumnFiltersChange: setColumnFilters,
    state: { sorting, columnVisibility, columnFilters },
    manualPagination: true,
    pageCount: Math.ceil(total / pageSize),
  });

  const totalPages = Math.ceil(total / pageSize);
  const start = page * pageSize + 1;
  const end = Math.min((page + 1) * pageSize, total);

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-muted-foreground tabular-nums">
          {total > 0
            ? `${fmtBR(start)}–${fmtBR(end)} de ${fmtBR(total)}`
            : "Nenhum resultado"}
        </p>
        <div className="flex items-center gap-2">
          {exportUrl && total > 0 && total <= 20000 && (
            <Button variant="outline" size="sm" asChild>
              <a href={exportUrl} download>
                <Download className="mr-1.5 h-3 w-3" />
                CSV
              </a>
            </Button>
          )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Columns3 className="mr-1.5 h-3 w-3" />
                Colunas
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="max-h-72 overflow-y-auto">
              {table.getAllColumns().filter((c) => c.getCanHide()).map((column) => (
                <DropdownMenuCheckboxItem
                  key={column.id}
                  checked={column.getIsVisible()}
                  onCheckedChange={(v) => column.toggleVisibility(!!v)}
                  className="text-xs capitalize"
                >
                  {column.id}
                </DropdownMenuCheckboxItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Table — contained scroll */}
      <div className="rounded-md border overflow-x-auto max-h-[520px] overflow-y-auto">
        <Table className="min-w-[800px]">
          <TableHeader className="sticky top-0 z-10">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="bg-muted/80 backdrop-blur-sm">
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className="text-xs font-medium uppercase tracking-wide text-muted-foreground whitespace-nowrap"
                  >
                    {header.isPlaceholder ? null : (
                      <button
                        type="button"
                        className="flex items-center gap-1 hover:text-foreground transition-colors"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                          <ArrowUpDown className="h-3 w-3 opacity-40" />
                        )}
                      </button>
                    )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  className={onRowClick ? "cursor-pointer hover:bg-muted/50" : undefined}
                  onClick={() => onRowClick?.(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="tabular-nums whitespace-nowrap max-w-[300px] truncate">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center text-muted-foreground">
                  {loading ? "Carregando..." : "Nenhum resultado encontrado"}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 0}
            onClick={() => onPageChange(page - 1)}
          >
            <ChevronLeft className="mr-1 h-3 w-3" />
            Anterior
          </Button>
          <span className="text-xs text-muted-foreground tabular-nums">
            {page + 1} / {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages - 1}
            onClick={() => onPageChange(page + 1)}
          >
            Pr\u00f3ximo
            <ChevronRight className="ml-1 h-3 w-3" />
          </Button>
        </div>
      )}
    </div>
  );
}

/** Helper: builds ColumnDef[] from first row keys (for dynamic datasets). */
export function columnsFromKeys(
  keys: string[],
  formatCell: (value: unknown) => string = defaultFormat
): ColumnDef<Record<string, unknown>, unknown>[] {
  return keys.map((key) => ({
    accessorKey: key,
    header: key,
    cell: ({ getValue }) => formatCell(getValue()),
  }));
}

function defaultFormat(value: unknown): string {
  if (value === null || value === undefined) return "\u2014";
  if (typeof value === "number") {
    return value % 1 === 0
      ? value.toLocaleString("pt-BR")
      : value.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
  }
  if (typeof value === "boolean") return value ? "Sim" : "N\u00e3o";
  const s = String(value);
  return s.length > 100 ? s.slice(0, 100) + "\u2026" : s;
}
