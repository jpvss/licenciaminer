/** Tipos do sistema Mineradora Modelo — cadeia de valor com IA. */

/** Etapa do mapa de atividades */
export interface ActivityStep {
  id: string;
  nome: string;
  descricao: string;
  status: "ok" | "gargalo" | "oportunidade";
  detalhes: string;
  kpisAfetados: string[];
}

/** Categoria de caso de uso de IA */
export type AICategory =
  | "computer-vision"
  | "predictive"
  | "optimization"
  | "nlp"
  | "automation"
  | "digital-twin";

/** Caso de uso de IA */
export interface AIUseCase {
  id: string;
  titulo: string;
  descricao: string;
  categoria: AICategory;
  roiEstimativa: string;
  complexidade: "baixa" | "media" | "alta";
  tempoValor: string;
  prerequisitos: string[];
  kpisAfetados: string[];
  exemplosReais: string[];
}

/** Nivel de maturidade digital */
export interface MaturityLevel {
  nivel: 1 | 2 | 3 | 4 | 5;
  nome: string;
  descricao: string;
  criterios: string[];
}

/** Fase do roadmap de implementacao */
export interface RoadmapPhase {
  fase: number;
  titulo: string;
  duracao: string;
  entregas: string[];
  dependencias: string[];
}

/** Projecao de melhoria com IA para um KPI */
export interface AIProjection {
  kpiNome: string;
  melhoriaEstimada: string;
  descricao: string;
}

/** Conteudo completo de um modulo da cadeia de valor */
export interface MiningModule {
  key: string;
  nome: string;
  descricao: string;
  cor: string;
  atividades: ActivityStep[];
  casosIA: AIUseCase[];
  maturidade: {
    nivelAtual: 1 | 2 | 3 | 4 | 5;
    niveis: MaturityLevel[];
  };
  roadmap: RoadmapPhase[];
  projecoesIA: AIProjection[];
}

/** Labels das categorias de IA */
export const AI_CATEGORY_LABELS: Record<AICategory, string> = {
  "computer-vision": "Computer Vision",
  predictive: "Analítica Preditiva",
  optimization: "Otimização",
  nlp: "NLP",
  automation: "Automação",
  "digital-twin": "Digital Twin",
};
