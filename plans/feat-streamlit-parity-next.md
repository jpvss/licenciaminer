# Feature Parity: Streamlit → Next.js — Comprehensive Audit

Last updated: 2026-04-01
Excludes: auth, multi-tenant, LLM chat sidebar (deferred).

---

## Methodology

Deep page-by-page audit comparing every widget, chart, filter, metric, table, and interaction in all 15 Streamlit pages against their 12 Next.js equivalents. Each gap categorized by user impact and whether it's a true regression vs. an intentional simplification.

---

## Page Map

| # | Streamlit Page | Next.js Route | Status |
|---|---------------|--------------|--------|
| 1 | `home.py` (Painel Principal) | `/` (dashboard page) | Merged — Next.js combines home + visão geral |
| 2 | `1_visao_geral.py` (Base de Dados) | `/` (dashboard page) | Merged into same page |
| 3 | `2_explorar_dados.py` (Explorar Licenças) | `/explorar` | ✅ Parity |
| 4 | `3_consulta.py` (Consulta por Empresa) | `/empresa` | Partial |
| 5 | `4_analise_decisoes.py` (Análise de Risco) | `/decisoes` | Partial |
| 6 | `due_diligence.py` (Due Diligence) | `/due-diligence` | Partial |
| 7 | `5_concessoes.py` (Base de Concessões) | `/concessoes` | ✅ Near-parity |
| 8 | `6_mapa_concessoes.py` (Mapa) | `/mapa` | ✅ Parity (upgrade: MapLibre vs Folium) |
| 9 | `viabilidade.py` (Viabilidade) | `/empresa` tab "Por Projeto" | ✅ Upgraded (Streamlit was placeholder, Next.js is functional) |
| 10 | `7_prospeccao.py` (Prospecção) | `/prospeccao` | Partial |
| 11 | `inteligencia_comercial.py` | `/inteligencia-comercial` | Partial |
| 12 | `monitoramento.py` | `/monitoramento` | ✅ Both placeholders |
| 13 | `mineradora_modelo.py` | `/mineradora-modelo` | Partial |
| 14 | `gestao_interna.py` | `/gestao-interna` | ✅ Both placeholders |

---

## Completed Work (for reference)

- ✅ Sidebar nav — 5 grouped sections with color-coded labels, disabled states, trust footer
- ✅ Dashboard — 4 KPIs, ComposedChart (dual-axis), insights sidebar, data sources, methodology
- ✅ Explorar Dados — dataset selector, 6 filters, filter chips, COLUMN_CONFIG formatting, paginated table, inline detail, CSV export, parecer accordion
- ✅ Consulta Empresa — 2 tabs (CNPJ + Projeto), example CNPJs, dossier profile with KPIs + 6 accordion sections + PDF download
- ✅ Viabilidade tab — donut chart, comparison bar, sample-size warning, case cards, example presets
- ✅ Análise Decisões — 7 tabs (trend, regional, modalidade, yearly+class, risk, caso detalhado, CMI), reference lines
- ✅ Due Diligence — 4-step wizard, document checklist, live scoring, ConformityGauge, recommendations, PDF
- ✅ Concessões — MultiSelect filters, KPIs, paginated table, inline detail, regime labels
- ✅ Mapa — MapLibre with polygon popups, UC/TI layers, color-by, legend, filter sidebar
- ✅ Prospecção — 3 tabs (oportunidades/empresas/municípios), score filter, cross-nav to concessões
- ✅ Inteligência Comercial — 4 tabs (PTAX, comex, arrecadação, território), Recharts
- ✅ Mineradora Modelo — 7 sector tabs, KPI cards + delta, AreaChart with target reference
- ✅ DataTable — pagination, column toggle, horizontal scroll, sticky headers
- ✅ RecordDetail — SEMAD record card with documents, parecer text, portal link
- ✅ Cross-page navigation — Prospecção→Concessões, Decisões→Explorar, URL params
- ✅ PDF report download with progress steps + risk level

---

## Remaining Gaps

### P0 — High Impact (user-visible regressions)

#### Gap A: Dashboard — Dynamic Insights from Live Data
**Streamlit** calculates 4 insight cards from live SQL queries:
1. Mining vs general approval rate comparison (with % difference)
2. Worst class (lowest approval rate, with N)
3. Most rigorous regional (with rate)
4. Companies with 6+ infractions that also have SEMAD decisions

**Next.js** shows 4 simplified insight cards that just format numbers from `OverviewStats` — no cross-dataset analytics.

**Why it matters**: The insights are the "executive summary" value-add. Without them, the dashboard is just numbers.

**Fix**:
- Backend: Add `GET /api/overview/insights` endpoint that returns computed insights (worst class, worst regional, infraction correlation, mining vs general)
- Frontend: [page.tsx](web/src/app/(dashboard)/page.tsx) — replace static InsightCard data with API-driven content
- Effort: Small-Medium

