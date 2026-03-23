# Session Handoff — 2026-03-23

## What's Running

1. **mg-textos** — extracting text from 1,081 remaining PDFs (~15 min remaining)
   - These are records that had PDF links restored but no text yet
   - Many will be scanned PDFs (no extractable text) — that's expected
   - Resumable: `licenciaminer collect mg-textos --mining-only`

2. **CNPJ enrichment** — 13,100/21,840 (60%, ~1.5 hrs remaining)
   - Resumable: `licenciaminer collect cnpj`

## What's Done

### Data Sources (10/12 collected)

| Source | Records | Status |
|--------|---------|--------|
| MG SEMAD decisions | 42,758 (8,072 mining) | ✅ |
| MG SEMAD PDF links | 8,045 mining records | ✅ Restored |
| MG SEMAD PDF text | 6,964+ (growing) | 🔄 Extracting remaining 1,081 |
| IBAMA licenses | 1,115 | ✅ |
| ANM processes (MG) | 50,723 | ✅ |
| IBAMA infractions | 702,280 | ✅ |
| ANM CFEM royalties | 91,026 | ✅ |
| ANM RAL production | 1,013 | ✅ |
| CNPJ data | ~13,100 (growing) | 🔄 Running |
| Spatial overlaps | 50,725 (UCs, TIs, biomas) | ✅ |
| COPAM CMI meetings | 135 meetings, 2,234 docs | ✅ |
| CECAV caves | — | ⏸ URL 404 |
| ANA water rights | — | ⏸ Portal 504 |

### Code (27 commits)
- 26 source files, 39 tests, ruff clean, mypy strict
- 15 CLI commands
- Incremental refresh pipeline
- 6 data integrity bugs found and fixed

### Documentation
- [DATA_REGISTRY.md](DATA_REGISTRY.md) — comprehensive source inventory
- [plans/product-layer.md](../plans/product-layer.md) — product development plan
- [research/competitor-landscape.md](research/competitor-landscape.md) — no direct competitor
- [research/other-states.md](research/other-states.md) — expansion roadmap
- [research/complementary-data-sources.md](research/complementary-data-sources.md) — prioritized sources
- [research/data-map-mg.md](research/data-map-mg.md) — how sources connect

### Key Insights (from real data)
- Mining approval rate in MG: **63%** (vs 78.3% all activities)
- Classe 5 mining: **39.4%** — significantly harder
- Companies with 6+ infractions: **73.7%** approval (larger = better at navigating)
- CFEM small payers (<R$10K): **70.3%** best; large (>R$1M): **56.7%** worst
- Zona da Mata: consistently hardest regional
- Approval trend improving: 54.3% (2019) → 75.8% (2025)

## Bugs Found and Fixed
1. IBAMA JSON envelope format
2. ANM pagination doesn't work — rewrote to UF→FASE→ANO
3. IBAMA infractions multi-CSV ZIP
4. CFEM comma separator
5. CNPJ API returning HTML → switched to BrasilAPI
6. Concat order dropping enriched rows (CRITICAL)
7. mg_semad.py Excel overwrites scraper data (CRITICAL)
8. add_metadata overwrites timestamps on existing records
9. NaN string false positives in has_content checks
10. CNPJ deduplication missing
11. mg-docs retry causing 12-hour hang → reduced to 2 retries

## Next Session: Product Development

See [plans/product-layer.md](../plans/product-layer.md) for full plan.

**Immediate first step:**
1. Pick a real mining project you know about
2. Run queries against our data manually
3. See if the insights are actually useful
4. This shapes the entire product

**Then:**
1. Generate 1 due diligence report (Shape C) — zero dev needed
2. Build similar case matching query
3. Build condition/rejection extraction from PDF text
4. FastAPI endpoints
5. Streamlit prototype

## CLI Commands Reference

```bash
# Core data
licenciaminer collect ibama
licenciaminer collect anm --uf MG
licenciaminer collect mg --scrape --all-activities
licenciaminer collect mg-docs --mining-only
licenciaminer collect mg-textos --mining-only

# Enrichment
licenciaminer collect infracoes
licenciaminer collect cfem
licenciaminer collect ral
licenciaminer collect cnpj
licenciaminer collect copam

# Spatial
licenciaminer collect spatial --layer all

# Analysis
licenciaminer analyze
licenciaminer analyze -o results.json
```
