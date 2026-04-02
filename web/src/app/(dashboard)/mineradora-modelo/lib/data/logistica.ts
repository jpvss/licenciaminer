import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const logisticaModule: MiningModule = {
  key: "logistica",
  nome: "Logística e Supply Chain",
  descricao:
    "Cadeia mina-ferrovia-porto: planejamento de demanda, gestão de estoque, transporte e embarque. Demurrage e lead time são os maiores destruidores de valor.",
  cor: "var(--brand-gold)",
  atividades: [
    {
      id: "lg-demanda",
      nome: "Planejamento de Demanda",
      descricao: "Previsão de vendas e programação de embarques.",
      status: "ok",
      detalhes:
        "Baseado em contratos de longo prazo e spot market. Variação de demanda por commodity e destino. Necessita integração com produção e estoque.",
      kpisAfetados: ["Giro de Estoque"],
    },
    {
      id: "lg-estoque",
      nome: "Gestão de Estoque",
      descricao: "Pilhas de estoque intermediário e no porto.",
      status: "oportunidade",
      detalhes:
        "Múltiplas pilhas com diferentes teores e granulometrias. Blending para atingir especificação de embarque. Gestão de lotes por rastreabilidade. ML pode otimizar blending para maximizar valor.",
      kpisAfetados: ["Giro de Estoque", "Lead Time Médio"],
    },
    {
      id: "lg-transporte",
      nome: "Transporte Mina-Porto",
      descricao: "Ferrovia ou rodovia da mina ao terminal portuário.",
      status: "gargalo",
      detalhes:
        "Ferrovia com capacidade limitada (slots de trem). Gargalo no pátio de descarga portuário. Coordenação entre produção, trem e navio é complexa. Qualquer atraso cascateia em demurrage.",
      kpisAfetados: ["Lead Time Médio", "Demurrage"],
    },
    {
      id: "lg-embarque",
      nome: "Embarque Portuário",
      descricao: "Carregamento de navios no terminal.",
      status: "gargalo",
      detalhes:
        "Demurrage de US$15-30k/dia/navio. Janela de atracação limitada. Condições climáticas (chuva, vento) causam paradas. Fila de navios no fundeadouro é custo puro.",
      kpisAfetados: ["Demurrage"],
    },
    {
      id: "lg-blending",
      nome: "Blending",
      descricao: "Mistura de lotes para atingir especificação de qualidade.",
      status: "oportunidade",
      detalhes:
        "Otimização de blending para minimizar custo e maximizar preço de venda. Restrições de teor (Fe, SiO2, Al2O3, P, Mn), umidade e granulometria. Problema combinatório ideal para otimização com IA.",
      kpisAfetados: ["Giro de Estoque"],
    },
  ],
  casosIA: [
    {
      id: "lg-ia-scheduling",
      titulo: "Scheduling Integrado Mina-Ferrovia-Porto",
      descricao:
        "RL + otimização para programar toda a cadeia logística de forma integrada: produção, trem, pátio e navio. Minimiza demurrage e maximiza utilização de capacidade.",
      categoria: "optimization",
      roiEstimativa: "-5% custo logístico, ROI em 3 meses",
      complexidade: "alta",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Visibilidade end-to-end (mina a porto)",
        "Dados de capacidade e restrições de cada elo",
        "Integração com operador logístico/ferrovia",
      ],
      kpisAfetados: ["Lead Time Médio", "Demurrage"],
      exemplosReais: [
        "BCG — scheduling para Rio Tinto (5x produtividade, ROI em 3 meses)",
        "SAP IBP — planejamento integrado de supply chain",
      ],
    },
    {
      id: "lg-ia-demurrage",
      titulo: "Predição de Demurrage com ML",
      descricao:
        "Modelo ML usando dados AIS (posição de navios), clima, fila no porto e produção para prever demurrage com 7-14 dias de antecedência. Permite ação corretiva proativa.",
      categoria: "predictive",
      roiEstimativa: "-15% demurrage",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Dados AIS de navios (MarineTraffic, VesselFinder)",
        "Histórico de demurrage > 12 meses",
        "Dados de produção e embarque diários",
      ],
      kpisAfetados: ["Demurrage"],
      exemplosReais: [
        "Plataformas de inteligência marítima com ML",
        "Soluções de port optimization com dados AIS",
      ],
    },
    {
      id: "lg-ia-demanda",
      titulo: "Forecasting de Demanda com ML",
      descricao:
        "Modelos de séries temporais (Prophet, LSTM) para prever demanda de consumíveis e materiais de manutenção. Integrado com gestão de estoque para reduzir ruptura e estoque morto.",
      categoria: "predictive",
      roiEstimativa: "-15-25% estoque",
      complexidade: "baixa",
      tempoValor: "2-4 meses",
      prerequisitos: [
        "ERP com histórico de compras > 24 meses",
        "Classificação ABC de materiais",
      ],
      kpisAfetados: ["Giro de Estoque", "Lead Time Médio"],
      exemplosReais: [
        "SAP IBP — demand planning com ML",
        "Soluções Prophet/LSTM para previsão de consumo",
      ],
    },
    {
      id: "lg-ia-blending",
      titulo: "Otimização de Blending com IA",
      descricao:
        "Otimização combinatória para definir melhor mistura de lotes no estoque, maximizando preço de venda e minimizando penalidades de qualidade.",
      categoria: "optimization",
      roiEstimativa: "+1-3 US$/t prêmio de qualidade",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Dados de qualidade por pilha/lote",
        "Especificações de contrato por cliente",
        "Modelo de precificação por qualidade",
      ],
      kpisAfetados: ["Giro de Estoque"],
      exemplosReais: [
        "Soluções de blend optimization para mineradoras de ferro",
        "Rio Tinto — blending otimizado para Pilbara",
      ],
    },
  ],
  maturidade: {
    nivelAtual: 2,
    niveis: MATURITY_SCALE,
  },
  roadmap: [
    {
      fase: 1,
      titulo: "Diagnóstico",
      duracao: "4-6 semanas",
      entregas: [
        "Mapeamento end-to-end da cadeia logística",
        "Análise de causas raiz de demurrage",
        "Avaliação de integração de dados entre elos",
        "Identificação de quick wins (blending, forecasting)",
        "Relatório com recomendações priorizadas",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "8-12 semanas",
      entregas: [
        "Modelo de predição de demurrage",
        "Otimização de blending para 1 produto",
        "Forecasting de demanda de consumíveis",
        "Dashboard de supply chain integrado",
      ],
      dependencias: ["Diagnóstico concluído", "Dados AIS e de produção integrados"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "6-18 meses",
      entregas: [
        "Scheduling integrado mina-ferrovia-porto",
        "Otimização de blending para todos os produtos",
        "Controle tower com visibilidade end-to-end",
        "Redução comprovada de demurrage",
      ],
      dependencias: ["Piloto validado", "Integração com operador logístico"],
    },
  ],
  projecoesIA: [
    { kpiNome: "Giro de Estoque", melhoriaEstimada: "+20%", descricao: "com forecasting IA" },
    { kpiNome: "Lead Time Médio", melhoriaEstimada: "-15%", descricao: "com scheduling integrado" },
    { kpiNome: "Demurrage", melhoriaEstimada: "-30%", descricao: "com predição + scheduling" },
  ],
};
