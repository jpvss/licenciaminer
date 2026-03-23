# feat: LicenciaMiner Product App — Final Plan

## Overview

A self-contained Streamlit web app with 3 tabs + LLM-powered chat + report generation. Every data point traceable to its source. Deployable as a single URL.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Streamlit App                   │
│  ┌──────────┬───────────┬──────────┐        │
│  │ Visão    │ Explorar  │ Consulta │        │
│  │ Geral    │ Dados     │          │        │
│  └────┬─────┴─────┬─────┴────┬─────┘        │
│       │           │          │               │
│  ┌────┴───────────┴──────────┴────┐         │
│  │    LLM Chat Sidebar            │         │
│  │    (Claude API, opt-in)        │         │
│  └────┬───────────────────────────┘         │
│       │                                      │
│  ┌────┴───────────────────────────┐         │
│  │  Data Layer (shared)           │         │
│  │  DuckDB (@st.cache_resource)   │         │
│  │  Views over Parquet files      │         │
│  │  Parameterized queries         │         │
│  └────┬───────────┬───────────────┘         │
│       │           │                          │
│  data/processed/  data/reference/            │
│  *.parquet        *.parquet                  │
│  metadata.json                               │
└─────────────────────────────────────────────┘
```

Self-contained: `uv run streamlit run app/app.py` — no external DB, no API server.

---

## Tab 1: Visão Geral

**Purpose**: First impression. What data do we have, where it's from, is it fresh, what does it tell us.

**Sections**:

1. **Metric cards** — 4 big numbers: decisões SEMAD, processos ANM, infrações IBAMA, taxa aprovação mineração
   - Each card shows "Fonte: X | Atualizado: DD/MM/YYYY"
   - Counts from DuckDB, freshness from `collection_metadata.json`

2. **Approval trend chart** — line chart 2016-2026 mining approval rate
   - Plotly, interactive
   - Source: `v_mg_semad` filtered to mining

3. **Data sources table** — every source with name, records, last updated, source URL
   - Each row links to the original portal
   - Color-coded freshness (green/yellow/red)

4. **Key insights** — 4-5 bullet points with N shown
   - "Classe 5: 39.4% aprovação (N=236)"
   - "Zona da Mata: regional mais rigorosa, 48.5% (N=998)"
   - "Empresas com 6+ infrações: 73.7% (N=95)"

5. **About section** (bottom) — methodology, limitations, what's NOT in the data
   - Replaces separate "Sobre" tab

**File**: `app/pages/1_visao_geral.py`

---

## Tab 2: Explorar Dados

**Purpose**: Browse any dataset. Verify any data point. The trust layer.

**Sections**:

1. **Dataset selector** — dropdown: SEMAD Decisões, ANM Processos, IBAMA Infrações, CFEM, CNPJ, COPAM, Spatial
   - Shows record count per dataset

2. **Filters** — dataset-specific filter widgets
   - SEMAD: decisão, classe, regional, atividade prefix, ano range, CNPJ search
   - ANM: FASE, SUBS, ano range
   - IBAMA infrações: UF, CNPJ search
   - CFEM: substância, ano
   - CNPJ: CNPJ search, porte, CNAE
   - COPAM: ano, título search

3. **Results table** — paginated, sortable
   - Shows "X de Y registros" count
   - DuckDB LIMIT/OFFSET — never materialize full table
   - `st.dataframe` with column config for formatting

4. **Row detail** — click row → `st.expander` with full record
   - All fields displayed
   - For SEMAD: link to `view-externo?id={detail_id}` portal page
   - For SEMAD with PDFs: document list with download links
   - For SEMAD with text: expandable parecer text (first 500 chars + "ver completo")

5. **Export** — `st.download_button` for filtered CSV

**File**: `app/pages/2_explorar_dados.py`

---

## Tab 3: Consulta

**Purpose**: The product differentiator. Ask a question, get an auditable answer with similar cases.

**Two entry modes** (radio button):

### Mode A: "Consulta por Projeto"
Inputs: atividade (dropdown), município (dropdown), classe (dropdown)

### Mode B: "Consulta por Empresa"
Input: CNPJ (text field)

**Output sections** (same for both modes):

1. **Contexto Estatístico**
   - Approval rate for this activity+class+regional (or this company)
   - Comparison to overall mining average
   - N shown, warning if N < 10
   - Source: `v_mg_semad`

2. **Restrições Espaciais** (Mode A only, or from company's ANM titles)
   - UC overlaps, TI overlaps, bioma
   - Source: `v_spatial`

3. **Perfil da Empresa** (Mode B, or from CNPJ in Mode A if provided)
   - Razão social, CNAE, porte, data abertura
   - Infraction count + total fines
   - CFEM payment regularity
   - Source: `v_cnpj`, `v_ibama_infracoes`, `v_cfem`

4. **Casos Similares** — 5 most comparable decisions
   - Progressive relaxation: activity+class+regional → activity+class → activity prefix
   - Each case shows: empresa, município, decisão, data, classe
   - Expandable: full parecer text
   - Link to SEMAD portal
   - Source: `v_mg_semad`

5. **Histórico COPAM** — CMI meetings mentioning this activity/company
   - Meeting date, title, document count
   - Links to PDFs
   - Source: `v_copam`

Each section has:
- "Fonte: [source name]" badge
- N (sample size) for any statistic
- Expandable "Como calculamos" showing the SQL query

**File**: `app/pages/3_consulta.py`

---

## LLM Chat Sidebar

**Purpose**: Natural language questions over the data. Powered by Claude API.

**Location**: Sidebar, available on all tabs. Opt-in (requires API key in .env).

**How it works**:

1. User types question: "Qual a chance de aprovação para lavra de ferro classe 5 em Barão de Cocais?"

2. System builds context from structured data:
   ```python
   def build_llm_context(query_params: dict) -> dict:
       """Returns structured dict with data from all sources."""
       return {
           "estatisticas": {
               "data": approval_rates_for_params,
               "n": sample_size,
               "fonte": "SEMAD MG",
           },
           "restricoes_espaciais": {
               "data": spatial_flags,
               "fonte": "ICMBio, FUNAI, IBGE",
           },
           "casos_similares": {
               "data": similar_cases[:5],
               "fonte": "SEMAD MG",
           },
           "infracoes": {
               "data": company_infractions,
               "status": "found" | "not_found" | "source_unavailable",
               "fonte": "IBAMA",
           },
       }
   ```

3. Context rendered as markdown for Claude prompt:
   - Every section prefixed with `(Fonte: ...)`
   - Statistics include N
   - Parecer text included verbatim (most recent, truncated to 3K chars by paragraph boundary)

4. Claude responds with analysis, citing sources

5. Response displayed with banner: "Gerado por IA — verificar com as fontes citadas"

**Key rules**:
- LLM never generates data — only narrates/summarizes what's provided
- Every fact in the response should be traceable to a context section
- If data is missing, context includes `"status": "not_found"` so LLM says "não temos dados" instead of hallucinating
- Chat is optional — app works fully without API key

**File**: `app/components/llm_chat.py`

---

## Report Generation

**Purpose**: Generate downloadable PDF due diligence report for a CNPJ.

**Location**: Button on Tab 3 (after Mode B query) or via LLM chat command.

**Report template**:

```
RELATÓRIO DE INTELIGÊNCIA AMBIENTAL
Gerado por LicenciaMiner em DD/MM/YYYY

