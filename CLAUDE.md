# Sistema Integrado Summo Quartile

Integrated platform for environmental, mineral, and operational intelligence.
Built on top of the LicenciaMiner analytical database.

## Quick Reference

- **Language**: Python 3.11+
- **DB**: DuckDB (parquet-native)
- **Package manager**: uv
- **App**: `uv run streamlit run app/app.py`
- **Collect**: `uv run python -m licenciaminer collect --all`
- **Test**: `uv run pytest tests/`
- **Lint**: `uv run ruff check src/ app/`
- **Type check**: `uv run mypy src/`
- **Install**: `uv sync --all-extras`

## Platform Structure (6 Business Units)

| Unit | Pages | Status |
|------|-------|--------|
| **Summo Ambiental** | Visão Geral, Explorar Dados, Consulta, Análise Decisões, Due Diligence | Active |
| **Direitos e Concessões** | Concessões, Mapa Geoespacial, Prospecção, Viabilidade | Active + placeholder |
| **Mineral Intelligence** | Inteligência Comercial, Monitoramento | Active + placeholder |
| **SQ Solutions** | Mineradora Modelo (IA) | Active (simulated data) |
| **Gestão Interna** | Gestão Interna SQ | Placeholder |

## Key Data Sources (16+)

| Source | Type | CLI Command |
|--------|------|-------------|
| IBAMA SISLIC | JSON API | `collect ibama` |
| ANM SIGMINE | ArcGIS REST | `collect anm` |
| MG SEMAD | Web scraper / Excel | `collect mg` |
| IBAMA Infrações | CSV | `collect infracoes` |
| ANM CFEM | CSV | `collect cfem` |
| ANM RAL | CSV | `collect ral` |
| ANM SCM | CSV | `collect scm` |
| COPAM CMI | Web scraper | `collect copam` |
| CNPJ (Receita) | REST API | `collect cnpj` |
| BCB PTAX | OData API | `collect bcb` |
| Comex Stat | REST API | `collect comex` |
| Spatial (UCs, TIs, biomas) | Shapefiles + WFS | `collect spatial` |
| Commodity prices | Manual CSV | Upload via UI |

## Critical Gotchas

- ANM API: max 5000 records/query, no pagination — iterate by UF or FASE
- IBAMA SISLIC: only emitted licenses (no rejections in open data)
- MG SEMAD: requires manual download (JS form) or `--scrape`
- "Licenciamento" at ANM = mining regime, NOT environmental licensing
- Bridge ANM↔environmental licensing via CNPJ or spatial overlap
- Date formats: IBAMA=DD/MM/YYYY strings, ANM=epoch ms, MG=DD/MM/YYYY
- Mining activity codes in MG: A-01 to A-07 per DN COPAM 217/2017
- Mineradora Modelo: 100% simulated data — clearly labeled

## Project Structure

- `app/app.py` — Streamlit entry point (st.navigation router)
- `app/pages/` — All page files (15 pages across 6 business units)
- `app/components/` — Shared components (data_loader, dd_inventory, dd_scoring, mining_simulator)
- `app/styles/theme.py` — "Geological Editorial" design system
- `src/licenciaminer/collectors/` — Data source fetchers (14 collectors)
- `src/licenciaminer/processors/` — Cleaning, normalization
- `src/licenciaminer/database/` — DuckDB schema (13 views), loader, queries
- `src/licenciaminer/analysis/` — Approval rates, reports
- `src/licenciaminer/cli.py` — Click CLI entry point
- `src/licenciaminer/config.py` — URLs, paths, constants
- `data/raw/` — Downloaded files (gitignored)
- `data/processed/` — Cleaned parquet (gitignored)
- `data/reference/` — Static reference tables, DD inventories, commodity prices
- `tests/` — pytest tests with fixtures in `tests/fixtures/`

## Coding Standards

- Type hints everywhere, docstrings in Portuguese
- Parquet as interchange format, DuckDB for queries
- Use `logging` not `print` (except CLI)
- pathlib for paths, .env for config
- Streamlit pages: inject_theme + hero_html + source_attribution pattern
