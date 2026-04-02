"use client";

import { useEffect, useState } from "react";
import {
  ExternalLink,
  FileText,
  Loader2,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { fetchExplorerRecord } from "@/lib/api";
import { fmtDate } from "@/lib/format";
import { DocumentLinks } from "./document-links";
import { ParecerAccordion } from "./parecer-accordion";

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

  if (!recordId) return null;

  const portalUrl = `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo?id=${recordId}`;

  return (
    <Card className="relative border-l-2 border-l-brand-teal animate-in fade-in slide-in-from-bottom-2 duration-300">
      <Button
        variant="ghost"
        size="icon"
        className="absolute right-3 top-3 h-7 w-7"
        onClick={onClose}
      >
        <X className="h-4 w-4" />
      </Button>

      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 font-heading text-base">
          <FileText className="h-4 w-4 text-brand-teal" />
          Detalhe do Registro
        </CardTitle>
      </CardHeader>

      <CardContent>
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <p className="text-sm text-destructive py-4">Erro: {error}</p>
        )}

        {record && !loading && (
          <div className="space-y-4">
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

            {/* Key fields — 2-col grid */}
            <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
              <Field label="CNPJ" value={str(record.cnpj_cpf)} mono />
              <Field label="Atividade" value={str(record.atividade)} />
              <Field label="Classe" value={str(record.classe)} />
              <Field label="Modalidade" value={str(record.modalidade)} />
              <Field label="Regional" value={str(record.regional)} />
              <Field label="Município" value={str(record.municipio)} />
              <Field label="Ano" value={str(record.ano)} />
              {record.data_decisao != null && (
                <Field label="Data Decisão" value={fmtDate(str(record.data_decisao))} />
              )}
            </dl>

            {/* Actions row */}
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" asChild>
                <a href={portalUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-3.5 w-3.5" />
                  Ver no Portal SEMAD
                </a>
              </Button>
            </div>

            {/* Document links */}
            {record.documentos_pdf != null && (
              <>
                <Separator />
                <div>
                  <h4 className="text-xs font-medium uppercase tracking-wide text-muted-foreground mb-2">
                    Documentos
                  </h4>
                  <DocumentLinks raw={str(record.documentos_pdf)} />
                </div>
              </>
            )}

            {/* Parecer text (lazy loaded) */}
            {dataset === "v_mg_semad" && recordId && (
              <ParecerAccordion dataset={dataset} recordId={recordId} />
            )}
          </div>
        )}

        {/* Non-SEMAD simple view */}
        {!loading && !error && recordId && dataset !== "v_mg_semad" && (
          <div className="py-6 text-center text-sm text-muted-foreground">
            <FileText className="mx-auto h-8 w-8 opacity-30 mb-2" />
            Visão detalhada disponível apenas para SEMAD.
          </div>
        )}
      </CardContent>
    </Card>
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

function str(v: unknown): string {
  if (v === null || v === undefined) return "\u2014";
  return String(v);
}
