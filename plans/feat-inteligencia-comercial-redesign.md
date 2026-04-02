# feat: Redesign Inteligencia Comercial as 1-Stop Mining Intelligence Hub

## Overview

Transform the Inteligencia Comercial page from a passive 4-tab chart gallery (493 LOC, 8 independent charts, zero interactivity) into a structured, GenAI-enhanced mining intelligence hub. The page becomes the primary decision-support tool for investors and analysts evaluating the Brazilian mining sector.

**Key principles:**
- Charts with metric selectors instead of redundant charts
- KPI strip always visible — the "ticker" for mining intelligence
- AI-powered narrative summaries contextualized to visible data
- All data structured for GenAI consumption (well-labeled, typed, summarizable)
- Data freshness indicators everywhere — stale data kills trust

---

## Problem Statement

The current page shows data but doesn't tell a story. An investor lands on 4 tabs with 8 disconnected charts, no KPIs, no time-series trends, no cross-source correlation, and no narrative. They must mentally assemble the picture from: a PTAX line chart, commodity price cards with 3 minerals (2024-only), export/import bars, CFEM by municipality, RAL by substance, and ANM by phase.

**What's wrong:**
1. **No headline numbers** — no KPI strip, user must hunt for the "so what"
2. **Redundant charts** — 6 horizontal bar charts that differ only by grouping column
3. **No time-series** — CFEM has `Ano`+`Mês` columns (91K records, 2022-2026) but only aggregates are shown
4. **No GenAI layer** — the chat sidebar exists but has zero page context
5. **No metric correlation** — can't compare CFEM vs. commodity prices vs. FX
6. **Sparse commodity data** — only 3 minerals, 2024-only, from a manual CSV
7. **No interactivity** — zero filters, zero drill-down, zero URL persistence

---

## Data Inventory (What We Actually Have)

| Source | View / File | Temporal | Records | Key Columns |
|--------|------------|----------|---------|-------------|
| BCB PTAX | `v_bcb_cotacoes` | Daily | 497 | `data`, `cotacao_venda` |
| CFEM | `v_cfem` | Monthly | 91,026 | `Ano`, `Mês`, `Substância`, `Município`, `UF`, `ValorRecolhido`, `CPF_CNPJ` |
| RAL | `v_ral` | Yearly | 1,013 | `Ano base`, `Substância Mineral`, `Classe Substância`, `Valor Venda (R$)`, `Quantidade Produção` |
| COMEX | `v_comex_mineracao` | Monthly | ~100K | `ano`, `mes`, `fluxo`, `valor_fob_usd`, `peso_kg`, `uf`, `pais`, `posicao_ncm` |
| ANM | `v_anm` | — | ~50K | `FASE`, `SUBS`, `AREA_HA` |
| Commodities | `commodity_prices.csv` | Monthly | 19 | `data`, `mineral`, `preco_usd` (only 3 minerals, 2024) |
| Substances | `substancias_classificacao.csv` | — | 65 | `substancia`, `categoria`, `valor_relativo`, `estrategico` |

**Key finding:** CFEM, COMEX, and RAL all have temporal columns — rich time-series charts are feasible.

---

## Proposed Architecture

### Page Layout (Desktop)

```
+------------------------------------------------------------------+
| Inteligencia Comercial Mineraria                                  |
| Visao integrada do setor mineral brasileiro                       |
+------------------------------------------------------------------+
| [KPI] USD/BRL  | [KPI] Ferro  | [KPI] Balanca | [KPI] CFEM YTD  |
|  5.72 ▼1.2%    | 108.9 ▲3.1%  | +$2.1B        | R$ 412mi ▲8%    |
|  ~~~sparkline~~ | ~~sparkline~ | ~~sparkline~~ | ~~sparkline~~~  |
+------------------------------------------------------------------+
| [Mercado] [Producao & Receita] [Territorio]         [?tab=...]   |
+------------------------------------------------------------------+
|                                    |                              |
|  MAIN CHART AREA                   |  AI INSIGHTS PANEL           |
|  [Select: metric preset ▼]        |  ┌─────────────────────────┐ |
|  [ComposedChart dual Y-axis]       |  │ Resumo de Mercado    🔄│ |
|  [Brush time range]                |  │                         │ |
|                                    |  │ O CFEM de MG cresceu   │ |
|  ~~~ 400px chart area ~~~          |  │ 8% YoY impulsionado... │ |
|                                    |  │                         │ |
|                                    |  │ Key signals:            │ |
|                                    |  │ • Ferro +3.1% (...)     │ |
|                                    |  │ • BRL depreciou 1.2%    │ |
|                                    |  │ • Para liderou export.  │ |
|                                    |  └─────────────────────────┘ |
+------------------------------------------------------------------+
| SUPPORTING DATA (2-3 col grid)                                    |
| [Card: Top Municipios] [Card: Top Substancias] [Card: By UF/Pais]|
+------------------------------------------------------------------+
| Fonte: BCB, ANM, Comex Stat, IBRAM | Dados atualizados: 22/03/26 |
+------------------------------------------------------------------+
```

