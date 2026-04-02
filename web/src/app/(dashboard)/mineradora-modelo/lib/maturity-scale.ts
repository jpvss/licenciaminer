import type { MaturityLevel } from "./types";

/** Escala de maturidade digital — 5 niveis, consistente para todos os modulos. */
export const MATURITY_SCALE: MaturityLevel[] = [
  {
    nivel: 1,
    nome: "Reativo",
    descricao:
      "Dados em silos, KPIs manuais, decisões reativas. Sem integração entre sistemas.",
    criterios: [
      "Dados coletados manualmente em planilhas",
      "KPIs calculados com defasagem de dias/semanas",
      "Sem sistema de gerenciamento de frota (FMS)",
      "Manutenção 100% corretiva",
      "Decisões baseadas em experiência, sem dados",
    ],
  },
  {
    nivel: 2,
    nome: "Descritivo",
    descricao:
      "Dados centralizados, dashboards em tempo real, KPIs automatizados. Sistemas integrados.",
    criterios: [
      "FMS ou SCADA implantado e operacional",
      "Dashboards de produção em tempo real",
      "KPIs atualizados automaticamente (turno/dia)",
      "GPS/IoT em equipamentos principais",
      "Histórico de dados > 12 meses disponível",
    ],
  },
  {
    nivel: 3,
    nome: "Preditivo",
    descricao:
      "Modelos ML para previsão, monitoramento baseado em condição, otimização pontual.",
    criterios: [
      "Modelos de ML em produção para ≥1 caso de uso",
      "Manutenção preditiva com sensores IoT",
      "Previsão de falhas com >80% de acurácia",
      "Otimização de despacho com algoritmos",
      "Data lake centralizado com pipeline de dados",
    ],
  },
  {
    nivel: 4,
    nome: "Prescritivo",
    descricao:
      "IA em closed-loop, otimização autônoma, digital twins operacionais.",
    criterios: [
      "IA ajustando parâmetros operacionais automaticamente",
      "Digital twin da operação para simulação",
      "Otimização integrada mina-planta-porto",
      "Centro de Excelência de IA operacional",
      "MLOps com CI/CD para modelos em produção",
    ],
  },
  {
    nivel: 5,
    nome: "Autônomo",
    descricao:
      "Operação totalmente autônoma, auto-otimização contínua sem intervenção humana.",
    criterios: [
      "Equipamentos autônomos (AHS, perfuração)",
      "Operação remota centralizada (ROC)",
      "Auto-otimização contínua do sistema",
      "IA generativa para planejamento estratégico",
      "Zero intervenção manual em operações de rotina",
    ],
  },
];
