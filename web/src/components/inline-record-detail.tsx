"use client";

import { useEffect, useState, useRef } from "react";
import {
  ExternalLink,
  FileText,
  Loader2,
  X,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { fetchExplorerRecord } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import { DocumentLinks } from "./document-links";
import { ParecerAccordion } from "./parecer-accordion";

interface InlineRecordDetailProps {
  dataset: string;
  recordId: string;
  onClose: () => void;
}

export function InlineRecordDetail({
  dataset,
  recordId,
  onClose,
}: InlineRecordDetailProps) {
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cardRef = useRef<HTMLDivElement>(null);

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

  // Scroll into view when detail loads
  useEffect(() => {
    if (record && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [record]);

  const portalUrl = recordId
    ? `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo?id=${recordId}`
    : null;

  if (dataset !== "v_mg_semad") {
    return (
      <Card ref={cardRef}>
        <CardContent className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <FileText className="h-5 w-5 opacity-40" />
            Visão detalhada disponível apenas para SEMAD.
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card ref={cardRef} className="border-l-4 border-l-brand-teal animate-in fade-in slide-in-from-top-2 duration-300">
      <CardContent className="p-0">
        {/* Close button */}
        <div className="flex items-center justify-between border-b px-5 py-3">
          <h3 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Detalhes do Registro
          </h3>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <p className="p-5 text-sm text-destructive">Erro: {error}</p>
        )}

        {record && !loading && (
          <div className="p-5 space-y-5">
            {/* Header row */}
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <h3 className="text-base font-semibold leading-tight">
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
                    className="mt-1.5"
                  >
                    {str(record.decisao)}
                  </Badge>
                )}
              </div>
              {portalUrl && (
                <Button variant="outline" size="sm" className="shrink-0" asChild>
                  <a href={portalUrl} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
                    Portal SEMAD
                  </a>
                </Button>
              )}
            </div>

            {/* Fields grid */}
            <dl className="grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-3 lg:grid-cols-4">
              <Field label="CNPJ" value={str(record.cnpj_cpf)} mono />
              <Field label="Atividade" value={str(record.atividade)} />
              <Field label="Classe · Modalidade" value={joinFields(str(record.classe), str(record.modalidade))} />
              <Field label="Regional" value={str(record.regional)} />
              <Field label="Município · Ano" value={joinFields(str(record.municipio), str(record.ano))} />
              {record.data_decisao != null && (
                <Field label="Data Decisão" value={fmtDate(str(record.data_decisao))} />
              )}
            </dl>

            {/* Documents section */}
            {record.documentos_pdf != null && str(record.documentos_pdf).length > 3 && (
              <>
                <Separator />
                <div>
                  <h4 className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Documentos
                  </h4>
                  <DocumentLinks raw={str(record.documentos_pdf)} />
                </div>
              </>
            )}

            {/* Parecer text (lazy) */}
            <ParecerAccordion dataset={dataset} recordId={recordId} />

            {/* Source attribution */}
            <Separator />
            <p className="text-[11px] font-mono text-muted-foreground/60">
              SEMAD MG &middot; ID {recordId}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  if (!value || value === "—") return null;
  return (
    <div>
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={mono ? "font-mono text-xs mt-0.5" : "text-sm mt-0.5"}>{value}</dd>
    </div>
  );
}

function str(v: unknown): string {
  if (v === null || v === undefined) return "—";
  return String(v);
}

function joinFields(...values: string[]): string {
  const valid = values.filter((v) => v && v !== "—");
  return valid.length > 0 ? valid.join(" · ") : "—";
}
