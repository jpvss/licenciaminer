import type { MiningModule } from "../types";
import { MATURITY_SCALE } from "../maturity-scale";

export const processamentoModule: MiningModule = {
  key: "processamento",
  nome: "Processamento Mineral",
  descricao:
    "Beneficiamento do ROM: britagem, moagem, concentração e filtragem. Transforma minério bruto em produto comercializável com teor e umidade especificados.",
  cor: "var(--chart-3)",
  atividades: [
    {
      id: "pm-britagem",
      nome: "Britagem",
      descricao: "Redução granulométrica primária e secundária.",
      status: "ok",
      detalhes:
        "Britadores de mandíbula (primário) e cone (secundário). Throughput controlado por alimentação. Desgaste de revestimento é o principal custo. Fragmentação da mina impacta diretamente a produtividade.",
      kpisAfetados: ["Throughput"],
    },
    {
      id: "pm-moagem",
      nome: "Moagem",
      descricao: "Moinhos SAG e de bolas para liberação mineral.",
      status: "gargalo",
      detalhes:
        "Maior consumo energético da planta (~40-50% do total). Granulometria de alimentação e dureza do minério variam significativamente. Otimização de carga de bolas e velocidade é complexa e frequentemente sub-ótima.",
      kpisAfetados: ["Throughput", "Recuperação Metalúrgica", "Utilização de Planta"],
    },
    {
      id: "pm-concentracao",
      nome: "Concentração",
      descricao: "Flotação, separação magnética ou gravítica para concentrar minério.",
      status: "gargalo",
      detalhes:
        "Recuperação metalúrgica varia 3-5% dependendo da alimentação. Dosagem de reagentes é ajustada manualmente. Espuma de flotação é indicador visual chave — difícil de quantificar sem CV.",
      kpisAfetados: ["Recuperação Metalúrgica", "Teor do Concentrado"],
    },
    {
      id: "pm-espessamento",
      nome: "Espessamento",
      descricao: "Remoção de água do concentrado por sedimentação.",
      status: "ok",
      detalhes:
        "Espessadores com dosagem de floculante. Água recuperada retorna ao processo. Controle de torque do rake e densidade de underflow.",
      kpisAfetados: ["Utilização de Planta"],
    },
    {
      id: "pm-filtragem",
      nome: "Filtragem",
      descricao: "Remoção final de água para transporte/embarque.",
      status: "oportunidade",
      detalhes:
        "Filtros de pressão ou a vácuo. Umidade do produto final impacta frete e penalidades comerciais. Otimização do ciclo de filtragem com sensores e ML pode reduzir umidade em 1-2pp.",
      kpisAfetados: ["Teor do Concentrado", "Throughput"],
    },
  ],
  casosIA: [
    {
      id: "pm-ia-closedloop",
      titulo: "Otimização Closed-Loop da Planta",
      descricao:
        "IA controlando todo o circuito de processamento como um sistema integrado: moagem, flotação, espessamento e filtragem otimizados simultaneamente para máxima recuperação com mínimo custo.",
      categoria: "optimization",
      roiEstimativa: "+4-5% EBITDA",
      complexidade: "alta",
      tempoValor: "12-18 meses",
      prerequisitos: [
        "Instrumentação completa (analisadores online, sensores)",
        "SCADA/DCS integrado",
        "Histórico operacional > 12 meses",
      ],
      kpisAfetados: ["Recuperação Metalúrgica", "Throughput", "Utilização de Planta"],
      exemplosReais: [
        "Imubit CLAO — closed-loop AI optimization",
        "McKinsey OptimusAI — otimização de planta mineral",
        "Metso ACT — controle avançado de processo",
      ],
    },
    {
      id: "pm-ia-froth",
      titulo: "Análise de Espuma com Deep Learning",
      descricao:
        "Câmeras sobre células de flotação + deep learning para classificar espuma e ajustar dosagem de reagentes automaticamente. Substitui controle visual do operador.",
      categoria: "computer-vision",
      roiEstimativa: "+1-3% recuperação",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Câmeras sobre células de flotação",
        "Dosagem automatizada de reagentes",
        "Dados históricos de imagem + teor",
      ],
      kpisAfetados: ["Recuperação Metalúrgica", "Teor do Concentrado"],
      exemplosReais: [
        "Hatch — breakthrough em processamento mineral com IA",
        "Metso Courier — análise online de flotação",
      ],
    },
    {
      id: "pm-ia-virtual",
      titulo: "Analisadores Virtuais (Soft Sensors)",
      descricao:
        "Modelos ML que predizem teor do concentrado e recuperação minutos antes da análise laboratorial, permitindo ajustes proativos.",
      categoria: "predictive",
      roiEstimativa: "-5-10% variabilidade de teor",
      complexidade: "media",
      tempoValor: "3-6 meses",
      prerequisitos: [
        "Analisadores online (XRF, granulometria)",
        "Dados de laboratório com timestamp",
        "SCADA para variáveis de processo",
      ],
      kpisAfetados: ["Teor do Concentrado", "Recuperação Metalúrgica"],
      exemplosReais: [
        "OSIsoft PI / AVEVA — plataforma de dados de processo",
        "Imubit — soft sensors industriais",
      ],
    },
    {
      id: "pm-ia-energia",
      titulo: "Otimização Energética da Moagem",
      descricao:
        "ML para otimizar parâmetros de moagem (velocidade, carga de bolas, alimentação) minimizando kWh/t sem comprometer liberação mineral.",
      categoria: "optimization",
      roiEstimativa: "-5-10% consumo energético",
      complexidade: "media",
      tempoValor: "6-12 meses",
      prerequisitos: [
        "Medidores de energia por equipamento",
        "Dados de granulometria de alimentação e produto",
        "Integração SCADA-ML",
      ],
      kpisAfetados: ["Throughput", "Utilização de Planta"],
      exemplosReais: [
        "ABB Ability — otimização de moagem",
        "Rockwell Automation — controle avançado de processo",
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
        "Mapeamento de instrumentação existente",
        "Avaliação de qualidade de dados SCADA/PI",
        "Identificação de variáveis-chave por circuito",
        "Baseline de KPIs operacionais",
        "Recomendações de instrumentação adicional",
      ],
      dependencias: [],
    },
    {
      fase: 2,
      titulo: "Piloto",
      duracao: "10-14 semanas",
      entregas: [
        "Soft sensors para teor e recuperação",
        "CV de espuma em 1 banco de flotação",
        "Dashboard de otimização energética da moagem",
        "Comparação baseline vs. piloto",
      ],
      dependencias: ["Diagnóstico concluído", "Instrumentação mínima instalada"],
    },
    {
      fase: 3,
      titulo: "Implementação em Escala",
      duracao: "8-18 meses",
      entregas: [
        "Closed-loop AI para circuito completo",
        "Digital twin da planta de beneficiamento",
        "Otimização integrada moagem-flotação-filtragem",
        "Redução comprovada de custo operacional",
      ],
      dependencias: ["Piloto validado", "SCADA/DCS integrado com plataforma ML"],
    },
  ],
  projecoesIA: [
    { kpiNome: "Recuperação Metalúrgica", melhoriaEstimada: "+2-4pp", descricao: "com closed-loop IA" },
    { kpiNome: "Utilização de Planta", melhoriaEstimada: "+3pp", descricao: "com otimização integrada" },
    { kpiNome: "Teor do Concentrado", melhoriaEstimada: "+0,5pp Fe", descricao: "com soft sensors" },
    { kpiNome: "Throughput", melhoriaEstimada: "+5-8%", descricao: "com otimização de moagem" },
  ],
};
