# Full Streamlit → Next.js Migration Plan

## Overview

Complete migration of all 14 Streamlit pages to the Next.js 16 + FastAPI stack. The Streamlit app is significantly richer than the current Next.js frontend — this plan closes the gap to full feature parity, then exceeds it with better interactivity (MapLibre maps, TanStack tables, streaming chat).

**Current state:** 5 functional pages + 2 stubs in Next.js, 34 API endpoints.
**Target state:** 12 functional pages, ~55 API endpoints, full feature parity + improvements.

---

## Architecture Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Data tables | @tanstack/react-table + shadcn Table | Official shadcn pattern, sorting/filtering/expansion/export |
| Maps | react-map-gl + MapLibre GL JS | WebGL, free, handles 5K+ polygons, no API key |
| Charts | Recharts (primary) + @nivo/heatmap (selective) | Already installed, shadcn-native |
| Formatting | Frontend `lib/format.ts` utilities | Backend returns raw values, charts need numbers |
| DD wizard state | localStorage with auto-save | Survives refresh, no auth needed |
| PDF storage | Sync generation with streaming response | Simple, no polling, no memory leak |
| Geospatial delivery | Simplified GeoJSON via API endpoint | Start simple, upgrade to vector tiles if needed |
| CSV export | Streaming backend endpoint | Client can't paginate 20K rows efficiently |

---

## Phase 0: Backend Gaps (Before Frontend Work)

**Must be completed first — frontend pages are blocked without these endpoints.**

### 0.1 Fix Existing Bugs

#### Fix explorer search (CRITICAL)
`api/routers/explorer.py:51-66` — search implementation clears all WHERE clauses, returning unfiltered results.

**Fix:** Build search as an additional WHERE clause (not a replacement), using parameterized LIKE across VARCHAR columns.

#### Fix explorer SELECT * (CRITICAL)
`api/routers/explorer.py` returns `SELECT *` including heavy text columns (`texto_documentos`, `documentos_pdf` — up to 8KB per row).

**Fix:** Exclude heavy columns from list response. Add column exclusion list per view.

#### Fix report store memory leak
`api/routers/reports.py` — `_report_store` dict accumulates PDFs in memory forever.

**Fix:** Replace async polling with synchronous streaming: `POST /report/{cnpj}/generate` returns PDF bytes directly via `StreamingResponse`. Remove job store entirely. Add timeout (60s max).

#### Tighten CORS
`api/main.py:44` — regex `r"https://.*\.(vercel\.app|railway\.app)$"` matches ANY Vercel/Railway app.

**Fix:** Use exact origins:
```python
allow_origins=[
    "http://localhost:3000",
    "https://summo-quartile.vercel.app",
    "https://licenciaminer-production.up.railway.app",
]
```

### 0.2 New Endpoints Needed

#### Explorer enhancements
```
GET  /api/explorer/{dataset}/{detail_id}     → Single record by detail_id (full fields)
GET  /api/explorer/{dataset}/{detail_id}/text → Parecer text only (lazy load)
GET  /api/explorer/{dataset}/export.csv       → Streaming CSV (max 20K rows, excludes text cols)
```

#### Concessoes router (new)
```
GET  /api/concessoes                → Filtered list (regime[], categoria[], substancia[], municipio[], cfem_status, estrategico, search, limit, offset)
GET  /api/concessoes/stats          → 4 KPIs (total, cfem_ativas, substancias, municipios)
GET  /api/concessoes/{processo}     → Single concession detail
```

#### Geospatial router (new)
```
GET  /api/geo/concessoes            → Simplified GeoJSON (filters: regime[], categoria[], substancia[], cfem_status, color_by; max 5000 features; tolerance param)
GET  /api/geo/restrictions/ucs      → UC polygons (simplified)
GET  /api/geo/restrictions/tis      → TI polygons (simplified)
```

