import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const RISK_CONFIG = {
  BAIXO: {
    label: "Baixo",
    className: "bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-300 dark:border-green-800",
  },
  MODERADO: {
    label: "Moderado",
    className: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  },
  ALTO: {
    label: "Alto",
    className: "bg-red-50 text-red-700 border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
  },
} as const;

export function RiskBadge({ level }: { level: string }) {
  const config = RISK_CONFIG[level as keyof typeof RISK_CONFIG] ?? RISK_CONFIG.MODERADO;
  return (
    <Badge variant="outline" className={cn("font-semibold", config.className)}>
      {config.label}
    </Badge>
  );
}