### Page Layout (Mobile)

```
+---------------------------+
| [KPI strip: horiz scroll] |
+---------------------------+
| [Tab bar: 3 tabs]         |
+---------------------------+
| [Select: metric ▼]        |
| [Chart: full width 280px] |
+---------------------------+
| [AI: collapsed accordion] |
+---------------------------+
| [Cards: stacked vertical] |
+---------------------------+
```

---

## Tab Content Mapping (4 → 3)

| New Tab | Content | Old Source |
|---------|---------|-----------|
| **Mercado** | PTAX chart, commodity prices, COMEX yearly, COMEX by country/UF | Old "Mercado" + "Comercio Exterior" |
| **Producao & Receita** | CFEM time-series, CFEM by municipality, CFEM by substance, RAL production, RAL by substance | Old "Producao e Arrecadacao" (expanded with time-series) |
| **Territorio** | ANM processes by phase, ANM by substance, strategic minerals breakdown, permit pipeline | Old "Gestao e Territorio" (expanded with substance classification) |

---

## Metric Selector Presets (Per Tab)

### Tab: Mercado

| Preset | Series | Chart Type | Left Y | Right Y |
|--------|--------|-----------|--------|---------|
| **Cambio** | PTAX cotacao_venda | Line | BRL | — |
| **Ferro vs Cambio** | Iron ore price (line) + PTAX (line, dashed) | ComposedChart | USD/t | BRL |
| **Comercio Exterior** | Export (bar) + Import (bar) by year | BarChart | USD FOB | — |
| **Comercio por Pais** | Top 10 countries by export value | Horizontal Bar | — | USD FOB |
| **Comercio por UF** | Top UFs by export value | Horizontal Bar | — | USD FOB |

### Tab: Producao & Receita

| Preset | Series | Chart Type | Left Y | Right Y |
|--------|--------|-----------|--------|---------|
| **CFEM Mensal** | CFEM total by month (bar) + YoY % change (line) | ComposedChart | R$ | % |
| **CFEM por Municipio** | Top 10 municipalities | Horizontal Bar | — | R$ |
| **CFEM por Substancia** | Top 10 substances | Horizontal Bar | — | R$ |
| **RAL Producao** | Top substances by production volume | Horizontal Bar | — | tonnes |
| **RAL Valor Venda** | Top substances by sales value | Horizontal Bar | — | R$ |

### Tab: Territorio

| Preset | Series | Chart Type | Left Y | Right Y |
|--------|--------|-----------|--------|---------|
| **Processos por Fase** | ANM process distribution | Horizontal Bar | — | count |
| **Processos por Substancia** | Top 15 substances | Horizontal Bar | — | count |
| **Minerais Estrategicos** | Strategic flag from `substancias_classificacao.csv` | Horizontal Bar (colored) | — | count |
| **Categorias** | Substance category breakdown | Pie/Donut or TreeMap | — | count |

---

## KPI Strip Specification

| # | KPI | Source | Sparkline Data | Delta | Feasibility |
|---|-----|--------|---------------|-------|-------------|
| 1 | **USD/BRL** | `v_bcb_cotacoes` latest | 30-day daily | vs 30d ago | ✅ 497 daily records |
| 2 | **Ferro 62% Fe** | `commodity_prices.csv` latest | 12-month | vs prev month | ⚠️ Only 2024 data (12 points) |
| 3 | **Balanca Comercial** | `v_comex_mineracao` SUM(export)-SUM(import) YTD | 5-year yearly | YoY | ✅ Monthly data 2021-2026 |
| 4 | **CFEM Acumulado** | `v_cfem` SUM(ValorRecolhido) current year | 4-year yearly | YoY | ✅ 91K records, 2022-2026 |

