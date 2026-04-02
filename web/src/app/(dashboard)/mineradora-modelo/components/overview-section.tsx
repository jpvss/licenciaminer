"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent } from "@/components/ui/card";
import { Brain, TrendingUp, Target } from "lucide-react";
import { getMaturityRadarData, getOverviewStats } from "../lib/data/modules-index";

interface OverviewSectionProps {
  onModuleClick: (key: string) => void;
}

export function OverviewSection({ onModuleClick }: OverviewSectionProps) {
  const radarData = getMaturityRadarData();
  const stats = getOverviewStats();

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {/* Radar chart */}
      <Card className="lg:col-span-2">
        <CardContent className="p-4">
          <h3 className="mb-1 font-heading text-sm font-semibold">
            Maturidade Digital por Módulo
          </h3>
          <p className="mb-3 text-[11px] text-muted-foreground">
            Avaliação da Mineradora Modelo em uma escala de 1 (Reativo) a 5 (Autônomo)
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="75%">
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis
                dataKey="modulo"
                tick={{ fontSize: 10, fill: "var(--muted-foreground)" }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 5]}
                tick={{ fontSize: 9, fill: "var(--muted-foreground)" }}
                tickCount={6}
              />
              <Radar
                name="Nível Atual"
                dataKey="nivel"
                stroke="var(--brand-teal)"
                fill="var(--brand-teal)"
                fillOpacity={0.2}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Stats cards */}
      <div className="flex flex-col gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-teal/10">
                <Brain className="h-4 w-4 text-brand-teal" />
              </div>
              <div>
                <p className="font-heading text-2xl font-bold tabular-nums">
                  {stats.totalCasosIA}
                </p>
                <p className="text-[11px] text-muted-foreground">
                  Casos de uso de IA mapeados
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-orange/10">
                <TrendingUp className="h-4 w-4 text-brand-orange" />
              </div>
              <div>
                <p className="font-heading text-2xl font-bold tabular-nums">
                  {stats.avgMaturity}/5
                </p>
                <p className="text-[11px] text-muted-foreground">
                  Maturidade digital média
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer transition-shadow hover:shadow-md"
          onClick={() => onModuleClick(stats.moduloPrioritario.key)}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-warning/10">
                <Target className="h-4 w-4 text-warning" />
              </div>
              <div>
                <p className="text-sm font-semibold">
                  {stats.moduloPrioritario.nome}
                </p>
                <p className="text-[11px] text-muted-foreground">
                  Maior oportunidade (nível {stats.moduloPrioritario.maturidade.nivelAtual})
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