#### Gap B: Dashboard — Data Sources Table with Live Metadata
**Streamlit** shows a dynamic table with **16 sources**, 4 columns (Fonte, Registros, Atualização, Link), green/red status dots, live record counts from `collection_metadata.json` + parquet row fallback, and "verificar ↗" links to each source URL.

**Next.js** has a hardcoded `DATA_SOURCES` array with only **9 rows** and 3 columns (Fonte, Tipo, Cobertura) — no record counts, no dates, no status dots, no links.

Missing sources in Next.js: IBAMA Infrações, ANM CFEM, ANM RAL, Receita Federal CNPJ, COPAM CMI, ICMBio UCs, FUNAI TIs, IBGE Biomas, Sobreposições Espaciais, ANM SCM, Concessões MG Consolidadas.

**Fix**:
- Backend: Add `GET /api/meta/sources` endpoint that reads `collection_metadata.json` and returns `{name, records, last_collected, url}[]` for all 16 sources (reuse logic from `get_source_info()` in `data_loader.py:106`)
- Frontend: [page.tsx](web/src/app/(dashboard)/page.tsx) — replace `DATA_SOURCES` constant with API fetch. Table columns: status dot + Fonte | Registros (right-aligned, formatted) | Atualização (date) | Link ("verificar ↗")
- Effort: Small-Medium

#### Gap C: Decisões — Missing Heatmap & Risk Factor Charts
**Streamlit Tab 2 "Fatores de Risco"** has 4 rich analysis sections:
1. Classe × Modalidade heatmap (2D approval rates with N counts)
2. CFEM profiles — 4 insight cards showing CFEM payment bands vs approval
3. Reincidência — approval rates by company decision-count bands
4. Arquivamento — top 10 classe×atividade combos by archive rate

**Next.js Tab 5 "Fatores de Risco"** has only 2 charts (infraction bands bar + scatter plot).

**Why it matters**: The heatmap is the signature analytics view — consultants use it to estimate approval probability for a specific classe+modalidade.

