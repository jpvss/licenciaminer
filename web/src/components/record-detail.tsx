"use client";

import { useEffect, useState } from "react";
import {
  ExternalLink,
  FileText,
  Loader2,
  ChevronDown,
} from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { fetchExplorerRecord, fetchExplorerRecordText } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import { DocumentLinks } from "./document-links";

interface RecordDetailProps {
  dataset: string;
  recordId: string | null;
  onClose: () => void;
}

export function RecordDetail({ dataset, recordId, onClose }: RecordDetailProps) {
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!recordId || dataset !== "v_mg_semad") {
      setRecord(null);
      return;
    }

    setLoading(true);
    setError(null);
    fetchExplorerRecord(dataset, recordId)
      .then(setRecord)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [dataset, recordId]);

  const open = recordId !== null;

  const portalUrl = recordId
    ? `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo?id=${recordId}`
    : null;

  return (
    <Sheet open={open} onOpenChange={(v) => !v && onClose()}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="font-heading text-base">
            Detalhe do Registro
          </SheetTitle>
        </SheetHeader>

        {loading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive py-4">Erro: {error}</p>
        )}

        {record && !loading && (
          <div className="space-y-4 py-4">
            {/* Header */}
            <div>
              <h3 className="font-medium text-sm">
                {str(record.empreendimento) || "Empreendimento"}
              </h3>
              {record.decisao != null && (
                <Badge
                  variant={
                    str(record.decisao).startsWith("Def")
                      ? "default"
                      : str(record.decisao).startsWith("Ind")
                        ? "destructive"
                        : "secondary"
                  }
                  className="mt-1"
                >
                  {str(record.decisao)}
                </Badge>
              )}
            </div>

            <Separator />

            {/* Key fields */}
            <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <Field label="CNPJ" value={str(record.cnpj_cpf)} mono />
              <Field label="Atividade" value={str(record.atividade)} />
              <Field label="Classe" value={str(record.classe)} />
              <Field label="Modalidade" value={str(record.modalidade)} />
              <Field label="Regional" value={str(record.regional)} />
              <Field label="Munic\u00edpio" value={str(record.municipio)} />
              <Field label="Ano" value={str(record.ano)} />
              {record.data_decisao != null && (
                <Field label="Data Decis\u00e3o" value={fmtDate(str(record.data_decisao))} />
              )}
            </dl>

            {/* Portal link */}
            {portalUrl && (
              <Button variant="outline" size="sm" className="w-full" asChild>
                <a href={portalUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-3.5 w-3.5" />
                  Ver no Portal SEMAD
                </a>
              </Button>
            )}

            <Separator />

            {/* Document links */}
            {record.documentos_pdf != null && (
              <div>
                <h4 className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">
                  Documentos
                </h4>
                <DocumentLinks raw={str(record.documentos_pdf)} />
              </div>
            )}

            {/* Parecer text (lazy loaded) */}
            {dataset === "v_mg_semad" && recordId && (
              <ParecerAccordion dataset={dataset} recordId={recordId} />
            )}
          </div>
        )}

        {/* Non-SEMAD simple view */}
        {!loading && !error && recordId && dataset !== "v_mg_semad" && (
          <div className="py-8 text-center text-sm text-muted-foreground">
            <FileText className="mx-auto h-8 w-8 opacity-30 mb-2" />
            Vis\u00e3o detalhada dispon\u00edvel apenas para SEMAD.
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  if (!value || value === "\u2014") return null;
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={mono ? "font-mono text-xs" : "text-sm"}>{value}</dd>
    </div>
  );
}

function ParecerAccordion({ dataset, recordId }: { dataset: string; recordId: string }) {
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
      <AccordionItem value="parecer">
        <AccordionTrigger className="text-xs font-medium" onClick={load}>
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

function str(v: unknown): string {
  if (v === null || v === undefined) return "\u2014";
  return String(v);
}
