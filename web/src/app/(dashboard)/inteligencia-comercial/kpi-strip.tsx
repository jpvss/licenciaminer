"use client";

import { useEffect, useState } from "react";
import {
  DollarSign,
  TrendingUp,
  Scale,
  Coins,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { fmtBR, fmtReais, fmtUSD } from "@/lib/format";
import { fetchKpiSummary, type KpiSummaryResponse } from "@/lib/api";

interface MiniSparklineProps {
  data: number[];
  color: string;
  width?: number;
  height?: number;
}

function MiniSparkline({ data, color, width = 80, height = 24 }: MiniSparklineProps) {
  if (data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg width={width} height={height} className="shrink-0">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

interface KpiCardProps {
  label: string;
  value: string;
  delta?: number;
  sparkline?: number[];
  sparkColor?: string;
  icon: React.ElementType;
  accentClass?: string;
}

function KpiCard({
  label,
  value,
  delta,
  sparkline,
  sparkColor = "var(--brand-teal)",
  icon: Icon,
  accentClass,
}: KpiCardProps) {
  return (
    <Card className="relative overflow-hidden">
      {accentClass && (
        <div className={cn("absolute inset-y-0 left-0 w-1", accentClass)} />
      )}
      <CardContent className="flex items-center gap-3 p-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-muted">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            {label}
          </p>
          <div className="flex items-center gap-2">
            <p className="text-lg font-bold font-heading font-tabular leading-none">
              {value}
            </p>
            {delta != null && (
              <Badge
                variant="secondary"
                className={cn(
                  "text-[10px] font-tabular px-1.5 py-0",
                  delta >= 0 ? "text-success" : "text-danger"
                )}
              >
                {delta >= 0 ? "+" : ""}
                {(delta * 100).toFixed(1)}%
              </Badge>
            )}
          </div>
        </div>
        {sparkline && sparkline.length >= 2 && (
          <MiniSparkline data={sparkline} color={sparkColor} />
        )}
      </CardContent>
    </Card>
  );
}

export function KpiStrip() {
  const [data, setData] = useState<KpiSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKpiSummary()
      .then(setData)
      .catch((e) => console.error("KPI summary:", e))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-14 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        label="USD/BRL"
        value={data.usd_brl ? `R$ ${fmtBR(data.usd_brl.latest, 4)}` : "—"}
        delta={data.usd_brl?.delta}
        sparkline={data.usd_brl?.sparkline}
        sparkColor="var(--brand-gold)"
        icon={DollarSign}
        accentClass="bg-brand-gold"
      />
      <KpiCard
        label="Ferro 62% Fe"
        value={data.ferro ? `${fmtUSD(data.ferro.latest)}` : "—"}
        delta={data.ferro?.delta}
        sparkline={data.ferro?.sparkline}
        sparkColor="var(--danger)"
        icon={TrendingUp}
        accentClass="bg-danger"
      />
      <KpiCard
        label="Balança Comercial"
        value={data.balanca_ytd ? fmtUSD(data.balanca_ytd.valor_usd ?? 0) : "—"}
        delta={data.balanca_ytd?.delta_yoy}
        sparkline={data.balanca_ytd?.sparkline}
        sparkColor="var(--brand-teal)"
        icon={Scale}
        accentClass="bg-brand-teal"
      />
      <KpiCard
        label="CFEM Acumulado"
        value={data.cfem_ytd ? fmtReais(data.cfem_ytd.valor_brl ?? 0) : "—"}
        delta={data.cfem_ytd?.delta_yoy}
        sparkline={data.cfem_ytd?.sparkline}
        sparkColor="var(--brand-orange)"
        icon={Coins}
        accentClass="bg-brand-orange"
      />
    </div>
  );
}
