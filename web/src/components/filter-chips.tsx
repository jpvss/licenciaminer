"use client";

import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface FilterChip {
  label: string;
  value: string;
  onRemove: () => void;
}

interface FilterChipsProps {
  chips: FilterChip[];
  onClearAll?: () => void;
}

export function FilterChips({ chips, onClearAll }: FilterChipsProps) {
  if (chips.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <span className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
        Filtros:
      </span>
      {chips.map((chip) => (
        <Badge
          key={`${chip.label}-${chip.value}`}
          variant="secondary"
          className="gap-1 pr-1 text-xs font-normal"
        >
          <span className="text-muted-foreground">{chip.label}:</span> {chip.value}
          <button
            onClick={chip.onRemove}
            className="ml-0.5 rounded-sm p-0.5 hover:bg-muted"
            aria-label={`Remover filtro ${chip.label}`}
          >
            <X className="h-2.5 w-2.5" />
          </button>
        </Badge>
      ))}
      {chips.length > 1 && onClearAll && (
        <button
          onClick={onClearAll}
          className="text-[10px] text-muted-foreground underline-offset-2 hover:underline"
        >
          Limpar todos
        </button>
      )}
    </div>
  );
}
