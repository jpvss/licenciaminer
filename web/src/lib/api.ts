const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

/* ── Overview ── */

interface RawOverviewStats {
  mg_summary: {
    total_decisoes: number;
    deferidos: number;
    indeferidos: number;
    outros: number;
    taxa_aprovacao_geral: number;
  };
  mining_summary: {
    total_decisoes: number;
    deferidos: number;
    indeferidos: number;
    arquivamentos: number;
    outros: number;
    taxa_aprovacao_mineracao: number;
  };
  ibama_summary: {
    total_licencas: number;
    tipos_distintos: number;
  };
  anm_summary: {
    total_processos: number;
    ufs_distintas: number;
    fases_distintas: number;
    area_total_ha: number;
  };
}

export interface OverviewStats {
  total_decisoes: number;
  deferidos: number;
  indeferidos: number;
  taxa_aprovacao: number;
  total_infracoes: number;
  total_processos_anm: number;
  taxa_aprovacao_mineracao: number;
  total_decisoes_mineracao: number;
}

export interface TrendPoint {
  ano: string;
  deferidos: number;
  total: number;
  taxa_aprovacao: number;
}

export async function fetchOverviewStats(): Promise<OverviewStats> {
  const raw = await apiFetch<RawOverviewStats>("/overview/stats");
  return {
    total_decisoes: raw.mg_summary.total_decisoes,
    deferidos: raw.mg_summary.deferidos,
    indeferidos: raw.mg_summary.indeferidos,
    taxa_aprovacao: raw.mining_summary.taxa_aprovacao_mineracao,
    total_infracoes: raw.ibama_summary.total_licencas,
    total_processos_anm: raw.anm_summary.total_processos,
    taxa_aprovacao_mineracao: raw.mining_summary.taxa_aprovacao_mineracao,
    total_decisoes_mineracao: raw.mining_summary.total_decisoes,
  };
}

export function fetchOverviewTrend() {
  return apiFetch<TrendPoint[]>("/overview/trend");
}

/* ── Empresa ── */

export interface EmpresaProfile {
  cnpj: string;
  profile: {
    razao_social: string;
    cnae_fiscal: string;
    cnae_descricao: string;
    porte: string;
    data_abertura: string;
    situacao: string;
    total_decisoes: number;
    deferidos: number;
    indeferidos: number;
    arquivamentos: number;
    taxa_aprovacao: number;
  } | null;
  infracoes: {
    total_infracoes: number;
    anos_com_infracao: number;
  };
  cfem: {
    meses_pagamento: number;
    total_pago: number;
  };
}

export interface Decision {
  processo: string;
  atividade: string;
  classe: number;
  modalidade: string;
  decisao: string;
  data_decisao: string;
  municipio: string;
}

export function fetchEmpresa(cnpj: string) {
  return apiFetch<EmpresaProfile>(`/empresa/${cnpj}`);
}

export function fetchEmpresaDecisions(cnpj: string) {
  return apiFetch<Decision[]>(`/empresa/${cnpj}/decisions`);
}

/* ── Report ── */

export interface ReportData {
  cnpj: string;
  razao_social: string;
  risk_level: string;
  findings: string[];
  taxa_aprovacao: number;
  total_decisoes: number;
  total_infracoes: number;
  cfem_total_pago: number;
  cfem_meses_pagamento: number;
  decisoes: Decision[];
  casos_similares: Record<string, unknown>[];
}

export function fetchReportData(cnpj: string) {
  return apiFetch<ReportData>(`/report/${cnpj}/data`);
}

/* ── Rankings ── */

export function fetchEmpresasRanking() {
  return apiFetch<Record<string, unknown>[]>("/empresas/ranking");
}

/* ── Decisions analytics ── */

export function fetchApprovalRates() {
  return apiFetch<Record<string, unknown>[]>("/decisions/approval-rates");
}

export function fetchDecisionsByModalidade() {
  return apiFetch<Record<string, unknown>[]>("/decisions/by-modalidade");
}

/* ── Decisions analytics ── */

export interface ApprovalRate {
  ano: number;
  classe: number;
  atividade: string;
  regional: string;
  total: number;
  deferidos: number;
  indeferidos: number;
  taxa_aprovacao: number;
}

export interface ModalidadeBreakdown {
  modalidade: string;
  decisao: string;
  n: number;
}

