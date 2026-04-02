"use client";

import { useEffect, useState } from "react";
import { Shield, TrendingDown, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { fmtBR } from "@/lib/format";
import { fetchRegulatoryPulse, type RegulatorySignal } from "@/lib/api";

export function RegulatoryPulse() {
  const [signals, setSignals] = useState<RegulatorySignal[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRegulatoryPulse()
      .then((r) => setSignals(r.signals))
      .catch(() => setSignals([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-10 flex-1" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!signals || signals.length === 0) return null;

  return (
    <Card className="border-muted">
      <CardHeader className="pb-2 pt-3 px-4">
        <CardTitle className="text-xs font-medium flex items-center gap-1.5 text-muted-foreground">
          <Shield className="h-3 w-3" />
          Pulso Regulatório
        </CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3">
        <div className="grid gap-2 grid-cols-2 lg:grid-cols-4">
          {signals.map((signal) => (
            <SignalBadge key={signal.key} signal={signal} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function SignalBadge({ signal }: { signal: RegulatorySignal }) {
  const formattedValue = signal.unit === "%"
    ? `${fmtBR(signal.value, 1)}%`
    : fmtBR(signal.value);

  return (
    <div className="flex items-center gap-2 rounded-lg border p-2">
      <div className="min-w-0 flex-1">
        <p className="text-[9px] font-medium uppercase tracking-wide text-muted-foreground truncate">
          {signal.label}
        </p>
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-bold tabular-nums">{formattedValue}</span>
          {signal.delta_pct != null && (
            <Badge
              variant="secondary"
              className={cn(
                "text-[9px] px-1 py-0 gap-0.5 font-tabular",
                signal.delta_pct > 0 ? "text-danger" : "text-success"
              )}
            >
              {signal.delta_pct > 0 ? (
                <TrendingUp className="h-2.5 w-2.5" />
              ) : (
                <TrendingDown className="h-2.5 w-2.5" />
              )}
              {signal.delta_pct > 0 ? "+" : ""}
              {signal.delta_pct.toFixed(1)}%
            </Badge>
          )}
        </div>
      </div>
      <p className="text-[8px] text-muted-foreground/60 shrink-0">{signal.fonte}</p>
    </div>
  );
}
