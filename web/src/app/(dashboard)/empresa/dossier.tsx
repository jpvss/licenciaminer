"use client";

import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Building2,
  Coins,
  FileWarning,
  Loader2,
  Scale,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
  fmtNumber,
  fmtPct,
  fmtReais,
  type ReportData,
} from "@/lib/api";

export function EmpresaDossier({ cnpj }: { cnpj: string }) {
  const [data, setData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchReportData(cnpj)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [cnpj]);

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
                CNPJ: {cnpj}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-xs text-muted-foreground">Nível de Risco</p>
              </div>
              <RiskBadge level={data.risk_level} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Decisões"
          value={fmtNumber(data.total_decisoes)}
          icon={BarChart3}
        />
        <StatCard
          label="Taxa Aprovação"
          value={fmtPct(data.taxa_aprovacao)}
          icon={TrendingUp}
          accentClass="bg-brand-teal"
        />
        <StatCard
          label="Infrações IBAMA"
          value={fmtNumber(data.total_infracoes)}
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
                <li
                  key={i}
                  className="flex items-start gap-2 text-sm leading-relaxed"
                >
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-orange" />
                  {finding}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Decision history */}
      {data.decisoes.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base font-heading">
              <BarChart3 className="h-4 w-4 text-brand-teal" />
              Histórico de Decisões
              <Badge variant="secondary" className="ml-2 font-tabular">
                {data.decisoes.length}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="px-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Processo</TableHead>
                    <TableHead>Atividade</TableHead>
                    <TableHead>Decisão</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Município</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.decisoes.slice(0, 20).map((d, i) => (
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
                      <TableCell className="text-xs font-tabular">
                        {d.data_decisao}
                      </TableCell>
                      <TableCell className="text-xs">{d.municipio}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
            {data.decisoes.length > 20 && (
              <p className="px-4 py-3 text-xs text-muted-foreground">
                Mostrando 20 de {data.decisoes.length} decisões
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function DecisionBadge({ decision }: { decision: string }) {
  const lower = (decision ?? "").toLowerCase();
  let variant: "default" | "secondary" | "destructive" | "outline" =
    "secondary";
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
