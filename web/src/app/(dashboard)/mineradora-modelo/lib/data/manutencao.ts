import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const manutencaoModule: MiningModule = {
  key: "manutencao",
  nome: "Manutenção",
  descricao:
    "Gestão de ativos e manutenção da frota e equipamentos de planta. Manutenção reativa ainda domina — a maior oportunidade de transformação digital na maioria das mineradoras.",
  cor: "var(--chart-4)",
  atividades: [
    {
      id: "mn-planejamento",
      nome: "Planejamento",
      descricao: "Programação de paradas e ordens de serviço.",
      status: "gargalo",
      detalhes:
        "Backlog de OS frequentemente desorganizado. Priorização baseada em urgência, não em criticidade. Planejamento de paradas com pouca antecedência. CMMS subutilizado.",
      kpisAfetados: ["Disponibilidade Física", "MTBF"],
    },
    {
      id: "mn-preventiva",
      nome: "Preventiva",
      descricao: "Manutenção programada baseada em tempo/horímetro.",
      status: "ok",
      detalhes:
        "Trocas de óleo, filtros e componentes por horímetro. Efetiva para itens com desgaste previsível, mas causa over-maintenance em componentes ainda saudáveis.",
      kpisAfetados: ["Custo por Tonelada", "Disponibilidade Física"],
    },
    {
      id: "mn-preditiva",
      nome: "Preditiva",
      descricao: "Monitoramento de condição com sensores (vibração, temperatura, óleo).",
      status: "oportunidade",
      detalhes:
        "Pouca adoção: <20% dos equipamentos monitorados. Quando implantada, reduz manutenção não planejada em 30-50%. IoT + ML pode estender vida útil de componentes e prever falhas com semanas de antecedência.",
      kpisAfetados: ["MTBF", "MTTR", "Disponibilidade Física", "Custo por Tonelada"],
    },
    {
      id: "mn-corretiva",
      nome: "Corretiva",
      descricao: "Reparo após falha — a mais cara e disruptiva.",
      status: "gargalo",
      detalhes:
        "Ainda representa >50% das intervenções. Cada hora de caminhão parado custa ~R$5.000 em produção perdida. Diagnóstico lento por falta de histórico organizado. Peças nem sempre disponíveis.",
      kpisAfetados: ["MTTR", "Disponibilidade Física", "Custo por Tonelada"],
    },
    {
      id: "mn-analise",
      nome: "Análise de Falhas",
      descricao: "RCA (Root Cause Analysis) e melhoria contínua.",
      status: "oportunidade",
      detalhes:
        "RCAs feitas de forma ad-hoc, sem banco de dados estruturado. Lições aprendidas não são disseminadas. NLP pode extrair padrões de falha de OS históricas e sugerir ações preventivas.",
      kpisAfetados: ["MTBF", "Custo por Tonelada"],
    },
  ],
  casosIA: [
    {
      id: "mn-ia-preditiva",
      titulo: "Manutenção Preditiva com IoT + ML",
      descricao:
        "Sensores de vibração, temperatura e análise de óleo conectados a modelos ML para prever falhas com semanas de antecedência. Gera OS automática no CMMS quando detecta anomalia.",
      categoria: "predictive",
      roiEstimativa: "-30-50% downtime não planejado",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Sensores IoT em equipamentos críticos",
        "CMMS operacional (SAP PM, Maximo)",
        "Conectividade na oficina e cava",
      ],
      kpisAfetados: ["MTBF", "Disponibilidade Física", "Custo por Tonelada"],
      exemplosReais: [
        "Nanoprecise — manutenção preditiva para mineração",
        "Caterpillar Cat Connect — telemática e diagnóstico",
        "Augury — diagnóstico de máquinas com IA",
      ],
    },
    {
      id: "mn-ia-rul",
      titulo: "Estimativa de Vida Útil Remanescente (RUL)",
      descricao:
        "Modelos LSTM/CNN para estimar remaining useful life de componentes críticos (motor, transmissão, cilindros). Permite substituição just-in-time, nem antes nem depois.",
      categoria: "predictive",
      roiEstimativa: "-20-40% custo de manutenção",
      complexidade: "alta",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Dados históricos de falha por componente (>2 anos)",
        "Sensores de condição instalados",
        "Mapeamento de modos de falha (FMEA)",
      ],
      kpisAfetados: ["MTBF", "Custo por Tonelada"],
      exemplosReais: [
        "Komatsu KOMTRAX — monitoramento remoto",
        "Intangles — plataforma de RUL para frotas",
      ],
    },
    {
      id: "mn-ia-nlp",
      titulo: "NLP para Análise de Ordens de Serviço",
      descricao:
        "Processamento de linguagem natural para extrair padrões de falha, causas raiz recorrentes e sugestões de ação de milhares de OS históricas escritas em texto livre.",
      categoria: "nlp",
      roiEstimativa: "-20% MTTR",
      complexidade: "baixa",
      tempoValor: "2-4 meses",
      prerequisitos: [
        "CMMS com histórico de OS > 12 meses",
        "OS com descrição textual (não apenas códigos)",
      ],
      kpisAfetados: ["MTTR", "MTBF"],
      exemplosReais: [
        "LLMs para análise de texto técnico de manutenção",
        "Soluções RAG sobre base de conhecimento de manutenção",
      ],
    },
    {
      id: "mn-ia-pecas",
      titulo: "Otimização de Estoque de Peças",
      descricao:
        "ML para prever demanda de peças de reposição baseado em previsão de falhas e plano de manutenção. Reduz estoque morto e garante disponibilidade de peças críticas.",
      categoria: "optimization",
      roiEstimativa: "-15-25% estoque de peças",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "ERP com histórico de consumo de peças",
        "Integração com modelo preditivo",
        "Classificação ABC de criticidade de peças",
      ],
      kpisAfetados: ["Custo por Tonelada", "MTTR"],
      exemplosReais: [
        "SAP IBP — planejamento de demanda com ML",
        "Caterpillar Parts.cat.com — plataforma preditiva de peças",
      ],
    },
    {
      id: "mn-ia-pneus",
      titulo: "Gestão Inteligente de Pneus",
      descricao:
        "IoT (TPMS) + ML para monitorar pressão, temperatura e desgaste de pneus OTR em tempo real. Otimiza rotação, detecta danos precoces e estende vida útil.",
      categoria: "predictive",
      roiEstimativa: "+10-20% vida útil de pneus",
      complexidade: "baixa",
      tempoValor: "2-4 meses",
      prerequisitos: [
        "TPMS (Tire Pressure Monitoring System) instalado",
        "Conectividade para dados em tempo real",
      ],
      kpisAfetados: ["Custo por Tonelada"],
      exemplosReais: [
        "Bridgestone iTrack — monitoramento de pneus OTR",
        "Michelin MEMS — sistema de gestão de pneus",
      ],
    },
  ],
  maturidade: {
    nivelAtual: 1,
    niveis: MATURITY_SCALE,
  },
  roadmap: [
    {
      fase: 1,
      titulo: "Diagnóstico",
      duracao: "4-6 semanas",
      entregas: [
        "Análise de backlog de OS e padrões de falha",
        "Mapeamento de equipamentos críticos (Pareto 80/20)",
        "Avaliação do CMMS e qualidade de dados",
        "Identificação de quick wins (NLP em OS, gestão de pneus)",
        "Relatório com roadmap de manutenção preditiva",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "8-12 semanas",
      entregas: [
        "NLP para análise de OS históricas",
        "Sensores IoT em 5 equipamentos mais críticos",
        "Modelo preditivo para 1 modo de falha principal",
        "Dashboard de manutenção preditiva",
      ],
      dependencias: ["Diagnóstico concluído", "IoT em equipamentos-piloto"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "6-18 meses",
      entregas: [
        "Preditiva em todos os equipamentos críticos",
        "Integração CMMS-ML para OS automática",
        "Otimização de estoque de peças com previsão de demanda",
        "Cultura de manutenção baseada em condição",
      ],
      dependencias: ["Piloto validado", "IoT em toda frota crítica"],
    },
  ],
  projecoesIA: [
    { kpiNome: "MTBF", melhoriaEstimada: "+40%", descricao: "com manutenção preditiva" },
    { kpiNome: "MTTR", melhoriaEstimada: "-25%", descricao: "com NLP + diagnóstico IA" },
    { kpiNome: "Disponibilidade Física", melhoriaEstimada: "+5pp", descricao: "com predição de falhas" },
    { kpiNome: "Custo por Tonelada", melhoriaEstimada: "-20%", descricao: "com otimização de peças" },
  ],
};
