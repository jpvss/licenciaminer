"use client";

import { useEffect, useState, useMemo } from "react";
import {
  ShieldCheck,
  ChevronRight,
  ChevronLeft,
  ChevronDown,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Download,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
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
  downloadReportPDF,
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

const ATIVIDADES = [
  { code: "A-01", label: "Pesquisa Mineral" },
  { code: "A-02", label: "Lavra a Céu Aberto" },
  { code: "A-03", label: "Lavra Subterrânea" },
  { code: "A-04", label: "Dragagem / Água Mineral" },
  { code: "A-05", label: "Beneficiamento" },
  { code: "A-06", label: "Pilha de Estéril / Barragem" },
  { code: "A-07", label: "Infraestrutura de Mineração" },
];

const CLASSES = [1, 2, 3, 4, 5, 6] as const;

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
  const [selectedAtividade, setSelectedAtividade] = useState("A-02");
  const [selectedClasse, setSelectedClasse] = useState("4");
  const [cnpj, setCnpj] = useState("");

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
  const [pdfLoading, setPdfLoading] = useState(false);

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
            <div className="grid gap-4 sm:grid-cols-2">
              {/* Left column */}
              <div className="space-y-4">
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

                <div>
                  <label className="mb-1 block text-sm font-medium">
                    Atividade
                  </label>
                  <Select value={selectedAtividade} onValueChange={setSelectedAtividade}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ATIVIDADES.map((a) => (
                        <SelectItem key={a.code} value={a.code}>
                          <span className="font-medium">{a.code}</span>
                          <span className="ml-2 text-muted-foreground">
                            — {a.label}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Código de atividade minerária (DN COPAM 217/2017)
                  </p>
                </div>
              </div>

              {/* Right column */}
              <div className="space-y-4">
                <div>
                  <label className="mb-1 block text-sm font-medium">
                    Classe Ambiental
                  </label>
                  <Select value={selectedClasse} onValueChange={setSelectedClasse}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {CLASSES.map((c) => (
                        <SelectItem key={c} value={String(c)}>
                          Classe {c}
                          <span className="ml-2 text-muted-foreground">
                            {c === 1 ? "— Impacto mínimo" : c === 6 ? "— Impacto máximo" : ""}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="mt-1 text-xs text-muted-foreground">
                    Classe de impacto ambiental (1 = mínimo, 6 = máximo)
                  </p>
                </div>

                <div>
                  <label className="mb-1 block text-sm font-medium">
                    CNPJ do Empreendedor
                    <span className="ml-1 text-xs font-normal text-muted-foreground">(opcional)</span>
                  </label>
                  <Input
                    placeholder="00.000.000/0000-00"
                    value={cnpj}
                    onChange={(e) => setCnpj(e.target.value)}
                  />
                  <p className="mt-1 text-xs text-muted-foreground">
                    Se informado, o relatório incluirá dados históricos da empresa
                  </p>
                </div>
              </div>
            </div>

            {/* Document preview */}
            {selectedLicense && documents && documents.length > 0 && (
              <div className="rounded-lg border bg-muted/30 p-4">
                <p className="text-sm font-medium">
                  <span className="font-tabular">{documents.length}</span> documentos aplicáveis
                  para {selectedLicense} (Classe {selectedClasse})
                </p>
                <Collapsible>
                  <CollapsibleTrigger asChild>
                    <Button variant="link" size="sm" className="mt-1 h-auto p-0 text-xs">
                      <ChevronDown className="mr-1 h-3 w-3" />
                      Ver lista de documentos
                    </Button>
                  </CollapsibleTrigger>
                  <CollapsibleContent>
                    <ol className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {documents.map((doc, i) => (
                        <li key={doc.documento}>
                          <span className="text-muted-foreground/60">{i + 1}.</span>{" "}
                          <span className="font-medium text-foreground">{doc.documento}</span>
                          {doc.descricao && (
                            <span className="ml-1">({doc.descricao})</span>
                          )}
                        </li>
                      ))}
                    </ol>
                  </CollapsibleContent>
                </Collapsible>
              </div>
            )}

            {loadingDocs && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Carregando documentos...
              </div>
            )}

            <p className="text-xs text-muted-foreground">
              A seleção do tipo de licença determina quais documentos e requisitos de teste
              serão aplicáveis na avaliação de conformidade.
            </p>

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
          {/* Config summary */}
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
            <span><strong>Licença:</strong> {selectedLicense}</span>
            <span><strong>Atividade:</strong> {selectedAtividade} — {ATIVIDADES.find((a) => a.code === selectedAtividade)?.label}</span>
            <span><strong>Classe:</strong> {selectedClasse}</span>
          </div>

          {/* Score hero with gauge */}
          <Card className="relative overflow-hidden">
            <div
              className="absolute inset-y-0 left-0 w-2"
              style={{ backgroundColor: result.cor }}
            />
            <CardContent className="p-6">
              <div className="flex flex-col items-center gap-6 sm:flex-row">
                <ConformityGauge
                  score={result.conformidade_nao_ponderada * 100}
                  color={result.cor}
                />
                <div className="flex-1 text-center sm:text-left">
                  <h2 className="text-xl font-bold font-heading">
                    {result.classificacao}
                  </h2>
                  <p className="text-sm text-muted-foreground">{result.descricao}</p>
                  <div className="mt-3 flex flex-wrap gap-4 text-xs">
                    <span>Requisitos avaliados: <strong className="font-tabular">{result.requisitos_aplicaveis}</strong></span>
                    <span>Documentos: <strong className="font-tabular">{documents?.length ?? 0}</strong></span>
                  </div>
                </div>
                <div className="flex flex-col gap-2">
                  {cnpj && (
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pdfLoading}
                      onClick={async () => {
                        setPdfLoading(true);
                        try {
                          await downloadReportPDF(cnpj.replace(/\D/g, ""));
                        } catch {
                          // PDF generation may not be available
                        } finally {
                          setPdfLoading(false);
                        }
                      }}
                    >
                      {pdfLoading ? (
                        <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Download className="mr-2 h-3.5 w-3.5" />
                      )}
                      Relatório PDF
                    </Button>
                  )}
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
                setSelectedAtividade("A-02");
                setSelectedClasse("4");
                setCnpj("");
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

function ConformityGauge({ score, color }: { score: number; color: string }) {
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (Math.min(score, 100) / 100) * circumference;

  return (
    <div className="relative flex h-28 w-28 shrink-0 items-center justify-center">
      <svg className="h-28 w-28 -rotate-90" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          className="text-muted/40"
        />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold font-tabular" style={{ color }}>
          {fmtPct(score)}
        </span>
        <span className="text-[10px] text-muted-foreground">Conformidade</span>
      </div>
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
