# feat: LicenciaMiner Product App MVP

## Overview

Build a self-contained, auditable web application that makes our MG mining licensing data explorable, trustworthy, and shareable with business stakeholders. The app serves as both the product prototype and the data validation interface.

**Not** a dashboard. An **intelligence platform** where every data point is traceable to its source, every statistic shows its sample size, and the data is structured for both human exploration and LLM context.

## Problem Statement

We have 10 data sources with ~1 million records cross-referenced via DuckDB. Currently accessible only through CLI commands and Python scripts. Business stakeholders (mining companies, consultancies, investors) need:

1. **Trust**: proof that data is real, current, and from official sources
2. **Exploration**: ability to search, filter, drill down into specific cases
3. **Context**: understanding what data we have, where it came from, and what it means
4. **Actionability**: answers to specific licensing questions, not raw data dumps

## Proposed Solution

A **Streamlit** multi-page app with 5 tabs, deployable as a single URL.

### Why Streamlit

- **Fastest path to shareable prototype** — single Python file, no frontend build
- **Native support for DataFrames, charts, tables** with 40K+ rows
- **Easy deployment** — Streamlit Cloud (free), or single `streamlit run` command
- **Iteration speed** — change code, browser auto-reloads
- **Python-native** — direct DuckDB/Pandas integration, no API layer needed for MVP
- **Good enough for validation** — upgrade to FastAPI+Next.js only after product-market fit

### When to move beyond Streamlit

- When we need user authentication/multi-tenant
- When we need custom UI interactions beyond Streamlit widgets
- When performance requires server-side rendering for 100+ concurrent users

---

## Technical Architecture

```
┌─────────────────────────────────────────┐
│           Streamlit App                  │
│  ┌───────┬──────┬──────┬──────┬──────┐ │
│  │Visão  │Dados │Busca │Empresa│Sobre │ │
│  │Geral  │      │      │       │      │ │
│  └───┬───┴──┬───┴──┬───┴──┬────┴──┬───┘ │
│      │      │      │      │       │      │
│  ┌───┴──────┴──────┴──────┴───────┴───┐ │
│  │         DuckDB (in-memory)         │ │
│  │    Views over Parquet files         │ │
│  └───┬──────┬──────┬──────┬───────┬───┘ │
│      │      │      │      │       │      │
│  data/processed/*.parquet              │
│  data/reference/*.parquet              │
│  collection_metadata.json              │
└─────────────────────────────────────────┘
```

No database server. No API. The app reads directly from parquet files via DuckDB views. This makes it fully self-contained — copy the directory, run `streamlit run`, done.

---

## App Structure: 5 Tabs

### Tab 1: Visão Geral (Executive View)

**Purpose**: Show stakeholders what we have, where it came from, and key insights. Build trust.

**Content**:

```
┌─────────────────────────────────────────────────┐
│  LicenciaMiner — Inteligência de Licenciamento  │
│  Ambiental Minerário em Minas Gerais            │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 RESUMO DO BANCO DE DADOS                    │
│  ┌────────────┬────────────┬───────────────┐    │
│  │ 42.758     │ 50.723     │ 702.280       │    │
│  │ Decisões   │ Processos  │ Infrações     │    │
│  │ SEMAD      │ ANM        │ IBAMA         │    │
│  │ ↗ Atualiz. │ ↗ Atualiz. │ ↗ Atualiz.   │    │
│  │ 22/03/2026 │ 21/03/2026 │ 21/03/2026   │    │
│  └────────────┴────────────┴───────────────┘    │
│                                                  │
│  📈 TAXA DE APROVAÇÃO MINERAÇÃO (MG)            │
│  [Gráfico de linha: 54.3% (2019) → 75.8% (2025)]│
│                                                  │
│  🗺️ FONTES DE DADOS                            │
│  ┌─────────────────────────────────────────┐    │
│  │ Fonte         │ Registros │ Atualização │    │
│  │ MG SEMAD      │ 42.758    │ 22/03/2026  │    │
│  │ ANM SIGMINE   │ 50.723    │ 21/03/2026  │    │
│  │ IBAMA SISLIC  │ 1.115     │ 21/03/2026  │    │
│  │ IBAMA Infraç. │ 702.280   │ 21/03/2026  │    │
│  │ CFEM          │ 91.026    │ 21/03/2026  │    │
│  │ CNPJ          │ 21.572    │ 23/03/2026  │    │
│  │ Spatial       │ 50.725    │ 22/03/2026  │    │
│  │ COPAM CMI     │ 135       │ 22/03/2026  │    │
│  │ RAL Produção  │ 1.013     │ 22/03/2026  │    │
│  │ PDF Textos    │ 6.968     │ 22/03/2026  │    │
│  └─────────────────────────────────────────┘    │
│  Cada linha clicável → abre fonte original       │
│                                                  │
│  📋 INSIGHTS CHAVE                              │
│  • Mineração: 63% aprovação (vs 78.3% geral)   │
│  • Classe 5: 39.4% — significativamente menor   │
│  • Zona da Mata: regional mais rigorosa (48.5%) │
│  • Empresas com infrações: 73.7% aprovação      │
│    (maiores empresas navegam melhor o sistema)   │
│                                                  │
│  Cada insight mostra N (tamanho da amostra)      │
│  e link para a query que o gerou                 │
└─────────────────────────────────────────────────┘
```