**Fix**:
- Frontend: [decisoes/page.tsx](web/src/app/(dashboard)/decisoes/page.tsx) — add heatmap (Recharts doesn't have native heatmap; use a grid of colored cells or a custom SVG). Add CFEM profiles + reincidência cards.
- Backend: May need `GET /api/decisions/heatmap` endpoint for classe×modalidade matrix, and `GET /api/decisions/cfem-profiles` for CFEM analysis
- Effort: Medium-Large

#### Gap D: Due Diligence Step 4 — Missing Result Tabs
**Streamlit** Step 4 has 4 tabs:
1. Visão Geral — config summary, 4 KPI cards, conformity scale legend
2. Por Documento — per-document scores with color + detail counts
3. Recomendações — grouped by priority (Alta red, Média orange) with truncation at 20
4. Contexto Histórico — approval rate for activity/class + CNPJ infraction check

**Next.js** Step 4 shows: score hero + 4 KPI cards + flat recommendation list + new evaluation button. Missing 3 of the 4 tabs.

**Fix**:
- Frontend: [due-diligence/page.tsx](web/src/app/(dashboard)/due-diligence/page.tsx) — add Tabs in Step 4 with: per-document breakdown, conformity scale legend, historical context section
- Backend: Reuse existing `/api/decisions/approval-rates` for historical context
- Effort: Medium

---

### P1 — Medium Impact (polish & completeness)

#### Gap E: Prospecção — Missing RAL Context Section
**Streamlit** has a "Contexto de Produção Mineral — MG" section after all 3 view modes showing RAL (Annual Mineral Production Report) data: substances, last year, years with data.

**Next.js** has no RAL section at all.

**Fix**:
- Backend: Check if `/api/intelligence/ral` or similar exists; if not, add `GET /api/prospeccao/ral-context`
- Frontend: [prospeccao/page.tsx](web/src/app/(dashboard)/prospeccao/page.tsx) — add RAL section below tabs
- Effort: Small

#### Gap F: Prospecção — Empresa Portfolio Expansion Incomplete
**Streamlit** "Análise por Empresa" tab: click a company row → shows full table of their concessions (processo, regime, substância, município, área, CFEM).

**Next.js**: click row → `expandedEmpresa` state toggles but shows minimal content ("Selecione esta aba para carregar dados" empty state or basic info).

**Fix**:
- Frontend: [prospeccao/page.tsx](web/src/app/(dashboard)/prospeccao/page.tsx) — when `expandedEmpresa` is set, fetch company's concessions from API and render table
- Effort: Small

#### Gap G: Inteligência Comercial — Commodity Prices Not Rendered
**Streamlit** reads `commodity_prices.csv` and displays individual `st.metric()` for each mineral (gold, iron ore, etc.) in Tab 1.

**Next.js** API endpoint `/intelligence/commodities` exists in `api.ts` but the component never calls it or renders the data.

**Fix**:
- Frontend: [inteligencia-comercial/page.tsx](web/src/app/(dashboard)/inteligencia-comercial/page.tsx) MercadoTab — fetch commodities, display as StatCard grid below PTAX chart
- Effort: Small

#### Gap H: Mineradora Modelo — Chart Min/Max Band + Delta Inversion
**Streamlit** charts show a shaded red band between min/max boundaries. Plus: delta color is inverted for cost/time KPIs (higher = bad → red).

**Next.js** only shows target as ReferenceLine, no min/max band. Delta always uses simple positive=green logic.

**Fix**:
- Frontend: [mineradora-modelo/page.tsx](web/src/app/(dashboard)/mineradora-modelo/page.tsx):
  - KPIChart: Add Recharts `<Area>` for min/max band (semi-transparent red)
  - KPICard: Add `invertDelta` prop based on KPI name list (matching Streamlit's INVERTED_DELTA list: "Ciclo de Transporte", "Consumo de Diesel", "MTTR", "Custo por Tonelada", etc.)
- Effort: Small

#### Gap I: Concessões — CSV Export + Strategic Minerals Toggle
**Streamlit** has:
1. CSV download button (conditional on <20k rows)
2. "Minerais estratégicos" toggle filter

**Next.js** has neither.

**Fix**:
- Frontend: [concessoes/page.tsx](web/src/app/(dashboard)/concessoes/page.tsx) — add export URL button (pattern from explorar), add strategic checkbox to filter card
- Effort: Small

#### Gap J: Explorar Dados — UF Filter for IBAMA + Source Attribution
**Streamlit** has:
1. UF filter specifically for IBAMA infractions dataset (MG/Todos)
2. Source attribution footer on each section

**Next.js** is missing both.

**Fix**:
- Frontend: [explorar/page.tsx](web/src/app/(dashboard)/explorar/page.tsx) — add conditional UF select when dataset is `v_ibama_infracoes`. Add source text captions.
- Effort: Small

---

### P2 — Low Impact (nice-to-have, cosmetic)

#### Gap K: Data Freshness Indicator in Sidebar
**Streamlit** sidebar shows "Dados: YYYY-MM-DD" with green dot from metadata.

**Next.js** sidebar has trust text but no date.

**Fix**: Backend `GET /api/meta/freshness` → sidebar footer shows date.
Effort: Trivial

#### Gap L: Dashboard — Source Attribution Under Each Metric
**Streamlit** shows source + date below each metric card.

**Next.js** StatCards have subtitles but not source attribution.

**Intentional?** Potentially — the Next.js design is cleaner. Recommend: skip unless user asks.

#### Gap M: Caso Detalhado (Decisões Tab 6) — Missing Case Card Expandables
**Streamlit** "Caso Detalhado" decision history shows expandable cards with Portal SEMAD links + lazy-loaded parecer text per decision.

**Next.js** shows scrollable list with decision badges + metadata but no individual expansion or parecer preview.

**Fix**: Add `<Collapsible>` per decision row with portal link + optional parecer fetch.
Effort: Small-Medium

#### Gap N: Due Diligence Step 2 — Missing Progress Bar
**Streamlit** shows a progress bar (X% complete) based on presented document count.

**Next.js** shows "X apresentados · Y parciais · Z pendentes" text summary but no visual bar.

**Fix**: Add `<Progress>` shadcn component.
Effort: Trivial

#### Gap O: Map Polygon Click → Concessões Navigation
**Streamlit** doesn't have this, but it was noted as a desired enhancement.

**Next.js** map has click popups but doesn't navigate to `/concessoes?search=<processo>`.

**Fix**: Add "Ver detalhes" link in popup → navigates to concessões.
Effort: Trivial

---

## Navigation Structure Differences

Streamlit has **15 nav items** across 5 sections. Next.js has **12 nav items** across 5 sections. The 3 "missing" items are intentional:

| Streamlit Item | Why Not in Next.js Nav | Where It Went |
|---|---|---|
| **"Painel Principal" (home.py)** + **"Base de Dados" (visão_geral.py)** | Streamlit had two separate pages: a landing page and an overview. Redundant. | Merged into single `/` dashboard page |
| **"Análise de Viabilidade" (viabilidade.py)** | Was a placeholder stub ("Em Construção") in Streamlit. | Became a functional tab inside `/empresa` ("Por Projeto") — better workflow since it's used alongside company dossier |

Both are **upgrades**, not regressions. The sidebar structure at `sidebar-nav.tsx` correctly maps all active business units.

---

## Intentional Differences (Not Gaps)

These differ from Streamlit **by design** — the Next.js version is better or equivalent:

| Difference | Streamlit | Next.js | Why Keep Next.js Version |
|-----------|-----------|---------|-------------------------|
| Filter layout | Sidebar | Inline cards | Better for responsive/mobile |
| Year filter | Range slider | Two number inputs | Equivalent, works on mobile |
| Toggle vs Checkbox | st.toggle | Checkbox | Standard web pattern |
| Chart library | Plotly | Recharts | Lighter, SSR-friendly |
| Map library | Folium (iframe) | MapLibre (native) | Smoother interactions, no iframe |
| Viabilidade | Placeholder stub | Full functional tab | Upgrade |
| Loading states | None (Streamlit cache) | Skeleton loaders | Better UX |
| Detail panels | Section-based | Animated inline cards | More polished |
| Case display | HTML cards | Table rows with badges | Equivalent density, cleaner |
| SQL query display | st.expander with code | Not shown | Intentional — end users don't need SQL |
| CSV upload (commodities) | File uploader | Not available | Admin feature, deferred to admin panel |

---

## Deferred (Not Part of Feature Parity)

| Feature | Reason |
|---------|--------|
| Auth + multi-tenant (Supabase) | User decision — deferred |
| LLM chat sidebar | Future phase (WebSocket endpoint ready) |
| Commodity price CSV upload | Admin feature, not user-facing |
| Parecer extraction (regex+LLM) | Separate plan: `plans/feat-parecer-extraction.md` |
| Data collection runs (Gap 7) | Runtime ops, not code: `collect mg-docs`, `collect mg-textos` |

---

## Execution Order

Prioritized by user-visible impact per unit of effort:

| # | Gap | Priority | Effort | Files Touched |
|---|-----|----------|--------|---------------|
| 1 | **Gap A**: Dashboard dynamic insights | P0 | S-M | page.tsx, api.ts, 1 backend endpoint |
| 2 | **Gap B**: Dashboard live source table | P0 | S | page.tsx, api.ts, 1 backend endpoint |
| 3 | **Gap D**: DD Step 4 result tabs | P0 | M | due-diligence/page.tsx |
| 4 | **Gap C**: Decisões heatmap + risk factors | P0 | M-L | decisoes/page.tsx, api.ts, 1-2 backend endpoints |
| 5 | **Gap H**: Mineradora min/max band + delta | P1 | S | mineradora-modelo/page.tsx |
| 6 | **Gap G**: Commodity prices rendering | P1 | S | inteligencia-comercial/page.tsx |
| 7 | **Gap F**: Prospecção empresa expansion | P1 | S | prospeccao/page.tsx |
| 8 | **Gap E**: Prospecção RAL context | P1 | S | prospeccao/page.tsx, 1 backend endpoint |
| 9 | **Gap I**: Concessões export + strategic toggle | P1 | S | concessoes/page.tsx |
| 10 | **Gap J**: Explorar UF filter + source text | P1 | S | explorar/page.tsx |
| 11 | **Gap K**: Sidebar freshness indicator | P2 | T | sidebar-nav.tsx, 1 backend endpoint |
| 12 | **Gap M**: Caso Detalhado expandables | P2 | S-M | decisoes/page.tsx |
| 13 | **Gap N**: DD Step 2 progress bar | P2 | T | due-diligence/page.tsx |
| 14 | **Gap O**: Map click → Concessões nav | P2 | T | mining-map.tsx |

**Estimated total**: ~3-4 focused sessions to reach true ~98% parity.

---

## New Backend Endpoints Needed

| Endpoint | Purpose | Gap |
|----------|---------|-----|
| `GET /api/overview/insights` | Computed dashboard insights (worst class, worst regional, infraction correlation) | A |
| `GET /api/meta/sources` | Source metadata with record counts + last_collected dates | B |
| `GET /api/decisions/heatmap` | Classe × Modalidade approval rate matrix | C |
| `GET /api/decisions/cfem-profiles` | CFEM payment bands vs approval rates | C |
| `GET /api/decisions/reincidencia` | Approval rates by company decision-count bands | C |
| `GET /api/prospeccao/ral-context` | RAL substance summary for MG | E |
| `GET /api/meta/freshness` | Data last-update timestamps per source | K |

---

## Verification Checklist

1. **Visual comparison**: Screenshot each Streamlit page → match in Next.js
2. **Feature checklist**: Every gap above verified as closed or intentionally skipped
3. **Data parity**: Same query on both apps returns identical results
4. **Mobile**: All pages responsive (Streamlit is not — this is an upgrade)
5. **Performance**: Page loads < 2s, chart renders < 1s
6. **Build**: `next build` passes clean with all pages as static
