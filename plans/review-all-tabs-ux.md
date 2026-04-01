# Review: All Tabs UX Enhancement — Systematic Tracker

**Approach:** For each tab, act as a senior BIE with mining domain knowledge.
Review current implementation, identify gaps, propose high-value low-effort improvements.

---

## Tab Review Status

| # | Tab | Status | Key Improvements |
|---|-----|--------|-----------------|
| 1 | Landing (app.py) | DONE | Clickable cards, dynamic stats, quick start guide |
| 2 | Visão Geral | DONE | Decision distribution, BR formatting, metadata fallback |
| 3 | Explorar Dados | PENDING | Review filters, table config, detail view, export |
| 4 | Consulta | DONE | Infraction details, CFEM breakdown, ANM titles, filiais, portal links, PDF report |
| 5 | Análise de Decisões | DONE | BR formatting, porte/date humanized, guidance caption |
| 6 | Concessões | DONE | BR formatting, pagination guard, help tooltips, detail panel |
| 7 | Mapa | DONE | Dark tile, BR formatting, help tooltips on UC/TI layers |
| 8 | Prospecção | DONE | BR formatting all 3 views, help tooltip on score, use_container_width |

---

## Review Methodology Per Tab

For each tab:
1. **Read the full file** — understand every query, every section
2. **Check what data is available but not shown** — query the DB for column richness
3. **Identify UX gaps** — where does a user get stuck? what's confusing?
4. **Propose improvements** — ranked by value/effort ratio
5. **Implement** — only high-value changes, no overengineering
6. **Test and deploy**

---

## Completed Reviews

### Tab 1: Landing (app.py) — DONE
- Clickable nav cards via styled st.page_link
- Dynamic stats from live queries with fmt_br
- "Como usar" expander with workflow guide + example CNPJs

### Tab 4: Consulta — DONE
- Infraction detail table (date, type, municipality, value, status)
- CFEM yearly breakdown by substance
- ANM titles section (new)
- Portal "Verificar" links on each decision
- Filiais detection (same CNPJ root)
- PDF report with session_state persistence
- Porte label humanized, date formatted DD/MM/YYYY

---

## Pending Reviews

### Tab 2: Visão Geral
**Current:** 4 metric cards, approval trend chart, 4 insight cards, data sources table, methodology expander
**To review:**
- Are the insights genuinely useful or just restating the metrics?
- Is the data sources table complete and accurate?
- Should we add more charts (decision distribution, regional comparison)?
- Missing: mining vs non-mining breakdown

### Tab 3: Explorar Dados
**Current:** Dataset selector, sidebar filters, paginated table, row detail (SEMAD only), CSV export
**To review:**
- Column config for all datasets (not just SEMAD)
- Filter UX: are the right filters shown per dataset?
- Detail view: only works for SEMAD — should other datasets have detail?
- Export: is the 20K row limit appropriate?

### Tab 5: Análise de Decisões
**Current:** 3 sub-tabs (Overview, Risk Factors, Case Detail)
**To review:**
- Overview: modalidade bar chart, heatmap, indeferimento trend, regional rigor
- Risk: infraction correlation, CFEM correlation, reincidência, archival analysis
- Case Detail: company selector, decision history, infraction/CFEM lookup
- Are the charts readable? Do they tell a story?
- Missing: cross-tab navigation (click a company → goes to Consulta?)

### Tab 6: Concessões
**Current:** Filtered list with KPIs, paginated table, row detail
**To review:**
- Are all relevant columns shown?
- Is the detail panel useful?
- Missing: link to Mapa for spatial context?

### Tab 7: Mapa
**Current:** Folium map with filters, restriction layers, legend
**To review:**
- Performance with batch GeoJSON (already fixed)
- Popup content: is it useful?
- Missing: click polygon → navigate to Concessões detail?

### Tab 8: Prospecção
**Current:** 3 views (Top Oportunidades, Por Empresa, Por Município)
**To review:**
- Is the scoring formula transparent enough?
- Missing: link from opportunity → Consulta for full dossier?
- Empresa view: portfolio analysis useful?
