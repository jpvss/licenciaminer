"use client";

import { useState, useMemo } from "react";
import { Check, ChevronsUpDown, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { cn } from "@/lib/utils";

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  labels?: Record<string, string>;
  maxDisplay?: number;
  className?: string;
}

export function MultiSelect({
  options,
  selected,
  onChange,
  placeholder = "Selecionar...",
  labels,
  maxDisplay = 2,
  className,
}: MultiSelectProps) {
  const [open, setOpen] = useState(false);

  const displayLabel = (value: string) => labels?.[value] ?? value;

  const allSelected = selected.length === options.length && options.length > 0;

  const toggleAll = () => {
    onChange(allSelected ? [] : [...options]);
  };

  const toggle = (value: string) => {
    onChange(
      selected.includes(value)
        ? selected.filter((s) => s !== value)
        : [...selected, value]
    );
  };

  const summary = useMemo(() => {
    if (selected.length === 0) return placeholder;
    if (allSelected) return "Todas";
    if (selected.length <= maxDisplay) {
      return selected.map(displayLabel).join(", ");
    }
    return `${selected.length} selecionados`;
  }, [selected, options.length, placeholder, maxDisplay, allSelected]);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "h-9 w-full justify-between font-normal text-left",
            selected.length === 0 && "text-muted-foreground",
            className
          )}
        >
          <span className="truncate">{summary}</span>
          <ChevronsUpDown className="ml-2 h-3.5 w-3.5 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0" align="start">
        <Command>
          <CommandInput placeholder="Buscar..." />
          <CommandList>
            <CommandEmpty>Nenhum resultado.</CommandEmpty>
            <CommandGroup>
              <CommandItem onSelect={toggleAll} className="font-medium">
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    allSelected ? "opacity-100" : "opacity-0"
                  )}
                />
                Todas
              </CommandItem>
              {options.map((option) => (
                <CommandItem key={option} value={option} onSelect={() => toggle(option)}>
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      selected.includes(option) ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {displayLabel(option)}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

export function MultiSelectChips({
  selected,
  onChange,
  labels,
}: {
  selected: string[];
  onChange: (selected: string[]) => void;
  labels?: Record<string, string>;
}) {
  if (selected.length === 0) return null;
  return (
    <div className="flex flex-wrap gap-1">
      {selected.map((value) => (
        <Badge key={value} variant="secondary" className="gap-1 pr-1 text-[10px]">
          {labels?.[value] ?? value}
          <button
            onClick={() => onChange(selected.filter((s) => s !== value))}
            className="ml-0.5 rounded-sm hover:bg-muted"
          >
            <X className="h-3 w-3" />
          </button>
        </Badge>
      ))}
    </div>
  );
}
