# LicenciaMiner

Analytical database for environmental licensing of mining projects in Brazil.

## Quick Reference

- **Language**: Python 3.11+
- **DB**: DuckDB (parquet-native)
- **Package manager**: uv
- **Run**: `uv run python -m licenciaminer collect --all` then `uv run python -m licenciaminer analyze`
- **Test**: `uv run pytest tests/`
- **Lint**: `uv run ruff check src/`
- **Type check**: `uv run mypy src/`
- **Install**: `uv sync --all-extras`

## Key Data Sources

| Source | Type | URL | Updated |
|--------|------|-----|---------|
| IBAMA SISLIC | JSON | `dadosabertos.ibama.gov.br/dados/SISLIC/sislic-licencas.json` | Daily |
| ANM SIGMINE | ArcGIS REST | `geo.anm.gov.br/arcgis/rest/services/SIGMINE/dados_anm/FeatureServer/0/query` | Daily |
| MG SEMAD | Excel (manual) | `sistemas.meioambiente.mg.gov.br/licenciamento/site/consulta-licenca` | ~Monthly |

## Critical Gotchas

- ANM API: max 5000 records/query, no pagination — iterate by UF or FASE
- IBAMA SISLIC: only emitted licenses (no rejections in open data)
- MG Excel: requires manual download (JS form)
- "Licenciamento" at ANM = mining regime, NOT environmental licensing
- Bridge ANM↔environmental licensing via CNPJ or spatial overlap
- Date formats: IBAMA=DD/MM/YYYY strings, ANM=epoch ms, MG=DD/MM/YYYY
- Mining activity codes in MG: A-01 to A-07 per DN COPAM 217/2017

## Project Structure

- `src/licenciaminer/collectors/` — data source fetchers (ibama, anm, mg_semad)
- `src/licenciaminer/processors/` — cleaning, normalization
- `src/licenciaminer/database/` — DuckDB schema, loader, pre-built queries
- `src/licenciaminer/analysis/` — approval rates, reports
- `src/licenciaminer/cli.py` — Click CLI entry point
- `src/licenciaminer/config.py` — URLs, paths, constants
- `data/raw/` — downloaded files (gitignored)
- `data/processed/` — cleaned parquet (gitignored)
- `data/reference/` — static reference tables (DN 217 classification matrix)
- `tests/` — pytest tests with fixtures in `tests/fixtures/`

## Coding Standards

- Type hints everywhere, docstrings in Portuguese
- Parquet as interchange format, DuckDB for queries
- Use `logging` not `print` (except CLI)
- pathlib for paths, .env for config
