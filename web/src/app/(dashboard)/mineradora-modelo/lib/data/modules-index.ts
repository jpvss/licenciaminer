import type { MiningModule } from "../types";
import { operacaoModule } from "./operacao";
import { planejamentoModule } from "./planejamento";
import { processamentoModule } from "./processamento";
import { rejeitosModule } from "./rejeitos";
import { manutencaoModule } from "./manutencao";
import { logisticaModule } from "./logistica";
import { ssmaModule } from "./ssma";

/** Todos os modulos da cadeia de valor, na ordem de apresentacao. */
export const MODULES: MiningModule[] = [
  planejamentoModule,
  operacaoModule,
  processamentoModule,
  rejeitosModule,
  manutencaoModule,
  logisticaModule,
  ssmaModule,
];

/** Lookup rapido por key. */
export const MODULE_MAP: Record<string, MiningModule> = Object.fromEntries(
  MODULES.map((m) => [m.key, m])
);

/** Dados para o radar chart de maturidade (overview). */
export function getMaturityRadarData() {
  return MODULES.map((m) => ({
    modulo: m.nome.replace("Operação de Mina", "Operação").replace("Logística e Supply Chain", "Logística"),
    nivel: m.maturidade.nivelAtual,
    fullMark: 5,
  }));
}

/** ROI total estimado (range textual). */
export function getOverviewStats() {
  const totalCasosIA = MODULES.reduce((sum, m) => sum + m.casosIA.length, 0);
  const avgMaturity =
    MODULES.reduce((sum, m) => sum + m.maturidade.nivelAtual, 0) / MODULES.length;

  // Encontra o modulo com menor maturidade (maior oportunidade)
  const lowestMaturity = MODULES.reduce((lowest, m) =>
    m.maturidade.nivelAtual < lowest.maturidade.nivelAtual ? m : lowest
  );

  return {
    totalModulos: MODULES.length,
    totalCasosIA,
    avgMaturity: Math.round(avgMaturity * 10) / 10,
    moduloPrioritario: lowestMaturity,
  };
}
