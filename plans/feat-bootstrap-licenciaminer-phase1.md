# feat: Bootstrap LicenciaMiner — Phase 1 Core Pipeline

## Overview

Bootstrap "Mapa da Conformidade" (LicenciaMiner) — a Python CLI that builds an analytical database of environmental licensing decisions for mining projects in Brazil. Phase 1 delivers the complete data pipeline: collection from 3 sources, DuckDB analytical layer, basic analysis, and CLI interface.

**Strategic focus**: MG data first for validation, since it's the only source with approval/rejection outcomes (deferimento/indeferimento).

## Problem Statement / Motivation

Environmental licensing for mining in Brazil is fragmented across 27 state agencies + IBAMA (federal). No tool consolidates historical licensing decisions, cross-references them with legal requirements, or enables data-driven analysis. The new Lei 15.190/2025 mandates 100% digital processes within 3 years — creating a strategic window for data capture.

**Why now**: MG SEMAD has ~42,758 downloadable decisions with approval/rejection outcomes. IBAMA and ANM APIs are live and confirmed. The data exists but no one is systematically collecting and analyzing it.

## Proposed Solution

A Python CLI (`licenciaminer`) that:
1. **Collects** data from IBAMA (JSON), ANM (ArcGIS REST), and MG SEMAD (Excel)
2. **Normalizes** heterogeneous formats into clean Parquet files
3. **Loads** Parquet into DuckDB views for analytical queries
4. **Analyzes** approval rates, patterns by class/substance/region/year

## Technical Approach

### Architecture

```
CLI (Click) → Collectors → Processors → Parquet → DuckDB Views → Analysis
                                          ↑
                                   data/processed/
```

Each collector is independent. Data flows through Parquet as the interchange format. DuckDB queries Parquet files directly via views (no data duplication).

### Key Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Package manager | **uv** | Fast, modern, lockfile support |
| Project layout | **src/ layout** | Prevents accidental imports |
| HTTP client | **httpx + tenacity** | Async-capable, retry with exponential backoff |
| CLI | **Click** | Best composability for multi-command pipelines |
| Database | **DuckDB** (views over Parquet) | No data duplication, automatic optimizations |
| Build backend | **hatchling** | Simple, fast |

### Implementation Phases

#### Phase 1.1: Project Scaffolding
**Estimated effort**: ~30 min

Tasks:
- [ ] Initialize git repository
- [ ] Create [pyproject.toml](pyproject.toml) with dependencies and entry points
- [ ] Create directory structure with `__init__.py` files
- [ ] Create [.gitignore](.gitignore) (ignore `data/raw/`, `data/processed/`, `.env`, `__pycache__/`, `*.egg-info/`, `.venv/`)
- [ ] Create [.env.example](.env.example) with configurable paths
- [ ] Create [src/licenciaminer/config.py](src/licenciaminer/config.py) — URLs, paths, constants
- [ ] Create [src/licenciaminer/__main__.py](src/licenciaminer/__main__.py)
- [ ] Create `data/raw/`, `data/processed/`, `data/reference/` directories with `.gitkeep`
- [ ] Update [CLAUDE.md](CLAUDE.md) with verification commands
- [ ] Run `uv sync` to verify environment

**Directory structure:**
```
licenciaminer/
├── CLAUDE.md
├── CLAUDE_CODE_KICKOFF.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   └── licenciaminer/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── collectors/
│       │   ├── __init__.py
│       │   ├── ibama.py
│       │   ├── anm.py
│       │   └── mg_semad.py
│       ├── processors/
│       │   ├── __init__.py
│       │   └── normalize.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   ├── loader.py
│       │   └── queries.py
│       └── analysis/
│           ├── __init__.py
│           └── reports.py
├── data/
│   ├── raw/.gitkeep
│   ├── processed/.gitkeep
│   └── reference/.gitkeep
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   └── .gitkeep
│   ├── test_ibama.py
│   ├── test_anm.py
│   ├── test_mg_semad.py
│   └── test_analysis.py
└── docs/
    └── research/
```

