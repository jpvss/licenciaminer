# Feature Parity: Streamlit → Next.js — Updated Tracker

Last updated: 2026-04-01
Excludes: auth, multi-tenant, LLM chat sidebar (deferred).

---

## Current State — ~85% Feature Parity

The Next.js app has all 12 active Streamlit pages ported with core functionality working.
Two major rounds of work have been completed:
1. **Phase 1-2**: Core pages, FastAPI backend (62 endpoints), charts, maps, tables
2. **Stash restoration (2026-04-01)**: Sidebar nav, insights panels, dossier profile, inline detail panels, table scroll fixes

### What's Built & Working (Next.js)
- ✅ Sidebar nav — 5 grouped sections with color-coded labels, disabled states
- ✅ Mobile nav — matching sections in Sheet drawer
- ✅ Dashboard — 4 KPIs, trend chart, insights sidebar, data sources table, methodology
- ✅ Explorar Dados — dataset selector, 6 filters, paginated table, inline detail card, CSV export
- ✅ Consulta Empresa — 2 tabs (CNPJ + Projeto), example CNPJs, dossier with profile
- ✅ Análise Decisões — 5 chart tabs, KPIs, insights sidebar, regional detail table
- ✅ Due Diligence — 4-step wizard, document checklist, scoring, PDF download
- ✅ Concessões — MultiSelect filters, KPI cards, paginated table, inline detail card
- ✅ Mapa Geoespacial — MapLibre, filter by regime/categoria/substância, UC/TI layers, color-by
- ✅ Prospecção — 3 tabs (oportunidades/empresas/municípios), score slider, filters
- ✅ Inteligência Comercial — 4 tabs (cotações/comex/produção/território), Recharts
- ✅ Mineradora Modelo — 7 sector tabs, KPI cards, trend charts, simulated data
- ✅ Monitoramento & Gestão Interna — under-construction placeholders
- ✅ DataTable component — pagination, sort, column toggle, horizontal scroll, sticky headers
- ✅ Inline RecordDetail — SEMAD record card with documents, parecer text, portal link
- ✅ PDF report download via API

### FastAPI Backend — Complete
62 endpoints across 12 routers. All data queries working. No new endpoints needed for remaining parity work (existing endpoints cover all gaps).

---

## Remaining Gaps — Organized by Priority

### 🔴 P0 — High Impact, Visible Gaps

#### Gap 1: Consulta Empresa — Missing Detail Sections
**Current**: Dossier shows KPIs + decisions + ANM titles + CFEM summary + similar cases.
**Missing vs Streamlit**:
- [ ] **Infrações IBAMA detail table** — Streamlit shows full table (data, tipo, município, valor, descrição, status) inside accordion. Next.js only shows count in KPI card.
  - API: `fetchReportData` already returns `infracoes` array — check if it has row-level detail or just count
  - If count-only, add `/api/empresa/{cnpj}/infracoes` endpoint
  - File: `web/src/app/(dashboard)/empresa/dossier.tsx` — add AccordionItem after CFEM section
- [ ] **CFEM yearly breakdown** — Streamlit shows table: Ano, Substância, Meses, Total (R$). Next.js shows only total + months count.
  - Check if `fetchReportData` returns breakdown or just aggregates
  - File: `web/src/app/(dashboard)/empresa/dossier.tsx` — expand CFEM accordion
- [ ] **Filiais (sister companies)** — Streamlit discovers CNPJs sharing same 8-digit root and lists them
  - Backend: Need `GET /api/empresa/{cnpj}/filiais` endpoint (query CNPJ table by root)
  - Frontend: Add accordion section showing related CNPJs with click-to-search
  - File: `web/src/app/(dashboard)/empresa/dossier.tsx`

#### Gap 2: Análise Decisões — Missing "Caso Detalhado" Tab
**Current**: 5 tabs covering trends, regional, modalidade, yearly, risk factors.
**Missing vs Streamlit**:
- [ ] **"Caso Detalhado" tab** — Single company deep dive: CNPJ/name search → decision history timeline → regional analysis → peer comparison
  - Backend: Reuse `/api/empresa/{cnpj}` data + `/api/decisoes/` filters
  - File: `web/src/app/(dashboard)/decisoes/page.tsx` — add 6th tab
- [ ] **"Deliberações CMI" tab** — COPAM council meeting decisions table
  - Backend: Need `GET /api/copam` endpoint (query `v_copam_deliberacoes`)
  - File: `web/src/app/(dashboard)/decisoes/page.tsx` — add 7th tab

#### Gap 3: Viabilidade Tab — Incomplete Results Display
**Current**: The "Por Projeto" tab exists with filters (atividade, classe, regional) but needs richer results.
**Missing vs Streamlit**:
- [ ] **Approval rate donut/ring chart** — green/red/gray segments showing deferido/indeferido/arquivamento
  - Use Recharts PieChart with inner radius
- [ ] **Comparison bar** — selected profile rate vs overall average with ±pp difference
- [ ] **Sample size warning** — when < 10 matching cases
- [ ] **Case detail expanders** — each similar case expandable with Portal SEMAD link + decision text preview
  - File: `web/src/app/(dashboard)/empresa/viabilidade-tab.tsx`

---

### 🟡 P1 — Enrichment & Polish

#### Gap 4: UX Polish Across Pages
- [ ] **Data freshness indicator** in sidebar footer — query API for last update date
  - Backend: Need `GET /api/meta/freshness` endpoint
  - File: `web/src/components/sidebar-nav.tsx`
