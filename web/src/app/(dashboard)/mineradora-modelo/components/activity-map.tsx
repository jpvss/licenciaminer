"use client";

import { useState } from "react";
import { ArrowRight, AlertTriangle, Lightbulb, CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ActivityStep } from "../lib/types";

const STATUS_CONFIG = {
  ok: {
    label: "OK",
    icon: CheckCircle2,
    badgeClass: "bg-muted text-muted-foreground",
    borderClass: "border-border",
  },
  gargalo: {
    label: "Gargalo",
    icon: AlertTriangle,
    badgeClass: "bg-destructive/10 text-destructive",
    borderClass: "border-destructive/40",
  },
  oportunidade: {
    label: "Oportunidade",
    icon: Lightbulb,
    badgeClass: "bg-brand-teal/10 text-brand-teal",
    borderClass: "border-brand-teal/40",
  },
} as const;

interface ActivityMapProps {
  atividades: ActivityStep[];
  accentColor: string;
}

export function ActivityMap({ atividades }: ActivityMapProps) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      {/* Horizontal flow */}
      <div className="flex items-center gap-2 overflow-x-auto pb-3">
        {atividades.map((step, i) => {
          const config = STATUS_CONFIG[step.status];
          const Icon = config.icon;
          const isExpanded = expanded === step.id;

          return (
            <div key={step.id} className="flex items-center gap-2">
              {i > 0 && (
                <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground/40" />
              )}
              <button
                onClick={() => setExpanded(isExpanded ? null : step.id)}
                className={`flex min-w-[140px] flex-col items-center gap-1.5 rounded-lg border p-3 transition-all hover:shadow-sm ${config.borderClass} ${isExpanded ? "ring-2 ring-ring" : ""}`}
              >
                <Icon className="h-4 w-4" />
                <span className="text-xs font-medium whitespace-nowrap">
                  {step.nome}
                </span>
                <Badge
                  variant="secondary"
                  className={`text-[10px] px-1.5 py-0 ${config.badgeClass}`}
                >
                  {config.label}
                </Badge>
              </button>
            </div>
          );
        })}
      </div>

      {/* Expanded detail */}
      {expanded && (() => {
        const step = atividades.find((a) => a.id === expanded);
        if (!step) return null;
        const config = STATUS_CONFIG[step.status];

        return (
          <Card className={`border ${config.borderClass}`}>
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center gap-2">
                <config.icon className="h-4 w-4" />
                <h4 className="font-heading text-sm font-semibold">{step.nome}</h4>
                <Badge
                  variant="secondary"
                  className={`text-[10px] ${config.badgeClass}`}
                >
                  {config.label}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {step.detalhes}
              </p>
              {step.kpisAfetados.length > 0 && (
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="text-[10px] font-medium text-muted-foreground">
                    KPIs afetados:
                  </span>
                  {step.kpisAfetados.map((kpi) => (
                    <Badge
                      key={kpi}
                      variant="outline"
                      className="text-[10px] px-1.5 py-0"
                    >
                      {kpi}
                    </Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        );
      })()}
    </div>
  );
}
