# feat: Dashboard de Analise de Decisoes de Licenciamento

## Overview

Build a new Streamlit dashboard page that provides structured analysis of environmental licensing decisions from MG SEMAD data, inspired by the "Parecer Unico" document structure (e.g., Parecer 2675/2023 - Vallourec/Mina Pau Branco). The goal is to answer: **why are licenses approved or rejected?** and surface the key factors that influence decisions — starting as a POC with existing structured data before expanding to full-text PDF analysis.

## Problem Statement / Motivation

Today the app shows *what* decisions were made (deferido/indeferido rates, trends by year/classe/regional), but not *why*. The Parecer Unico document reveals rich structured decision factors:

- **Infractions history** reducing license validity (Art. 32 Decreto 47.383/2018)
- **Condicionantes** (12 mandatory conditions in Vallourec's case)
- **Environmental overlaps** (UCs, TIs, biomas, cavidades)
- **TAC agreements** (Termo de Ajustamento de Conduta)
- **Intervention areas** (suppression of vegetation, hectares)
- **License type/modality** correlating with outcomes
- **Corrective vs. regular licensing** patterns

The stakeholder need is to understand if systematized analysis of these factors across 8,000+ mining decisions is feasible — and if so, what actionable intelligence it produces.

## Feasibility Assessment

**Yes, this is feasible as a POC.** Here's what we have:

### Data Available (structured, no PDF parsing needed)

| Data Point | Source | Records | Coverage |
|------------|--------|---------|----------|
| Decision outcome (deferido/indeferido/arquivamento) | MG SEMAD | 8,072 mining | 100% |
| License modality (LAS RAS, LAC 1, LAC 2, LOC, etc.) | MG SEMAD | 8,072 | 99.5% |
| Classe (1-6, environmental impact class) | MG SEMAD | 8,072 | 100% |
| Activity code (A-02-03-8, etc.) | MG SEMAD | 8,072 | 100% |
| Regional (licensing office) | MG SEMAD | 8,072 | 100% |
| CNPJ (company identifier) | MG SEMAD | 8,072 | ~90% |
| IBAMA infractions per company | IBAMA infracoes | 702K | Linkable via CNPJ |
| CFEM royalty payments | ANM CFEM | 91K | Linkable via CNPJ |
| Spatial overlaps (UC, TI, bioma) | ANM spatial | 50K | Linkable via ANM processo |
| PDF document text | MG SEMAD texto_documentos | 6,968 | 86% of mining records |
| COPAM meetings | COPAM CMI | 135 | Partial |

### What the Parecer Unico Teaches Us (structure to replicate)

The Parecer 2675/2023 (127 pages) follows this standard structure:

1. **Capa** — Summary: empreendedor, CNPJ, municipio, atividade, classe, fase, situacao (deferimento/indeferimento), processos vinculados
2. **Responsaveis tecnicos** — Consulting firms, professionals, ARTs
3. **Resumo** — Brief narrative of what's being licensed and why
4. **Introducao** — Historical context, previous licenses, production volumes
5. **Caracterizacao do empreendimento** — Technical details (sections 3-14)
6. **Analise legal** — Compliance checks (sections 15.1-15.15):
   - Reserva Legal, APP, Educacao Ambiental, Conformidade Municipal
   - Criterios locacionais (UC overlaps)
   - Orgaos intervenientes (IPHAN, IEPHA, ICMBio)
   - Intervencoes ambientais e compensacoes
   - Recursos hidricos (outorgas)
   - Taxas e emolumentos
   - Autos de infracao (infractions → license validity reduction)
   - Validade da licenca (calculation with infraction penalties)
7. **Conclusao** — Final recommendation (deferimento/indeferimento)
8. **Anexos** — Condicionantes, automonitoramento

### POC Strategy: Start with Structured Data, Validate Questions

Instead of parsing PDFs first, we extract maximum value from our **existing structured + cross-referenced data** to validate which questions matter most.

## Proposed Solution

### New Page: "4_analise_decisoes.py" — Analise de Decisoes

A single new Streamlit page with 3 tabs:

#### Tab 1: Visao Geral das Decisoes (Decision Overview)

**Purpose**: Answer "what patterns exist in approval/rejection?"

**Metrics Row (4 KPIs)**:
- Taxa geral de deferimento (mineracao)
- Indeferimentos no ultimo ano
- Arquivamentos (% and trend)
- Modalidade com maior rejeicao

**Chart 1: Decisao por Modalidade** (stacked bar)
- X-axis: modalidade (LAS RAS, LAS Cadastro, LAC 1, LAC 2, LOC, etc.)
- Stacks: deferido / indeferido / arquivamento
- Insight: LAS RAS/Cadastro (simpler) vs LAC (complex) rejection rates

**Chart 2: Decisao por Classe x Atividade** (heatmap)
- Rows: atividade (A-02-03-8, A-02-06-2, etc.)
- Columns: classe (1-6)
- Color: approval rate (malachite→oxide gradient)
- Shows which activity+class combos are hardest to approve

**Chart 3: Tendencia Temporal** (line + area)
- Monthly or yearly indeferimento rate
- Overlay: total volume of decisions
- Detect if rejection rates are increasing/decreasing

**Chart 4: Mapa de Rigor Regional** (bar chart or small table)
- Regional offices ranked by rejection rate
- With N (sample size) to avoid small-sample bias

#### Tab 2: Fatores de Risco (Risk Factor Analysis)

**Purpose**: Answer "what factors correlate with rejection?"

This tab cross-references SEMAD decisions with other data sources.

**Analysis 1: Infracoes IBAMA → Decisao**
- Query: Companies with IBAMA infractions vs. those without
- Metric: Approval rate for each group
- Chart: Side-by-side bars or donut comparison
- Insight: Does having infractions predict rejection?

**Analysis 2: CFEM (Royalties) → Decisao**
- Query: Companies paying CFEM vs. not
- Metric: Approval rate for each group
- Insight: Does regular royalty payment correlate with better outcomes?

**Analysis 3: Classe + Modalidade Interaction**
- Pivot: For each classe, which modalidade has the worst outcome?
- Key insight from Parecer 2675: Corrective licensing (LOC) vs. regular licensing have different dynamics

**Analysis 4: Reincidencia (Repeat Applicants)**
- Query: Companies with multiple decisions over time
- Metric: Does outcome improve or worsen over repeated applications?
- Chart: Grouped by # of previous decisions

**Analysis 5: Arquivamento Analysis**
- Deep dive into "arquivamento" (shelved/abandoned cases)
- By classe, atividade, regional — where do cases die?
- This is often more informative than rejection, as it indicates process failures

#### Tab 3: Caso Detalhado (Detailed Case Explorer)

**Purpose**: Show a "mini Parecer" for individual cases, mimicking the PDF structure.

**Input**: Select a case from filtered list or search by empreendimento/CNPJ.

**Output Card** (inspired by Parecer Unico capa):
- **Header**: Empreendimento, CNPJ, Municipio
- **Decision badge**: deferido/indeferido/arquivamento (colored)
- **Key Facts**: Atividade, Classe, Modalidade, Regional, Ano
- **Cross-references**:
  - IBAMA infractions count for this CNPJ
  - CFEM payment history
  - Other SEMAD decisions for same CNPJ (timeline)
  - ANM mining titles (if linkable)
- **Documents**: Link to PDF documents (from `documentos_pdf` field)
- **Extracted Text Preview**: First 500 chars of `texto_documentos` (if available)

This tab validates whether users find the "dossier" format valuable before we invest in full PDF parsing.

## Technical Approach

### Architecture

No new data collection or processing needed. This is purely a **new Streamlit page + new DuckDB queries**.

```
app/pages/4_analise_decisoes.py    ← New page (main deliverable)
src/licenciaminer/database/queries.py  ← Add 5-8 new queries
```

### New Queries Needed

```sql
-- 1. Decision distribution by modalidade (mining only)
QUERY_DECISAO_POR_MODALIDADE = """
SELECT modalidade, decisao, COUNT(*) as n
FROM v_mg_semad
WHERE atividade LIKE 'A-0%'
GROUP BY modalidade, decisao
ORDER BY n DESC
"""

-- 2. Heatmap: approval rate by atividade x classe
QUERY_APROVACAO_ATIVIDADE_CLASSE = """
SELECT
  SPLIT_PART(atividade, '-', 1) || '-' || SPLIT_PART(atividade, '-', 2) || '-' || SPLIT_PART(SPLIT_PART(atividade, '-', 3), ' ', 1) as atividade_code,
  classe,
  COUNT(*) as total,
  COUNT(CASE WHEN decisao = 'deferido' THEN 1 END) as deferidos,
  ROUND(100.0 * COUNT(CASE WHEN decisao = 'deferido' THEN 1 END) / COUNT(*), 1) as taxa_aprovacao
FROM v_mg_semad
WHERE atividade LIKE 'A-0%'
GROUP BY 1, 2
HAVING COUNT(*) >= 5
ORDER BY taxa_aprovacao ASC
"""

-- 3. Infractions correlation
QUERY_INFRACOES_DECISAO = """
WITH empresa_infracoes AS (
  SELECT REPLACE(REPLACE(cpf_cnpj_infrator, '.', ''), '-', '') as cnpj,
         COUNT(*) as n_infracoes
  FROM v_ibama_infracoes
  GROUP BY 1
)
SELECT
  CASE WHEN ei.n_infracoes IS NULL THEN 'Sem infracoes'
       WHEN ei.n_infracoes <= 2 THEN '1-2 infracoes'
       WHEN ei.n_infracoes <= 5 THEN '3-5 infracoes'
       ELSE '6+ infracoes' END as faixa_infracoes,
  s.decisao,
  COUNT(*) as n
FROM v_mg_semad s
LEFT JOIN empresa_infracoes ei ON s.cnpj_cpf = ei.cnpj
WHERE s.atividade LIKE 'A-0%'
GROUP BY 1, 2
ORDER BY 1, 2
"""

-- 4. Repeat applicant analysis
QUERY_REINCIDENCIA = """
WITH empresa_historico AS (
  SELECT cnpj_cpf,
         COUNT(*) as total_decisoes,
         COUNT(CASE WHEN decisao = 'deferido' THEN 1 END) as deferidos
  FROM v_mg_semad
  WHERE atividade LIKE 'A-0%' AND cnpj_cpf IS NOT NULL AND cnpj_cpf != ''
  GROUP BY cnpj_cpf
  HAVING COUNT(*) >= 2
)
SELECT
  CASE WHEN total_decisoes <= 3 THEN '2-3 decisoes'
       WHEN total_decisoes <= 10 THEN '4-10 decisoes'
       ELSE '10+ decisoes' END as faixa,
  COUNT(*) as empresas,
  ROUND(AVG(100.0 * deferidos / total_decisoes), 1) as taxa_media_aprovacao
FROM empresa_historico
GROUP BY 1
ORDER BY 1
"""

-- 5. Arquivamento deep dive
QUERY_ARQUIVAMENTO_ANALYSIS = """
SELECT
  classe,
  SPLIT_PART(atividade, '-', 1) || '-' || SPLIT_PART(atividade, '-', 2) as atividade_grupo,
  COUNT(*) as total,
  COUNT(CASE WHEN decisao = 'arquivamento' THEN 1 END) as arquivamentos,
  ROUND(100.0 * COUNT(CASE WHEN decisao = 'arquivamento' THEN 1 END) / COUNT(*), 1) as taxa_arquivamento
FROM v_mg_semad
WHERE atividade LIKE 'A-0%'
GROUP BY 1, 2
HAVING COUNT(*) >= 10
ORDER BY taxa_arquivamento DESC
"""
```

### UI Components

Reuse existing design system from `app/styles/theme.py`:
- Metric cards with gold borders
- Insight cards with colored left borders
- Color coding: malachite (deferido), oxide (indeferido), slate (arquivamento), amber (highlight)
- Typography: DM Serif Display for headings, Instrument Sans for body

### Chart Library

Use Plotly (already in the project) for:
- Stacked bar charts
- Heatmaps
- Line + area charts
- Donut comparisons

## Acceptance Criteria

### Functional Requirements

- [ ] New page "Analise de Decisoes" accessible from sidebar and home navigation
- [ ] Tab 1: 4 KPI metrics + 4 charts showing decision patterns by modalidade, classe, atividade, regional
- [ ] Tab 2: 5 cross-reference analyses (infracoes, CFEM, classe+modalidade, reincidencia, arquivamento)
- [ ] Tab 3: Individual case detail card with cross-referenced dossier
- [ ] All charts follow existing "Geological Editorial" design system
- [ ] All data fully auditable — source attribution on every metric
- [ ] Filter: "Apenas mineracao" toggle (default on)
- [ ] Filter: Year range selector

### Non-Functional Requirements

- [ ] Page loads in <3 seconds on Streamlit Cloud (400MB memory limit)
- [ ] No new data collection or processing required
- [ ] No new Python dependencies

### Quality Gates

- [ ] Existing tests still pass (`uv run pytest tests/`)
- [ ] Lint passes (`uv run ruff check src/`)
- [ ] Manual QA: verify metrics match what "Explorar Dados" page shows for same filters

## Success Metrics

**POC is validated if**:
1. The decision-by-modalidade chart reveals meaningful differences (>10pp spread in approval rates)
2. The infraction correlation analysis shows statistically observable pattern (not random noise)
3. A user (you) can look at a specific case in Tab 3 and confirm the cross-referenced data tells a coherent story

**Expansion triggers** (if POC validates):
- Parse `texto_documentos` to extract condicionantes count, infraction mentions, TAC references
- Build LLM-powered "Parecer summary" from PDF text
- Add predictive model for approval likelihood

## Dependencies & Risks

### Dependencies
- Existing parquet data (already collected, no new fetching)
- Existing DuckDB views and query infrastructure
- Existing Streamlit app structure and design system

### Risks
- **CNPJ linkage quality**: Not all SEMAD records have clean CNPJs. Mitigation: show "N matched" counts.
- **Small sample sizes**: Some atividade+classe combos have <10 records. Mitigation: minimum threshold filter.
- **Arquivamento ambiguity**: "arquivamento" could mean many things (abandoned by applicant, administrative shelving, etc.). Mitigation: present as exploratory, not causal.

## Implementation Phases

### Phase 1: POC (this plan) — New page with structured data
- 5 new queries in `queries.py`
- 1 new Streamlit page `4_analise_decisoes.py`
- 3 tabs with charts and cross-references
- Estimated: single session

### Phase 2: Text Mining (future)
- Parse `texto_documentos` (6,968 records with text)
- Extract: condicionantes count, infraction references, TAC mentions, area (hectares)
- Add NLP-derived columns to analysis

### Phase 3: LLM Intelligence (future)
- Use Claude API to summarize Parecer text into structured fields
- Build "motivos de indeferimento" classifier from text
- Generate natural-language insights per case

## File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `app/pages/4_analise_decisoes.py` | CREATE | New dashboard page (~400 lines) |
| `src/licenciaminer/database/queries.py` | EDIT | Add 5-8 new SQL queries |
| `app/app.py` | EDIT | Add navigation card for new page |

## References

- Parecer Unico 2675/2023 (Vallourec Mina Pau Branco): `docs/research/CAPA DO PARECER ÚNICO DE LICENCIAMENTO CONVENCIONAL Nº 2675:2023.pdf`
- Existing queries: `src/licenciaminer/database/queries.py`
- Design system: `app/styles/theme.py`
- Current overview page (pattern to follow): `app/pages/1_visao_geral.py`
- Data loader: `src/licenciaminer/database/loader.py`
