# Claude Code Kickoff Prompt — LicenciaMiner

Copy everything below into your first Claude Code session to bootstrap the project.

---

## PROMPT

```
You are helping me build "LicenciaMiner" — an analytical database and compliance-checking tool for environmental licensing of mining projects in Brazil. This is a SaaS product targeting mining companies and environmental consultancies.

## PROJECT CONTEXT

Environmental licensing for mining in Brazil is fragmented across 27 state agencies + IBAMA (federal), each with its own legal framework, systems, and criteria. No tool exists that consolidates historical licensing decisions, cross-references them with legal requirements, and predicts approval likelihood. We are building the data foundation for that tool.

The new Lei 15.190/2025 (Lei Geral do Licenciamento Ambiental) entered into force in February 2026, mandating 100% digital processes within 3 years — creating a strategic window for data capture.

## WHAT WE'VE ALREADY VALIDATED (via deep research)

### Data Sources — Confirmed Available and Live

1. **IBAMA SISLIC (federal licenses)** — JSON updated DAILY (last confirmed: March 20, 2026)
   - URL: `https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json`
   - Also CSV/XML at same path with different extension
   - Fields: `desTipoLicenca`, `numeroProcesso`, `pac`, `dataVencimento`, `empreendimento`, `numLicenca`, `nomePessoa`, `Atualizacao`, `dataEmissao`, `tipologia`
   - Filter mining: `tipologia` contains "Mineração"
   - LIMITATION: Only contains EMITTED licenses (deferrals). No indeferimentos in this dataset.

2. **ANM SIGMINE (mining titles)** — ArcGIS REST API, updated daily
   - FeatureServer: `https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query`
   - Fields: `PROCESSO`, `NUMERO`, `ANO`, `AREA_HA`, `FASE`, `ULT_EVENTO`, `NOME`, `SUBS`, `USO`, `UF`
   - MaxRecordCount: 5000 per query. Does NOT support pagination — use spatial or attribute filters to iterate
   - Shapefiles (full Brazil): `https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip`
   - CSVs: `https://app.anm.gov.br/dadosabertos/scm/` (Licenciamento.csv, Alvara_de_Pesquisa.csv, etc.)
   - IMPORTANT: "Licenciamento" here means the ANM mining regime, NOT environmental licensing
   - DOES NOT contain environmental licensing data — bridge to IBAMA/OEMAs via CNPJ or spatial overlap

3. **MG SEMAD (Minas Gerais decisions)** — THE BEST SOURCE
   - Portal: `https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca`
   - ~42,758 decisions downloadable as Excel 2007+
   - Fields: Regional, Município, Empreendimento, CNPJ/CPF, Modalidade, Processo Administrativo, Protocolo, Código de Atividade, Atividade, Classe (1-6), Ano, Mês, Data Publicação DOEMG, **Decisão** (deferido/indeferido)
   - Mining codes: A-01 (underground), A-02 (open pit), A-03 (immediate use materials), A-04 (mineral water), A-05 (operational units like tailings dams), A-06 (oil/gas), A-07 (mineral research)
   - COPAM meeting minutes with technical opinions (PDFs): `https://sistemas.meioambiente.mg.gov.br/reunioes/`
   - REQUIRES MANUAL DOWNLOAD — JavaScript form, cannot be automated with simple GET
   - Transparency portal (alternate): `https://transparencia.meioambiente.mg.gov.br/views/introducao_processos.php`

4. **Geospatial restriction layers** — all freely available
   - ICMBio UCs: via `geobr` Python package → `geobr.read_conservation_units()`
   - FUNAI TIs: `https://www.gov.br/funai/pt-br/atuacao/terras-indigenas/geoprocessamento-e-mapas` + WFS at `geoserver.funai.gov.br`
   - IBGE biomes: via `geobr.read_biomes()` 
   - CECAV caves: 22,623 caves in shapefile from ICMBio
   - CAR/SICAR: `https://consultapublica.car.gov.br/publico/imoveis/index`
   - MapBiomas Mining: GEE asset `projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_mining_substances_v3`

5. **ANA water rights**: `https://dadosabertos.ana.gov.br/` — outorgas with mining-specific finalidades

### Key Research Findings

- **>90% approval rate** in MG mining chamber (COPAM CMI) — documented by CGE-MG audit and academic studies (Catão 2022, FJP)
- **No competitor** does predictive analysis of licensing approval
- IBAMA + ABDI signed ACT for "Destrava Brasil" — government investing R$ 10.28M in AI for mining process analysis
- MG FEAM already uses Vertex AI (Google Cloud) for licensing support
- **MapBiomas Monitor da Mineração** (Dec 2025): 257,591 mining processes analyzed
- IBAMA pareceres técnicos are public (IN 184/2008) and accessible as PDFs
- DN COPAM 217/2017 classification system (porte × potencial poluidor → classe 1-6) is fully structurable

## TECH STACK