**pyproject.toml:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "licenciaminer"
version = "0.1.0"
description = "Base analítica de licenciamento ambiental minerário no Brasil"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "duckdb>=1.2",
    "httpx>=0.27",
    "pandas>=2.2",
    "pyarrow>=18.0",
    "openpyxl>=3.1",
    "tenacity>=9.0",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-httpx>=0.35",
    "ruff>=0.8",
    "mypy>=1.13",
]

[project.scripts]
licenciaminer = "licenciaminer.cli:cli"

[tool.hatch.build.targets.wheel]
packages = ["src/licenciaminer"]

[tool.ruff]
target-version = "py311"
line-length = 99

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**config.py:**
```python
"""Configurações centrais do LicenciaMiner."""
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REFERENCE_DIR = DATA_DIR / "reference"
DB_PATH = Path(os.getenv("DB_PATH", DATA_DIR / "licenciaminer.duckdb"))

# URLs
IBAMA_SISLIC_URL = os.getenv(
    "IBAMA_SISLIC_URL",
    "https://dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json",
)
ANM_FEATURESERVER_URL = os.getenv(
    "ANM_FEATURESERVER_URL",
    "https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query",
)

# ANM
ANM_PRIORITY_UFS = ["MG", "PA", "GO", "BA", "MT", "MA"]
ANM_MAX_RECORDS = 5000
ANM_FASES = [
    "REQUERIMENTO DE PESQUISA",
    "AUTORIZAÇÃO DE PESQUISA",
    "REQUERIMENTO DE LAVRA",
    "CONCESSÃO DE LAVRA",
    "LICENCIAMENTO",
    "REGISTRO DE EXTRAÇÃO",
    "DISPONIBILIDADE",
]

# MG SEMAD
MG_DEFAULT_FILE = RAW_DIR / "mg_decisoes.xlsx"
MG_MINING_CODE_PREFIX = "A-0"

# Timeouts
HTTP_TIMEOUT = 120.0
RETRY_ATTEMPTS = 5
RETRY_MIN_WAIT = 2
RETRY_MAX_WAIT = 60
```

Success criteria:
- [ ] `uv sync` succeeds
- [ ] `uv run python -m licenciaminer --help` shows CLI help
- [ ] Directory structure exists as specified

---

#### Phase 1.2: IBAMA Collector
**Estimated effort**: ~20 min

Tasks:
- [ ] Implement [src/licenciaminer/collectors/ibama.py](src/licenciaminer/collectors/ibama.py)
- [ ] Download full JSON from SISLIC endpoint
- [ ] Filter records where `tipologia` contains "Mineração"
- [ ] Normalize columns to snake_case
- [ ] Parse dates from DD/MM/YYYY strings
- [ ] Add `_source` and `_collected_at` metadata columns
- [ ] Save as `data/processed/ibama_licencas.parquet`
- [ ] Write temp file, rename atomically on success
- [ ] Write test [tests/test_ibama.py](tests/test_ibama.py) with mock HTTP response
- [ ] Create test fixture [tests/fixtures/ibama_sample.json](tests/fixtures/ibama_sample.json)

**Key implementation detail** — the IBAMA endpoint is a static JSON dump, not an API. Download the entire file, filter in memory:

```python
@retry(stop=stop_after_attempt(5), wait=wait_exponential(min=2, max=60))
def collect_ibama(output_dir: Path) -> Path:
    """Coleta licenças ambientais de mineração do IBAMA SISLIC."""
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(IBAMA_SISLIC_URL)
        response.raise_for_status()
        data = response.json()

    df = pd.DataFrame(data)
    df = df[df["tipologia"].str.contains("Mineração", case=False, na=False)]
    # normalize columns, parse dates...
    # write to temp, rename atomically
```

Success criteria:
- [ ] `uv run python -m licenciaminer collect ibama` downloads and saves parquet
- [ ] Parquet contains only mining-related licenses
- [ ] Dates are properly parsed as datetime columns
- [ ] Tests pass with mocked HTTP response

---

#### Phase 1.3: ANM Collector
**Estimated effort**: ~45 min

