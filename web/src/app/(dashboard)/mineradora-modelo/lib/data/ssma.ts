import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const ssmaModule: MiningModule = {
  key: "ssma",
  nome: "SSMA-ESG",
  descricao:
    "Saúde, Segurança, Meio Ambiente e ESG. Área de maior escrutínio por investidores e reguladores. Acidentes e não-conformidades podem paralisar a operação.",
  cor: "var(--chart-5)",
  atividades: [
    {
      id: "ss-identificacao",
      nome: "Identificação de Riscos",
      descricao: "Mapeamento de perigos e avaliação de riscos ocupacionais.",
      status: "ok",
      detalhes:
        "APR (Análise Preliminar de Riscos) e FMEA de segurança. Matriz de risco atualizada periodicamente. Foco em atividades de alto risco: trabalho em altura, espaço confinado, equipamentos móveis.",
      kpisAfetados: ["TRIFR"],
    },
    {
      id: "ss-monitoramento",
      nome: "Monitoramento em Campo",
      descricao: "Inspeções, auditorias e observações de segurança.",
      status: "gargalo",
      detalhes:
        "Inspeções manuais com checklists em papel/tablet. Cobertura limitada (<30% das áreas/turno). PPE compliance verificada visualmente. Subnotificação de quase-acidentes estimada em 50-70%.",
      kpisAfetados: ["TRIFR"],
    },
    {
      id: "ss-resposta",
      nome: "Resposta a Incidentes",
      descricao: "Atendimento de emergência e investigação de acidentes.",
      status: "ok",
      detalhes:
        "Brigada de emergência treinada. CIPA ativa. Investigação de acidentes com método de árvore de causas. Tempo de resposta adequado para emergências médicas.",
      kpisAfetados: ["TRIFR"],
    },
    {
      id: "ss-reporte",
      nome: "Reporte ESG",
      descricao: "Relatórios de sustentabilidade, GRI, TCFD, SASB.",
      status: "gargalo",
      detalhes:
        "Coleta de dados ESG manual e fragmentada. Relatório anual consome 3-4 meses de trabalho. Dados de emissões Escopo 1+2 estimados, não medidos. Investidores exigem dados cada vez mais granulares e frequentes.",
      kpisAfetados: ["Investimento Social"],
    },
    {
      id: "ss-melhoria",
      nome: "Melhoria Contínua",
      descricao: "Análise de tendências e programas de prevenção.",
      status: "oportunidade",
      detalhes:
        "Dados de quase-acidentes e incidentes pouco explorados analiticamente. Análise preditiva de acidentes pode identificar condições precursoras. Programas de segurança comportamental com dados limitados.",
      kpisAfetados: ["TRIFR", "Investimento Social"],
    },
  ],
  casosIA: [
    {
      id: "ss-ia-fadiga",
      titulo: "Detecção de Fadiga e Distração",
      descricao:
        "Câmeras in-cab e wearables (EEG smart caps) para monitorar estado de alerta de operadores em tempo real. Alerta operador e supervisor quando detecta microsono ou distração.",
      categoria: "computer-vision",
      roiEstimativa: "-70% acidentes por fadiga",
      complexidade: "baixa",
      tempoValor: "1-3 meses",
      prerequisitos: [
        "Câmeras in-cab ou smart caps",
        "Conectividade para alertas",
        "Protocolo de resposta",
      ],
      kpisAfetados: ["TRIFR"],
      exemplosReais: [
        "BHP — smart caps EEG em toda frota",
        "Fatigue Science Readi — plataforma de fadiga",
        "Glencore — wearables com 90% redução de incidentes graves",
      ],
    },
    {
      id: "ss-ia-ppe",
      titulo: "Compliance de EPI com Computer Vision",
      descricao:
        "YOLO/detectores de objetos para verificar uso correto de EPI (capacete, colete, óculos, bota) em tempo real via câmeras de CFTV existentes.",
      categoria: "computer-vision",
      roiEstimativa: "+95% compliance de EPI",
      complexidade: "baixa",
      tempoValor: "2-4 meses",
      prerequisitos: [
        "Câmeras CFTV em pontos-chave (portaria, oficina, planta)",
        "Infraestrutura de edge computing",
      ],
      kpisAfetados: ["TRIFR"],
      exemplosReais: [
        "viAct.ai — monitoramento de EPI com CV",
        "Ultralytics YOLO — detecção em tempo real",
      ],
    },
    {
      id: "ss-ia-esg",
      titulo: "Reporte ESG Automatizado com NLP/RAG",
      descricao:
        "LLM + RAG para automatizar coleta, consolidação e geração de relatórios ESG. Extrai dados de múltiplos sistemas e gera narrativas seguindo GRI/SASB/TCFD.",
      categoria: "nlp",
      roiEstimativa: "-50-70% tempo de reporte",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Dados ESG em sistemas acessíveis (ERP, CMMS, ambiental)",
        "Framework de reporte definido (GRI, SASB)",
        "Revisão humana do output",
      ],
      kpisAfetados: ["Investimento Social"],
      exemplosReais: [
        "Soluções RAG para reporte regulatório e ESG",
        "Microsoft — IA para sustentabilidade corporativa",
      ],
    },
    {
      id: "ss-ia-preventiva",
      titulo: "Análise Preditiva de Acidentes",
      descricao:
        "ML para identificar padrões precursores de acidentes: combinação de clima, turno, equipamento, operador e atividade que historicamente correlacionam com incidentes.",
      categoria: "predictive",
      roiEstimativa: "-25% taxa de incidentes",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Banco de dados de incidentes e quase-acidentes > 3 anos",
        "Dados operacionais (turno, equipamento, clima)",
        "Cultura de reporte de quase-acidentes",
      ],
      kpisAfetados: ["TRIFR"],
      exemplosReais: [
        "Análise preditiva de segurança em mineradoras",
        "Modelos de previsão de acidentes baseados em precursores",
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
        "Análise de histórico de acidentes e quase-acidentes",
        "Avaliação de infraestrutura de CFTV e wearables",
        "Mapeamento do processo de reporte ESG atual",
        "Identificação de quick wins (CV de EPI, detecção de fadiga)",
        "Relatório com plano de ação de segurança digital",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "6-10 semanas",
      entregas: [
        "CV para compliance de EPI em 2 pontos",
        "Smart caps em 10 operadores de caminhão",
        "Protótipo de reporte ESG automatizado",
        "Medição de impacto vs. baseline",
      ],
      dependencias: ["Diagnóstico concluído", "Infraestrutura de câmeras"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "6-12 meses",
      entregas: [
        "CV de EPI em todos os pontos de acesso",
        "Detecção de fadiga em toda frota pesada",
        "Análise preditiva de acidentes operacional",
        "Reporte ESG automatizado com revisão humana",
      ],
      dependencias: ["Piloto validado", "Cultura de reporte estabelecida"],
    },
  ],
  projecoesIA: [
    { kpiNome: "TRIFR", melhoriaEstimada: "-50%", descricao: "com detecção de fadiga + CV" },
    { kpiNome: "Investimento Social", melhoriaEstimada: "+30%", descricao: "com eficiência de reporte ESG" },
  ],
};
