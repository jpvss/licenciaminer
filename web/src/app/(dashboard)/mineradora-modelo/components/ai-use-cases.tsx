"use client";

import { useState } from "react";
import {
  Eye,
  TrendingUp,
  Zap,
  MessageSquare,
  Bot,
  Box,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AIUseCase, AICategory } from "../lib/types";
import { AI_CATEGORY_LABELS } from "../lib/types";

const CATEGORY_ICONS: Record<AICategory, typeof Eye> = {
  "computer-vision": Eye,
  predictive: TrendingUp,
  optimization: Zap,
  nlp: MessageSquare,
  automation: Bot,
  "digital-twin": Box,
};

const COMPLEXITY_DOTS: Record<string, number> = {
  baixa: 1,
  media: 2,
  alta: 3,
};

interface AIUseCasesProps {
  casos: AIUseCase[];
}

export function AIUseCases({ casos }: AIUseCasesProps) {
  const [filter, setFilter] = useState<AICategory | "all">("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const categories = Array.from(new Set(casos.map((c) => c.categoria)));
  const filtered = filter === "all" ? casos : casos.filter((c) => c.categoria === filter);

  return (
    <div className="space-y-4">
      {/* Filter chips */}
      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => setFilter("all")}
          className={`rounded-full px-3 py-1 text-[11px] font-medium transition-colors ${
            filter === "all"
              ? "bg-foreground text-background"
              : "bg-muted text-muted-foreground hover:bg-muted/80"
          }`}
        >
          Todos ({casos.length})
        </button>
        {categories.map((cat) => {
          const Icon = CATEGORY_ICONS[cat];
          const count = casos.filter((c) => c.categoria === cat).length;
          return (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`flex items-center gap-1 rounded-full px-3 py-1 text-[11px] font-medium transition-colors ${
                filter === cat
                  ? "bg-foreground text-background"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              <Icon className="h-3 w-3" />
              {AI_CATEGORY_LABELS[cat]} ({count})
            </button>
          );
        })}
      </div>

      {/* Cards grid */}
      <div className="grid gap-4 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
        {filtered.map((caso) => {
          const CatIcon = CATEGORY_ICONS[caso.categoria];
          const isExpanded = expandedId === caso.id;
          const dots = COMPLEXITY_DOTS[caso.complexidade] ?? 2;

          return (
            <Card key={caso.id} className="relative overflow-hidden">
              <div className="absolute top-0 right-0 flex items-center gap-1 rounded-bl-lg bg-muted px-2 py-1">
                <CatIcon className="h-3 w-3 text-muted-foreground" />
                <span className="text-[10px] text-muted-foreground">
                  {AI_CATEGORY_LABELS[caso.categoria]}
                </span>
              </div>
              <CardContent className="space-y-3 p-4 pt-6">
                <h4 className="font-heading text-sm font-semibold pr-20">
                  {caso.titulo}
                </h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {caso.descricao}
                </p>

                {/* Metrics row */}
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline" className="text-[10px] font-semibold text-success border-success/30">
                    {caso.roiEstimativa}
                  </Badge>
                  <div className="flex items-center gap-0.5" title={`Complexidade: ${caso.complexidade}`}>
                    {Array.from({ length: 3 }).map((_, i) => (
                      <div
                        key={i}
                        className={`h-1.5 w-1.5 rounded-full ${
                          i < dots ? "bg-foreground" : "bg-muted"
                        }`}
                      />
                    ))}
                    <span className="ml-1 text-[10px] text-muted-foreground">
                      {caso.complexidade}
                    </span>
                  </div>
                  <span className="text-[10px] text-muted-foreground">
                    {caso.tempoValor}
                  </span>
                </div>

                {/* KPIs affected */}
                <div className="flex flex-wrap gap-1">
                  {caso.kpisAfetados.map((kpi) => (
                    <Badge
                      key={kpi}
                      variant="secondary"
                      className="text-[10px] px-1.5 py-0"
                    >
                      {kpi}
                    </Badge>
                  ))}
                </div>

                {/* Expand toggle */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : caso.id)}
                  className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground transition-colors"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="h-3 w-3" /> Menos detalhes
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-3 w-3" /> Pré-requisitos e exemplos
                    </>
                  )}
                </button>

                {isExpanded && (
                  <div className="space-y-2 border-t pt-2">
                    {caso.prerequisitos.length > 0 && (
                      <div>
                        <p className="text-[10px] font-medium text-muted-foreground mb-1">
                          Pré-requisitos:
                        </p>
                        <ul className="space-y-0.5">
                          {caso.prerequisitos.map((p, i) => (
                            <li
                              key={i}
                              className="text-[10px] text-muted-foreground pl-2 before:content-['•'] before:mr-1"
                            >
                              {p}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {caso.exemplosReais.length > 0 && (
                      <div>
                        <p className="text-[10px] font-medium text-muted-foreground mb-1">
                          Exemplos reais:
                        </p>
                        <ul className="space-y-0.5">
                          {caso.exemplosReais.map((ex, i) => (
                            <li
                              key={i}
                              className="text-[10px] text-muted-foreground pl-2 before:content-['•'] before:mr-1"
                            >
                              {ex}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