Tasks:
- [ ] Implement [src/licenciaminer/collectors/anm.py](src/licenciaminer/collectors/anm.py)
- [ ] Query ArcGIS FeatureServer by UF (priority states: MG, PA, GO, BA, MT, MA)
- [ ] Handle 5000-record limit with pagination via `resultOffset`
- [ ] Check `exceededTransferLimit` flag in response
- [ ] Fallback: subdivide by FASE if offset not supported
- [ ] Log warning if any combo still hits 5000 (potential truncation)
- [ ] Convert epoch millisecond dates to datetime
- [ ] Use `returnGeometry=false` to reduce response size
- [ ] Rate-limit requests (1 second between queries)
- [ ] Add `_source` and `_collected_at` metadata
- [ ] Save as `data/processed/anm_processos.parquet`
- [ ] Write test [tests/test_anm.py](tests/test_anm.py) with mock responses
- [ ] Create test fixture [tests/fixtures/anm_sample.json](tests/fixtures/anm_sample.json)

**Key implementation** — three-level iteration strategy:

```python
def collect_anm(output_dir: Path, ufs: list[str] | None = None) -> Path:
    """Coleta processos minerários da ANM via SIGMINE."""
    ufs = ufs or ANM_PRIORITY_UFS
    all_records: list[dict] = []

    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        for uf in ufs:
            records = _query_by_uf(client, uf)
            all_records.extend(records)

    # normalize, convert dates, save parquet

def _query_by_uf(client, uf) -> list[dict]:
    """Tenta paginação por offset. Se falhar, subdivide por FASE."""
    records = _paginated_query(client, where=f"UF='{uf}'")
    if records is not None:
        return records
    # Fallback: iterate by FASE
    all_records = []
    for fase in ANM_FASES:
        records = _paginated_query(client, where=f"UF='{uf}' AND FASE='{fase}'")
        if records is not None:
            all_records.extend(records)
        else:
            logger.warning("UF=%s FASE=%s excedeu 5000 — dados truncados", uf, fase)
    return all_records

def _paginated_query(client, where) -> list[dict] | None:
    """Consulta com paginação via resultOffset. Retorna None se paginação não suportada."""
    all_features = []
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": "*",
            "returnGeometry": "false",
            "f": "json",
            "resultOffset": str(offset),
            "resultRecordCount": str(ANM_MAX_RECORDS),
            "orderByFields": "FID ASC",
        }
        response = client.get(ANM_FEATURESERVER_URL, params=params)
        response.raise_for_status()
        data = response.json()

        features = [f["attributes"] for f in data.get("features", [])]
        all_features.extend(features)

        if not data.get("exceededTransferLimit", False):
            break
        offset += len(features)
        time.sleep(1.0)

    return all_features
```

**Critical edge case**: MG has ~55,000 mining processes. If the server ignores `resultOffset`, the first query returns exactly 5000, and `exceededTransferLimit` is absent, we detect this by checking `len(features) == ANM_MAX_RECORDS` and falling back to FASE subdivision.

Success criteria:
- [ ] `uv run python -m licenciaminer collect anm` collects data for priority UFs
- [ ] No silent truncation — warnings logged for any batch hitting 5000
- [ ] Dates converted from epoch ms
- [ ] Tests pass with mocked API responses

---

#### Phase 1.4: MG SEMAD Processor
**Estimated effort**: ~30 min

Tasks:
- [ ] Implement [src/licenciaminer/collectors/mg_semad.py](src/licenciaminer/collectors/mg_semad.py)
- [ ] Read Excel from configurable path (default: `data/raw/mg_decisoes.xlsx`)
- [ ] Validate expected columns exist (fail on missing critical: Decisão, Código de Atividade)
- [ ] Filter rows where Código de Atividade starts with "A-0" (mining)
- [ ] Normalize column names to snake_case without accents
- [ ] Parse dates from DD/MM/YYYY
- [ ] Normalize CNPJ/CPF formatting (strip punctuation)
- [ ] Map Decisão values to standardized enum: "deferido" / "indeferido" / "outro"
- [ ] Add `_source` and `_collected_at` metadata
- [ ] Save as `data/processed/mg_semad_licencas.parquet`
- [ ] Write test [tests/test_mg_semad.py](tests/test_mg_semad.py) with sample Excel fixture
- [ ] Create test fixture [tests/fixtures/mg_sample.xlsx](tests/fixtures/mg_sample.xlsx)

