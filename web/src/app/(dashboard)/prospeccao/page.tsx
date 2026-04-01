import { TrendingUp } from "lucide-react";

export default function ProspeccaoPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Prospecção
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Identificação de oportunidades por atividade, região e histórico
        </p>
      </div>
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
        <TrendingUp className="h-12 w-12 text-muted-foreground/30" />
        <p className="mt-4 text-sm text-muted-foreground">
          Em desenvolvimento — filtros inteligentes + recomendações
        </p>
      </div>
    </div>
  );
}
