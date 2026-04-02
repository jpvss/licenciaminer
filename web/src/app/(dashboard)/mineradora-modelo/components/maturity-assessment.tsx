"use client";

import { useState } from "react";
import { Check, Circle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { MaturityLevel } from "../lib/types";

interface MaturityAssessmentProps {
  nivelAtual: 1 | 2 | 3 | 4 | 5;
  niveis: MaturityLevel[];
  accentColor: string;
}

export function MaturityAssessment({
  nivelAtual,
  niveis,
  accentColor,
}: MaturityAssessmentProps) {
  const [selectedLevel, setSelectedLevel] = useState<number>(nivelAtual);

  const selected = niveis.find((n) => n.nivel === selectedLevel);

  return (
    <div className="space-y-4">
      {/* Scale visualization */}
      <div className="flex items-center justify-between px-2">
        {niveis.map((nivel, i) => {
          const isCompleted = nivel.nivel < nivelAtual;
          const isCurrent = nivel.nivel === nivelAtual;
          const isFuture = nivel.nivel > nivelAtual;
          const isSelected = nivel.nivel === selectedLevel;

          return (
            <div key={nivel.nivel} className="flex flex-1 items-center">
              {/* Node */}
              <button
                onClick={() => setSelectedLevel(nivel.nivel)}
                className="relative flex flex-col items-center gap-1.5"
              >
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full border-2 transition-all ${
                    isCompleted
                      ? "border-success bg-success text-white"
                      : isCurrent
                        ? "border-current bg-current text-white"
                        : "border-muted-foreground/30 bg-background text-muted-foreground/50"
                  } ${isSelected ? "ring-2 ring-ring ring-offset-2" : ""}`}
                  style={isCurrent ? { borderColor: accentColor, backgroundColor: accentColor } : undefined}
                >
                  {isCompleted ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <span className="text-xs font-bold">{nivel.nivel}</span>
                  )}
                </div>
                <span
                  className={`text-[10px] font-medium whitespace-nowrap ${
                    isCurrent
                      ? "text-foreground font-semibold"
                      : isFuture
                        ? "text-muted-foreground/50"
                        : "text-muted-foreground"
                  }`}
                >
                  {nivel.nome}
                </span>
                {isCurrent && (
                  <span
                    className="text-[9px] font-semibold"
                    style={{ color: accentColor }}
                  >
                    Atual
                  </span>
                )}
              </button>

              {/* Connector line */}
              {i < niveis.length - 1 && (
                <div
                  className={`mx-1 h-0.5 flex-1 ${
                    nivel.nivel < nivelAtual
                      ? "bg-success"
                      : "bg-muted-foreground/20"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Selected level detail */}
      {selected && (
        <Card>
          <CardContent className="p-4 space-y-3">
            <div className="flex items-center gap-2">
              <div
                className="flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold text-white"
                style={{ backgroundColor: selected.nivel <= nivelAtual ? accentColor : "var(--muted-foreground)" }}
              >
                {selected.nivel}
              </div>
              <h4 className="font-heading text-sm font-semibold">
                Nível {selected.nivel} — {selected.nome}
              </h4>
              {selected.nivel === nivelAtual && (
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                  style={{ backgroundColor: accentColor }}
                >
                  Nível Atual
                </span>
              )}
              {selected.nivel === nivelAtual + 1 && (
                <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                  Próximo Nível
                </span>
              )}
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {selected.descricao}
            </p>
            <div className="space-y-1.5">
              <p className="text-[10px] font-medium text-muted-foreground">
                Critérios:
              </p>
              {selected.criterios.map((criterio, i) => {
                const met = selected.nivel <= nivelAtual;
                return (
                  <div key={i} className="flex items-start gap-2">
                    {met ? (
                      <Check className="mt-0.5 h-3 w-3 shrink-0 text-success" />
                    ) : (
                      <Circle className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground/30" />
                    )}
                    <span
                      className={`text-[11px] ${
                        met ? "text-foreground" : "text-muted-foreground"
                      }`}
                    >
                      {criterio}
                    </span>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