**Key fields from MG SEMAD Excel:**

| Original Column | Normalized | Type | Notes |
|---|---|---|---|
| Regional | regional | str | SUPRAM regional office |
| Município | municipio | str | Municipality |
| Empreendimento | empreendimento | str | Enterprise name |
| CNPJ/CPF | cnpj_cpf | str | Strip punctuation |
| Modalidade | modalidade | str | LAS/LAC/LAT |
| Processo Administrativo | processo_administrativo | str | Process number |
| Código de Atividade | codigo_atividade | str | A-01 to A-07 + sub-codes |
| Atividade | atividade | str | Activity description |
| Classe | classe | int | 1-6 per DN COPAM 217 |
| Ano | ano | int | Year |
| Mês | mes | int | Month |
| Data Publicação DOEMG | data_publicacao | date | DD/MM/YYYY |
| **Decisão** | **decisao** | str | **deferido/indeferido** — the gold |

Success criteria:
- [ ] `uv run python -m licenciaminer collect mg` processes Excel and saves parquet
- [ ] Only mining activities (A-0x codes) are included
- [ ] Decisão column is properly normalized
- [ ] Handles missing file gracefully (clear error message)
- [ ] Tests pass with fixture Excel

---

#### Phase 1.5: Normalizer Module
**Estimated effort**: ~15 min

Tasks:
- [ ] Implement [src/licenciaminer/processors/normalize.py](src/licenciaminer/processors/normalize.py)
- [ ] `normalize_columns(df)` — snake_case, remove accents
- [ ] `normalize_cnpj(value)` — strip punctuation, validate length (14 for CNPJ, 11 for CPF)
- [ ] `parse_date_br(series)` — DD/MM/YYYY → datetime
- [ ] `parse_date_epoch_ms(series)` — epoch ms → datetime
- [ ] `add_metadata(df, source)` — add `_source`, `_collected_at` columns
- [ ] `atomic_parquet_write(df, path)` — write to temp, rename

Success criteria:
- [ ] Shared utilities used by all three collectors
- [ ] Unit tests for each function

---

#### Phase 1.6: DuckDB Loader & Schema
**Estimated effort**: ~25 min

Tasks:
- [ ] Implement [src/licenciaminer/database/schema.py](src/licenciaminer/database/schema.py) — schema definitions
- [ ] Implement [src/licenciaminer/database/loader.py](src/licenciaminer/database/loader.py) — create views from parquets
- [ ] Implement [src/licenciaminer/database/queries.py](src/licenciaminer/database/queries.py) — pre-built analytical queries
- [ ] Create views: `v_ibama`, `v_anm`, `v_mg_semad`
- [ ] Create unified view `v_licencas_todas` using UNION ALL BY NAME
- [ ] Handle missing parquet files gracefully (skip view, log warning)

**DuckDB views over Parquet (not tables):**

```python
def create_views(con: duckdb.DuckDBPyConnection, data_dir: Path) -> dict[str, bool]:
    """Cria views DuckDB apontando para arquivos parquet processados."""
    sources = {
        "v_ibama": data_dir / "processed" / "ibama_licencas.parquet",
        "v_anm": data_dir / "processed" / "anm_processos.parquet",
        "v_mg_semad": data_dir / "processed" / "mg_semad_licencas.parquet",
    }
    loaded = {}
    for view_name, path in sources.items():
        if path.exists():
            con.execute(f"CREATE OR REPLACE VIEW {view_name} AS SELECT * FROM read_parquet('{path}')")
            loaded[view_name] = True
        else:
            logger.warning("Arquivo não encontrado: %s — view %s não criada", path, view_name)
            loaded[view_name] = False
    return loaded
```

**Pre-built queries in [queries.py](src/licenciaminer/database/queries.py):**