1. IDENTIFICAÇÃO DA EMPRESA
   [From v_cnpj — razão social, CNAE, porte, data abertura]
   Fonte: Receita Federal via BrasilAPI

2. HISTÓRICO DE LICENCIAMENTO AMBIENTAL (MG)
   [From v_mg_semad — decision timeline, approval rate vs average]
   Fonte: SEMAD MG — N decisões encontradas

3. TÍTULOS MINERÁRIOS
   [From v_anm — active processes, phases, substances, areas]
   Fonte: ANM SIGMINE

4. RESTRIÇÕES ESPACIAIS
   [From v_spatial — UC, TI, bioma overlaps]
   Fonte: ICMBio, FUNAI, IBGE

5. INFRAÇÕES AMBIENTAIS
   [From v_ibama_infracoes — count, types, amounts, most recent]
   Fonte: IBAMA Dados Abertos

6. ARRECADAÇÃO CFEM
   [From v_cfem — payment history, regularity]
   Fonte: ANM Arrecadação

7. CASOS SIMILARES
   [From v_mg_semad — 3-5 most comparable decisions]
   Fonte: SEMAD MG

8. HISTÓRICO COPAM
   [From v_copam — relevant CMI meeting references]
   Fonte: COPAM CMI

METODOLOGIA: [brief explanation]
FONTES: [list every source used with URL]
LIMITAÇÕES: [what this report does NOT cover]

