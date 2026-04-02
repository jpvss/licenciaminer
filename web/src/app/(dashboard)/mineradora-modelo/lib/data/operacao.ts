import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const operacaoModule: MiningModule = {
  key: "operacao",
  nome: "Operação de Mina",
  descricao:
    "Ciclo completo de lavra: perfuração, desmonte, carregamento, transporte e serviços auxiliares. Representa ~60% do custo operacional total da mina.",
  cor: "var(--brand-orange)",
  atividades: [
    {
      id: "op-perfuracao",
      nome: "Perfuração",
      descricao: "Furos de desmonte para detonação de bancadas.",
      status: "ok",
      detalhes:
        "Perfuratrizes rotativas e DTH operando em bancadas de 12m. Malha de perfuração definida pelo plano de fogo. Oportunidade de otimização com dados de dureza da rocha.",
      kpisAfetados: ["Produtividade da Frota"],
    },
    {
      id: "op-desmonte",
      nome: "Desmonte",
      descricao: "Detonação com explosivos para fragmentação do maciço rochoso.",
      status: "ok",
      detalhes:
        "Plano de fogo dimensionado por geólogo de mina. Fragmentação impacta diretamente a produtividade de carregamento e britagem. Monitoramento de vibração e ultralançamento.",
      kpisAfetados: ["Produtividade da Frota", "Ciclo de Transporte"],
    },
    {
      id: "op-carregamento",
      nome: "Carregamento",
      descricao: "Escavadeiras e carregadeiras enchendo caminhões na frente de lavra.",
      status: "gargalo",
      detalhes:
        "Principal gargalo: tempo de fila de caminhões na escavadeira. Causa raiz: despacho ineficiente e desequilíbrio frota/equipamento. Fila média de 8-12 min impacta ciclo total e produtividade. Match fator escavadeira/caminhão frequentemente sub-ótimo.",
      kpisAfetados: ["Produtividade da Frota", "Ciclo de Transporte"],
    },
    {
      id: "op-transporte",
      nome: "Transporte",
      descricao: "Frota de caminhões fora-de-estrada entre frente de lavra e britagem/pilhas.",
      status: "gargalo",
      detalhes:
        "Maior custo operacional (~50% do custo de mina). Consumo de diesel é o principal driver. Condição de estradas (ondulações, poeira, inclinação) afeta velocidade e desgaste de pneus. Velocidade média abaixo do ideal por congestionamento em cruzamentos.",
      kpisAfetados: [
        "Consumo de Diesel",
        "Ciclo de Transporte",
        "Produtividade da Frota",
      ],
    },
    {
      id: "op-descarga",
      nome: "Descarga",
      descricao: "Basculamento em britador primário, pilhas de estoque ou bota-fora.",
      status: "ok",
      detalhes:
        "Ponto de descarga definido pelo despacho. Tempo de manobra e basculamento ~3 min. Oportunidade de otimização com câmeras para detectar posicionamento ideal.",
      kpisAfetados: ["Ciclo de Transporte"],
    },
    {
      id: "op-servicos",
      nome: "Serviços Auxiliares",
      descricao: "Manutenção de estradas, drenagem, topografia e apoio operacional.",
      status: "oportunidade",
      detalhes:
        "Atividade subutilizada para monitoramento com IA. Estradas em más condições aumentam consumo de diesel em até 15%. Drenagem deficiente causa paradas em períodos chuvosos. Computer vision em drones pode monitorar condição de pista continuamente.",
      kpisAfetados: [
        "Ciclo de Transporte",
        "Disponibilidade Física",
        "Consumo de Diesel",
      ],
    },
  ],
  casosIA: [
    {
      id: "op-ia-despacho",
      titulo: "Despacho Inteligente com IA",
      descricao:
        "Otimização em tempo real da alocação caminhão-escavadeira usando ML + heurísticas. Substitui dispatch baseado em regras fixas por decisões dinâmicas considerando fila, distância, teor e prioridade.",
      categoria: "optimization",
      roiEstimativa: "+5-15% produtividade",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "FMS implantado com GPS em toda frota",
        "Histórico de ciclos > 6 meses",
        "Integração com modelo de blocos",
      ],
      kpisAfetados: ["Produtividade da Frota", "Ciclo de Transporte"],
      exemplosReais: [
        "Wenco — FMS com dispatch inteligente",
        "Hexagon Jigsaw — otimização de frota",
        "Modular Mining DISPATCH — líder de mercado",
      ],
    },
    {
      id: "op-ia-ahs",
      titulo: "Caminhões Autônomos (AHS)",
      descricao:
        "Autonomous Haulage System com percepção LiDAR + GPS RTK. Operação 24/7 sem operador, eliminando tempo de troca de turno, fadiga e variabilidade humana.",
      categoria: "automation",
      roiEstimativa: "-15-20% custo operacional",
      complexidade: "alta",
      tempoValor: "18-36 meses",
      prerequisitos: [
        "Infraestrutura de rede na cava (WiFi/LTE)",
        "Centro de operação remota (ROC)",
        "Segregação de tráfego autônomo/tripulado",
        "Investimento em frota compatível (Komatsu/Cat)",
      ],
      kpisAfetados: [
        "Utilização Física",
        "Produtividade da Frota",
        "Consumo de Diesel",
      ],
      exemplosReais: [
        "Rio Tinto — 130+ caminhões Komatsu autônomos (Pilbara)",
        "Caterpillar MineStar Command — AHS integrado",
        "Fortescue — maior frota AHS Cat do mundo",
      ],
    },
    {
      id: "op-ia-fadiga",
      titulo: "Detecção de Fadiga em Tempo Real",
      descricao:
        "Wearables (EEG smart caps) e câmeras in-cab para monitorar estado de alerta do operador. Alertas em tempo real para operador e sala de controle quando detecta microsono ou fadiga.",
      categoria: "computer-vision",
      roiEstimativa: "-70% acidentes por fadiga",
      complexidade: "baixa",
      tempoValor: "1-3 meses",
      prerequisitos: [
        "Câmeras in-cab ou smart caps",
        "Conectividade para alertas em tempo real",
        "Protocolo de resposta a alertas",
      ],
      kpisAfetados: ["Disponibilidade Física"],
      exemplosReais: [
        "BHP — smart caps com EEG em toda frota",
        "Fatigue Science Readi — plataforma de fadiga",
        "Glencore — wearables com 90% redução de incidentes graves",
      ],
    },
    {
      id: "op-ia-estradas",
      titulo: "Monitoramento de Estradas com CV",
      descricao:
        "Computer vision em drones ou câmeras em veículos para avaliar condição de pista: buracos, ondulações, excesso de poeira, inclinação. Gera alertas automáticos para equipe de serviços auxiliares.",
      categoria: "computer-vision",
      roiEstimativa: "-8% consumo diesel",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Drone ou câmeras em veículos leves",
        "Modelo de CV treinado para defeitos de pista",
        "Sistema de gestão de ordens de serviço",
      ],
      kpisAfetados: ["Consumo de Diesel", "Ciclo de Transporte"],
      exemplosReais: [
        "viAct.ai — monitoramento de canteiro com CV",
        "Ultralytics YOLO — detecção de objetos em tempo real",
      ],
    },
    {
      id: "op-ia-perfuracao",
      titulo: "Otimização de Perfuração com ML",
      descricao:
        "ML para ajustar parâmetros de perfuração (velocidade, pressão, malha) baseado em dureza da rocha e geologia do bloco. Reduz custo de explosivos e melhora fragmentação.",
      categoria: "predictive",
      roiEstimativa: "-5-10% custo de explosivos",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Sensores MWD (Measurement While Drilling)",
        "Modelo de blocos atualizado",
        "Histórico de planos de fogo e resultados",
      ],
      kpisAfetados: ["Produtividade da Frota"],
      exemplosReais: [
        "MineSense ShovelSense — análise de material em tempo real",
        "K-MINE — planejamento de mina com IA",
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
        "Levantamento de sistemas existentes (FMS, SCADA, GPS)",
        "Mapeamento de dados disponíveis e qualidade",
        "Assessment de maturidade digital atual",
        "Identificação de quick wins (ROI em <3 meses)",
        "Relatório diagnóstico + plano de ação priorizado",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "8-12 semanas",
      entregas: [
        "Implementação de 1-2 casos de uso priorizados",
        "Integração com dados existentes do FMS",
        "Treinamento de equipe operacional",
        "Medição de baseline vs. resultados do piloto",
        "Business case validado para escala",
      ],
      dependencias: ["Diagnóstico concluído", "Sponsor executivo definido"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "6-18 meses",
      entregas: [
        "Rollout dos casos de uso validados para toda operação",
        "Integração com sistemas corporativos (ERP, BI)",
        "Centro de Excelência de IA (governança, MLOps)",
        "Programa de change management",
        "Operação digital madura (nível 3-4)",
      ],
      dependencias: ["Piloto validado", "Orçamento aprovado"],
    },
  ],
  projecoesIA: [
    {
      kpiNome: "Produtividade da Frota",
      melhoriaEstimada: "+15%",
      descricao: "com dispatch IA",
    },
    {
      kpiNome: "Ciclo de Transporte",
      melhoriaEstimada: "-12%",
      descricao: "com otimização de rotas",
    },
    {
      kpiNome: "Consumo de Diesel",
      melhoriaEstimada: "-10%",
      descricao: "com driving assist IA",
    },
    {
      kpiNome: "Disponibilidade Física",
      melhoriaEstimada: "+5pp",
      descricao: "com manutenção preditiva",
    },
    {
      kpiNome: "Utilização Física",
      melhoriaEstimada: "+8pp",
      descricao: "com AHS",
    },
  ],
};
