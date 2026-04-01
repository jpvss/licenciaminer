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
  detail_id?: string | number;
  [key: string]: unknown;
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

export interface InfractionBand {
  faixa_infracoes: string;
  total: number;
  deferidos: number;
  indeferidos: number;
  taxa_aprovacao: number;
}

export interface InfractionsVsApproval {
  total_infracoes: number;
  total_decisoes: number;
  deferidos: number;
  taxa_aprovacao: number;
}

export interface ClassModalidade {
  classe: number;
  modalidade: string;
  total: number;
  deferidos: number;
  taxa_aprovacao: number;
}

export function fetchInfractionBands() {
  return apiFetch<InfractionBand[]>("/decisions/infraction-bands");
}

export function fetchInfractionsVsApproval() {
  return apiFetch<InfractionsVsApproval[]>("/decisions/infractions-vs-approval");
}

export function fetchClassModalidade() {
  return apiFetch<ClassModalidade[]>("/decisions/class-modalidade");
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

/* ── Explorer ── */

export interface ExplorerResponse {
  dataset: string;
  total: number;
  limit: number;
  offset: number;
  rows: Record<string, unknown>[];
}

export interface ExplorerFilters {
  limit?: number;
  offset?: number;
  search?: string;
  decisao?: string;
  classe?: number;
  ano_min?: number;
  ano_max?: number;
  mining_only?: boolean;
}

export interface RecordText {
  text: string;
  truncated: boolean;
  total_length: number;
}

export function fetchExplorerDatasets() {
  return apiFetch<Record<string, string>>("/explorer/datasets");
}

export function fetchExplorerData(dataset: string, params?: ExplorerFilters) {
  const qs = new URLSearchParams();
  if (params?.limit) qs.set("limit", String(params.limit));
  if (params?.offset) qs.set("offset", String(params.offset));
  if (params?.search) qs.set("search", params.search);
  if (params?.decisao) qs.set("decisao", params.decisao);
  if (params?.classe) qs.set("classe", String(params.classe));
  if (params?.ano_min) qs.set("ano_min", String(params.ano_min));
  if (params?.ano_max) qs.set("ano_max", String(params.ano_max));
  if (params?.mining_only) qs.set("mining_only", "true");
  const q = qs.toString();
  return apiFetch<ExplorerResponse>(`/explorer/${dataset}${q ? `?${q}` : ""}`);
}

export function fetchExplorerRecord(dataset: string, recordId: string) {
  return apiFetch<Record<string, unknown>>(
    `/explorer/${dataset}/record/${encodeURIComponent(recordId)}`
  );
}

export function fetchExplorerRecordText(dataset: string, recordId: string) {
  return apiFetch<RecordText>(
    `/explorer/${dataset}/record/${encodeURIComponent(recordId)}/text`
  );
}

export function explorerExportUrl(dataset: string, params?: ExplorerFilters): string {
  const qs = new URLSearchParams();
  if (params?.search) qs.set("search", params.search);
  if (params?.decisao) qs.set("decisao", params.decisao);
  if (params?.classe) qs.set("classe", String(params.classe));
  if (params?.ano_min) qs.set("ano_min", String(params.ano_min));
  if (params?.ano_max) qs.set("ano_max", String(params.ano_max));
  if (params?.mining_only) qs.set("mining_only", "true");
  const q = qs.toString();
  return `${API_BASE}/explorer/${dataset}/export.csv${q ? `?${q}` : ""}`;
}

/* ── Empresa ANM ── */

export interface ANMTitulo {
  PROCESSO: string;
  FASE: string;
  SUBS: string;
  AREA_HA: number;
  ANO: number;
  UF: string;
}

export function fetchEmpresaANM(cnpj: string) {
  return apiFetch<{ titular: string; total: number; titulos: ANMTitulo[] }>(
    `/empresa/${cnpj}/anm`
  );
}

/* ── Report PDF ── */

export async function downloadReportPDF(cnpj: string): Promise<void> {
  const res = await fetch(`${API_BASE}/report/${cnpj}/download-sync`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Erro ao gerar relatório: ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `relatorio_${cnpj}_${new Date().toISOString().slice(0, 10)}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
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

/* ── Concessões ── */

export interface ConcessoesFilters {
  search?: string;
  regime?: string[];
  categoria?: string[];
  substancia?: string[];
  municipio?: string[];
  cfem_status?: "ativo" | "inativo";
  estrategico?: boolean;
  limit?: number;
  offset?: number;
}

export interface ConcessoesStats {
  total: number;
  cfem_ativas: number | null;
  substancias: number;
  municipios: number;
}

export interface ConcessoesFilterOptions {
  regimes: string[];
  categorias: string[];
  substancias: string[];
  municipios: string[];
  regime_labels: Record<string, string>;
  view: string;
}

export interface ConcessoesResponse {
  view: string;
  total: number;
  limit: number;
  offset: number;
  regime_labels: Record<string, string>;
  rows: Record<string, unknown>[];
}

function concessoesQS(params?: ConcessoesFilters): string {
  if (!params) return "";
  const qs = new URLSearchParams();
  if (params.search) qs.set("search", params.search);
  params.regime?.forEach((v) => qs.append("regime", v));
  params.categoria?.forEach((v) => qs.append("categoria", v));
  params.substancia?.forEach((v) => qs.append("substancia", v));
  params.municipio?.forEach((v) => qs.append("municipio", v));
  if (params.cfem_status) qs.set("cfem_status", params.cfem_status);
  if (params.estrategico != null) qs.set("estrategico", String(params.estrategico));
  if (params.limit) qs.set("limit", String(params.limit));
  if (params.offset) qs.set("offset", String(params.offset));
  const q = qs.toString();
  return q ? `?${q}` : "";
}

export function fetchConcessoesFilters() {
  return apiFetch<ConcessoesFilterOptions>("/concessoes/filters");
}

export function fetchConcessoesStats(params?: ConcessoesFilters) {
  return apiFetch<ConcessoesStats>(`/concessoes/stats${concessoesQS(params)}`);
}

export function fetchConcessoes(params?: ConcessoesFilters) {
  return apiFetch<ConcessoesResponse>(`/concessoes${concessoesQS(params)}`);
}

export function fetchConcessaoDetail(processo: string) {
  return apiFetch<Record<string, unknown>>(`/concessoes/${encodeURIComponent(processo)}`);
}

/* ── Prospecção ── */

export interface ProspeccaoFilters {
  min_score?: number;
  regime?: string[];
  categoria?: string[];
  estrategico?: boolean;
  limit?: number;
  offset?: number;
}

export interface ProspeccaoOpportunity {
  processo_norm: string;
  regime: string;
  titular: string;
  substancia_principal: string;
  municipio_principal: string;
  categoria: string;
  AREA_HA: number;
  ativo_cfem: boolean;
  cfem_total: number;
  estrategico: string;
  score: number;
  motivo: string;
}

export interface ProspeccaoResponse {
  total: number;
  limit: number;
  offset: number;
  stats: {
    total: number;
    avg_score: number;
    strategic_count: number;
    total_area: number;
  };
  rows: ProspeccaoOpportunity[];
}

export interface EmpresaPortfolio {
  titular: string;
  total_concessoes: number;
  substancias_distintas: number;
  ativas_cfem: number;
  inativas: number;
  cfem_total: number;
  area_total: number;
}

export interface MunicipioConcentration {
  municipio: string;
  substancia: string;
  concessoes: number;
  ativas: number;
  area_total: number;
  cfem_total: number;
}

function prospeccaoQS(params?: ProspeccaoFilters): string {
  if (!params) return "";
  const qs = new URLSearchParams();
  if (params.min_score != null) qs.set("min_score", String(params.min_score));
  params.regime?.forEach((v) => qs.append("regime", v));
  params.categoria?.forEach((v) => qs.append("categoria", v));
  if (params.estrategico != null) qs.set("estrategico", String(params.estrategico));
  if (params.limit) qs.set("limit", String(params.limit));
  if (params.offset) qs.set("offset", String(params.offset));
  const q = qs.toString();
  return q ? `?${q}` : "";
}

export function fetchOpportunities(params?: ProspeccaoFilters) {
  return apiFetch<ProspeccaoResponse>(`/prospeccao/opportunities${prospeccaoQS(params)}`);
}

export function fetchEmpresaPortfolios() {
  return apiFetch<{ stats: Record<string, unknown>; rows: EmpresaPortfolio[] }>("/prospeccao/empresas");
}

export function fetchMunicipioConcentration() {
  return apiFetch<{ total: number; rows: MunicipioConcentration[] }>("/prospeccao/municipios");
}

export function fetchScoreBreakdown() {
  return apiFetch<{ max_score: number; criteria: { criterion: string; points: number }[] }>("/prospeccao/score-breakdown");
}

/* ── Geospatial ── */

export interface GeoConcessoesResponse {
  total: number;
  returned: number;
  truncated: boolean;
  enriched: boolean;
  geojson: GeoJSON.FeatureCollection;
}

export interface GeoStats {
  total_polygons: number;
  total_all: number;
  enriched: boolean;
  enriched_count?: number;
  distinct_substances?: number;
  total_area_ha?: number;
}

export interface GeoFilterOptions {
  options: {
    regimes: string[];
    categorias: string[];
    substancias: string[];
    fases?: string[];
  };
  color_palettes: {
    categoria: Record<string, string>;
    regime: Record<string, string>;
    fase: Record<string, string>;
  };
}

function geoQS(params?: {
  regime?: string[];
  categoria?: string[];
  substancia?: string[];
  cfem_status?: string;
  estrategico?: boolean;
  limit?: number;
}): string {
  if (!params) return "";
  const qs = new URLSearchParams();
  params.regime?.forEach((v) => qs.append("regime", v));
  params.categoria?.forEach((v) => qs.append("categoria", v));
  params.substancia?.forEach((v) => qs.append("substancia", v));
  if (params.cfem_status) qs.set("cfem_status", params.cfem_status);
  if (params.estrategico != null) qs.set("estrategico", String(params.estrategico));
  if (params.limit) qs.set("limit", String(params.limit));
  const q = qs.toString();
  return q ? `?${q}` : "";
}

export function fetchGeoConcessoes(params?: Parameters<typeof geoQS>[0]) {
  return apiFetch<GeoConcessoesResponse>(`/geo/concessoes${geoQS(params)}`);
}

export function fetchGeoStats(params?: Parameters<typeof geoQS>[0]) {
  return apiFetch<GeoStats>(`/geo/concessoes/stats${geoQS(params)}`);
}

export function fetchGeoFilters() {
  return apiFetch<GeoFilterOptions>("/geo/concessoes/filters");
}

export function fetchGeoLayer(layer: "ucs" | "tis") {
  return apiFetch<GeoJSON.FeatureCollection>(`/geo/layers/${layer}`);
}

/* ── Formatting re-exports (canonical source: lib/format.ts) ── */

export { fmtReais, fmtPct, fmtBR as fmtNumber } from "./format";