export interface RejectionTrend {
  ano: number;
  total: number;
  deferidos: number;
  indeferidos: number;
  arquivamentos: number;
  taxa_indeferimento: number;
  taxa_arquivamento: number;
}

export interface RegionalRigor {
  regional: string;
  total: number;
  deferidos: number;
  indeferidos: number;
  taxa_aprovacao: number;
  taxa_indeferimento: number;
}

export function fetchRejectionTrend() {
  return apiFetch<RejectionTrend[]>("/decisions/rejection-trend");
}

export function fetchRegionalRigor() {
  return apiFetch<RegionalRigor[]>("/decisions/regional-rigor");
}

/* ── Due Diligence ── */

export interface LicenseType {
  code: string;
  description: string;
}

export interface DDDocument {
  documento: string;
  modalidade: string;
  licenca: string;
  descricao: string;
}

export interface DDRequirement {
  requisito_id: string;
  documento: string;
  topico: string;
  teste_aderencia: string;
  evidencia_esperada: string;
}

export interface DDScoreResult {
  total_requisitos: number;
  requisitos_aplicaveis: number;
  atende: number;
  atende_parcial: number;
  nao_atende: number;
  nao_aplica: number;
  conformidade_nao_ponderada: number;
  conformidade_ponderada: number;
  nota_maxima: number;
  nota_obtida: number;
  classificacao: string;
  cor: string;
  descricao: string;
  checklist?: Record<string, unknown>;
  recomendacoes: {
    requisito_id: string;
    tipo: string;
    prioridade: string;
    documento: string;
    topico: string;
    teste: string;
    evidencia: string;
  }[];
}

export function fetchLicenseTypes() {
  return apiFetch<LicenseType[]>("/due-diligence/license-types");
}

export function fetchDDDocuments(licencaTipo: string) {
  return apiFetch<{ licenca_tipo: string; total: number; documents: DDDocument[] }>(
    `/due-diligence/documents?licenca_tipo=${encodeURIComponent(licencaTipo)}`
  );
}

export function fetchDDRequirements(documento: string) {
  return apiFetch<{ documento: string; total: number; requirements: DDRequirement[] }>(
    `/due-diligence/requirements?documento=${encodeURIComponent(documento)}`
  );
}

export function submitDDScore(payload: {
  avaliacoes: Record<string, string>;
  pesos?: Record<string, number>;
  doc_status?: Record<string, string>;
}) {
  return apiFetch<DDScoreResult>("/due-diligence/score", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/* ── Explorer / Concessões ── */

export interface ExplorerResponse {
  dataset: string;
  total: number;
  limit: number;
  offset: number;
  rows: Record<string, unknown>[];
}

export function fetchExplorerDatasets() {
  return apiFetch<Record<string, string>>("/explorer/datasets");
}

export function fetchExplorerData(
  dataset: string,
  params?: { limit?: number; offset?: number; decisao?: string; classe?: number; ano_min?: number; ano_max?: number }
) {
  const qs = new URLSearchParams();
  if (params?.limit) qs.set("limit", String(params.limit));
  if (params?.offset) qs.set("offset", String(params.offset));
  if (params?.decisao) qs.set("decisao", params.decisao);
  if (params?.classe) qs.set("classe", String(params.classe));
  if (params?.ano_min) qs.set("ano_min", String(params.ano_min));
  if (params?.ano_max) qs.set("ano_max", String(params.ano_max));
  const q = qs.toString();
  return apiFetch<ExplorerResponse>(`/explorer/${dataset}${q ? `?${q}` : ""}`);
}

/* ── LLM Chat ── */

export function streamChat(
  messages: { role: string; content: string }[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<void> {
  return fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal,
  }).then(async (res) => {
    if (!res.ok) throw new Error(`Chat API ${res.status}`);
    const reader = res.body?.getReader();
    if (!reader) return;
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });
      for (const line of chunk.split("\n")) {
        if (line.startsWith("data: ") && line !== "data: [DONE]") {
          onChunk(line.slice(6));
        }
      }
    }
  });
}

/* ── Formatting helpers ── */

export function fmtReais(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value);
}

export function fmtPct(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function fmtNumber(value: number): string {
  return new Intl.NumberFormat("pt-BR").format(value);
}
