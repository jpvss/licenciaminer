# feat: LicenciaMiner Next Steps Roadmap

**Type:** Enhancement roadmap
**Priority:** Strategic
**Status:** Post-stabilization — app works, now needs differentiation

## Revised Execution Order (decided 2026-03-24)

```
#1 PDF Reports        → DONE (2026-03-24)
#2 UI/UX Polish       → DONE (2026-03-24, all 8 tabs reviewed)
#3 COPAM/RAL exposure → DONE (2026-03-24)
#4 Parecer Extraction → NEXT — builds the moat (conditions + rejection reasons)
#5 LLM Chat           → AFTER #4, when it has real intelligence to offer
```

**Rationale:** LLM chat was deprioritized — without parecer text analysis,
it just rephrases numbers (gimmick). PDF reports validate product-market fit
and create immediate revenue. LLM becomes genuinely valuable AFTER #4 gives
it conditions/rejection reasons to synthesize.

---

## Current State (March 2026)

The app is **70% built**. After the stabilization sprint (PR #1), we have:

- 14 data sources integrated (~1M records)
- 7 Streamlit pages deployed and working
- Thread-safe DuckDB, parameterized queries, batch map rendering
- Custom "Geological Editorial" design system
- All automated collectors functional via `collect --all`

**What's missing:** The features that turn this from a "compliance database" into a "consultant copilot" — LLM intelligence, report generation, and deeper text analysis.

---

## Proposed Next Steps (Ranked by Impact)

### 1. LLM Chat Sidebar — Claude API Integration

**Impact:** Transforms passive dashboard into active intelligence tool
**Effort:** Medium (2-3 days)
**Dependencies:** `anthropic>=0.86.0` already in deps, `ANTHROPIC_API_KEY` in .env

#### Why this is #1

The entire product thesis is "intelligence, not just data." Today a user sees approval rates and tables. With LLM integration, they can ask:

- "Qual a chance de aprovação para lavra de ferro, classe 4, na regional de Governador Valadares?"
- "Quais empresas com mais de 5 infrações IBAMA ainda conseguiram deferimento?"
- "Resuma os fatores de risco para este CNPJ"

Every answer is grounded in the existing queries — no hallucination risk because the data is structured and auditable.

#### Proposed Architecture

```
app/components/llm_chat.py
├── build_context(query_type, params) → dict
│   ├── Runs relevant SQL queries (approval_stats, similar_cases, infractions)
│   ├── Formats as structured context for Claude
│   └── Includes source attribution metadata
├── stream_response(user_question, context) → generator
│   ├── Uses anthropic.Anthropic().messages.stream()
│   ├── System prompt: "You are an environmental licensing analyst..."
│   └── Enforces citation of data sources
└── render_chat_sidebar()
    ├── st.chat_input() in sidebar
    ├── st.write_stream() for streaming responses
    └── "Gerado por IA — verifique nas fontes citadas" disclaimer
```

#### Key Design Decisions

- **Context window strategy:** Pre-query relevant data based on current page + user question, inject as structured JSON. Not RAG — our data is already structured.
- **Auditability:** Every LLM response includes the SQL queries used to build context. User can expand "Ver dados utilizados" to see exact source.
- **Scope:** Start with Tab 3 (Consulta) and Tab 4 (Análise) — these are where intelligence queries make most sense.
- **Cost control:** Cache context building, rate-limit to 20 queries/session.

#### Acceptance Criteria

- [ ] Chat sidebar renders on Consulta and Análise pages
- [ ] User can ask natural language questions about licensing data
- [ ] Responses cite specific data sources (SEMAD, IBAMA, ANM)
- [ ] "Gerado por IA" disclaimer visible on every response
- [ ] Streaming works (not blocking until full response)
- [ ] Graceful degradation when ANTHROPIC_API_KEY not set
- [ ] Context building reuses existing `run_query()` infrastructure

---

### 2. PDF Report Generation — Due Diligence Reports

**Impact:** Immediate revenue path (R$5-15K per report for law firms/investors)
**Effort:** Medium (2-3 days)
**Dependencies:** `fpdf2>=2.8.7` already in deps

#### Why this is #2

This is the Shape C revenue model from the product plan. A mining consultancy or law firm doing environmental due diligence needs a comprehensive profile. Today they'd spend days querying government portals. We can generate it in seconds.

#### Report Structure

```
1. Capa — Logo, CNPJ, data de geração, disclaimer
2. Perfil da Empresa — Razão social, CNAE, porte, situação cadastral
3. Histórico de Licenciamento — Timeline de decisões SEMAD com deferimentos/indeferimentos
4. Análise de Risco — Taxa de aprovação vs média, comparação por classe/regional
5. Infrações Ambientais — Histórico IBAMA com gravidade e valores
6. Títulos Minerários — Processos ANM, fases, áreas
7. Pagamentos CFEM — Histórico de royalties, status de adimplência
8. Análise Espacial — Sobreposições com UCs, TIs, biomas
```

Each section includes:
- Source attribution with URLs
- "Data verified on DD/MM/YYYY" timestamp
- Visual indicators (green/amber/red risk levels)

#### Integration Point

Button on Tab 3 (Consulta) → "Gerar Relatório PDF" after CNPJ search. Reuses all existing queries:
- `QUERY_CNPJ_PROFILE`
- `QUERY_CNPJ_INFRACOES`
- `QUERY_CNPJ_CFEM`
- `QUERY_CNPJ_ANM_TITULOS`
- `QUERY_HISTORICO_CNPJ`
- `QUERY_SPATIAL_VS_APROVACAO`

#### Acceptance Criteria

- [ ] "Gerar Relatório" button appears after CNPJ search on Tab 3
- [ ] PDF generates with 8 sections, proper Portuguese formatting
- [ ] Each section cites the source URL
- [ ] PDF is downloadable via `st.download_button`
- [ ] Works with partial data (some sections show "Dados não disponíveis")
- [ ] Generation takes < 10 seconds

---

### 3. UI/UX Modernization — Premium Feel

**Impact:** Perception of quality, credibility for consultancy clients
**Effort:** Small-Medium (1-2 days)
**Dependencies:** None — CSS + Streamlit `column_config`

#### Why this is #3

User feedback (from memory): "expects premium UI, not functional-but-plain." The design system exists (`theme.py` with 840 lines of CSS), but pages underutilize it.

#### Specific Improvements

**Tables:**
- Add `st.column_config` to all dataframes:
  - `DateColumn` for dates (DD/MM/YYYY format)
  - `ProgressColumn` for approval rates
  - `LinkColumn` for "verificar" URLs
  - `NumberColumn` with Brazilian formatting (R$ 1.234,56)
- Conditional row highlighting (green=deferido, red=indeferido)

**Charts:**
- Add `@st.fragment` to heavy chart sections (avoid full-page reruns on filter changes)
- Plotly charts: enable legend click-to-toggle

**Loading states:**
- Add `st.spinner` with themed messages for queries > 1s
- Skeleton loading for KPI cards

**Navigation:**
- Migrate to `st.navigation` + `st.Page` (grouped sidebar sections)
- Inject theme once in `app.py` instead of per-page

**Expand `.streamlit/config.toml` theme:**
```toml
[theme]
base = "dark"
primaryColor = "#D4A847"
backgroundColor = "#0C0E12"
secondaryBackgroundColor = "#12151B"
textColor = "#E8E4DC"
font = "sans serif"
```

#### Acceptance Criteria

- [ ] All tables use `column_config` with proper formatting
- [ ] Brazilian number formatting throughout (R$ X.XXX,XX)
- [ ] Sidebar navigation grouped into sections (Inteligência, Dados, Geoespacial)
- [ ] Chart interactions don't reload entire page
- [ ] Config.toml theme colors match CSS custom properties

---

### 4. Parecer Text Analysis — Condition & Rejection Extraction

**Impact:** Unlocks "Similar case analysis" — core differentiator for Shape A
**Effort:** Large (3-5 days)
**Dependencies:** Parecer texts already extracted (86.6% coverage per methodology)

#### Why this matters

Today we know IF a project was approved/rejected. We don't know WHY. The parecer texts contain:

- **Condicionantes** — conditions imposed on approvals ("monitorar qualidade da água trimestralmente")
- **Motivos de indeferimento** — rejection reasons ("área sobrepõe UC de proteção integral")
- **Requisitos técnicos** — what was required and whether it was met

Extracting these makes the "Casos Similares" feature genuinely predictive instead of just statistical.

#### Approach

Two options:
1. **Regex + heuristic extraction** — cheaper, faster, works for structured pareceres
2. **LLM extraction** — more accurate, handles varied formats, costs per document

Recommend starting with regex for condicionantes (they follow patterns like "CONDICIONANTE:", numbered lists), then LLM for rejection reasons (more varied language).

#### New Columns

```python
# Add to v_mg_semad view:
condicionantes: list[str]        # Extracted conditions
motivo_indeferimento: str | None  # Primary rejection reason
requisitos_atendidos: bool | None # Whether technical requirements were met
```

#### Acceptance Criteria

- [ ] Extract condicionantes from 80%+ of deferimento pareceres
- [ ] Extract rejection reasons from 70%+ of indeferimento pareceres
- [ ] New columns exposed in data explorer and consulta pages
- [ ] "Casos Similares" shows conditions imposed on similar approvals
- [ ] Processing runs as CLI command: `licenciaminer extract-conditions`

---

### 5. Expose COPAM & RAL Data in UI

**Impact:** Low-medium (completes data coverage, fulfills "14 fontes" promise)
**Effort:** Small (half day)
**Dependencies:** Data already collected

#### Current Gap

`v_copam` (135 CMI meeting records) and `v_ral` (1,013 production records) exist as DuckDB views but no page queries them.

#### Proposed Integration

- **COPAM meetings** → Add to Tab 4 (Análise) as "Deliberações CMI" sub-tab
- **RAL production** → Add to company profile in Tab 3 (Consulta) as "Produção Mineral" section
- **RAL production** → Enrich prospection score in Tab 7 (add production volume as scoring factor)

#### Acceptance Criteria

- [ ] COPAM meetings visible in Análise page
- [ ] RAL production shown in company profile after CNPJ search
- [ ] RAL data used in prospection scoring formula
- [ ] Both datasets appear in Explorar Dados dropdown (already working via `get_dataset_options`)

---

## Recommended Execution Order

```
Week 1: LLM Chat (#1) + COPAM/RAL exposure (#5)
         ↓
Week 2: PDF Reports (#2) + UI Modernization (#3)
         ↓
Week 3: Parecer Extraction (#4)
         ↓
Week 4: Testing, polish, user validation with 3-5 target consultancies
```

**Rationale:** LLM chat is the highest-impact differentiator and validates whether the product thesis works. PDF reports are the fastest path to revenue. UI polish increases credibility for demos. Parecer extraction is the deep moat but needs more engineering time.

---

## What NOT to Build Yet

- **Authentication / multi-tenant** — premature until product-market fit validated
- **Real-time data collection** — daily batch is sufficient for licensing decisions
- **Other states beyond MG** — validate MG first, then expand
- **Custom dashboards per user** — URL state persistence is enough for now
- **Mobile app** — Streamlit responsive is sufficient

---

## References

### Internal
- [plans/feat-product-app-final.md](plans/feat-product-app-final.md) — Original product plan with Shapes A/B/C
- [plans/product-layer.md](plans/product-layer.md) — Product layer architecture
- [plans/fix-app-stabilization-deep-review.md](plans/fix-app-stabilization-deep-review.md) — Stabilization plan (completed)
- [app/components/data_loader.py](app/components/data_loader.py) — Query infrastructure (safe_query, run_query)
- [src/licenciaminer/database/queries.py](src/licenciaminer/database/queries.py) — All SQL queries for context building

### External
- [Anthropic Python SDK streaming](https://docs.anthropic.com/en/api/messages-streaming)
- [Streamlit st.write_stream](https://docs.streamlit.io/develop/api-reference/write-magic/st.write_stream)
- [Streamlit st.navigation](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
- [fpdf2 documentation](https://py-pdf.github.io/fpdf2/)