- [ ] **Trust statement** in sidebar: "Fontes públicas oficiais · Cada registro rastreável à origem"
- [ ] **Explorar Dados instructional caption** above dataset selector
- [ ] **Prospecção score breakdown** — tooltip/popover explaining the 5 scoring components (inactivity 30pts, strategic 25pts, area 8-15pts, no CFEM 15pts, category 8-15pts)
  - File: `web/src/app/(dashboard)/prospeccao/page.tsx`
- [ ] **Active filter chips** — create `<FilterChips>` component showing active filters as removable badges, add to Explorar, Concessões, Mapa, Prospecção
  - New file: `web/src/components/filter-chips.tsx`

#### Gap 5: Chart Enhancements
- [ ] **Trend chart dual axis** — Dashboard trend chart should have volume bars on secondary axis (like Streamlit), not just the line
  - File: `web/src/app/(dashboard)/trend-chart.tsx`
- [ ] **Reference lines** on bar charts — add average indicators to regional rigor and yearly approval charts
  - File: `web/src/app/(dashboard)/decisoes/page.tsx`
- [ ] **Approval by class distribution** chart — missing from decisões
  - Backend: may need `/api/decisoes/by-class` endpoint or can aggregate from existing data

#### Gap 6: PDF Report UX
- [ ] **Progress indicator** during PDF generation — "Coletando dados de 10 fontes..."
- [ ] **Risk level in success message** after generation
- [ ] **Persist download state** — don't lose PDF reference on tab switch
  - File: `web/src/app/(dashboard)/empresa/dossier.tsx`

#### Gap 7: Data Enrichment (Backend)
- [ ] Run `uv run python -m licenciaminer collect mg-docs` to populate `documentos_pdf` for remaining ~34k SEMAD records
  - This makes the "Documentos" section in record detail actually show content
  - Rate-limited: several hours runtime
- [ ] Run `uv run python -m licenciaminer collect mg-textos` to extract parecer text from PDFs
  - Makes the "Texto do Parecer" accordion actually have content

---

### 🟢 P2 — Nice-to-Have / Completeness

#### Gap 8: Cross-Page Navigation
- [ ] Click company in Prospecção → navigate to Consulta Empresa with CNPJ pre-filled
- [ ] Click polygon on Mapa → navigate to Concessões detail
- [ ] Click regional in Decisões → filter Explorar by that regional
  - These are UX enhancements, not parity gaps

#### Gap 9: Due Diligence Polish
- [ ] **Conformity gauge visualization** — circular ring chart showing overall score
- [ ] **Risk classification display** — badge with color and explanation
- [ ] Better document preview count after configuration step
  - File: `web/src/app/(dashboard)/due-diligence/page.tsx`

#### Gap 10: Explorar Dados — Per-Dataset Column Config
- [ ] Currently all datasets use same generic column rendering
- [ ] IBAMA dataset should highlight specific columns (licença type, empreendimento, vencimento)
- [ ] CFEM dataset should format currency columns
- [ ] ANM dataset should show processo as monospaced
  - File: `web/src/app/(dashboard)/explorar/page.tsx`

---

## Deferred (Not Part of Feature Parity)

| Feature | Reason |
|---------|--------|
| Auth + multi-tenant | User decision — deferred |
| LLM chat sidebar | Future phase (WebSocket endpoint ready) |
| Commodity price CSV upload | Admin feature, not priority |
| Parecer extraction (regex+LLM) | Separate plan: `plans/feat-parecer-extraction.md` |

---

## Execution Order

Suggested order for maximum impact with minimum context switching:

| # | Gap | Effort | Files Touched | New Endpoints |
|---|-----|--------|---------------|---------------|
| 1 | Gap 1: Empresa dossier enrichment | Medium | dossier.tsx, api.ts | 0-2 |
| 2 | Gap 3: Viabilidade results display | Medium | viabilidade-tab.tsx | 0 |
| 3 | Gap 4: UX polish (text, chips, freshness) | Small | Multiple pages | 1 |
| 4 | Gap 2: Decisões missing tabs | Medium-Large | decisoes/page.tsx, api.ts | 1 |
| 5 | Gap 5: Chart enhancements | Small | trend-chart.tsx, decisoes | 0-1 |
| 6 | Gap 6: PDF report UX | Small | dossier.tsx | 0 |
| 7 | Gap 7: Data enrichment (backend) | Low code, high runtime | CLI commands | 0 |
| 8 | Gap 8-10: Polish & cross-nav | Small each | Various | 0 |

---

## New Backend Endpoints Needed

| Endpoint | Purpose | Gap |
|----------|---------|-----|
| `GET /api/empresa/{cnpj}/filiais` | Sister companies by CNPJ root | Gap 1 |
| `GET /api/empresa/{cnpj}/infracoes` | IBAMA infraction detail rows | Gap 1 (if not in report) |
| `GET /api/copam` | COPAM deliberations table | Gap 2 |
| `GET /api/meta/freshness` | Data last-update timestamps | Gap 4 |
| `GET /api/decisoes/by-class` | Approval rates by impact class | Gap 5 (optional) |

---

## Verification

1. **Visual comparison**: Screenshot each Streamlit page, match in Next.js
2. **Feature checklist**: Every checkbox above verified
3. **Data parity**: Same query on both apps returns identical results
4. **Mobile**: All pages responsive (Streamlit is not — this is an upgrade)
5. **Performance**: Page loads < 2s, chart renders < 1s
6. **Navigation**: All business units represented in sidebar with correct grouping
