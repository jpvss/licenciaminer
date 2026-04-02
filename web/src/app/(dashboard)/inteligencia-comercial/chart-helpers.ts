/**
 * Chart configuration, preset definitions, and shared constants
 * for the Inteligencia Comercial page.
 */

import { fmtReais, fmtUSD, fmtBR } from "@/lib/format";

/* ── Tooltip style ── */

export const CHART_TOOLTIP_STYLE = {
  background: "var(--card)",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  fontSize: 12,
};

/* ── Chart color tokens ── */

export const COLORS = {
  teal: "var(--brand-teal)",
  orange: "var(--brand-orange)",
  gold: "var(--brand-gold)",
  success: "var(--success)",
  danger: "var(--danger)",
  chart1: "var(--chart-1)",
  chart2: "var(--chart-2)",
  chart3: "var(--chart-3)",
  chart4: "var(--chart-4)",
  chart5: "var(--chart-5)",
  muted: "var(--muted-foreground)",
  border: "var(--border)",
} as const;

/* ── Series Configuration ── */

export type ChartMode = "composed" | "bar-h" | "bar-v";

export interface SeriesConfig {
  key: string;
  label: string;
  type: "bar" | "line" | "area";
  yAxisId: "left" | "right";
  color: string;
  format: (v: number) => string;
}

export interface PresetConfig {
  id: string;
  label: string;
  mode: ChartMode;
  /** Data key for X-axis in composed/bar-v modes */
  xKey: string;
  /** Data key for Y-axis category in bar-h mode */
  yKey?: string;
  series: SeriesConfig[];
  /** Source attribution */
  fonte: string;
}

/* ── Mercado Presets ── */

export const MERCADO_PRESETS: PresetConfig[] = [
  {
    id: "cambio",
    label: "Câmbio USD/BRL",
    mode: "composed",
    xKey: "data",
    series: [
      { key: "valor", label: "USD/BRL", type: "line", yAxisId: "left", color: COLORS.gold, format: (v) => fmtBR(v, 4) },
    ],
    fonte: "Fonte: BCB PTAX",
  },
  {
    id: "comex-anual",
    label: "Comércio Exterior (Anual)",
    mode: "bar-v",
    xKey: "ano",
    series: [
      { key: "Exportação", label: "Exportação", type: "bar", yAxisId: "left", color: COLORS.teal, format: fmtUSD },
      { key: "Importação", label: "Importação", type: "bar", yAxisId: "left", color: COLORS.orange, format: fmtUSD },
    ],
    fonte: "Fonte: Comex Stat / MDIC — NCM Cap. 26 (Minérios)",
  },
  {
    id: "comex-pais",
    label: "Comércio por País",
    mode: "bar-h",
    xKey: "valor_fob_usd",
    yKey: "pais",
    series: [
      { key: "valor_fob_usd", label: "USD FOB", type: "bar", yAxisId: "left", color: COLORS.teal, format: fmtUSD },
    ],
    fonte: "Fonte: Comex Stat / MDIC",
  },
  {
    id: "comex-uf",
    label: "Comércio por UF",
    mode: "bar-h",
    xKey: "valor_fob_usd",
    yKey: "uf",
    series: [
      { key: "valor_fob_usd", label: "USD FOB", type: "bar", yAxisId: "left", color: COLORS.chart2, format: fmtUSD },
    ],
    fonte: "Fonte: Comex Stat / MDIC",
  },
];

/* ── Producao & Receita Presets ── */

export const PRODUCAO_PRESETS: PresetConfig[] = [
  {
    id: "cfem-mensal",
    label: "CFEM Mensal",
    mode: "composed",
    xKey: "periodo",
    series: [
      { key: "total", label: "CFEM (R$)", type: "bar", yAxisId: "left", color: COLORS.gold, format: fmtReais },
    ],
    fonte: "Fonte: ANM — CFEM Arrecadação",
  },
  {
    id: "cfem-municipio",
    label: "CFEM por Município",
    mode: "bar-h",
    xKey: "total",
    yKey: "municipio",
    series: [
      { key: "total", label: "CFEM (R$)", type: "bar", yAxisId: "left", color: COLORS.gold, format: fmtReais },
    ],
    fonte: "Fonte: ANM — CFEM Arrecadação",
  },
  {
    id: "cfem-substancia",
    label: "CFEM por Substância",
    mode: "bar-h",
    xKey: "total",
    yKey: "substancia",
    series: [
      { key: "total", label: "CFEM (R$)", type: "bar", yAxisId: "left", color: COLORS.orange, format: fmtReais },
    ],
    fonte: "Fonte: ANM — CFEM Arrecadação",
  },
  {
    id: "ral-producao",
    label: "RAL Valor Venda",
    mode: "bar-h",
    xKey: "valor_venda",
    yKey: "substancia",
    series: [
      { key: "valor_venda", label: "Valor Venda (R$)", type: "bar", yAxisId: "left", color: COLORS.teal, format: fmtReais },
    ],
    fonte: "Fonte: ANM — Relatório Anual de Lavra",
  },
];

/* ── Territorio Presets ── */

export const TERRITORIO_PRESETS: PresetConfig[] = [
  {
    id: "anm-fase",
    label: "Processos por Fase",
    mode: "bar-h",
    xKey: "n",
    yKey: "fase",
    series: [
      { key: "n", label: "Processos", type: "bar", yAxisId: "left", color: COLORS.teal, format: (v) => fmtBR(v) },
    ],
    fonte: "Fonte: ANM / SIGMINE",
  },
  {
    id: "anm-substancia",
    label: "Processos por Substância",
    mode: "bar-h",
    xKey: "n",
    yKey: "substancia",
    series: [
      { key: "n", label: "Processos", type: "bar", yAxisId: "left", color: COLORS.orange, format: (v) => fmtBR(v) },
    ],
    fonte: "Fonte: ANM / SIGMINE",
  },
  {
    id: "minerais-estrategicos",
    label: "Minerais Estratégicos",
    mode: "bar-h",
    xKey: "n",
    yKey: "substancia",
    series: [
      { key: "n", label: "Processos", type: "bar", yAxisId: "left", color: COLORS.chart4, format: (v) => fmtBR(v) },
    ],
    fonte: "Fonte: ANM / SIGMINE + Classificação SQ",
  },
  {
    id: "categorias",
    label: "Categorias de Minerais",
    mode: "bar-h",
    xKey: "n",
    yKey: "categoria",
    series: [
      { key: "n", label: "Processos", type: "bar", yAxisId: "left", color: COLORS.chart5, format: (v) => fmtBR(v) },
    ],
    fonte: "Fonte: ANM / SIGMINE + Classificação SQ",
  },
];

/* ── All presets by tab ── */

export const PRESETS_BY_TAB: Record<string, PresetConfig[]> = {
  mercado: MERCADO_PRESETS,
  producao: PRODUCAO_PRESETS,
  territorio: TERRITORIO_PRESETS,
};