- **Language**: Python 3.11+
- **Database**: DuckDB (analytical queries, parquet native, zero-config) — migrate to PostgreSQL+PostGIS later if needed
- **Data pipeline**: requests + pandas + pyarrow for ETL
- **Geospatial**: geopandas + shapely + geobr (for Brazilian geodata)
- **API framework**: FastAPI (for future SaaS endpoints)
- **Frontend**: will be built separately (likely Next.js) — not in this scope
- **NLP (future)**: for PDF extraction from pareceres/EIAs

## PROJECT STRUCTURE

```
licenciaminer/
├── CLAUDE.md                    # This file — project context for Claude Code
├── pyproject.toml               # Project config (uv/pip)
├── README.md
├── src/
│   ├── __init__.py
│   ├── config.py                # URLs, paths, constants
│   ├── collectors/              # Data source collectors
│   │   ├── __init__.py
│   │   ├── ibama.py             # SISLIC JSON/CSV collector
│   │   ├── anm.py               # SIGMINE API collector
│   │   ├── mg_semad.py          # MG decisions processor
│   │   ├── geospatial.py        # Restriction layers (UCs, TIs, biomes, caves)
│   │   └── ana.py               # Water rights
│   ├── processors/              # Data cleaning and enrichment
│   │   ├── __init__.py
│   │   ├── normalize.py         # Column mapping, date parsing, dedup
│   │   ├── classify.py          # DN 217 classification engine
│   │   ├── spatial_join.py      # Join mining polygons with restriction layers
│   │   └── bridge.py            # ANM↔IBAMA/OEMA linkage via CNPJ/spatial
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.py            # DuckDB schema definitions
│   │   ├── loader.py            # Load parquet → DuckDB
│   │   └── queries.py           # Pre-built analytical queries
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── approval_rates.py    # Deferimento/indeferimento statistics
│   │   ├── patterns.py          # Pattern detection (by class, substance, region, time)
│   │   └── checklist.py         # Requirements checklist generator by tipologia/classe
│   └── cli.py                   # CLI entry point
├── data/
│   ├── raw/                     # Downloaded source files (gitignored)
│   ├── processed/               # Cleaned parquet files (gitignored)
│   └── reference/               # Static reference data (DN 217 tables, etc.)
├── notebooks/                   # Jupyter for exploration
│   └── 01_eda.ipynb
├── tests/
│   └── ...
└── .gitignore
```

## DEVELOPMENT PHASES

### Phase 1: Core Pipeline (THIS SPRINT)
1. Set up project structure with pyproject.toml (use `uv` if available, else pip)
2. Build IBAMA collector — download JSON, filter mineração, normalize, save as parquet
3. Build ANM collector — query FeatureServer for priority states (MG, PA, GO, BA, MT, MA), handle 5K batch limit, save as parquet
4. Build MG processor — read Excel (user places file manually), filter mining codes A-0x, normalize, save as parquet
5. Build DuckDB schema and loader — create tables, unified view
6. Build basic analysis module — approval rates, patterns by class/substance/region/year
7. CLI entry point with commands: `collect`, `process`, `analyze`, `status`

### Phase 2: Geospatial Enrichment
1. Download and cache restriction layers (UCs, TIs, biomes, caves) via geobr
2. Build spatial join: for each ANM polygon, compute overlap with restriction layers
3. Create risk score based on number/type of spatial overlaps
4. Bridge ANM↔MG SEMAD processes via CNPJ

### Phase 3: Classification Engine
1. Implement DN COPAM 217/2017 classification matrix (porte × potencial poluidor → classe)
2. Build requirements checklist generator per tipologia and classe
3. Map required studies (EIA/RIMA, RCA, PCA, PRAD) to each classification

### Phase 4: API Layer (future)
1. FastAPI endpoints for querying the database
2. Endpoint: given coordinates + mineral type + area → return required class, documents, historical approval rate for similar projects

## CRITICAL CONSTRAINTS

- ANM SIGMINE API: MaxRecordCount=5000, does NOT support pagination (resultOffset ignored). Must iterate using WHERE clauses (by UF, by FASE, etc.)
- IBAMA SISLIC: Contains only EMITTED licenses. Indeferimentos are NOT in the open data — only available via SISLIC web portal scraping or LAI request
- MG Excel: Must be manually downloaded by user. The portal uses JavaScript forms.
- Date formats vary: IBAMA uses DD/MM/YYYY strings, ANM uses epoch milliseconds, MG uses DD/MM/YYYY
- CNPJ formatting varies between sources (with/without punctuation)
- "Licenciamento" in ANM context ≠ environmental licensing — it's a mining regime type

## CODING STANDARDS

- Type hints on all functions
- Docstrings in Portuguese (this is a Brazilian product)
- Use pathlib for all file paths
- Use logging module, not print statements (except CLI output)
- Parquet as interchange format between stages
- DuckDB for all analytical queries — avoid loading full datasets into pandas when possible
- Tests for collectors (mock API responses) and processors (sample data fixtures)
- .env file for any configurable paths (DATA_DIR, DB_PATH)

## START

Begin with Phase 1. Set up the project structure, then implement the IBAMA collector first (it's the simplest — single JSON download). After that, ANM collector, then MG processor. Wire them together with the DuckDB loader and basic analysis. Give me a CLI I can run with `python -m licenciaminer collect --all` and `python -m licenciaminer analyze`.
```
