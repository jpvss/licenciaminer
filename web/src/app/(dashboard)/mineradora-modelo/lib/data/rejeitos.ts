import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const rejeitosModule: MiningModule = {
  key: "rejeitos",
  nome: "Rejeitos e Meio Ambiente",
  descricao:
    "Gestão de barragens/pilhas de rejeitos, monitoramento ambiental, recirculação de água e conformidade regulatória. Área de maior risco reputacional e regulatório.",
  cor: "var(--success)",
  atividades: [
    {
      id: "rj-disposicao",
      nome: "Disposição",
      descricao: "Empilhamento a seco ou disposição em barragem.",
      status: "ok",
      detalhes:
        "Pilha seca (filtrada) é o método adotado. Volume mensal de ~120 mil m³. Monitoramento de estabilidade com instrumentação geotécnica (piezômetros, inclinômetros, marcos topográficos).",
      kpisAfetados: ["Volume Disposto", "Fator de Segurança"],
    },
    {
      id: "rj-monitoramento",
      nome: "Monitoramento Geotécnico",
      descricao: "Instrumentação e inspeções para fator de segurança.",
      status: "gargalo",
      detalhes:
        "Leituras manuais de piezômetros com frequência insuficiente. Detecção de anomalias depende de interpretação humana. InSAR e sensores IoT podem detectar deformações milimétricas 48h antes de eventos críticos.",
      kpisAfetados: ["Fator de Segurança"],
    },
    {
      id: "rj-agua",
      nome: "Recirculação de Água",
      descricao: "Tratamento e reúso de água de processo.",
      status: "oportunidade",
      detalhes:
        "Taxa de recirculação atual ~85%. Meta é >90%. Otimização com IA pode reduzir captação de água fresca em 5-15%. Balanço hídrico impactado por sazonalidade (chuva vs. seca).",
      kpisAfetados: ["Recirculação de Água"],
    },
    {
      id: "rj-recuperacao",
      nome: "Recuperação Ambiental",
      descricao: "Revegetação e reabilitação de áreas mineradas.",
      status: "ok",
      detalhes:
        "PRAD (Plano de Recuperação de Áreas Degradadas) em execução. Monitoramento de solo e vegetação. Drones com NDVI para avaliar saúde da vegetação.",
      kpisAfetados: ["Recirculação de Água"],
    },
  ],
  casosIA: [
    {
      id: "rj-ia-estabilidade",
      titulo: "Predição de Estabilidade com ML",
      descricao:
        "Modelos XGBoost e LSTM para prever fator de segurança baseado em dados de instrumentação, clima e operação. Detecta anomalias 48h antes de métodos convencionais.",
      categoria: "predictive",
      roiEstimativa: "30-40% detecção mais precoce",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Instrumentação geotécnica digital (IoT)",
        "Estação meteorológica automatizada",
        "Histórico de dados > 24 meses",
      ],
      kpisAfetados: ["Fator de Segurança"],
      exemplosReais: [
        "VROC AI — monitoramento preditivo de TSFs",
        "SAP — solução integrada para gestão de barragens",
      ],
    },
    {
      id: "rj-ia-insar",
      titulo: "InSAR + Deep Learning para Deformação",
      descricao:
        "Radar satelital (InSAR) combinado com deep learning para detectar deformações milimétricas na superfície de barragens e pilhas, complementando instrumentação pontual.",
      categoria: "computer-vision",
      roiEstimativa: "Cobertura 100% da superfície",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Contrato com provedor de imagens SAR (Sentinel-1, TerraSAR-X)",
        "Baseline de deformação estabelecida",
      ],
      kpisAfetados: ["Fator de Segurança"],
      exemplosReais: [
        "XR Tech Group — InSAR para mineração",
        "FlyPix AI — análise de imagens satelitais",
        "GeoFEM — monitoramento de barragens 2026",
      ],
    },
    {
      id: "rj-ia-agua",
      titulo: "Otimização de Balanço Hídrico com IA",
      descricao:
        "ML para otimizar recirculação de água considerando clima, operação e qualidade. Reduz captação de água fresca e custo de tratamento.",
      categoria: "optimization",
      roiEstimativa: "-5-15% captação de água",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Medidores de vazão em pontos-chave",
        "Estação meteorológica com previsão",
        "Dados de qualidade de água online",
      ],
      kpisAfetados: ["Recirculação de Água", "Volume Disposto"],
      exemplosReais: [
        "Microsoft — plataforma de IA para recursos hídricos em mineração",
      ],
    },
    {
      id: "rj-ia-digital-twin",
      titulo: "Digital Twin de Barragem/Pilha",
      descricao:
        "Réplica digital da estrutura de rejeitos integrando dados geotécnicos, hidrológicos e meteorológicos. Simula cenários extremos (chuva excepcional, sismos) para avaliação de risco.",
      categoria: "digital-twin",
      roiEstimativa: "Conformidade GISTM",
      complexidade: "alta",
      tempoValor: "12-24 meses",
      prerequisitos: [
        "Modelo geotécnico calibrado",
        "Instrumentação IoT completa",
        "Dados meteorológicos em tempo real",
      ],
      kpisAfetados: ["Fator de Segurança", "Volume Disposto"],
      exemplosReais: [
        "GeoFEM — digital twin para barragens de rejeitos",
        "Dassault Systèmes — simulação geotécnica",
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
        "Auditoria de instrumentação geotécnica existente",
        "Avaliação de conformidade GISTM",
        "Mapeamento do balanço hídrico",
        "Gap analysis de dados para modelos preditivos",
        "Plano de ação priorizado por risco",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "8-12 semanas",
      entregas: [
        "Modelo preditivo de fator de segurança",
        "Monitoramento InSAR para 1 estrutura",
        "Dashboard de balanço hídrico em tempo real",
        "Validação contra dados históricos",
      ],
      dependencias: ["Diagnóstico concluído", "IoT em instrumentação-chave"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "12-24 meses",
      entregas: [
        "Sistema preditivo integrado a todas as estruturas",
        "Digital twin operacional com simulação de cenários",
        "Otimização hídrica closed-loop",
        "Conformidade total com GISTM",
      ],
      dependencias: ["Piloto validado", "Infraestrutura IoT completa"],
    },
  ],
  projecoesIA: [
    { kpiNome: "Fator de Segurança", melhoriaEstimada: "+0,1", descricao: "com monitoramento preditivo" },
    { kpiNome: "Recirculação de Água", melhoriaEstimada: "+5pp", descricao: "com otimização hídrica IA" },
    { kpiNome: "Volume Disposto", melhoriaEstimada: "-10%", descricao: "com otimização de processo" },
  ],
};