**Implementation:** Load parquet geometries via GeoPandas in DuckDB, simplify with `ST_Simplify(geom, tolerance)`, convert to GeoJSON `FeatureCollection`. Response size target: <2MB for 5000 features.

#### Prospeccao router (new)
```
GET  /api/prospeccao/opportunities  → Scored list (filters: min_score, regime[], categoria[], estrategico; limit, offset)
GET  /api/prospeccao/portfolio      → Company portfolio analysis (top 100 by concession count)
GET  /api/prospeccao/by-municipality → Substance concentration by municipality (top 30)
GET  /api/prospeccao/export.csv     → Scored shortlist CSV
```

**Scoring SQL** (port from `7_prospeccao.py`):
```sql
SELECT *,
  (CASE WHEN ativo_cfem IS NULL OR ativo_cfem = false THEN 30 ELSE 0 END
   + CASE WHEN estrategico = 'sim' THEN 25 ELSE 0 END
   + CASE WHEN AREA_HA > 500 THEN 15 WHEN AREA_HA > 100 THEN 8 ELSE 0 END
   + CASE WHEN cfem_total IS NULL OR cfem_total = 0 THEN 15 ELSE 0 END
   + CASE WHEN categoria IN ('Preciosos','Estratégicos') THEN 15
         WHEN categoria IN ('Ferrosos','Não-Ferrosos') THEN 8 ELSE 0 END
  ) AS score
FROM v_concessoes
WHERE score >= :min_score
ORDER BY score DESC
```

#### Intelligence router (new)
```
GET  /api/intelligence/ptax         → BCB USD/BRL time series
GET  /api/intelligence/comex        → Comex Stat export/import by year
GET  /api/intelligence/cfem/top-municipios → Top 15 CFEM municipalities
GET  /api/intelligence/cfem/top-substancias → Top 10 CFEM substances
GET  /api/intelligence/ral/producao → RAL production by substance
GET  /api/intelligence/anm/fases    → ANM processes by FASE
```

#### Simulator router (new)
```
GET  /api/simulator/sectors         → List of 7 sectors with KPI definitions
GET  /api/simulator/data            → 24-month simulated data (pre-generated on startup, cached)
```

#### Overview enhancements
```
GET  /api/overview/sources          → Data sources table (16+ sources, row counts, freshness, URLs)
GET  /api/overview/insights         → 4 insight cards (mining vs general, hardest class, strictest regional, infraction correlation)
```

**Total new endpoints: ~21. Total after: ~55.**

### 0.3 Frontend Utilities Needed