Gerado automaticamente por LicenciaMiner.
Os dados são de fontes públicas oficiais. Verificar nos portais originais.
```

**Implementation**: Python function that queries all sources for a CNPJ, renders markdown, converts to PDF via `fpdf2` or `weasyprint`.

**File**: `app/components/report_generator.py`

---

## File Structure

```
app/
├── app.py                     # Entry point, sidebar, LLM chat
├── pages/
│   ├── 1_visao_geral.py      # Executive view + about
│   ├── 2_explorar_dados.py   # Data explorer
│   └── 3_consulta.py         # Intelligence query + company profile
├── components/
│   ├── data_loader.py        # DuckDB wrapper with @st.cache_resource
│   ├── llm_chat.py           # Claude API chat (optional)
│   └── report_generator.py   # PDF report generation
└── queries.py                 # Parameterized queries for the app
```

7 files. `data_loader.py` imports from `licenciaminer.database.loader`.
`queries.py` extends `licenciaminer.database.queries` with parameterized versions.

---

## Pre-requisites (before building app)

Must fix in existing codebase first:

- [ ] Register `v_copam` and `v_ral` views in `schema.py`
- [ ] Wire cross-source queries into `reports.py` (currently dead code)
- [ ] Create parameterized CNPJ lookup query
- [ ] Create parameterized similar-case query (progressive relaxation)
- [ ] Complete `collection_metadata.json` for all sources
- [ ] Add `streamlit`, `plotly`, `fpdf2` to pyproject.toml

---

## Implementation Phases

### Phase 5A: Data Layer Fixes + Foundation (Day 1)
- [ ] Fix pre-requisites above
- [ ] Create `app/` directory structure
- [ ] `data_loader.py` — DuckDB with `@st.cache_resource`, load metadata
- [ ] `app.py` — entry point with page config
- [ ] Verify: `streamlit run app/app.py` shows empty app

### Phase 5B: Visão Geral (Day 2)
- [ ] Metric cards (4 numbers + freshness)
- [ ] Approval trend chart (Plotly line)
- [ ] Data sources table with links + freshness colors
- [ ] Key insights with N
- [ ] About section at bottom
- [ ] Verify: stakeholder can see what data exists and where it's from

### Phase 5C: Explorar Dados (Day 3)
- [ ] Dataset selector dropdown
- [ ] Dynamic filters per dataset
- [ ] Paginated table (LIMIT/OFFSET via DuckDB)
- [ ] Row detail with source link
- [ ] SEMAD: PDF links + expandable parecer text
- [ ] CSV export
- [ ] Verify: stakeholder can browse any dataset and verify data points

### Phase 5D: Consulta (Day 4)
- [ ] Two-mode search (projeto / empresa)
- [ ] Statistical context section
- [ ] Spatial restrictions section
- [ ] Company profile section
- [ ] Similar cases with expandable parecer text
- [ ] COPAM history
- [ ] Each section with Fonte badge + N
- [ ] Verify: stakeholder can ask "what are my chances" and get a credible answer

### Phase 5E: LLM Chat + Reports (Day 5-6)
- [ ] `build_llm_context()` — structured dict from all sources
- [ ] `llm_chat.py` — sidebar chat with Claude API
- [ ] Context rendering with Fonte attribution
- [ ] "Gerado por IA" banner on responses
- [ ] `report_generator.py` — PDF from CNPJ query
- [ ] Download button on Tab 3
- [ ] Verify: chat answers questions citing sources; PDF report is downloadable

### Phase 5F: Deploy (Day 7)
- [ ] Streamlit Cloud deployment
- [ ] Test with real URL
- [ ] Share with first stakeholders
- [ ] Document deployment process

---

## Acceptance Criteria

### Trust & Auditability
- [ ] Every data point shows "Fonte: [source]" with verification link
- [ ] Every statistic shows N (sample size)
- [ ] Warning shown when N < 10
- [ ] "Última atualização" visible for every data source
- [ ] LLM responses labeled "Gerado por IA"
- [ ] PDF reports list all sources used
- [ ] Tab 1 documents known limitations

### Functional
- [ ] All 3 tabs render without errors
- [ ] Data explorer handles 42K+ rows (paginated)
- [ ] CNPJ search returns cross-source profile
- [ ] Similar case matching returns relevant results
- [ ] LLM chat works when API key provided, gracefully hidden when not
- [ ] PDF report generates and downloads
- [ ] CSV export works

### Technical
- [ ] `@st.cache_resource` for DuckDB connection
- [ ] `@st.cache_data` for query results
- [ ] Never `SELECT *` on large tables without LIMIT
- [ ] App loads in < 5 seconds
- [ ] Works on Streamlit Cloud free tier (1GB RAM)
- [ ] Imports from `licenciaminer` package (reuse, don't reimplement)

---

## Dependencies to Add

```toml
# pyproject.toml
[project.optional-dependencies]
app = [
    "streamlit>=1.40",
    "plotly>=6.0",
    "fpdf2>=2.8",
    "anthropic>=0.40",  # Claude API for LLM chat
]
```

---

## Phase 2 (After Stakeholder Feedback)

Only build if stakeholders request:
- FastAPI endpoints for programmatic access
- PDF parecer section parsing (condicionantes extraction)
- DuckDB FTS index for full-text search
- LLM tool definitions for agent frameworks
- URL-persisted filter state
- Mobile layout

---

## References

- [plans/product-layer.md](product-layer.md) — original 3-shape product plan
- [docs/DATA_REGISTRY.md](../docs/DATA_REGISTRY.md) — data source inventory
- [src/licenciaminer/database/queries.py](../src/licenciaminer/database/queries.py) — existing queries
- [src/licenciaminer/database/loader.py](../src/licenciaminer/database/loader.py) — DuckDB loader to reuse

## Review Findings Incorporated

- Architecture: `@st.cache_resource` critical, reuse existing package
- Simplicity: 3 tabs not 5, inline everything, no component library
- Agent-native: `build_llm_context` returns dict not string, status fields for missing data
- Codebase: cross-source queries are dead code, 2 views missing, metadata incomplete
- Best practices: source URLs everywhere, freshness indicators, AG-Grid optional

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
