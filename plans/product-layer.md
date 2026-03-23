# Product Layer Plan — LicenciaMiner

## Product Vision

"The Bloomberg Terminal for environmental licensing in Brazilian mining."

Three product shapes, in order of development:

### Shape C: Due Diligence Reports (First Revenue)
- One-time deep report on a company, project, or region
- Generated semi-manually: DuckDB queries + Claude for narrative
- R$5-15K per report
- **Zero additional dev needed** — use existing data + queries
- Target: law firms, investors, M&A advisors
- **Start immediately**

### Shape A: Consultant Copilot (Core Product)
- Self-serve briefing page for environmental consultancies
- Search by activity code + municipality + class + CNPJ
- Returns: statistical context, spatial restrictions, similar cases, conditions, rejection reasons
- R$1-5K/month subscription
- Target: 200+ environmental consultancies in MG
- **Build after validating Shape C**

### Shape B: Portfolio Dashboard (Scale Product)
- Company-level view of all licenses, titles, risks
- CNPJ-based aggregation across all sources
- Alerts for expiring licenses, new decisions
- R$2-10K/month subscription
- Target: mining companies
- **Build after Shape A is validated**

---

## Shape A: Consultant Copilot — Technical Plan

### Components to Build

| Component | Effort | Description |
|-----------|--------|-------------|
| **Similar case matching** | 1 week | Given activity+class+regional, find N most similar SEMAD decisions using DuckDB |
| **Condition extraction** | 2 weeks | Regex/NLP to extract "condicionantes" from deferido Parecer Técnico text |
| **Rejection reason extraction** | 1 week | Extract key phrases from indeferido/arquivamento text |
| **Company profile aggregation** | 3 days | CNPJ → infractions + CFEM + decisions + ANM titles |
| **Spatial risk view** | 3 days | Given coordinates/municipality, show UC/TI/cave/biome overlaps |
| **FastAPI endpoints** | 1 week | Query API for briefing page |
| **Frontend** | 1-2 weeks | Search form + briefing page (Streamlit to start, then proper frontend) |

### Briefing Page Sections

Each section cites its data source. No LLM-generated content without explicit labeling.

1. **Contexto Estatístico** — approval rates for this activity+class+regional combination
   - Source: SEMAD decisions (v_mg_semad)

2. **Restrições Espaciais** — UCs, TIs, caves, biome at the project location
   - Source: spatial overlaps (v_spatial)

3. **Condições Prováveis** — what conditions were imposed in similar approved cases
   - Source: extracted from Parecer Técnico text of deferidos

4. **Motivos de Rejeição** — why similar projects failed
   - Source: extracted from indeferido/arquivamento text

5. **Perfil da Empresa** — infraction history, CFEM, company age/size
   - Source: IBAMA infrações + CFEM + CNPJ data

6. **Casos Similares** — 3-5 most comparable historical decisions with links to full Parecer text
   - Source: SEMAD decisions matched by activity+class+regional

7. **Histórico COPAM** — relevant CMI voting records
   - Source: COPAM CMI meetings

### Similar Case Matching Algorithm

Simple and auditable (no ML black box):

```sql
-- Find most similar cases
SELECT *
FROM v_mg_semad
WHERE atividade LIKE '{activity_prefix}%'
  AND classe = {classe}
  AND regional = '{regional}'
  AND LENGTH(texto_documentos) > 100
ORDER BY
  -- Exact activity match first, then prefix
  CASE WHEN atividade = '{exact_activity}' THEN 0 ELSE 1 END,
  -- Most recent first
  data_de_publicacao DESC
LIMIT 5
```

If fewer than 5 results, relax filters progressively:
1. Same activity + class + regional → exact match
2. Same activity + class (any regional) → broader
3. Same activity prefix (any class) → broadest

### Auditability Requirements

- Every data point on the briefing page links to its source record
- "Condições Prováveis" shows which specific Parecer each condition came from
- No percentages without showing the N (sample size)
- If N < 10, show warning: "Poucos casos similares — use com cautela"
- PDF text is shown verbatim, never summarized by LLM (unless explicitly requested)

---

## Shape C: Due Diligence Report — Template

Can be generated today with existing DuckDB queries:

```
RELATÓRIO DE DILIGÊNCIA AMBIENTAL
Empresa: [CNPJ]
Data: [today]

1. IDENTIFICAÇÃO
   - Razão social, CNAE, porte, data abertura (CNPJ data)

2. HISTÓRICO DE LICENCIAMENTO (MG)
   - Total de decisões, taxa de aprovação
   - Timeline of decisions
   - Current active licenses

3. TÍTULOS MINERÁRIOS (ANM)
   - Active processes, phases, substances, areas
   - Spatial restrictions (UC/TI/biome overlaps)

4. REGISTRO DE INFRAÇÕES (IBAMA)
   - Total infractions, types, amounts
   - Most recent infraction

5. ARRECADAÇÃO CFEM
   - Payment history, regularity
   - Total paid

6. ANÁLISE DE RISCO
   - Approval rate vs industry average
   - Spatial restriction flags
   - Infraction history assessment

7. CASOS SIMILARES
   - 3-5 most comparable decisions
   - Key conditions imposed / rejection reasons

Sources: [list every data source used]
```

---

## Development Roadmap

### Phase 5: Product Foundation (4-6 weeks)
- [ ] Similar case matching query
- [ ] Condition extraction from Parecer text
- [ ] Rejection reason extraction
- [ ] FastAPI endpoints
- [ ] Streamlit prototype

### Phase 6: Validation (2-4 weeks)
- [ ] Generate 3-5 due diligence reports (Shape C)
- [ ] Present Consultant Copilot to 5 consultancies
- [ ] Iterate based on feedback

### Phase 7: Production (4-8 weeks)
- [ ] Proper frontend (Next.js or similar)
- [ ] User authentication
- [ ] Subscription billing
- [ ] Automated refresh pipeline (cron/scheduler)

---

## Key Principles

1. **Auditability over automation** — every data point traceable to source
2. **No hallucinations** — LLM only used for explicit summarization, never for data
3. **Show don't tell** — link to the actual Parecer Técnico, don't paraphrase it
4. **Consultants first** — they understand the domain, they'll validate the product
5. **Revenue before polish** — Shape C reports can generate revenue today