```python
# MG: Taxa de aprovação por classe/substância/regional/ano
QUERY_MG_APPROVAL_RATES = """
SELECT
    ano,
    classe,
    codigo_atividade,
    regional,
    COUNT(*) AS total,
    SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
    SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
    ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) / COUNT(*), 1) AS taxa_aprovacao
FROM v_mg_semad
GROUP BY ano, classe, codigo_atividade, regional
ORDER BY ano DESC, classe
"""

# IBAMA: Contagem por tipo de licença/ano
QUERY_IBAMA_BY_TYPE_YEAR = """
SELECT
    EXTRACT(YEAR FROM data_emissao) AS ano,
    tipo_licenca,
    COUNT(*) AS total
FROM v_ibama
GROUP BY ano, tipo_licenca
ORDER BY ano DESC, total DESC
"""

# ANM: Distribuição por fase/UF
QUERY_ANM_BY_FASE_UF = """
SELECT
    UF,
    FASE,
    COUNT(*) AS total,
    ROUND(SUM(AREA_HA), 1) AS area_total_ha
FROM v_anm
GROUP BY UF, FASE
ORDER BY UF, total DESC
"""
```

Success criteria:
- [ ] DuckDB views created from existing parquet files
- [ ] Missing parquets handled gracefully
- [ ] Pre-built queries return correct results against test fixtures
- [ ] Tests pass

---

#### Phase 1.7: Analysis Module
**Estimated effort**: ~20 min

Tasks:
- [ ] Implement [src/licenciaminer/analysis/reports.py](src/licenciaminer/analysis/reports.py)
- [ ] `analyze_mg_approval_rates(con)` — approval rates by class/substance/regional/year
- [ ] `analyze_ibama_licenses(con)` — license counts by type/year
- [ ] `analyze_anm_distribution(con)` — process distribution by fase/UF
- [ ] `run_analysis(data_dir, output)` — orchestrate all analyses
- [ ] Format output as text tables to stdout
- [ ] Support `--output` flag for JSON export
- [ ] Each analysis runs independently (missing source = skip with warning)

Success criteria:
- [ ] `uv run python -m licenciaminer analyze` outputs formatted tables
- [ ] Works with partial data (any subset of sources)
- [ ] JSON export works with `--output results.json`
- [ ] Tests pass with fixture data

---

#### Phase 1.8: CLI Wiring
**Estimated effort**: ~20 min

Tasks:
- [ ] Implement [src/licenciaminer/cli.py](src/licenciaminer/cli.py) with Click
- [ ] Command group: `licenciaminer`
  - Global options: `--verbose`, `--data-dir`
- [ ] Subgroup: `collect`
  - `collect ibama` — run IBAMA collector
  - `collect anm` — run ANM collector (with `--uf` option)
  - `collect mg` — run MG processor (with `--file` option)
  - `collect all` — run IBAMA + ANM, conditionally MG if file exists
- [ ] Command: `analyze`
  - Options: `--output`, `--format`
- [ ] Lazy imports in command functions (keep startup fast)
- [ ] Logging setup: INFO default, DEBUG with `-v`
- [ ] Create [src/licenciaminer/__main__.py](src/licenciaminer/__main__.py)

**CLI interface:**
```
$ licenciaminer --help
Usage: licenciaminer [OPTIONS] COMMAND [ARGS]...

  LicenciaMiner — Base analítica de licenciamento ambiental minerário.

Options:
  -v, --verbose    Ativar logs detalhados.
  --data-dir PATH  Diretório de dados.
  --help           Show this message and exit.

Commands:
  collect   Coletar dados das fontes.
  analyze   Executar análises sobre os dados coletados.

$ licenciaminer collect --help
Commands:
  ibama  Coletar licenças do IBAMA SISLIC.
  anm    Coletar processos da ANM SIGMINE.
  mg     Processar dados da SEMAD/MG.
  all    Coletar de todas as fontes disponíveis.
```

Success criteria:
- [ ] `python -m licenciaminer collect --all` runs all collectors
- [ ] `python -m licenciaminer analyze` runs analysis
- [ ] `-v` flag enables debug logging
- [ ] `--data-dir` overrides default data directory
- [ ] Entry point works: `uv run licenciaminer --help`

---

#### Phase 1.9: Tests & Validation
**Estimated effort**: ~30 min

Tasks:
- [ ] Create [tests/conftest.py](tests/conftest.py) with shared fixtures
  - `tmp_data_dir` — temporary directory structure
  - `sample_ibama_response` — mock IBAMA JSON
  - `sample_anm_response` — mock ANM ArcGIS JSON
  - `sample_mg_excel` — small test Excel file