#### `web/src/lib/format.ts` — Brazilian formatting
```typescript
export const fmtBR = (n: number, decimals = 0) =>
  n.toLocaleString("pt-BR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

export const fmtReais = (n: number) =>
  n.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export const fmtPct = (n: number) =>
  `${n.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`;

export const fmtDate = (d: string) => {
  const date = new Date(d);
  return date.toLocaleDateString("pt-BR");
};

export const fmtHa = (n: number) =>
  `${fmtBR(n, 1)} ha`;
```

#### New npm dependencies
```bash
cd web
npm install @tanstack/react-table react-map-gl maplibre-gl
npx shadcn@latest add dialog accordion dropdown-menu checkbox radio-group progress command
```

---

## Phase 1: Enhance Existing Pages (Week 1)

### 1.1 Data Explorer Overhaul (`/concessoes` → rename to `/explorar`)

**Current:** Basic dataset selector + raw table + pagination.
**Target:** Full-featured explorer matching Streamlit's `2_explorar_dados.py`.

#### New components needed:
- `web/src/components/data-table.tsx` — Reusable TanStack table with sorting, column visibility, row expansion
- `web/src/components/data-table-toolbar.tsx` — Filter bar (search input + dataset-specific filter dropdowns)
- `web/src/components/record-detail.tsx` — Detail panel for clicked row (Sheet or inline expansion)
- `web/src/components/document-links.tsx` — Parse and render `documentos_pdf` field

#### Features:
1. **Dataset selector** — dropdown with all available views (from `/api/explorer/datasets`)
2. **Sidebar filters** (conditionally rendered by dataset):
   - All datasets: text search across VARCHAR columns
   - `v_mg_semad`: decision type, classe (1-6), year range slider, mining-only toggle
   - `v_ibama_infracoes`: UF filter
3. **TanStack table** with:
   - Sortable columns (click header)
   - Column visibility toggle (DropdownMenu with checkboxes)
   - Hidden heavy columns (`texto_documentos`, `documentos_pdf`, `documents_str`)
   - Formatted cells: numbers (pt-BR), dates (DD/MM/YYYY), badges for `decisao`
   - Pagination (50/page) with "1-50 de 7,932" display
4. **Row click → detail panel** (Sheet from right, 480px):
   - Record header: empreendimento + decision badge
   - CNPJ (monospace), atividade, classe, modalidade, regional, municipio, ano
   - Portal link: `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/view-externo?id={detail_id}`
   - Document links: parse `documentos_pdf` ("name|url;name|url") → clickable list with icons
   - Parecer text: Accordion that lazy-loads from `/api/explorer/{dataset}/{detail_id}/text`
5. **CSV export** button — triggers `/api/explorer/{dataset}/export.csv` (streaming download, max 20K)
6. **Empty states** — dataset not selected, no results, loading skeletons

#### Edge cases:
- Dataset change: close detail panel, reset filters, reset page to 0
- Row click on non-SEMAD dataset: show simpler detail (no portal link, no documents)
- Export disabled if total > 20,000 (show "Refine seus filtros")

### 1.2 Company Dossier Enhancement (`/empresa`)

**Current:** CNPJ search → profile header + 4 KPIs + findings + decision table.
**Target:** Full dossier matching Streamlit's `3_consulta.py`.

#### Missing sections to add:

1. **IBAMA Infractions detail** — expandable table below KPI cards
   - Columns: Data, Tipo, Municipio, Valor (R$), Descricao (80 chars), Status, Cancelado
   - Data from existing `/api/empresa/{cnpj}` response (infractions array)
   - Red accent if >= 3 infractions

2. **CFEM Payments detail** — expandable table
   - Columns: Ano, Substancia, Meses, Total (R$)
   - Data from `/api/empresa/{cnpj}` response (cfem array)

3. **ANM Titulos table** — expandable section
   - Columns: Processo, Fase, Substancia, Area (ha), Ano
   - Data from `/api/empresa/{cnpj}/anm`

4. **Outras Filiais section** — same CNPJ root (8 digits), different branches
   - Show CNPJ, decision count, sample empreendimento
   - "Pesquise o CNPJ da filial para ver dossiê completo"

5. **PDF Report button** — "Gerar Relatório PDF"
   - Calls `POST /api/report/{cnpj}/generate`
   - Shows loading spinner: "Gerando relatório (10 fontes, 8 seções)..."
   - On success: triggers download of `relatorio_{cnpj}_{YYYYMMDD}.pdf`
   - Shows risk level badge after generation

6. **Portal links** on decision table rows
   - Each row links to SEMAD portal: `view-externo?id={detail_id}`

7. **"Por Projeto" tab** (new)
   - Inputs: activity code (A-01 to A-07), classe (1-6), regional
   - Shows: contextual approval stats, comparison bar vs. state average, similar cases carousel
   - Donut chart for approval distribution

### 1.3 Decisões Analytics Polish (`/decisoes`)

**Current:** 4 KPIs + 4 chart tabs. Largely complete.
**Minor additions:**
- Add filter controls (activity, classe, regional) above tabs
- Add data export button per chart
- Add Classe vs. Approval Rate chart (from Tab 2 of Streamlit's risk factors)
- Add Infractions vs. Approval scatter/bubble chart

---

## Phase 2: New Core Pages (Week 2)

### 2.1 Base de Dados Dashboard (new route: `/dados`)

**Maps to:** Streamlit's `1_visao_geral.py`

#### Layout:
1. **4-column KPI cards:**
   - Decisões SEMAD: total count + source date
   - Processos ANM: MG count
   - Infrações IBAMA: MG count
   - Aprovação Mineração: rate % + N decisions
2. **Two-column section:**
   - Left: Approval rate trend chart (ComposedChart — Line for rate + Bar for count, YAxis dual)
   - Right: 4 insight cards (colored left border, expandable)
3. **Data sources table:**
   - 16+ rows: Source name, type, records, last collected (freshness dot), URL link
   - Freshness: green (< 7 days), amber (< 30 days), red (> 30 days)
4. **Methodology accordion** — "Sobre" section

#### API calls:
- `GET /api/overview/stats` (existing)
- `GET /api/overview/trend` (existing)
- `GET /api/overview/sources` (new)
- `GET /api/overview/insights` (new)

### 2.2 Concessões Table (new route: `/concessoes-base`)

**Maps to:** Streamlit's `5_concessoes.py`

#### Layout:
1. **4 KPI cards** — total, CFEM ativas, substâncias, municípios
2. **Filter sidebar** (Sheet on mobile, inline on desktop):
   - Text search
   - Multi-select: regime (with labels), categoria, substância (limit 200), município (limit 300)
   - CFEM status radio: Todos / Ativo / Inativo
3. **TanStack table** — processo, titular, substância, categoria, regime (with label), área (ha), CFEM badge
4. **Row click → detail panel** (Sheet):
   - Titular, processo, CNPJ, regime label
   - Área total, CFEM status + total paid
   - Strategic status, mineral category
   - Link to map page (filtered to this concession)

#### API calls:
- `GET /api/concessoes/stats` (new)
- `GET /api/concessoes` (new, with filters)
- `GET /api/concessoes/{processo}` (new)

### 2.3 Geospatial Map (`/mapa` — replace stub)

**Maps to:** Streamlit's `6_mapa_concessoes.py`

#### Implementation:
1. **MapLibre GL** via react-map-gl (dynamic import, ssr: false)
2. **Base map:** OpenFreeMap liberty style (free, no API key)
3. **Initial view:** MG center (-19.9, -43.9), zoom 6
4. **Concession layer:**
   - Source: GeoJSON from `/api/geo/concessoes`
   - Fill + outline layers
   - Color by: `match` expression based on selected color-by property
   - Color palettes (port from Streamlit):
     - Categoria: Ferrosos(red), Preciosos(orange), Estratégicos(golden), etc.
     - Regime: portaria_lavra(orange), licenciamento(blue), plg(golden)
     - FASE: CONCESSÃO(orange), LICENCIAMENTO(blue), PESQUISA(green)
     - CFEM: ativo(green), inativo(red)
5. **Restriction layers** (toggle via checkboxes):
   - UCs: green fill (15% opacity), from `/api/geo/restrictions/ucs`
   - TIs: red fill (15% opacity), from `/api/geo/restrictions/tis`
6. **Interactions:**
   - Click polygon → Popup with processo, titular, substância, área, FASE
   - Mobile: bottom sheet instead of popup
   - Hover: highlight polygon outline
7. **Sidebar filters:** regime, categoria, substância, CFEM, strategic, color-by selector
8. **4 KPI cards** above map: polygons shown, enriched, substances, total area
9. **Legend** — dynamic based on color-by selection
10. **Performance:**
    - Cap at 5,000 features (warning if more)
    - Simplification tolerance param sent to API
    - Map preserves viewport on filter changes

#### New components:
- `web/src/components/mining-map.tsx` — MapLibre wrapper
- `web/src/components/map-popup.tsx` — Concession popup content
- `web/src/components/map-legend.tsx` — Dynamic color legend
- `web/src/components/map-filters.tsx` — Sidebar filter panel

### 2.4 Prospecção (`/prospeccao` — replace stub)

**Maps to:** Streamlit's `7_prospeccao.py`

#### Layout:
1. **View switcher** (Tabs): Top Oportunidades | Por Empresa | Por Município
2. **Filter sidebar:**
   - Score mínimo slider (0-100, default 30)
   - Regime multi-select
   - Categoria multi-select
   - Apenas estratégicos toggle
3. **Top Oportunidades view:**
   - 4 KPI cards: opportunities count, avg score, strategic minerals, total area
   - TanStack table: processo, titular, substância, categoria, regime, área, score, motivo
   - Score badge (color-coded: green >=70, amber >=40, red <40)
   - CSV export button
4. **Por Empresa view:**
   - Table: titular, # concessões, avg score, total area
   - Click → expands to show company's concessions
5. **Por Município view:**
   - Table: município, top substances, count, total area

#### API calls:
- `GET /api/prospeccao/opportunities` (new)
- `GET /api/prospeccao/portfolio` (new)
- `GET /api/prospeccao/by-municipality` (new)
- `GET /api/prospeccao/export.csv` (new)

---

## Phase 3: Intelligence & Simulator Pages (Week 3)

### 3.1 Inteligência Comercial (new route: `/inteligencia`)

**Maps to:** Streamlit's `inteligencia_comercial.py`

#### 4-tab layout:

**Tab 1: Mercado & Cotações**
- USD/BRL chart (ComposedChart — line with area fill, from `/api/intelligence/ptax`)
- Latest quote metric card
- Commodity prices display (from reference CSVs)

**Tab 2: Comércio Exterior**
- Export/Import by year (stacked BarChart, from `/api/intelligence/comex`)
- Top export UFs bar chart

**Tab 3: Produção & Arrecadação**
- CFEM top 15 municipalities (horizontal BarChart)
- CFEM top 10 substances (horizontal BarChart)
- RAL production by substance (BarChart)

**Tab 4: Gestão Territorial**
- ANM processes by FASE (BarChart)
- ANM top 15 substances (horizontal BarChart)

### 3.2 Mineradora Modelo (new route: `/mineradora-modelo`)

**Maps to:** Streamlit's `mineradora_modelo.py`

#### Layout:
1. **Warning banner** — "DADOS SIMULADOS — Ferramenta de demonstração" (amber, persistent)
2. **7 sector tabs** — Planejamento, Operação, Processamento, Rejeitos, Manutenção, Logística, SSMA
3. **Per sector:**
   - 3-4 KPI cards with: current value, delta from previous month (color: green improving, red degrading), target badge
   - Time series charts per KPI (AreaChart with target reference line, 24 months)
   - Min/max band visualization

#### API calls:
- `GET /api/simulator/sectors` (new)
- `GET /api/simulator/data` (new)

### 3.3 Due Diligence Enhancements

**Current DD wizard is 80% complete. Add:**
1. **localStorage persistence** — auto-save every evaluation change, resume on page load
2. **License type change warning** — confirmation dialog clears Steps 2-4
3. **Document grouping by modalidade** in Step 2
4. **Progress bar** in Step 2 (X/Y documents evaluated)
5. **"Por Documento" tab** in Step 4 results — per-document breakdown
6. **PDF export** of conformity report

---

## Phase 4: Cross-Cutting & Polish (Week 4)

### 4.1 Navigation Updates

Update sidebar to match all new routes:

```
Summo Ambiental
  ├── Painel Principal (/)
  ├── Base de Dados (/dados)
  ├── Explorar Licenças (/explorar)
  ├── Consulta por Empresa (/empresa)
  ├── Análise de Risco (/decisoes)
  └── Due Diligence (/due-diligence)

Direitos e Concessões
  ├── Base de Concessões (/concessoes-base)
  ├── Mapa Geoespacial (/mapa)
  └── Prospecção (/prospeccao)

Mineral Intelligence
  └── Inteligência Comercial (/inteligencia)

SQ Solutions
  └── Mineradora Modelo (/mineradora-modelo)
```

### 4.2 Data Freshness Indicator

- Sidebar footer: "Dados: DD/MM/YYYY" with colored dot
- Green: < 7 days, Amber: < 30 days, Red: > 30 days
- Data from `/api/overview/metadata` (existing)

### 4.3 Cross-Page Deep Linking

- Explorer: `?dataset=v_mg_semad&detail_id=12345` → opens detail panel
- Empresa: `?cnpj=12345678000100` → auto-searches
- Mapa: `?processo=12345` → zooms to polygon
- Prospecção: `?view=empresa&titular=VALE` → filters company
- Concessões detail → "Ver no mapa" button

### 4.4 PDF Report Download

Replace async polling with synchronous streaming:
```typescript
// web/src/lib/api.ts
export async function downloadReport(cnpj: string): Promise<void> {
  const res = await fetch(`${API_BASE}/report/${cnpj}/generate`, { method: "POST" });
  if (!res.ok) throw new Error(`Report generation failed: ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `relatorio_${cnpj}_${new Date().toISOString().slice(0, 10)}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
```

### 4.5 CSV Export Pattern

Reusable across Explorer, Concessões, Prospecção:
```typescript
export async function downloadCSV(endpoint: string, filename: string): Promise<void> {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) throw new Error(`Export failed: ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
```

### 4.6 Mobile Responsiveness

- **Tables:** horizontal scroll wrapper, column hiding on mobile (show essential columns only)
- **KPI grids:** 4-col → 2-col (sm) → 1-col (xs)
- **Map:** full-width, bottom sheet for popup (not floating popup)
- **Filters:** collapsed into Sheet drawer on mobile
- **Charts:** full-width, reduced height on mobile

### 4.7 Placeholder Pages

Keep as-is with "Em desenvolvimento" state:
- `/viabilidade` — Análise de Viabilidade
- `/monitoramento` — Monitoramento de Indicadores
- `/gestao-interna` — Gestão Interna SQ

---

## Acceptance Criteria

### Functional Requirements
- [ ] All 14 Streamlit page features are accessible in Next.js
- [ ] Data Explorer: row click shows full detail + document links + parecer text
- [ ] Company Dossier: all 7 sections (profile, infrações, CFEM, ANM, filiais, decisions, PDF)
- [ ] Map: 5,000 polygons render in < 3 seconds, color coding works for all 4 modes
- [ ] Prospecção: scoring matches Streamlit SQL exactly, all 3 views functional
- [ ] CSV export works from Explorer, Concessões, and Prospecção
- [ ] PDF report generates and downloads successfully
- [ ] DD wizard state persists across browser refresh
- [ ] All pages work on mobile (iPhone 14 viewport minimum)

### Non-Functional Requirements
- [ ] GeoJSON response < 2MB for 5,000 features
- [ ] Page load time < 2 seconds (except map < 4 seconds)
- [ ] No SQL injection vectors (all queries parameterized)
- [ ] CORS restricted to exact deployment URLs
- [ ] Brazilian formatting (pt-BR) consistent across all numbers, dates, currencies

### Quality Gates
- [ ] All 55 existing Python tests pass
- [ ] Next.js build passes with zero TypeScript errors
- [ ] Manual visual comparison: screenshot every Streamlit page, verify Next.js matches features

---

## Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| GeoJSON too large (>10MB) | High | Server-side simplification with tolerance param, progressive loading |
| DuckDB concurrency under load | Medium | Connection pooling, read-only cursors, query timeout |
| PDF generation timeout (>60s) | Medium | Streaming response, timeout limit, retry UI |
| DD wizard data loss on crash | Medium | localStorage auto-save every change |
| MapLibre bundle size (~200KB) | Low | Dynamic import with ssr:false, loading skeleton |
| 1,934 DD requirements UI lag | Medium | Virtual scroll for long lists, group by document |

---

## Files to Create/Modify

### New API routers:
- `api/routers/concessoes.py` — Concessions CRUD + filters
- `api/routers/geospatial.py` — GeoJSON endpoints + restriction layers
- `api/routers/prospeccao.py` — Scoring + portfolio + municipality
- `api/routers/intelligence.py` — BCB/Comex/CFEM/RAL/ANM aggregations
- `api/routers/simulator.py` — Mining KPI simulator

### Modified API files:
- `api/main.py` — Register new routers, tighten CORS
- `api/routers/explorer.py` — Fix search, add detail/text/export endpoints
- `api/routers/reports.py` — Sync streaming response, remove job store
- `api/routers/overview.py` — Add sources and insights endpoints

### New frontend files:
- `web/src/lib/format.ts` — Brazilian formatting utilities
- `web/src/components/data-table.tsx` — Reusable TanStack table
- `web/src/components/data-table-toolbar.tsx` — Filter controls
- `web/src/components/record-detail.tsx` — Detail Sheet panel
- `web/src/components/document-links.tsx` — PDF link parser
- `web/src/components/mining-map.tsx` — MapLibre wrapper
- `web/src/components/map-popup.tsx` — Polygon popup
- `web/src/components/map-legend.tsx` — Dynamic legend
- `web/src/components/map-filters.tsx` — Map filter sidebar
- `web/src/app/(dashboard)/explorar/page.tsx` — Data Explorer
- `web/src/app/(dashboard)/dados/page.tsx` — Base de Dados
- `web/src/app/(dashboard)/concessoes-base/page.tsx` — Concessões table
- `web/src/app/(dashboard)/inteligencia/page.tsx` — Commercial Intelligence
- `web/src/app/(dashboard)/mineradora-modelo/page.tsx` — Mining Simulator

### Modified frontend files:
- `web/src/app/(dashboard)/mapa/page.tsx` — Replace stub with MapLibre
- `web/src/app/(dashboard)/prospeccao/page.tsx` — Replace stub with scoring
- `web/src/app/(dashboard)/empresa/dossier.tsx` — Add missing sections
- `web/src/app/(dashboard)/empresa/page.tsx` — Add "Por Projeto" tab
- `web/src/app/(dashboard)/due-diligence/page.tsx` — localStorage, grouping, PDF
- `web/src/app/(dashboard)/decisoes/page.tsx` — Add filters, extra charts
- `web/src/app/(dashboard)/layout.tsx` — Updated sidebar nav
- `web/src/components/sidebar-nav.tsx` — New routes
- `web/src/lib/api.ts` — All new endpoint functions + types

---

## Implementation Order

```
Phase 0: Backend gaps          ████████░░░░░░░░░░░░  (Week 0-1)
  0.1 Fix explorer bugs
  0.2 Fix report store
  0.3 Tighten CORS
  0.4 New routers: concessoes, geo, prospeccao, intelligence, simulator
  0.5 Frontend utilities (format.ts, npm installs)

Phase 1: Enhance existing      ░░░░████████░░░░░░░░  (Week 1)
  1.1 Data Explorer overhaul (TanStack table + detail panel)
  1.2 Company Dossier completion (7 sections + PDF)
  1.3 Decisões polish (filters, extra charts)

Phase 2: New core pages        ░░░░░░░░████████░░░░  (Week 2)
  2.1 Base de Dados dashboard
  2.2 Concessões table
  2.3 Geospatial Map (MapLibre)
  2.4 Prospecção (scoring + 3 views)

Phase 3: Intel + Simulator     ░░░░░░░░░░░░████░░░░  (Week 3)
  3.1 Inteligência Comercial (4 tabs)
  3.2 Mineradora Modelo (7 sectors)
  3.3 DD enhancements

Phase 4: Polish + Deploy       ░░░░░░░░░░░░░░░░████  (Week 4)
  4.1 Navigation updates
  4.2 Data freshness indicator
  4.3 Cross-page deep linking
  4.4 Mobile responsiveness
  4.5 Placeholder pages
  4.6 Visual QA vs Streamlit screenshots
```