**Data sources for this tab**:
- `collection_metadata.json` → freshness dates
- DuckDB summary queries → counts, rates
- Hard-coded source URLs → verification links

**Implementation**: `app/pages/1_visao_geral.py`

---

### Tab 2: Explorar Dados (Data Explorer)

**Purpose**: Browse enriched datasets with filtering, search, export. The "trust layer" — users can verify any data point.

**Content**:

```
┌─────────────────────────────────────────────────┐
│  EXPLORAR DADOS                                  │
│                                                  │
│  Dataset: [MG SEMAD Decisões           ▼]       │
│                                                  │
│  Filtros:                                        │
│  Decisão:  [Todos ▼] Classe: [Todos ▼]          │
│  Regional: [Todos ▼] Atividade: [A-0... ▼]      │
│  Ano:      [2018 ▼] a [2026 ▼]                  │
│  CNPJ:     [________________]                    │
│                                                  │
│  Mostrando 1.847 de 8.072 registros              │
│  [Exportar CSV] [Exportar JSON]                  │
│                                                  │
│  ┌────┬──────────┬──────────┬───────┬──────┐    │
│  │Ano │Empresa   │Atividade │Classe │Decisão│    │
│  ├────┼──────────┼──────────┼───────┼──────┤    │
│  │2026│SD Com... │A-05-01-0 │2      │✅ Def│    │
│  │2026│Quartz... │A-02-07-0 │2      │❌ Ind│    │
│  │2026│Ferro ... │A-02-03-8 │2      │📁 Arq│    │
│  └────┴──────────┴──────────┴───────┴──────┘    │
│                                                  │
│  Clicar em uma linha → expande:                  │
│  ┌─────────────────────────────────────────┐    │
│  │ DETALHES DO REGISTRO                    │    │
│  │ Empreendimento: SD Comércio de Min...   │    │
│  │ CNPJ: 25.354.614/0003-64               │    │
│  │ Regional: Central Metropolitana         │    │
│  │ Modalidade: LAS RAS                     │    │
│  │ Data publicação: 13/03/2026             │    │
│  │                                         │    │
│  │ 🔗 Ver no portal SEMAD                  │    │
│  │    → link direto para view-externo      │    │
│  │                                         │    │
│  │ 📄 Documentos (2 PDFs):                │    │
│  │    • PARECER TECNICO.pdf [baixar]       │    │
│  │    • CERTIFICADO.pdf [baixar]           │    │
│  │                                         │    │
│  │ 📝 Texto do Parecer (22.025 chars):    │    │
│  │    [Expandir texto completo]            │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  Datasets disponíveis:                           │
│  • MG SEMAD Decisões (42.758)                   │
│  • ANM Processos (50.723)                       │
│  • IBAMA Infrações (702.280)                    │
│  • CFEM Pagamentos (91.026)                     │
│  • CNPJ Empresas (21.572)                       │
│  • COPAM Reuniões (135)                         │
│  • Sobreposições Espaciais (50.725)             │
└─────────────────────────────────────────────────┘
```

**Key features**:
- Every record links to its original source URL
- PDF documents downloadable directly
- Parecer Técnico text expandable inline
- Filters persist via URL params (shareable filtered views)
- Export filtered data as CSV or JSON

**Implementation**: `app/pages/2_explorar_dados.py`

---

### Tab 3: Consulta de Inteligência (Intelligence Query)

**Purpose**: The Consultant Copilot — search by project parameters, get a structured briefing.

**Content**: As designed in the previous product plan (activity + município + classe + CNPJ → briefing page with 7 sections).

**Key addition**: Every section shows a "Como chegamos nesse dado" (How we got this data) expandable that shows the exact DuckDB query used.

**Implementation**: `app/pages/3_consulta.py`

---

### Tab 4: Perfil da Empresa (Company Profile)

**Purpose**: Enter a CNPJ, see everything we know across all sources.

**Content**:

```
┌─────────────────────────────────────────────────┐
│  PERFIL DA EMPRESA                               │
│                                                  │
│  CNPJ: [25.354.614/0003-64        ] [Buscar]   │
│                                                  │
│  SD COMERCIO DE MINERAIS LTDA                    │
│  CNAE: 0810-0/05 | Porte: DEMAIS | Desde: 2016  │
│  Situação: ATIVA                                 │
│  Fonte: Receita Federal via BrasilAPI            │
│                                                  │
│  ── HISTÓRICO DE LICENCIAMENTO ──               │
│  3 decisões | 2 deferidos | 0 indeferidos       │
│  Taxa: 66.7% (média mineração: 63%)             │
│  Fonte: SEMAD MG                                 │
│  [Ver decisões detalhadas]                       │
│                                                  │
│  ── TÍTULOS MINERÁRIOS ──                       │
│  2 processos ANM ativos                          │
│  FASE: Autorização de Pesquisa                   │
│  Substância: FERRO | Área: 150,5 ha             │
│  Fonte: ANM SIGMINE                              │
│                                                  │
│  ── INFRAÇÕES AMBIENTAIS ──                     │
│  0 infrações IBAMA registradas                   │
│  Fonte: IBAMA Dados Abertos                      │
│                                                  │
│  ── PAGAMENTOS CFEM ──                          │
│  Não encontrado nos registros CFEM (2022-2026)  │
│  Fonte: ANM Arrecadação                          │
│                                                  │
│  ── RESTRIÇÕES ESPACIAIS ──                     │
│  Processos em UC: Nenhum                         │
│  Processos em TI: Nenhum                         │
│  Bioma: Cerrado                                  │
│  Fonte: ICMBio, FUNAI, IBGE                     │
│                                                  │
│  Cada seção mostra: Fonte + link de verificação  │
└─────────────────────────────────────────────────┘
```

**Implementation**: `app/pages/4_empresa.py`

---

### Tab 5: Sobre / Metodologia (About / Methodology)

**Purpose**: Full transparency on data collection, methodology, limitations.

**Content**:
- Data sources table (from DATA_REGISTRY.md)
- Collection methodology for each source
- Known limitations (scanned PDFs, CNPJ coverage, ANM no-pagination)
- Refresh frequency and last update dates
- How cross-source joins work (CNPJ bridge)
- What's NOT in the data (IBAMA rejections, federal-jurisdiction mines in MG)
- Contact/feedback

**Implementation**: `app/pages/5_sobre.py`

---

## Data Layer: Structured for LLM + Statistics

### Principle: Separation of Raw, Enriched, and Computed

```
data/processed/
  ├── Raw collections (parquet per source)
  │   ├── mg_semad_licencas.parquet      # Includes enriched cols
  │   ├── anm_processos.parquet
  │   ├── ibama_infracoes.parquet
  │   ├── anm_cfem.parquet
  │   ├── cnpj_empresas.parquet
  │   ├── copam_cmi_reunioes.parquet
  │   └── anm_ral.parquet
  │
  ├── Computed views (DuckDB, no files)
  │   ├── v_empresa_profile              # CNPJ aggregation
  │   ├── v_infracoes_vs_aprovacao       # Cross-source insight
  │   └── v_cfem_vs_aprovacao            # Cross-source insight
  │
  └── collection_metadata.json           # Freshness tracking
```

### For LLM Context

When passing data to an LLM (for due diligence report generation), structure as:

```python
def build_llm_context(cnpj: str) -> str:
    """Constrói contexto estruturado para LLM a partir do CNPJ."""
    # Each section is labeled with source for auditability
    context = f"""
## EMPRESA (Fonte: Receita Federal)
{empresa_data}

## HISTÓRICO LICENCIAMENTO MG (Fonte: SEMAD MG, {n} decisões)
{decisoes_summary}

## PARECER TÉCNICO MAIS RECENTE (Fonte: SEMAD, extraído de PDF)
{parecer_text[:5000]}  # Truncate to fit context

## INFRAÇÕES IBAMA (Fonte: IBAMA Dados Abertos)
{infracoes_summary}

## TÍTULOS MINERÁRIOS (Fonte: ANM SIGMINE)
{titulos_summary}

## RESTRIÇÕES ESPACIAIS (Fonte: ICMBio, FUNAI, IBGE)
{spatial_summary}
"""
    return context
```

**Key rules for LLM context**:
- Always prefix each section with `(Fonte: ...)` for traceability
- Truncate PDF text to most recent/relevant 5K chars
- Include counts (N) with any statistics
- Never ask LLM to generate data — only to summarize/narrate what's provided
- Mark any LLM output as "Gerado por IA — verificar com as fontes citadas"

### For Statistics

All statistical queries include:
- Sample size (N)
- Filter criteria used
- Source view name
- Warning if N < 10

```python
def format_stat(label: str, value: float, n: int, source: str) -> dict:
    return {
        "label": label,
        "value": value,
        "n": n,
        "source": source,
        "warning": "Poucos casos (N<10)" if n < 10 else None,
        "query": f"SELECT ... FROM {source} WHERE ..."  # Reproducible
    }
```

---

