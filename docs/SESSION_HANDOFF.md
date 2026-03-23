# Session Handoff — 2026-03-23

## Current State

**Data collection: COMPLETE.** 10/12 sources, ~1 million records, all enriched.
**App: FUNCTIONAL but needs UI/UX overhaul.** 3 tabs working, needs design polish + LLM chat + reports.

## What Exists

### Data (all parquet, all collected)

| Source | File | Records |
|--------|------|---------|
| MG SEMAD decisions | mg_semad_licencas.parquet | 42,758 |
| MG SEMAD PDF text | (in mg_semad_licencas) | 6,968 with text |
| MG SEMAD PDF links | (in mg_semad_licencas) | 8,045 with links |
| IBAMA licenses | ibama_licencas.parquet | 1,115 |
| ANM processes (MG) | anm_processos.parquet | 50,723 |
| IBAMA infractions | ibama_infracoes.parquet | 702,280 |
| ANM CFEM royalties | anm_cfem.parquet | 91,026 |
| ANM RAL production | anm_ral.parquet | 1,013 |
| CNPJ profiles | cnpj_empresas.parquet | 21,572 |
| Spatial overlaps | anm_spatial_overlaps.parquet | 50,725 |
| COPAM CMI meetings | copam_cmi_reunioes.parquet | 135 |
| Reference shapefiles | data/reference/*.parquet | UCs, TIs, biomas, ANM geo |

Blocked: CECAV caves (URL 404), ANA water rights (portal 504)

### App (Streamlit, 3 tabs)

```
app/
├── app.py                     # Landing page + CSS
├── pages/
│   ├── 1_visao_geral.py      # Metrics, trend chart, sources, insights
│   ├── 2_explorar_dados.py   # Data explorer with click-to-detail
│   └── 3_consulta.py         # Intelligence query by project/CNPJ
├── components/
│   ├── __init__.py
│   └── data_loader.py        # DuckDB with @st.cache_resource
└── __init__.py
```

Run: `uv run streamlit run app/app.py`

### Code Stats
- 32 commits on main
- 30+ source files
- 39 tests passing (ruff clean, mypy strict)
- 15 CLI commands for data collection
- 9 DuckDB views, 10+ analytical queries
- Incremental refresh pipeline

### Documentation
- [DATA_REGISTRY.md](DATA_REGISTRY.md) — every source with refresh commands
- [plans/feat-product-app-final.md](../plans/feat-product-app-final.md) — full product plan
- [plans/product-layer.md](../plans/product-layer.md) — 3-shape product strategy
- [research/](research/) — 5 research documents (competitors, other states, data sources, data map, APIs)

## Next Session: UI/UX Overhaul + LLM Features

### Priority 1: UI Redesign (all 3 tabs)
- Run frontend-design skill for premium aesthetic
- Current app is functional but visually plain — needs to look like a premium data product
- Design direction decided: industrial/utilitarian with amber accents
- Key UX: click-to-detail works but overall experience is underwhelming

### Priority 2: Phase 5E — LLM Chat + Reports
- `build_llm_context()` — structured dict from all sources for a CNPJ
- Sidebar chat with Claude API (optional, needs ANTHROPIC_API_KEY)
- PDF due diligence report generator
- "Gerado por IA" banner on all LLM outputs

### Priority 3: Deploy
- Streamlit Cloud deployment
- Share URL with stakeholders

## Known Issues

### UX
- App feels "underwhelming" vs the intelligence platform vision
- Filters cause full page re-render (Streamlit limitation)
- "explorar dados" click-to-detail works but needs visual polish
- Landing page is bare

### Technical
- SQL injection partially fixed (search sanitized, CNPJ parameterized) but some f-string queries remain in consulta.py
- `query_similar_cases()` imported but not used (inline query instead)
- `collection_metadata.json` doesn't track all sources
- Cross-source queries defined in queries.py but not wired into reports.py `analyze` command

### Data
- 13.4% of mining PDFs are scanned (no extractable text) — mostly pre-2020
- CNPJ data: ~30% invalid CNPJs from source (handled gracefully)
- ANM join to SEMAD via CNPJ has 37.6% match rate (company names differ)

## Key Findings (from real data, validated)

- Mining approval rate MG: **63%** (vs 78.3% all activities)
- Classe 5: **39.4%** approval
- Zona da Mata: **48.5%** (hardest regional)
- Companies with 6+ infractions: **73.7%** (larger companies navigate better)
- CFEM small payers (<R$10K): **70.3%** best; large (>R$1M): **56.7%** worst
- Trend improving: 54.3% (2019) → 75.8% (2025)
- No direct competitor in this space (TAM: R$15-75M/year)

## CLI Reference

```bash
# Data collection
licenciaminer collect mg --scrape --all-activities    # Incremental
licenciaminer collect mg-docs --mining-only            # PDF links
licenciaminer collect mg-textos --mining-only           # PDF text
licenciaminer collect ibama                             # Federal licenses
licenciaminer collect infracoes                         # IBAMA infractions
licenciaminer collect cfem                              # CFEM royalties
licenciaminer collect ral                               # RAL production
licenciaminer collect cnpj                              # CNPJ profiles
licenciaminer collect copam                             # COPAM meetings
licenciaminer collect anm --uf MG                      # ANM processes
licenciaminer collect spatial --layer all               # Spatial data

# App
uv run streamlit run app/app.py

# Analysis
licenciaminer analyze
licenciaminer analyze -o results.json

# Quality
uv run pytest tests/
uv run ruff check src/ app/
uv run mypy src/
```