- [ ] Test each collector with mocked HTTP/files
- [ ] Test normalizer functions
- [ ] Test DuckDB loader with fixture parquets
- [ ] Test analysis queries against known data
- [ ] Test CLI commands with Click's CliRunner
- [ ] Run `uv run ruff check src/`
- [ ] Run `uv run mypy src/`

Success criteria:
- [ ] `uv run pytest tests/ -v` — all tests pass
- [ ] `uv run ruff check src/` — no lint errors
- [ ] `uv run mypy src/` — no type errors

---

## Acceptance Criteria

### Functional Requirements

- [ ] `python -m licenciaminer collect ibama` downloads IBAMA mining licenses to parquet
- [ ] `python -m licenciaminer collect anm` collects ANM processes for priority UFs to parquet
- [ ] `python -m licenciaminer collect mg` processes MG Excel (if file exists) to parquet
- [ ] `python -m licenciaminer collect all` runs all available collectors
- [ ] `python -m licenciaminer analyze` outputs formatted analysis tables
- [ ] MG analysis shows approval rates by classe/atividade/regional/ano
- [ ] IBAMA analysis shows license counts by type/year
- [ ] ANM analysis shows process distribution by fase/UF
- [ ] Analysis works with partial data (any subset of sources)

### Non-Functional Requirements

- [ ] Type hints on all functions
- [ ] Docstrings in Portuguese
- [ ] `pathlib` for all file paths
- [ ] `logging` not `print` (except CLI output)
- [ ] Parquet as interchange format
- [ ] Retry logic on HTTP requests (exponential backoff)
- [ ] Atomic file writes (temp → rename)
- [ ] No silent data truncation (warn on ANM 5000 limit)

### Quality Gates

- [ ] `pytest tests/` passes
- [ ] `ruff check src/` passes
- [ ] `mypy src/` passes (strict mode)

## Dependencies & Prerequisites

- Python 3.11+
- `uv` package manager
- Internet access (for IBAMA and ANM APIs)
- MG SEMAD Excel file (manual download by user)

## Risk Analysis & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| ANM API ignores `resultOffset` | Silent data truncation for large UFs | Fallback to FASE subdivision + warn on 5000 hits |
| IBAMA JSON endpoint is very large | Memory issues | Stream response if >100MB; unlikely based on ~450 records |
| Government APIs are down | Collection fails | Retry with exponential backoff (5 attempts) |
| MG Excel format changes | Processing fails | Validate columns on load, clear error messages |
| MG has >5000 records per UF+FASE at ANM | Data loss | Log explicit warning; plan to add ANO subdivision |

## Future Considerations

- **Phase 2**: Geospatial enrichment (UCs, TIs, biomes via geobr)
- **Phase 3**: DN COPAM 217/2017 classification engine
- **Phase 4**: FastAPI endpoints
- **CNPJ bridging**: Link ANM mining rights to environmental licenses
- **Spatial overlap**: GIS join between ANM polygons and restriction layers
- **NLP**: PDF extraction from pareceres técnicos

## References & Research

### Internal References
- [CLAUDE.md](CLAUDE.md) — Project conventions and gotchas
- [CLAUDE_CODE_KICKOFF.md](CLAUDE_CODE_KICKOFF.md) — Full project specification
- [docs/research/api-research.md](docs/research/api-research.md) — API documentation and tech decisions
- [docs/research/specflow-gaps.md](docs/research/specflow-gaps.md) — Edge cases and design decisions

### External References
- [IBAMA SISLIC Dataset](https://dadosabertos.ibama.gov.br/dataset/licencas-ambientais-de-atividades-e-empreendimentos-licenciados-pelo-ibama)
- [ANM SIGMINE FeatureServer](https://geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0)
- [MG SEMAD Consulta Licença](https://sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca)
- [DN COPAM 217/2017 (PDF)](http://www.siam.mg.gov.br/sla/download.pdf?idNorma=45558)
- [DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview)
- [Click Documentation](https://click.palletsprojects.com/)
- [ArcGIS REST Query API](https://developers.arcgis.com/rest/services-reference/enterprise/query-feature-service-layer/)
- [Lei 15.190/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/L15190.htm)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