> Note: Gold and Niobium prices dropped from KPI strip due to sparse data (3 points each). They remain in the Mercado tab commodity cards.

---

## GenAI Integration — AI Insights Panel

### Architecture

```
Frontend (page.tsx)                     FastAPI                          Anthropic
─────────────────                     ──────────                       ─────────
1. User lands on tab / changes metric
2. Collect context:
   - Active tab + preset
   - KPI values + deltas
   - Top 5 chart data points
   - Data freshness timestamps
3. POST /intelligence/ai-summary ───►  4. Build system prompt:
                                          - Role: mining analyst
                                          - Context: structured JSON
                                          - Directive: 3-5 bullets,
                                            cite numbers, Portuguese
                                       5. messages.stream() ──────────► Claude Sonnet
                                       6. StreamingResponse (SSE) ◄──── streaming chunks
7. Display streaming text ◄──────────
8. Cache result per context key
```

### Trigger: Manual "Gerar Analise" button (not auto)

Rationale: auto-regeneration on every filter change is expensive and distracting. A manual button with visible "Gerar Analise" CTA is more intentional. Cache the result per `{tab, preset, year}` tuple to avoid redundant calls.

### Context JSON Shape (sent to LLM)

```json
{
  "pagina": "inteligencia-comercial",
  "aba": "producao-receita",
  "preset": "cfem-mensal",
  "periodo": "2022-01 a 2026-03",
  "kpis": {
    "usd_brl": { "valor": 5.72, "delta_30d": -0.012 },
    "ferro_62fe": { "valor": 108.9, "delta_mes": 0.031 },
    "balanca_ytd_usd": { "valor": 2100000000, "delta_yoy": -0.12 },
    "cfem_ytd_brl": { "valor": 412000000, "delta_yoy": 0.08 }
  },
  "dados_visiveis": {
    "top_5": [
      { "municipio": "Congonhas", "cfem_total": 45000000 },
      { "municipio": "Itabira", "cfem_total": 38000000 }
    ],
    "tendencia": "CFEM mensal cresceu 8% YoY, puxado por Ferro em MG",
    "anomalias": ["Ouro Preto caiu 22% vs trimestre anterior"]
  },
  "freshness": {
    "cfem": "2026-03-22",
    "ptax": "2026-03-28",
    "comex": "2026-04-01"
  }
}
```

### Fallback When No API Key

If `ANTHROPIC_API_KEY` is not configured:
- AI panel collapses to 0 width
- Main chart expands to 100%
- No error shown — panel simply doesn't appear
- Detect via a lightweight `/intelligence/ai-status` endpoint that returns `{available: bool}`

---

## New Backend Endpoints

### 1. CFEM Time-Series

```
GET /intelligence/cfem/time-series?ano_min=2022&ano_max=2026&substancia=FERRO&municipio=Congonhas
→ { rows: [{ ano: 2022, mes: 1, total: 1234.56 }, ...] }
```

SQL:
```sql
SELECT Ano as ano, "Mês" as mes,
       SUM(TRY_CAST(REPLACE(REPLACE("ValorRecolhido", '.', ''), ',', '.') AS DOUBLE)) as total
FROM v_cfem
WHERE Ano BETWEEN ? AND ?
  AND (? IS NULL OR "Substância" = ?)
  AND (? IS NULL OR "Município" = ?)
GROUP BY Ano, "Mês"
ORDER BY Ano, "Mês"
```

### 2. COMEX by Country

```
GET /intelligence/comex/by-country?fluxo=Exportacao&limit=10
→ { rows: [{ pais: "China", valor_fob_usd: 12345678, peso_kg: 99999 }, ...] }
```

### 3. COMEX Monthly Time-Series

```
GET /intelligence/comex/monthly?ano_min=2021&ano_max=2026
→ { rows: [{ ano: 2021, mes: 1, fluxo: "Exportacao", valor_fob_usd: 123456 }, ...] }
```

### 4. RAL by Substance with Value

```
GET /intelligence/ral/top-substancias-value?limit=10
→ { rows: [{ substancia: "Ferro", valor_venda: 123456789, qtd_producao: 9999 }, ...] }
```

### 5. KPI Summary

