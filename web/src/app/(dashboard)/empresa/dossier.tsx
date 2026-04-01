"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Building2,
  Coins,
  Download,
  ExternalLink,
  FileText,
  FileWarning,
  Loader2,
  MapPin,
  Scale,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { StatCard } from "@/components/stat-card";
import { RiskBadge } from "@/components/risk-badge";
import {
  fetchReportData,
  fetchEmpresa,
  fetchEmpresaANM,
  downloadReportPDF,
  type ReportData,
  type ANMTitulo,
  type EmpresaProfile,
} from "@/lib/api";
import { fmtBR, fmtPct, fmtReais, fmtDate, fmtCNPJ, fmtHa } from "@/lib/format";

export function EmpresaDossier({ cnpj }: { cnpj: string }) {
  const [data, setData] = useState<ReportData | null>(null);
  const [profile, setProfile] = useState<EmpresaProfile | null>(null);
  const [anmTitulos, setAnmTitulos] = useState<ANMTitulo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfError, setPdfError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setAnmTitulos([]);
    setProfile(null);

    Promise.all([
      fetchReportData(cnpj),
      fetchEmpresa(cnpj).catch(() => null),
      fetchEmpresaANM(cnpj).catch(() => ({ titular: "", total: 0, titulos: [] })),
    ])
      .then(([reportData, empresaData, anmData]) => {
        setData(reportData);
        if (empresaData) setProfile(empresaData);
        if (anmData && Array.isArray(anmData.titulos)) {
          setAnmTitulos(anmData.titulos);
        } else if (Array.isArray(anmData)) {
          setAnmTitulos(anmData as ANMTitulo[]);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [cnpj]);

  const handlePDFDownload = async () => {
    setPdfLoading(true);
    setPdfError(null);
    try {
      await downloadReportPDF(cnpj);
    } catch (e) {
      setPdfError(e instanceof Error ? e.message : "Erro ao gerar PDF");
    } finally {
      setPdfLoading(false);
    }
  };

  if (loading) return <DossierSkeleton />;
  if (error)
    return (
      <Card className="border-destructive/30">
        <CardContent className="flex items-center gap-3 p-6">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          <div>
            <p className="font-medium">Erro ao consultar</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Company header */}
      <Card className="relative overflow-hidden">
        <div className="absolute inset-y-0 left-0 w-1.5 bg-brand-teal" />
        <CardContent className="p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <h2 className="font-heading text-xl font-bold">
                {data.razao_social}
              </h2>
              <p className="mt-1 text-sm font-mono text-muted-foreground">
                CNPJ: {fmtCNPJ(cnpj)}
              </p>
              {profile?.profile && (
                <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  {profile.profile.cnae_fiscal && (
                    <span>CNAE: {profile.profile.cnae_fiscal} — {profile.profile.cnae_descricao}</span>
                  )}
                  {profile.profile.porte && (
                    <span>Porte: {profile.profile.porte}</span>
                  )}
                  {profile.profile.data_abertura && (
                    <span>Abertura: {fmtDate(profile.profile.data_abertura)}</span>
                  )}
                </div>
              )}
            </div>
            <div className="flex items-center gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePDFDownload}
                disabled={pdfLoading}
              >
                {pdfLoading ? (
                  <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Download className="mr-2 h-3.5 w-3.5" />
                )}
                PDF
              </Button>
              <RiskBadge level={data.risk_level} />
            </div>
          </div>
          {pdfError && (
            <p className="mt-2 text-xs text-destructive">{pdfError}</p>
          )}
        </CardContent>
      </Card>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Decis\u00f5es"
          value={fmtBR(data.total_decisoes)}
          icon={BarChart3}
        />
        <StatCard
          label="Taxa Aprova\u00e7\u00e3o"
          value={fmtPct(data.taxa_aprovacao)}
          icon={TrendingUp}
          accentClass="bg-brand-teal"
        />
        <StatCard
          label="Infra\u00e7\u00f5es IBAMA"
          value={fmtBR(data.total_infracoes)}
          icon={FileWarning}
          accentClass={
            data.total_infracoes >= 6
              ? "bg-danger"
              : data.total_infracoes >= 1
                ? "bg-warning"
                : "bg-success"
          }
        />
        <StatCard
          label="CFEM Pago"
          value={fmtReais(data.cfem_total_pago)}
          subtitle={`${data.cfem_meses_pagamento} meses`}
          icon={Coins}
        />
      </div>

      {/* Findings */}
      {data.findings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-heading">
              <Scale className="h-4 w-4 text-brand-orange" />
              Achados Principais
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.findings.map((finding, i) => (
                <li key={i} className="flex items-start gap-2 text-sm leading-relaxed">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-orange" />
                  {finding}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Expandable detail sections */}
      <Accordion type="multiple" className="space-y-3">
        {/* Decision history */}
        {data.decisoes.length > 0 && (
          <AccordionItem value="decisoes" className="rounded-xl border bg-card shadow-sm">
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <div className="flex items-center gap-2 font-heading text-base">
                <BarChart3 className="h-4 w-4 text-brand-teal" />
                Hist\u00f3rico de Decis\u00f5es
                <Badge variant="secondary" className="ml-2 tabular-nums">
                  {data.decisoes.length}
                </Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-0 pb-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Processo</TableHead>
                      <TableHead>Atividade</TableHead>
                      <TableHead>Decis\u00e3o</TableHead>
                      <TableHead>Data</TableHead>
                      <TableHead>Munic\u00edpio</TableHead>
                      <TableHead className="w-10"></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.decisoes.map((d, i) => (
                      <TableRow key={i}>
                        <TableCell className="font-mono text-xs">
                          {d.processo}
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate text-xs">
                          {d.atividade}
                        </TableCell>
                        <TableCell>
                          <DecisionBadge decision={d.decisao} />
                        </TableCell>
                        <TableCell className="text-xs tabular-nums">
                          {d.data_decisao}
                        </TableCell>
                        <TableCell className="text-xs">{d.municipio}</TableCell>
                        <TableCell>
                          {d.detail_id != null ? (
                            <a
                              href={`https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo?id=${d.detail_id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-muted-foreground hover:text-foreground"
                            >
                              <ExternalLink className="h-3.5 w-3.5" />
                            </a>
                          ) : null}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* ANM Titles */}
        {anmTitulos.length > 0 && (
          <AccordionItem value="anm" className="rounded-xl border bg-card shadow-sm">
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <div className="flex items-center gap-2 font-heading text-base">
                <MapPin className="h-4 w-4 text-brand-orange" />
                T\u00edtulos Minerários ANM
                <Badge variant="secondary" className="ml-2 tabular-nums">
                  {anmTitulos.length}
                </Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-0 pb-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Processo</TableHead>
                      <TableHead>Fase</TableHead>
                      <TableHead>Substância</TableHead>
                      <TableHead>Área</TableHead>
                      <TableHead>UF</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {anmTitulos.map((t, i) => (
                      <TableRow key={i}>
                        <TableCell className="font-mono text-xs">
                          {t.PROCESSO}
                        </TableCell>
                        <TableCell className="text-xs">{t.FASE}</TableCell>
                        <TableCell className="text-xs">{t.SUBS}</TableCell>
                        <TableCell className="text-xs tabular-nums">
                          {t.AREA_HA != null ? fmtHa(t.AREA_HA) : "\u2014"}
                        </TableCell>
                        <TableCell className="text-xs">{t.UF}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* CFEM detail */}
        {data.cfem_meses_pagamento > 0 && (
          <AccordionItem value="cfem" className="rounded-xl border bg-card shadow-sm">
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <div className="flex items-center gap-2 font-heading text-base">
                <Coins className="h-4 w-4 text-brand-gold" />
                CFEM — Compensa\u00e7\u00e3o Financeira
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-4">
              <dl className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <dt className="text-xs text-muted-foreground">Total Pago</dt>
                  <dd className="font-medium tabular-nums">{fmtReais(data.cfem_total_pago)}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground">Meses com Pagamento</dt>
                  <dd className="font-medium tabular-nums">{data.cfem_meses_pagamento}</dd>
                </div>
              </dl>
            </AccordionContent>
          </AccordionItem>
        )}

        {/* Similar cases */}
        {data.casos_similares.length > 0 && (
          <AccordionItem value="similares" className="rounded-xl border bg-card shadow-sm">
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <div className="flex items-center gap-2 font-heading text-base">
                <FileText className="h-4 w-4 text-brand-teal" />
                Casos Similares
                <Badge variant="secondary" className="ml-2 tabular-nums">
                  {data.casos_similares.length}
                </Badge>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-0 pb-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Empreendimento</TableHead>
                      <TableHead>Decis\u00e3o</TableHead>
                      <TableHead>Atividade</TableHead>
                      <TableHead>Munic\u00edpio</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.casos_similares.map((c, i) => (
                      <TableRow key={i}>
                        <TableCell className="text-xs max-w-[200px] truncate">
                          {String(c.empreendimento ?? "\u2014")}
                        </TableCell>
                        <TableCell>
                          <DecisionBadge decision={String(c.decisao ?? "")} />
                        </TableCell>
                        <TableCell className="text-xs max-w-[180px] truncate">
                          {String(c.atividade ?? "")}
                        </TableCell>
                        <TableCell className="text-xs">
                          {String(c.municipio ?? "")}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </AccordionContent>
          </AccordionItem>
        )}
      </Accordion>
    </div>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const lower = (decision ?? "").toLowerCase();
  let variant: "default" | "secondary" | "destructive" | "outline" = "secondary";
  if (lower.includes("deferid")) variant = "default";
  else if (lower.includes("indefer")) variant = "destructive";
  else if (lower.includes("arquiv")) variant = "outline";

  return (
    <Badge variant={variant} className="text-[10px] font-medium">
      {decision}
    </Badge>
  );
}

function DossierSkeleton() {
  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-6">
          <Skeleton className="h-6 w-64" />
          <Skeleton className="mt-2 h-4 w-40" />
        </CardContent>
      </Card>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-5">
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