## File Structure

```
app/
├── app.py                    # Main Streamlit entry point
├── pages/
│   ├── 1_visao_geral.py     # Executive view
│   ├── 2_explorar_dados.py  # Data explorer
│   ├── 3_consulta.py        # Intelligence query
│   ├── 4_empresa.py         # Company profile
│   └── 5_sobre.py           # About/methodology
├── components/
│   ├── data_loader.py       # DuckDB connection + view creation
│   ├── source_badge.py      # Reusable "Fonte: X" badge
│   ├── stat_card.py         # Statistic with N and source
│   ├── case_viewer.py       # Similar case expandable card
│   └── export.py            # CSV/JSON export helpers
└── config.py                # App configuration
```

---

## Implementation Phases

### Phase 5A: Foundation (3 days)
- [ ] Streamlit app skeleton with 5 tabs
- [ ] `data_loader.py` — DuckDB connection, all views registered
- [ ] `source_badge.py` — reusable component showing "Fonte: X ↗"
- [ ] Tab 5 (Sobre) — render DATA_REGISTRY.md content
- [ ] Tab 1 (Visão Geral) — metric cards from collection_metadata.json + summary queries

### Phase 5B: Data Explorer (3 days)
- [ ] Tab 2 — dataset selector, filters, paginated table
- [ ] Row expansion with detail view
- [ ] Source URL links for each record
- [ ] PDF document links and text viewer
- [ ] CSV/JSON export

### Phase 5C: Intelligence Query (1 week)
- [ ] Tab 3 — search form (activity, município, classe, CNPJ)
- [ ] Similar case matching query (progressive relaxation)
- [ ] Statistical context section
- [ ] Spatial restrictions section
- [ ] Company profile summary
- [ ] Each section with "Fonte" and "Como chegamos nesse dado"

### Phase 5D: Company Profile (3 days)
- [ ] Tab 4 — CNPJ search
- [ ] Aggregate data from all sources by CNPJ
- [ ] Decision history timeline
- [ ] Infraction history
- [ ] CFEM payment summary
- [ ] Spatial restrictions for their ANM titles

### Phase 5E: Polish & Deploy (2 days)
- [ ] Approval rate trend chart (Tab 1)
- [ ] Regional comparison chart
- [ ] Mobile-responsive layout
- [ ] Deploy to Streamlit Cloud or similar
- [ ] Shareable URL for stakeholder validation

---

## Acceptance Criteria

### Functional
- [ ] All 5 tabs render without errors
- [ ] Every data point shows its source (Fonte badge)
- [ ] Every statistic shows N (sample size)
- [ ] Source URLs open in new tab to verification portal
- [ ] Data explorer handles 42K+ rows without crashing
- [ ] CNPJ search returns cross-source profile
- [ ] Intelligence query returns relevant similar cases
- [ ] CSV export works for filtered datasets
- [ ] collection_metadata.json drives freshness indicators

### Non-Functional
- [ ] App loads in < 5 seconds
- [ ] No LLM-generated data without explicit "IA" label
- [ ] Works on Streamlit Cloud (free tier)
- [ ] Single `streamlit run app/app.py` to start
- [ ] No external database dependencies (DuckDB in-memory from parquets)

### Trust & Auditability
- [ ] Tab 5 (Sobre) explains every data source
- [ ] Known limitations are documented in the app
- [ ] "Última atualização" shown for every data source
- [ ] Warning shown when N < 10 for any statistic
- [ ] PDF text shown verbatim, never summarized without labeling

---

## Success Metrics

1. **Stakeholder engagement**: 3+ business stakeholders spend >15 min exploring the app
2. **Data trust**: stakeholders can verify 3+ data points against original sources
3. **Actionable insight**: at least 1 stakeholder says "I didn't know this" about a specific statistic
4. **Iteration signal**: stakeholders request specific features or additional data

---

## Dependencies

- `streamlit>=1.40` (add to pyproject.toml)
- `plotly>=6.0` (for charts)
- Existing: duckdb, pandas, pyarrow (already installed)
- Data: all 10 sources collected (done)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Streamlit too slow for 42K+ row tables | Use DuckDB server-side filtering, paginate results |
| PDF text too large for browser | Lazy load, show first 500 chars with "expand" |
| Stakeholders want features we can't build fast | Document requests, prioritize by frequency |
| Data freshness questions | collection_metadata.json + visible timestamps everywhere |

---

## References

- [plans/product-layer.md](product-layer.md) — original product plan (3 shapes)
- [docs/DATA_REGISTRY.md](../docs/DATA_REGISTRY.md) — data source inventory
- [docs/research/competitor-landscape.md](../docs/research/competitor-landscape.md) — no direct competitor
- [src/licenciaminer/database/queries.py](../src/licenciaminer/database/queries.py) — existing cross-source queries

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
