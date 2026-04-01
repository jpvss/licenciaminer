"use client";

import { useEffect, useState, useMemo } from "react";
import {
  ShieldCheck,
  ChevronRight,
  ChevronLeft,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  fetchLicenseTypes,
  fetchDDDocuments,
  fetchDDRequirements,
  submitDDScore,
  fmtPct,
  type LicenseType,
  type DDDocument,
  type DDRequirement,
  type DDScoreResult,
} from "@/lib/api";

type Evaluation = "Atende" | "Atende Parcialmente" | "Não Atende" | "Não Aplica";

const EVAL_OPTIONS: { value: Evaluation; label: string; color: string }[] = [
  { value: "Atende", label: "Atende", color: "text-success" },
  { value: "Atende Parcialmente", label: "Parcial", color: "text-warning" },
  { value: "Não Atende", label: "Não Atende", color: "text-danger" },
  { value: "Não Aplica", label: "N/A", color: "text-muted-foreground" },
];

const STEPS = [
  { num: 1, label: "Configuração" },
  { num: 2, label: "Documentos" },
  { num: 3, label: "Avaliação" },
  { num: 4, label: "Resultado" },
];

export default function DueDiligencePage() {
  const [step, setStep] = useState(1);

  // Step 1
  const [licenseTypes, setLicenseTypes] = useState<LicenseType[] | null>(null);
  const [selectedLicense, setSelectedLicense] = useState("");

  // Step 2
  const [documents, setDocuments] = useState<DDDocument[] | null>(null);
  const [docStatus, setDocStatus] = useState<Record<string, string>>({});
  const [loadingDocs, setLoadingDocs] = useState(false);

  // Step 3
  const [requirements, setRequirements] = useState<DDRequirement[]>([]);
  const [evaluations, setEvaluations] = useState<Record<string, string>>({});
  const [loadingReqs, setLoadingReqs] = useState(false);

  // Step 4
  const [result, setResult] = useState<DDScoreResult | null>(null);
  const [scoring, setScoring] = useState(false);

  // Load license types
  useEffect(() => {
    fetchLicenseTypes().then(setLicenseTypes).catch(() => {});
  }, []);

  // Load documents when license changes
  useEffect(() => {
    if (!selectedLicense) return;
    setLoadingDocs(true);
    fetchDDDocuments(selectedLicense)
      .then((res) => {
        setDocuments(res.documents);
        // Default all to "Não Apresentado"
        const status: Record<string, string> = {};
        res.documents.forEach((d) => (status[d.documento] = "Não Apresentado"));
        setDocStatus(status);
      })
      .finally(() => setLoadingDocs(false));
  }, [selectedLicense]);

  // Presented docs
  const presentedDocs = useMemo(
    () =>
      documents?.filter(
        (d) => docStatus[d.documento] === "Apresentado" || docStatus[d.documento] === "Parcial"
      ) ?? [],
    [documents, docStatus]
  );

  // Load requirements when moving to step 3
  const loadRequirements = async () => {
    setLoadingReqs(true);
    const allReqs: DDRequirement[] = [];
    for (const doc of presentedDocs) {
      try {
        const res = await fetchDDRequirements(doc.documento);
        allReqs.push(...res.requirements);
      } catch {
        // skip failed
      }
    }
    setRequirements(allReqs);
    setLoadingReqs(false);
  };

  // Submit score
  const handleScore = async () => {
    setScoring(true);
    try {
      const res = await submitDDScore({
        avaliacoes: evaluations,
        doc_status: docStatus,
      });
      setResult(res);
      setStep(4);
    } catch {
      // handle error
    } finally {
      setScoring(false);
    }
  };

  // Group requirements by document
  const reqsByDoc = useMemo(() => {
    const map: Record<string, DDRequirement[]> = {};
    requirements.forEach((r) => {
      if (!map[r.documento]) map[r.documento] = [];
      map[r.documento].push(r);
    });
    return map;
  }, [requirements]);

  // Live conformity score
  const liveScore = useMemo(() => {
    const evaluated = Object.entries(evaluations).filter(([, v]) => v !== "Não Aplica");
    if (evaluated.length === 0) return null;
    const total = evaluated.length;
    const score = evaluated.reduce((acc, [, v]) => {
      if (v === "Atende") return acc + 1;
      if (v === "Atende Parcialmente") return acc + 0.5;
      return acc;
    }, 0);
    return (score / total) * 100;
  }, [evaluations]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Due Diligence Ambiental
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Auditoria de conformidade documental para licenciamento ambiental
        </p>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-1">
        {STEPS.map((s, i) => (
          <div key={s.num} className="flex items-center">
            <div
              className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
                step === s.num
                  ? "bg-brand-orange text-white"
                  : step > s.num
                  ? "bg-success/10 text-success"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              <span className="font-tabular">{s.num}</span>
              <span className="hidden sm:inline">{s.label}</span>
            </div>
            {i < STEPS.length - 1 && (
              <ChevronRight className="mx-1 h-4 w-4 text-muted-foreground/50" />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Configuration */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-heading">
              <ShieldCheck className="h-4 w-4 text-brand-orange" />
              Configuração do Projeto
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="max-w-md space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium">
                  Tipo de Licença
                </label>
                {licenseTypes ? (
                  <Select value={selectedLicense} onValueChange={setSelectedLicense}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo de licença" />
                    </SelectTrigger>
                    <SelectContent>
                      {licenseTypes.map((lt) => (
                        <SelectItem key={lt.code} value={lt.code}>
                          <span className="font-medium">{lt.code}</span>
                          <span className="ml-2 text-muted-foreground">
                            — {lt.description}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Skeleton className="h-10 w-full" />
                )}
              </div>

              <p className="text-xs text-muted-foreground">
                A seleção do tipo de licença determina quais documentos e requisitos de teste
                serão aplicáveis na avaliação de conformidade.
              </p>
            </div>

            <div className="flex justify-end">
              <Button
                disabled={!selectedLicense || loadingDocs}
                onClick={() => setStep(2)}
              >
                Próximo
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Document checklist */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 font-heading">
              <FileText className="h-4 w-4 text-brand-teal" />
              Checklist de Documentos
              {documents && (
                <Badge variant="secondary" className="ml-2">
                  {documents.length} documentos
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary */}
            {documents && (
              <div className="flex gap-4 text-sm">
                <span className="text-success">
                  {Object.values(docStatus).filter((v) => v === "Apresentado").length} apresentados
                </span>
                <span className="text-warning">
                  {Object.values(docStatus).filter((v) => v === "Parcial").length} parciais
                </span>
                <span className="text-muted-foreground">
                  {Object.values(docStatus).filter((v) => v === "Não Apresentado").length} pendentes
                </span>
              </div>
            )}

            {loadingDocs ? (
              <div className="space-y-2">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {documents?.map((doc) => (
                  <div
                    key={doc.documento}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{doc.documento}</p>
                      {doc.descricao && (
                        <p className="mt-0.5 text-xs text-muted-foreground line-clamp-1">
                          {doc.descricao}
                        </p>
                      )}
                    </div>
                    <Select
                      value={docStatus[doc.documento] ?? "Não Apresentado"}
                      onValueChange={(v) =>
                        setDocStatus((prev) => ({ ...prev, [doc.documento]: v }))
                      }
                    >
                      <SelectTrigger className="w-[160px] shrink-0 ml-4">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Apresentado">
                          <span className="text-success">Apresentado</span>
                        </SelectItem>
                        <SelectItem value="Parcial">
                          <span className="text-warning">Parcial</span>
                        </SelectItem>
                        <SelectItem value="Não Apresentado">
                          <span className="text-muted-foreground">Não Apresentado</span>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-between">
              <Button variant="outline" onClick={() => setStep(1)}>
                <ChevronLeft className="mr-1 h-4 w-4" />
                Voltar
              </Button>
              <Button
                disabled={presentedDocs.length === 0}
                onClick={async () => {
                  await loadRequirements();
                  setStep(3);
                }}
              >
                {loadingReqs ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : null}
                Próximo
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Conformance assessment */}
      {step === 3 && (
        <div className="space-y-4">
          {/* Live score bar */}
          <Card>
            <CardContent className="flex items-center gap-4 p-4">
              <div className="flex-1">
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium">Conformidade</span>
                  <span className="font-tabular font-bold">
                    {liveScore !== null ? fmtPct(liveScore) : "—"}
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${liveScore ?? 0}%`,
                      backgroundColor:
                        liveScore === null
                          ? "var(--muted)"
                          : liveScore >= 90
                          ? "var(--success)"
                          : liveScore >= 65
                          ? "var(--warning)"
                          : "var(--danger)",
                    }}
                  />
                </div>
              </div>
              <Badge variant="outline" className="font-tabular">
                {Object.keys(evaluations).length} / {requirements.length} avaliados
              </Badge>
            </CardContent>
          </Card>

          {/* Requirements by document */}
          {Object.entries(reqsByDoc).map(([docName, reqs]) => (
            <Card key={docName}>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base font-heading">
                  <FileText className="h-4 w-4 text-brand-teal" />
                  {docName}
                  <Badge variant="secondary" className="ml-auto font-tabular">
                    {reqs.filter((r) => evaluations[r.requisito_id]).length}/{reqs.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {reqs.map((req) => (
                  <div
                    key={req.requisito_id}
                    className="rounded-lg border p-3 space-y-2"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">{req.teste_aderencia}</p>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {req.topico} · {req.requisito_id}
                        </p>
                        {req.evidencia_esperada && (
                          <p className="mt-1 text-xs text-muted-foreground/70 italic">
                            Evidência: {req.evidencia_esperada}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {EVAL_OPTIONS.map((opt) => (
                        <Button
                          key={opt.value}
                          variant={
                            evaluations[req.requisito_id] === opt.value
                              ? "default"
                              : "outline"
                          }
                          size="sm"
                          className={
                            evaluations[req.requisito_id] === opt.value
                              ? opt.value === "Atende"
                                ? "bg-success hover:bg-success/90"
                                : opt.value === "Atende Parcialmente"
                                ? "bg-warning hover:bg-warning/90"
                                : opt.value === "Não Atende"
                                ? "bg-danger hover:bg-danger/90"
                                : ""
                              : ""
                          }
                          onClick={() =>
                            setEvaluations((prev) => ({
                              ...prev,
                              [req.requisito_id]: opt.value,
                            }))
                          }
                        >
                          {opt.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setStep(2)}>
              <ChevronLeft className="mr-1 h-4 w-4" />
              Voltar
            </Button>
            <Button
              disabled={Object.keys(evaluations).length === 0 || scoring}
              onClick={handleScore}
            >
              {scoring && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Calcular Resultado
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Step 4: Results */}
      {step === 4 && result && (
        <div className="space-y-6">
          {/* Score hero */}
          <Card className="relative overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 w-2"
              style={{ backgroundColor: result.cor }}
            />
            <CardContent className="p-6">
              <div className="flex flex-col items-center gap-4 sm:flex-row">
                <div
                  className="flex h-20 w-20 items-center justify-center rounded-full text-2xl font-bold text-white font-tabular"
                  style={{ backgroundColor: result.cor }}
                >
                  {fmtPct(result.conformidade_nao_ponderada * 100)}
                </div>
                <div className="text-center sm:text-left">
                  <h2 className="text-xl font-bold font-heading">
                    {result.classificacao}
                  </h2>
                  <p className="text-sm text-muted-foreground">{result.descricao}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* KPI cards */}
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <ResultKPI
              icon={CheckCircle2}
              label="Atende"
              value={result.atende}
              color="text-success"
            />
            <ResultKPI
              icon={AlertTriangle}
              label="Atende Parcialmente"
              value={result.atende_parcial}
              color="text-warning"
            />
            <ResultKPI
              icon={XCircle}
              label="Não Atende"
              value={result.nao_atende}
              color="text-danger"
            />
            <ResultKPI
              icon={FileText}
              label="Não Aplica"
              value={result.nao_aplica}
              color="text-muted-foreground"
            />
          </div>

          {/* Recommendations */}
          {result.recomendacoes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 font-heading">
                  <AlertTriangle className="h-4 w-4 text-brand-orange" />
                  Recomendações ({result.recomendacoes.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.recomendacoes.map((rec, i) => (
                  <div
                    key={i}
                    className="rounded-lg border p-3"
                  >
                    <div className="flex items-start gap-3">
                      <Badge
                        variant={
                          rec.prioridade === "Alta" ? "destructive" : "secondary"
                        }
                        className="mt-0.5 shrink-0"
                      >
                        {rec.prioridade}
                      </Badge>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">{rec.tipo}</p>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                          {rec.documento} · {rec.topico}
                        </p>
                        <p className="mt-1 text-sm">{rec.teste}</p>
                        {rec.evidencia && (
                          <p className="mt-1 text-xs text-muted-foreground italic">
                            Evidência esperada: {rec.evidencia}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Start over */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              onClick={() => {
                setStep(1);
                setSelectedLicense("");
                setDocuments(null);
                setDocStatus({});
                setRequirements([]);
                setEvaluations({});
                setResult(null);
              }}
            >
              Nova Avaliação
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

function ResultKPI({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: typeof CheckCircle2;
  label: string;
  value: number;
  color: string;
}) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <Icon className={`h-5 w-5 ${color}`} />
        <div>
          <p className="text-2xl font-bold font-heading font-tabular">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