```
GET /intelligence/kpi-summary
→ {
    usd_brl: { latest: 5.72, delta_30d: -0.012, sparkline: [5.68, 5.71, ...] },
    ferro: { latest: 108.9, delta_prev: 0.031, sparkline: [105.4, 108.9] },
    balanca_ytd: { valor_usd: 2100000000, delta_yoy: -0.12, sparkline: [2400, 2100] },
    cfem_ytd: { valor_brl: 412000000, delta_yoy: 0.08, sparkline: [380, 412] },
    freshness: { ptax: "2026-03-28", cfem: "2026-03-22", comex: "2026-04-01" }
  }
```

### 6. AI Market Summary (SSE)

```
POST /intelligence/ai-summary/stream
Body: { context: <context JSON above> }
→ SSE stream: data: {"text": "chunk..."}\n\n ... data: [DONE]\n\n
```

### 7. AI Status

```
GET /intelligence/ai-status
→ { available: true }
```

### 8. Strategic Minerals (new, uses reference CSV)

```
GET /intelligence/minerals/strategic
→ { rows: [{ substancia: "Niobio", categoria: "Metalicos Estrategicos", estrategico: true }, ...] }
```

---

## URL State Schema

```
/inteligencia-comercial?tab=mercado&metric=ferro-cambio&ano_min=2023&ano_max=2026
```

| Param | Values | Default |
|-------|--------|---------|
| `tab` | `mercado`, `producao`, `territorio` | `mercado` |
| `metric` | Preset key (e.g., `cambio`, `ferro-cambio`, `comex-anual`, `cfem-mensal`, etc.) | First preset of active tab |
| `ano_min` | 2021-2026 | Earliest available |
| `ano_max` | 2021-2026 | Latest available |
| `substancia` | Substance name | — (all) |
| `uf` | UF code | — (all) |

---

## Frontend Component Structure

```
inteligencia-comercial/
├── page.tsx              # Main page: KPI strip, tabs, layout, URL state (replaces current 493 LOC)
├── kpi-strip.tsx         # 4 KPI cards with sparklines (NEW)
├── metric-chart.tsx      # ComposedChart with Select preset, dual Y, Brush (NEW)
├── ai-panel.tsx          # AI insights panel with SSE streaming (NEW)
├── tab-mercado.tsx       # Mercado tab content: metric chart + supporting cards (NEW)
├── tab-producao.tsx      # Producao & Receita tab content (NEW)
├── tab-territorio.tsx    # Territorio tab content (NEW)
└── chart-helpers.ts      # Series configs, color maps, preset definitions (NEW)
```

**Why split:** Current 493 LOC single file → ~7 focused files. Each tab is independently lazy-loadable. The metric chart is reusable across tabs.

---

## Implementation Phases

### Phase A: Foundation (Structure + KPIs + Tab Layout)

**Backend:**
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/kpi-summary` endpoint
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/cfem/time-series` endpoint
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/comex/by-country` endpoint
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/comex/monthly` endpoint
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/ral/top-substancias-value` endpoint
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/minerals/strategic` endpoint

**Frontend:**
- [ ] `web/src/lib/api.ts` — Add fetch functions + types for all new endpoints
- [ ] `web/src/lib/format.ts` — Add `fmtUSD()` formatter for dollar values
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/kpi-strip.tsx` — KPI cards with sparklines
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/page.tsx` — New 3-tab layout with URL state, Suspense wrapper, lazy tab loading
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/tab-mercado.tsx` — Mercado content
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/tab-producao.tsx` — Producao content
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/tab-territorio.tsx` — Territorio content

### Phase B: Metric Selectors + Interactive Charts

- [ ] `web/src/app/(dashboard)/inteligencia-comercial/chart-helpers.ts` — Series configs, preset definitions, color maps
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/metric-chart.tsx` — ComposedChart with Select for presets, dual Y-axis, Brush
- [ ] Wire metric presets into each tab
- [ ] Add Recharts Brush for time-range on time-series charts
- [ ] Add substance classification enrichment to Territorio tab (from `substancias_classificacao.csv`)

### Phase C: GenAI Insights Panel

**Backend:**
- [ ] `api/routers/intelligence.py` — Add `GET /intelligence/ai-status` endpoint
- [ ] `api/routers/intelligence.py` — Add `POST /intelligence/ai-summary/stream` SSE endpoint with structured context
- [ ] System prompt: mining analyst role, Portuguese, cite specific numbers, 3-5 bullet insights

