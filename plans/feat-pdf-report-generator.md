# feat: PDF Report Generator — Relatório de Inteligência Ambiental

**Type:** Feature
**Priority:** #1 (revenue validation)
**Status:** In progress
**Depends on:** Existing queries in `queries.py`, `fpdf2` (already in deps)

---

## Overview

Generate professional PDF "Relatórios de Inteligência Ambiental" from a CNPJ query. This is the Shape C revenue model — a tangible deliverable that validates whether consultancies/law firms will pay for cross-source environmental intelligence.

**Positioning:** NOT "due diligence" (implies field visits + ART liability). Call it "Relatório de Inteligência Ambiental" — data intelligence, complementary to traditional DD.

**Key insight:** The value is cross-source intelligence no human can compile quickly. A senior consultant billing R$300/hr needs 20-40 hours to compile what we produce in 30 seconds.

---

## Report Structure (8 sections)

### Capa
- LicenciaMiner branding (gold on dark or dark on white)
- "RELATÓRIO DE INTELIGÊNCIA AMBIENTAL"
- Company name, CNPJ, report date
- Risk level badge (BAIXO / MODERADO / ALTO)
- Report UUID for traceability
- "CONFIDENCIAL" marking

### 1. Sumário Executivo
- Traffic-light KPI cards: Risco Geral, Licenças, Infrações, CFEM
- Top 3 findings (auto-generated from data)
- Overall approval rate vs. state average
- Source: `QUERY_CNPJ_PROFILE`, `QUERY_CNPJ_INFRACOES`, `QUERY_CNPJ_CFEM`

### 2. Perfil da Empresa
- Razão social, CNPJ, CNAE, porte, data abertura, situação
- Source: `QUERY_CNPJ_PROFILE` (joins v_mg_semad + v_cnpj)

### 3. Histórico de Licenciamento
- Table of all decisions (ano, atividade, classe, modalidade, decisão)
- Timeline visualization (Plotly → PNG)
- Source: `QUERY_HISTORICO_CNPJ`

### 4. Análise Comparativa
- Approval rate: this company vs. same activity/class vs. state average
- Bar chart comparing rates
- Similar cases summary (5 most recent)
- Source: `query_approval_stats()`, `query_similar_cases()`

### 5. Conformidade — Infrações IBAMA
- Total infractions, years with infractions
- Risk bracket (0, 1-2, 3-5, 6+) with statistical context
- Source: `QUERY_CNPJ_INFRACOES`, `QUERY_INFRACOES_FAIXA_DECISAO`

### 6. Títulos Minerários e CFEM
- ANM processes (phase, substance, area)
- CFEM payment total and status (ativo/inativo)
- Source: `QUERY_CNPJ_ANM_TITULOS`, `QUERY_CNPJ_CFEM`

### 7. Restrições Espaciais
- UC/TI overlap flags from spatial analysis
- Biome context
- Source: `QUERY_SPATIAL_VS_APROVACAO` (statistical, not per-company yet)

### 8. Aviso Legal
- Full LGPD-compliant disclaimer
- "Relatório de inteligência, não parecer técnico"
- Data sources with consultation dates
- Report UUID, system version

---

## Technical Approach

### Engine: fpdf2 (already in deps)
- Custom `LicenciaMinerReport(FPDF)` class
- Brand colors from theme.py palette (inverted for print: white bg, dark text, gold accents)
- Professional typography via embedded TTF fonts
- Charts: Plotly → PNG → embed in PDF

### File Structure
```
app/components/report_generator.py    — Main report class + section renderers
app/components/report_data.py         — Data fetching (wraps existing queries)
```

### Integration Point
- Button on Tab 3 (Consulta) after CNPJ search: "Gerar Relatório PDF"
- `st.download_button` with generated PDF bytes

---

## Queries Used Per Section

| Section | Query | Params |
|---------|-------|--------|
| Capa + Sumário | `QUERY_CNPJ_PROFILE` | `[cnpj]` |
| Sumário | `QUERY_CNPJ_INFRACOES` | `[cnpj]` |
| Sumário | `QUERY_CNPJ_CFEM` | `[cnpj]` |
| Perfil | `QUERY_CNPJ_PROFILE` | `[cnpj]` |
| Histórico | `QUERY_HISTORICO_CNPJ` | `[cnpj]` |
| Comparativa | `query_approval_stats(atividade, classe, regional)` | dynamic |
| Comparativa | `query_similar_cases(atividade, classe, regional)` | dynamic |
| Infrações | `QUERY_CNPJ_INFRACOES` | `[cnpj]` |
| Infrações | `QUERY_INFRACOES_FAIXA_DECISAO` | none |
| Títulos | `QUERY_CNPJ_ANM_TITULOS` | `[empresa_name]` |
| CFEM | `QUERY_CNPJ_CFEM` | `[cnpj]` |
| Espacial | `QUERY_SPATIAL_VS_APROVACAO` | none |

---

## Acceptance Criteria

- [ ] "Gerar Relatório" button on Tab 3 after CNPJ search
- [ ] PDF with 8 sections, Portuguese text, proper formatting
- [ ] Each section cites source with URL and consultation date
- [ ] Traffic-light risk indicators (green/amber/red)
- [ ] Decision history table with outcome badges
- [ ] Approval rate comparison chart (company vs. average)
- [ ] Works with partial data (missing sections show "Dados não disponíveis")
- [ ] Legal disclaimer with LGPD compliance
- [ ] Report UUID and generation timestamp
- [ ] Download via `st.download_button`
- [ ] Generation < 10 seconds
