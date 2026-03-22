# Session Handoff — 2026-03-22

## What's Running

**CNPJ enrichment** running in background:
- ~21,840 unique CNPJs to query (14 already done)
- BrasilAPI at 0.5s/query = ~3 hours
- Resumable — skips already-fetched CNPJs
- ~70% hit rate (30% are invalid/malformed CNPJs from source)

## What's Done

### Data Collected

| Source | File | Records | Status |
|--------|------|---------|--------|
| MG SEMAD decisions | `mg_semad_licencas.parquet` | 42,758 (8,072 mining) | ✅ |
| MG SEMAD PDF links | (in mg_semad_licencas) | 8,045 with links, 14,735 PDFs | ✅ |
| MG SEMAD PDF text | (in mg_semad_licencas) | **6,964 extracted** (86.6% coverage) | ✅ |
| IBAMA licenses | `ibama_licencas.parquet` | 1,115 | ✅ |
| ANM processes (MG) | `anm_processos.parquet` | 50,723 | ✅ |
| IBAMA infractions | `ibama_infracoes.parquet` | 702,280 (all Brazil, 113K MG) | ✅ |
| ANM CFEM royalties | `anm_cfem.parquet` | 91,026 (MG, 2022-2026) | ✅ |
| CNPJ data | `cnpj_empresas.parquet` | 14 (test) | 🔄 Full run in progress |

### PDF Extraction Results
- 253.5 MB of text extracted from 6,964 mining decision PDFs
- Average 36,395 chars per record (~18 pages)
- Deferido: 4,621 records (avg 43K chars)
- Indeferido: 1,197 records (avg 19K chars)
- Arquivamento: 810 records (avg 17K chars)
- 1,081 PDFs could not be extracted (likely scanned images)

### Cross-Source Analysis Working
DuckDB views linking SEMAD ↔ IBAMA infractions ↔ CFEM via CNPJ.

**Key findings:**
- Companies with IBAMA infractions: **66.6% approval** vs 62.3% without
  (counterintuitive — larger established operations navigate better)
- CFEM payers: **65.6% approval** vs 60.5% non-payers
- Outlier: CNPJ 00881112000107 — 0% approval (0/20 deferidos, 18 indeferidos)

### Code Quality
- 39 tests passing, ruff clean, mypy strict (21 source files)
- 14 git commits on main

## Known Issues

1. **IBAMA infractions CNPJs have punctuation** — fixed in queries with REGEXP_REPLACE
2. **CNPJ collector**: ~30% invalid CNPJs from source data (handled gracefully, returns 400)
3. **PDF extraction**: 13.4% of records with PDF links had no extractable text (scanned PDFs)
4. **CFEM ValorRecolhido**: stored as string with comma decimal — needs REPLACE in queries

## Next Steps

### Immediate
1. Check CNPJ enrichment completed
2. Add CNPJ data to cross-source queries (company age, porte, CNAE)

### Sprint 3: Spatial Overlays
3. Download shapefiles: ICMBio UCs, FUNAI TIs, CECAV caves, IBGE biomes
4. Add geopandas dependency
5. Spatial join with ANM polygons
6. Create restriction overlay columns

### Sprint 4: COPAM Governance
7. Scrape CMI meeting list (~150-200 of 1,761 meetings)
8. Fetch detail pages + PDF links
9. Download Decision PDFs
10. NLP extraction of voting records

### Product
11. Design predictive model features from cross-source data
12. Build risk score prototype
13. Consider FastAPI endpoints for queries

## CLI Commands

```bash
# Core data
licenciaminer collect ibama
licenciaminer collect anm --uf MG
licenciaminer collect mg --scrape --all-activities

# Enrichment
licenciaminer collect mg-docs --mining-only
licenciaminer collect mg-textos --mining-only
licenciaminer collect infracoes
licenciaminer collect cfem
licenciaminer collect cnpj

# Analysis
licenciaminer analyze
licenciaminer analyze -o results.json
```

## File Sizes

```
data/processed/
  mg_semad_licencas.parquet    120.0 MB  (42,758 records + PDF text)
  ibama_infracoes.parquet      129.9 MB  (702,280 records)
  anm_processos.parquet          4.0 MB  (50,723 records)
  anm_cfem.parquet               2.4 MB  (91,026 records)
  ibama_licencas.parquet         0.04 MB (1,115 records)
  cnpj_empresas.parquet          0.01 MB (14 records, growing)
```
