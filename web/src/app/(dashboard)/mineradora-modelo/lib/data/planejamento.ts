import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const planejamentoModule: MiningModule = {
  key: "planejamento",
  nome: "Planejamento de Mina",
  descricao:
    "Modelagem geológica, sequenciamento de lavra e reconciliação. Define o plano de longo, médio e curto prazo que guia toda a operação.",
  cor: "var(--brand-teal)",
  atividades: [
    {
      id: "pl-modelo",
      nome: "Modelo Geológico",
      descricao: "Modelagem de blocos e estimativa de teores por krigagem.",
      status: "oportunidade",
      detalhes:
        "ML pode prever teores entre furos de sonda com 30-50% menos sondagem. Reduz custo exploratório e melhora confiabilidade do modelo de blocos.",
      kpisAfetados: ["Aderência ao Plano", "Conformidade de Cava"],
    },
    {
      id: "pl-design",
      nome: "Design de Cava",
      descricao: "Otimização de cava final e fases de lavra (Lerchs-Grossmann/Whittle).",
      status: "ok",
      detalhes:
        "Definição de pit shells e pushbacks com software especializado. Parâmetros econômicos (preço, custo, recuperação) determinam limites ótimos.",
      kpisAfetados: ["REM (Relação Estéril/Minério)", "Conformidade de Cava"],
    },
    {
      id: "pl-sequenciamento",
      nome: "Sequenciamento",
      descricao: "Programação de lavra de curto prazo (semanal/mensal).",
      status: "gargalo",
      detalhes:
        "Complexidade combinatória altíssima: qual bloco lavrar, quando, para onde enviar. Frequentemente feito manualmente em planilhas. Reconciliação entre plano e realizado raramente fecha.",
      kpisAfetados: ["Aderência ao Plano", "REM (Relação Estéril/Minério)"],
    },
    {
      id: "pl-controle",
      nome: "Controle de Teor",
      descricao: "Amostragem e análise de teor na frente de lavra.",
      status: "gargalo",
      detalhes:
        "Defasagem entre amostragem e resultado laboratorial (horas/dias). Material pode ser enviado para destino errado. Sensores XRF em tempo real podem reduzir diluição em 15-20%.",
      kpisAfetados: ["Aderência ao Plano", "Conformidade de Cava"],
    },
    {
      id: "pl-reconciliacao",
      nome: "Reconciliação",
      descricao: "Comparação plano vs. realizado (modelo vs. produção).",
      status: "oportunidade",
      detalhes:
        "Variância modelo-planta frequentemente >10%. Fator F1/F2/F3 para calibração do modelo. IA pode identificar padrões de desvio e ajustar modelo em tempo real.",
      kpisAfetados: ["Aderência ao Plano", "Conformidade de Cava"],
    },
  ],
  casosIA: [
    {
      id: "pl-ia-grade",
      titulo: "Predição de Teor com ML",
      descricao:
        "Modelos de Machine Learning para estimar teores entre furos de sonda, reduzindo necessidade de sondagem adicional e melhorando resolução do modelo de blocos.",
      categoria: "predictive",
      roiEstimativa: "-30-50% custo de sondagem",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Banco de dados de sondagem digitalizado",
        "Modelo de blocos em software compatível (Vulcan, Surpac)",
        "Equipe de geoestatística",
      ],
      kpisAfetados: ["Aderência ao Plano", "Conformidade de Cava"],
      exemplosReais: [
        "Maptek Vulcan — integração ML com modelo de blocos",
        "Micromine Origin — geoestatística avançada",
      ],
    },
    {
      id: "pl-ia-pit",
      titulo: "Otimização de Sequenciamento com RL",
      descricao:
        "Reinforcement Learning para otimizar sequenciamento de lavra, maximizando VPL e respeitando restrições operacionais (ângulo de talude, teor mínimo, REM máximo).",
      categoria: "optimization",
      roiEstimativa: "+2-5% VPL da mina",
      complexidade: "alta",
      tempoValor: "12-18 meses",
      prerequisitos: [
        "Modelo de blocos atualizado",
        "Parâmetros econômicos definidos",
        "Infraestrutura computacional (GPU)",
      ],
      kpisAfetados: ["Aderência ao Plano", "REM (Relação Estéril/Minério)"],
      exemplosReais: [
        "Deswik — otimização de scheduling",
        "K-MINE — IA para planejamento de mina",
      ],
    },
    {
      id: "pl-ia-fragment",
      titulo: "Análise de Fragmentação com CV",
      descricao:
        "Computer Vision para medir distribuição granulométrica do material desmontado automaticamente, ajustando plano de fogo em tempo real.",
      categoria: "computer-vision",
      roiEstimativa: "+5-8% produtividade de britagem",
      complexidade: "baixa",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Câmeras na frente de lavra ou em caminhões",
        "Software de análise de imagem (Split-Desktop, WipFrag)",
      ],
      kpisAfetados: ["Aderência ao Plano"],
      exemplosReais: [
        "Split Engineering — análise de fragmentação padrão da indústria",
        "WipWare — sistema de câmera para fragmentação",
      ],
    },
    {
      id: "pl-ia-dt",
      titulo: "Digital Twin da Mina",
      descricao:
        "Réplica digital da mina integrando modelo geológico, topografia atual (LiDAR), equipamentos (GPS) e operação (FMS) para simulação de cenários em tempo real.",
      categoria: "digital-twin",
      roiEstimativa: "+3-7% aderência ao plano",
      complexidade: "alta",
      tempoValor: "12-24 meses",
      prerequisitos: [
        "LiDAR ou drone para topografia atualizada",
        "Integração FMS + modelo de blocos + ERP",
        "Infraestrutura cloud",
      ],
      kpisAfetados: ["Aderência ao Plano", "Conformidade de Cava", "REM (Relação Estéril/Minério)"],
      exemplosReais: [
        "Dassault Systèmes GEOVIA — plataforma de digital twin para mineração",
        "Bentley Systems iTwin — infraestrutura digital",
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
        "Auditoria do modelo geológico e processo de reconciliação",
        "Avaliação da qualidade dos dados de sondagem",
        "Mapeamento do workflow de sequenciamento atual",
        "Identificação de gaps entre plano e realizado",
        "Relatório com recomendações priorizadas",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "8-12 semanas",
      entregas: [
        "Modelo ML de predição de teor para 1 zona da mina",
        "Análise de fragmentação com CV em 1 frente de lavra",
        "Comparação de acurácia ML vs. krigagem tradicional",
        "Validação de ROI do piloto",
      ],
      dependencias: ["Diagnóstico concluído", "Dados de sondagem organizados"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "6-18 meses",
      entregas: [
        "ML integrado ao workflow de modelagem geológica",
        "Sequenciamento otimizado com IA para toda a mina",
        "Digital twin operacional com atualização diária",
        "Reconciliação automatizada com alertas",
      ],
      dependencias: ["Piloto validado", "Integração com software de mina"],
    },
  ],
  projecoesIA: [
    { kpiNome: "Aderência ao Plano", melhoriaEstimada: "+5pp", descricao: "com sequenciamento IA" },
    { kpiNome: "REM (Relação Estéril/Minério)", melhoriaEstimada: "-8%", descricao: "com otimização de lavra" },
    { kpiNome: "Conformidade de Cava", melhoriaEstimada: "+3pp", descricao: "com digital twin" },
  ],
};
