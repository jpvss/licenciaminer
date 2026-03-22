# Session Handoff — 2026-03-21

## What's Running

**PDF text extraction** is running in background:
- Progress: ~1,000/8,040 mining records (12%)
- ETA: ~3 hours from now (~01:45 UTC)
- Saves every 50 records to `data/processed/mg_semad_licencas.parquet`
- Fully resumable — skips already-processed records
- Command: `licenciaminer collect mg-textos --mining-only`

## What's Done

### Data Collected

| Source | File | Records | Status |
|--------|------|---------|--------|
| MG SEMAD decisions | `mg_semad_licencas.parquet` | 42,758 (8,072 mining) | ✅ Scraped from portal |
| MG SEMAD PDF links | (in mg_semad_licencas) | 8,045 with links, 14,735 PDFs | ✅ Enriched |
| MG SEMAD PDF text | (in mg_semad_licencas) | ~1,000 extracted so far | 🔄 Running |
| IBAMA licenses | `ibama_licencas.parquet` | 1,115 | ✅ |
| ANM processes (MG) | `anm_processos.parquet` | 50,723 | ✅ |
| IBAMA infractions | `ibama_infracoes.parquet` | 702,280 (all Brazil) | ✅ |
| ANM CFEM royalties | `anm_cfem.parquet` | 91,026 (MG, 2022-2026) | ✅ |
| CNPJ data | `cnpj_empresas.parquet` | 14 (test batch) | ✅ Working, needs full run |

### Code Quality
- 39 tests passing
- ruff: clean
- mypy: clean (strict mode, 21 source files)
- 11 git commits on main

### Research Completed
- `docs/research/api-research.md` — API documentation
- `docs/research/specflow-gaps.md` — edge cases and design decisions
- `docs/research/competitor-landscape.md` — no direct competitor, TAM R$15-75M/yr
- `docs/research/other-states.md` — SP (CETESB) easiest expansion
- `docs/research/complementary-data-sources.md` — 8 quick-win sources
- `docs/research/data-map-mg.md` — comprehensive MG data map

## Known Issues

1. **IBAMA infractions**: no `uf_infracao` column found — collected all Brazil (702K records). Filter by CNPJ join at query time.
2. **CNPJ collector**: ~30% of "CNPJs" from SEMAD are invalid (malformed, zero-padded CPFs). BrasilAPI returns 400 for these — handled gracefully.
3. **ANM collector**: `resultOffset` doesn't work on ANM server. Uses UF→FASE→ANO iteration instead. Fully working.
4. **IBAMA collector**: JSON wrapped in `{"data": [...]}` envelope — handled.

## Next Session Todo

### Immediate (validate before building more)
1. **Check PDF extraction completed** — verify record count and data quality
2. **Spot-check 10 records** per source against original portals
3. **Run CNPJ enrichment** full batch (~21K CNPJs, ~3 hours at 0.5s/query)

### Sprint 2 Remaining
4. **DuckDB views** linking SEMAD decisions ↔ infractions ↔ CFEM via CNPJ
5. **First cross-source query**: "Do companies with IBAMA infractions have lower approval rates?"
6. **ANM RAL** production data (need to locate correct CSV URL in dados.gov.br)

### Sprint 3: Spatial Overlays
7. Download ICMBio UCs, FUNAI TIs, CECAV caves, IBGE biomes (shapefiles)
8. Add geopandas dependency
9. Spatial join with ANM polygons
10. Add overlap columns to enriched dataset

### Sprint 4: COPAM Governance
11. Scrape CMI meeting list (filter ~150-200 of 1,761 meetings)
12. Download Decision + Pauta PDFs from detail pages
13. Extract voting records via NLP

## Architecture Notes

```
CLI Commands Available:
  licenciaminer collect ibama          # IBAMA licenses
  licenciaminer collect anm --uf MG   # ANM processes
  licenciaminer collect mg --scrape    # MG SEMAD (scraper)
  licenciaminer collect mg --file X    # MG SEMAD (Excel)
  licenciaminer collect mg-docs        # PDF link enrichment
  licenciaminer collect mg-textos      # PDF text extraction
  licenciaminer collect infracoes      # IBAMA infractions
  licenciaminer collect cfem           # ANM CFEM royalties
  licenciaminer collect cnpj           # CNPJ enrichment
  licenciaminer analyze                # Run analysis
```

All data flows through Parquet → DuckDB views. Each source has `_source` and `_collected_at` metadata columns. Sprint 2 sources also have `_source_url` for auditability.

## Key Findings

- **Mining approval rate in MG: 63%** (vs 78.3% for all activities)
- **Classe 5 mining: 39.4%** approval — significantly harder
- **Regional variation: 48.5% (Zona da Mata) to 83.9% (Alto Paranaíba)**
- **Approval trend improving**: 54.3% (2019) → 75.8% (2025)
- **Parecer Técnico PDFs average 22K chars** — contain full technical analysis, conditions, and rejection reasoning
- **No direct competitor** exists for this data/analytics combination
