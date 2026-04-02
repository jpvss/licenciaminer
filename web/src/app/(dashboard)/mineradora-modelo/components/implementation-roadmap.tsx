"use client";

import { Clock, CheckCircle2, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { RoadmapPhase } from "../lib/types";

interface ImplementationRoadmapProps {
  fases: RoadmapPhase[];
  accentColor: string;
  onRequestDiagnostico?: () => void;
}

export function ImplementationRoadmap({
  fases,
  accentColor,
  onRequestDiagnostico,
}: ImplementationRoadmapProps) {
  return (
    <div className="space-y-4">
      {/* Timeline */}
      <div className="space-y-0">
        {fases.map((fase, i) => (
          <div key={fase.fase} className="relative flex gap-4">
            {/* Timeline line */}
            <div className="flex flex-col items-center">
              <div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                style={{ backgroundColor: accentColor }}
              >
                {fase.fase}
              </div>
              {i < fases.length - 1 && (
                <div
                  className="w-0.5 flex-1 min-h-[24px]"
                  style={{ backgroundColor: accentColor, opacity: 0.2 }}
                />
              )}
            </div>

            {/* Phase content */}
            <Card className="mb-4 flex-1">
              <CardContent className="p-4 space-y-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <h4 className="font-heading text-sm font-semibold">
                    Fase {fase.fase}: {fase.titulo}
                  </h4>
                  <Badge variant="outline" className="text-[10px] gap-1">
                    <Clock className="h-3 w-3" />
                    {fase.duracao}
                  </Badge>
                </div>

                <div className="space-y-1.5">
                  <p className="text-[10px] font-medium text-muted-foreground">
                    Entregas:
                  </p>
                  {fase.entregas.map((entrega, j) => (
                    <div key={j} className="flex items-start gap-2">
                      <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground/40" />
                      <span className="text-[11px] text-muted-foreground">
                        {entrega}
                      </span>
                    </div>
                  ))}
                </div>

                {fase.dependencias.length > 0 && (
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="text-[10px] font-medium text-muted-foreground">
                      Depende de:
                    </span>
                    {fase.dependencias.map((dep, j) => (
                      <Badge
                        key={j}
                        variant="secondary"
                        className="text-[10px] px-1.5 py-0"
                      >
                        {dep}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ))}
      </div>

      {/* CTA */}
      {onRequestDiagnostico && (
        <Card className="border-dashed" style={{ borderColor: accentColor }}>
          <CardContent className="flex items-center justify-between gap-4 p-4">
            <div>
              <p className="text-sm font-semibold">
                Quer transformar sua operação com IA?
              </p>
              <p className="text-xs text-muted-foreground">
                Comece com um diagnóstico de 4-6 semanas para identificar as maiores oportunidades.
              </p>
            </div>
            <button
              onClick={onRequestDiagnostico}
              className="flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold text-white transition-opacity hover:opacity-90"
              style={{ backgroundColor: accentColor }}
            >
              Solicitar Diagnóstico
              <ArrowRight className="h-4 w-4" />
            </button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
