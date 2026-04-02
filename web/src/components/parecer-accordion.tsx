"use client";

import { useState } from "react";
import { FileText, Loader2 } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { fetchExplorerRecordText } from "@/lib/api";
import { cn } from "@/lib/utils";

export function ParecerAccordion({
  dataset,
  recordId,
  className,
}: {
  dataset: string;
  recordId: string;
  className?: string;
}) {
  const [text, setText] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = () => {
    if (loaded) return;
    setLoading(true);
    fetchExplorerRecordText(dataset, recordId)
      .then((r) => {
        setText(r.text || "(Sem texto)");
        setLoaded(true);
      })
      .catch(() => setText("Erro ao carregar texto."))
      .finally(() => setLoading(false));
  };

  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="parecer" className={cn("border-none", className)}>
        <AccordionTrigger className="text-xs font-medium py-2" onClick={load}>
          <span className="flex items-center gap-2">
            <FileText className="h-3.5 w-3.5" />
            Texto do Parecer
            {loading && <Loader2 className="h-3 w-3 animate-spin" />}
          </span>
        </AccordionTrigger>
        <AccordionContent>
          <pre className="whitespace-pre-wrap text-xs text-muted-foreground max-h-80 overflow-y-auto rounded bg-muted/30 p-3">
            {text || "Carregando..."}
          </pre>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
}