**Frontend:**
- [ ] `web/src/lib/api.ts` — Add `streamMarketSummary()` and `fetchAiStatus()` functions
- [ ] `web/src/app/(dashboard)/inteligencia-comercial/ai-panel.tsx` — Streaming display, "Gerar Analise" button, cache per context, loading skeleton, graceful fallback when unavailable
- [ ] Integrate into page layout: 65/35 split on desktop, collapsed accordion on mobile
- [ ] Auto-hide panel when `ai-status.available === false`

### Phase D: Polish + Cross-Page Links

- [ ] Source attributions on all charts (`Fonte: ANM, BCB, Comex Stat`)
- [ ] Data freshness indicator in page footer
- [ ] Click handlers on chart bars → navigate to relevant filtered pages (Concessoes, Prospeccao)
- [ ] Cross-page inbound links from Prospeccao ("Ver inteligencia de mercado para Ferro")
- [ ] Mobile responsive: horizontal-scroll KPI strip, stacked cards, collapsed AI panel
- [ ] Empty states for all data sections
- [ ] Loading skeletons per component

---

## Acceptance Criteria

### Functional

- [ ] Page loads with KPI strip showing 4 headline numbers with sparklines and delta indicators
- [ ] 3 tabs (Mercado, Producao & Receita, Territorio) — no content lost from old 4 tabs
- [ ] Each tab has a metric selector (Select dropdown) with 3-5 presets
- [ ] ComposedChart supports dual Y-axes when mixing units (USD + BRL, R$ + %)
- [ ] CFEM time-series chart shows monthly data from 2022-2026 with Brush
- [ ] COMEX chart shows export vs import by year and by country
- [ ] AI Insights panel streams a narrative summary when "Gerar Analise" is clicked
- [ ] AI panel gracefully hidden when API key not configured (chart expands to 100%)
- [ ] Tab state persisted in URL (`?tab=producao&metric=cfem-mensal`)
- [ ] All charts have "Fonte:" attribution

### Non-Functional

- [ ] Page initial load: < 2s with skeleton states (no blank screens)
- [ ] No build errors (`npm run build`)
- [ ] No new lint warnings
- [ ] Responsive: works on 375px (mobile) through 1920px (desktop)
- [ ] AI summary cached per context key — no redundant LLM calls

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Commodity CSV too sparse for meaningful sparklines | KPI #2 shows flat line | Show only latest price + text delta, no sparkline for sparse data |
| CFEM `ValorRecolhido` parsing issues (BR format strings) | Incorrect totals | Reuse existing `TRY_CAST(REPLACE(...))` pattern from current endpoints |
| AI cost accumulation | $0.003/call × many users | Manual trigger + caching + debounce. Monitor via Anthropic dashboard. |
| Anthropic API rate limits (429) | AI panel shows error | Show "Tente novamente em alguns segundos" with retry button |
| COMEX data delay (monthly publication) | Stale trade balance | Show freshness timestamp. Data is inherently delayed. |

---

## Files Changed (Estimated)

| Action | File | LOC |
|--------|------|-----|
| REWRITE | `web/src/app/(dashboard)/inteligencia-comercial/page.tsx` | ~200 (from 493) |
| CREATE | `inteligencia-comercial/kpi-strip.tsx` | ~120 |
| CREATE | `inteligencia-comercial/metric-chart.tsx` | ~180 |
| CREATE | `inteligencia-comercial/ai-panel.tsx` | ~150 |
| CREATE | `inteligencia-comercial/tab-mercado.tsx` | ~150 |
| CREATE | `inteligencia-comercial/tab-producao.tsx` | ~150 |
| CREATE | `inteligencia-comercial/tab-territorio.tsx` | ~130 |
| CREATE | `inteligencia-comercial/chart-helpers.ts` | ~100 |
| MODIFY | `api/routers/intelligence.py` | +200 (6 new endpoints) |
| MODIFY | `web/src/lib/api.ts` | +80 (new fetch functions) |
| MODIFY | `web/src/lib/format.ts` | +10 (fmtUSD) |
| **Total** | | **~1,470 new / 493 replaced = ~+977 net** |

---

## Out of Scope (Deferred)

- News feed / RSS aggregation — requires greenfield data pipeline, defer to future sprint
- Commodity price auto-collection — requires external API integration
- React Query / SWR caching layer — beneficial but not blocking
- Dark mode toggle — CSS vars exist, no UI yet
- Export to PDF/Excel from intelligence page
- Admin panel for commodity price uploads
