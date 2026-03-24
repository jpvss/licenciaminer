# fix: App Stabilization & Deep Review

**Type:** Bug fix + Refactor
**Priority:** Critical
**Scope:** All 7 Streamlit pages, data layer, CLI, dependencies
**Framework Decision:** Stay with Streamlit (see evaluation below)

---

## Overview

The LicenciaMiner Streamlit app has accumulated significant bugs: tables not loading, broken SQL joins, thread-unsafe DuckDB connections, SQL injection vulnerabilities, map performance issues, missing dependencies, and hardcoded statistics. This plan identifies every issue and provides a phased fix strategy.

## Framework Evaluation: Should We Stay with Streamlit?

**Recommendation: Stay with Streamlit**, with targeted fixes for each pain point.

| Criterion | Streamlit | Dash | Panel | Marimo | FastHTML | Evidence |
|-----------|-----------|------|-------|--------|----------|----------|
| Claude Code fluency | **Best** | Good | Poor | Moderate | Moderate | Poor |
| DuckDB integration | Good | Good | Good | Good | Good | Best |
| Map performance | Bad→Good (PyDeck) | Good | Best | Limited | Manual | Basic |
| UX quality ceiling | Medium (CSS hacks) | High | Medium | Medium | Highest | Med-High |
| Migration cost | **Zero** | Moderate | High | High | Very High | High |

**Why stay:**
1. **Claude Code-first development** — Streamlit has the largest AI training corpus of any Python dashboard framework. Switching to Dash would make AI interactions 30-50% less efficient.
2. **Existing investment** — 7 pages, custom "Geological Editorial" design system, DuckDB integration. Migration = 2-4 weeks of rewriting instead of building features.
3. **Targeted fixes exist** — Every limitation has a specific solution:
   - Full re-execution → `@st.fragment` (Streamlit 1.37+)
   - Map performance → Replace Folium row-by-row with batch GeoJSON or PyDeck
   - Table performance → `st.dataframe` with `column_config`
   - Navigation → Migrate to `st.navigation` + `st.Page`

**When to reconsider:** If after these fixes, you still need multi-user concurrent access with complex cross-filtering, Dash is the clear migration target. Your Plotly charts and DuckDB layer transfer directly.

---

## Bug Inventory (34 Issues)

### CRITICAL (Data corruption, crashes, security)

| # | Bug | File | Line | Impact |
|---|-----|------|------|--------|
| C1 | Thread-unsafe DuckDB connection shared across sessions | `app/components/data_loader.py` | 36-42 | Crashes under concurrent access |
| C2 | `normalize_cnpj` validation is a no-op (both branches return `digits`) | `src/licenciaminer/processors/normalize.py` | 54-63 | Invalid CNPJs propagate through all joins |
| C3 | Spatial join uses `NOME` (company name) stripped to digits instead of CNPJ | `src/licenciaminer/database/queries.py` | 251 | Entire spatial analysis returns garbage |
| C4 | SQL injection in text search (only strips `'`, `;`, `--`) | `app/pages/2_explorar_dados.py` | 67-75 | Data exfiltration possible |
| C5 | SQL injection in concessoes search | `app/pages/5_concessoes.py` | 124-137 | Same as C4 |
| C6 | SQL injection via f-string in consulta cases query | `app/pages/3_consulta.py` | 346-358 | Same as C4 |
| C7 | SQL injection in `query_approval_stats` regional parameter | `src/licenciaminer/database/queries.py` | 328-330 | Same as C4 |
| C8 | Missing `folium`, `geopandas`, `streamlit-folium` in `requirements.txt` | `requirements.txt` | - | Map page crashes on Streamlit Cloud |

### HIGH (Wrong data displayed, features broken)

| # | Bug | File | Line | Impact |
|---|-----|------|------|--------|
| H1 | `ibama_infracoes` view fails if only single parquet exists (schema expects parts) | `src/licenciaminer/database/schema.py` | 12-15 | Page 1 shows "0 infracoes" silently |
| H2 | Missing metadata for 5 data sources → source table shows "---" | `data/processed/collection_metadata.json` | - | Undermines auditability |
| H3 | `collect --all` only runs 3 of 10+ collectors | `src/licenciaminer/cli.py` | 290-306 | Users get partial data |
| H4 | Prospeccao page hard-stops if `v_concessoes` missing (no fallback to `v_scm`) | `app/pages/7_prospeccao.py` | 34-49 | Page 7 unreachable after `collect --all` |
| H5 | Silent failure: all pages default to 0 on query error (no "data unavailable" indicator) | Multiple pages | - | Users mistake "error" for "zero results" |
| H6 | COPAM and RAL data collected but never exposed in UI | - | - | Significant data invisible to users |
| H7 | `plotly_chart` uses invalid `width="stretch"` (should be `use_container_width=True`) | `app/pages/1_visao_geral.py` | 196 | Chart may not fill container |
| H8 | Column name inconsistency: `data_de_publicacao` vs `data_publicacao_doemg` | `app/pages/3_consulta.py` vs `src/licenciaminer/collectors/mg_semad.py` | 161 / 114 | Queries fail depending on data source path |

### MEDIUM (Performance, UX, maintenance)

| # | Bug | File | Line | Impact |
|---|-----|------|------|--------|
| M1 | Map creates 5000 individual GeoJSON objects in a loop | `app/pages/6_mapa_concessoes.py` | 306-359 | Map takes minutes to render |
| M2 | `ibama_infracoes` scans 702K rows for every MG-only query | Schema + queries | - | 6x unnecessary scan |
| M3 | Hardcoded `"8.000+ decisoes mineracao"` in nav card | `app/app.py` | 112 | Stale number, undermines trust |
| M4 | Hardcoded `"12 FONTES OFICIAIS"` (actual: 14) | `app/app.py` | 122 | Factually wrong |
| M5 | Year slider hardcoded to 2026 max | `app/pages/2_explorar_dados.py` | 95 | Will need manual update each year |
| M6 | Navigation cards only show 4 of 7 pages | `app/app.py` | 70-114 | Pages 5-7 undiscoverable |
| M7 | Version mismatch: `__init__.py` says 0.1.0, `pyproject.toml` says 0.2.0 | `src/licenciaminer/__init__.py` / `pyproject.toml` | 2 / 7 | Confusion |
| M8 | `mg_semad` data includes all activities (42K rows), only 8K are mining | `data/processed/mg_semad_licencas_*.parquet` | - | Unfiltered views show non-mining data |
| M9 | `ORDER BY 1 DESC` on string columns gives wrong sorting | `app/pages/2_explorar_dados.py` | 151 | Confusing data explorer ordering |
| M10 | Double-caching with mismatched TTLs (`cache_data` inside `cache_data`) | `app/pages/5_concessoes.py` | 59-103 | Cache thrashing |
| M11 | REGIME_LABELS dict duplicated across 3 pages | Pages 5, 6, 7 | - | Maintenance hazard |
| M12 | No cache invalidation mechanism (stale data after re-collection) | `app/components/data_loader.py` | - | Must restart server to see new data |
| M13 | Unused `anthropic` dependency | `pyproject.toml` | 25 | Unnecessary install time |
| M14 | `@st.cache_data` on `_load_geometries()` serializes large GeoDataFrame on every access | `app/pages/6_mapa_concessoes.py` | - | Memory overhead |

### LOW (Code quality, minor inconsistencies)

| # | Bug | File | Line | Impact |
|---|-----|------|------|--------|
| L1 | `mg_semad` `ano` column is VARCHAR, not INTEGER | Data files | - | Fragile sorting (works by accident) |
| L2 | No light-mode fallback in CSS variables | `app/styles/theme.py` | - | UI invisible for light-mode users |

---

## Implementation Plan

### Phase 1: Critical Fixes (Data integrity + Security)

Priority: **Do first. These cause crashes, wrong data, or security holes.**

#### 1.1 Fix DuckDB thread safety (`data_loader.py`)
Replace shared connection pattern with cursor-per-query:

```python
# app/components/data_loader.py
@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(db_path)
    create_views(con, DATA_DIR)
    return con

@st.cache_data(ttl=300)
def run_query(query: str, params: tuple | None = None) -> list[dict]:
    con = get_connection()
    cursor = con.cursor()
    try:
        result = cursor.execute(query, params) if params else cursor.execute(query)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row, strict=False)) for row in result.fetchall()]
    finally:
        cursor.close()
```

Fixes: **C1**

#### 1.2 Fix `normalize_cnpj` validation
```python
# src/licenciaminer/processors/normalize.py:63
# Change: return digits
# To:     return ""
```

Fixes: **C2**

#### 1.3 Fix spatial join query
Replace broken `NOME`-to-CNPJ join with SCM-bridged join:
```sql
-- queries.py QUERY_SPATIAL_VS_APROVACAO
-- Replace: dm.cnpj_cpf = REGEXP_REPLACE(COALESCE(anm.NOME, ''), '[^0-9]', '', 'g')
-- With:    dm.cnpj_cpf = scm.cpf_cnpj_do_titular
--          AND scm.processo_norm = sp.PROCESSO
```

Fixes: **C3**

#### 1.4 Fix all SQL injection sites
Convert all f-string SQL to parameterized queries. Key files:
- `app/pages/2_explorar_dados.py` lines 67-75
- `app/pages/5_concessoes.py` lines 124-137
- `app/pages/3_consulta.py` lines 346-358
- `src/licenciaminer/database/queries.py` lines 326-330

Pattern: Replace `f"WHERE field LIKE '%{text}%'"` with `WHERE field LIKE ?` + `(f'%{text}%',)` params.

Fixes: **C4, C5, C6, C7**

#### 1.5 Fix missing dependencies in `requirements.txt`
Add: `folium`, `geopandas`, `streamlit-folium`

Fixes: **C8**

---

### Phase 2: Data Layer Fixes (Missing/broken views, queries)

Priority: **Tables not loading, wrong data displayed.**

#### 2.1 Fix `ibama_infracoes` schema fallback
In `schema.py` / `loader.py`, check for parts first, fall back to single file:

```python
# loader.py create_views()
parts = [data_dir / f"ibama_infracoes_part{i}.parquet" for i in (1, 2)]
single = data_dir / "ibama_infracoes.parquet"
if all(p.exists() for p in parts):
    paths = [str(p) for p in parts]
elif single.exists():
    paths = [str(single)]
else:
    logger.warning("ibama_infracoes: no parquet found")
    return
con.execute(f"CREATE VIEW v_ibama_infracoes AS SELECT * FROM read_parquet({paths})")
```

Fixes: **H1**

#### 2.2 Fix metadata completeness
Update `collection_metadata.json` with correct record counts and dates for all existing parquet files. Add a helper that auto-generates metadata from parquet row counts.

Fixes: **H2**

#### 2.3 Fix `collect --all` to include all automated collectors
```python
# cli.py collect_all()
# Add: infracoes, cfem, cnpj, ral, copam, spatial
# Then: join-concessoes
# Skip: mg (manual), mg-docs, mg-textos, outorgas
```

Fixes: **H3**

#### 2.4 Add `v_scm` fallback to Prospeccao page
Match the pattern already in page 5 (`5_concessoes.py`).

Fixes: **H4**

#### 2.5 Add error state differentiation
Create `safe_query()` helper that distinguishes:
- "0 results" → show `0` with normal styling
- "View missing" → show amber badge: "Fonte nao coletada"
- "Query error" → show red error with details

```python
# app/components/data_loader.py
def safe_query(query: str, context: str = "", fallback=None):
    try:
        return run_query(query)
    except duckdb.CatalogException:
        st.warning(f"Dados nao disponiveis: {context}. Execute `licenciaminer collect`.")
        return fallback
    except Exception as e:
        st.error(f"Erro em {context}: {e}")
        return fallback
```

Fixes: **H5**

#### 2.6 Fix column name inconsistency
Standardize `data_de_publicacao` across scraper and Excel paths. Update queries to use the canonical name.

Fixes: **H8**

#### 2.7 Fix `plotly_chart` parameter
Replace `width="stretch"` with `use_container_width=True` in `1_visao_geral.py`.

Fixes: **H7**

---

### Phase 3: Performance & UX Fixes

Priority: **App feels fast and correct.**

#### 3.1 Fix map performance
Replace row-by-row loop with batch GeoJSON:

```python
# app/pages/6_mapa_concessoes.py
# Replace lines 306-359 with:
folium.GeoJson(
    filtered.to_json(),
    style_function=lambda feature: {
        "fillColor": _color_for(feature, color_by),
        "weight": 1,
        "fillOpacity": 0.4,
    },
    popup=folium.GeoJsonPopup(fields=popup_fields),
    tooltip=folium.GeoJsonTooltip(fields=["processo_norm"]),
).add_to(m)
```

Consider migrating to `st.pydeck_chart` for GPU-accelerated rendering (handles 100K+ polygons).

Fixes: **M1**

#### 3.2 Fix hardcoded statistics
Replace `"8.000+ decisoes mineracao"` and `"12 FONTES OFICIAIS"` with dynamic queries.

Fixes: **M3, M4**

#### 3.3 Fix year slider
Replace hardcoded 2026 with `datetime.now().year`.

Fixes: **M5**

#### 3.4 Add missing navigation cards
Add cards for pages 5 (Concessoes), 6 (Mapa), 7 (Prospeccao) on the home page.

Fixes: **M6**

#### 3.5 Fix version mismatch
Sync `__init__.py` version to `pyproject.toml`.

Fixes: **M7**

#### 3.6 Fix data explorer ordering
Replace `ORDER BY 1 DESC` with explicit column ordering per dataset.

Fixes: **M9**

#### 3.7 Extract shared constants
Move `REGIME_LABELS` and other duplicated dicts to `data_loader.py` or a shared `constants.py`.

Fixes: **M11**

#### 3.8 Add cache refresh mechanism
Add a "Atualizar dados" button in the sidebar that calls `st.cache_data.clear()` and `st.cache_resource.clear()`.

Fixes: **M12**

---

### Phase 4: Enhancements (Expose hidden data, improve architecture)

Priority: **After all bugs are fixed.**

#### 4.1 Expose COPAM and RAL data
- Add COPAM meeting outcomes to "Fatores de Risco" tab
- Add RAL production data to company profile and prospection score
- At minimum, ensure they appear correctly in Explorar Dados dropdown

Fixes: **H6**

#### 4.2 Migrate to `st.navigation` + `st.Page`
Replace legacy `pages/` directory pattern with modern navigation:

```python
# app.py
pg = st.navigation({
    "Inteligencia": [overview, analise],
    "Dados": [explorer, consulta],
    "Geoespacial": [concessoes, mapa, prospeccao],
})
```

Benefits: grouped sidebar navigation, no `sys.path` hacks, inject theme once.

#### 4.3 Add `@st.fragment` for expensive sections
Wrap map rendering and heavy filter sections in `@st.fragment` to avoid full-page reruns on filter changes.

#### 4.4 Expand `config.toml` theme
Add `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor` to match CSS system.

---

## Acceptance Criteria

### Functional Requirements
- [ ] All 7 pages load without errors when all data is collected
- [ ] All 7 pages show meaningful error states when data is missing (not silent zeros)
- [ ] `collect --all` populates all automated data sources
- [ ] Map renders 5000+ polygons in under 5 seconds
- [ ] Text search inputs are safe from SQL injection
- [ ] CNPJ validation rejects invalid lengths
- [ ] Spatial analysis returns meaningful results via correct join
- [ ] Data sources table shows correct record counts and dates
- [ ] Home page statistics are dynamic, not hardcoded

### Non-Functional Requirements
- [ ] App handles 2+ concurrent sessions without crashes
- [ ] `requirements.txt` includes all dependencies for Streamlit Cloud
- [ ] Version numbers are consistent across the project

### Quality Gates
- [ ] `uv run pytest tests/` passes
- [ ] `uv run ruff check src/` passes
- [ ] `uv run mypy src/` passes
- [ ] Manual test: open each page with full data
- [ ] Manual test: open each page with zero data (no parquets)

---

## Risk Analysis

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Parameterizing queries changes behavior for edge-case filters | Medium | Test each page's search with special characters: `%`, `_`, `'`, `"`, `\` |
| `normalize_cnpj` fix breaks downstream joins | Medium | Run all queries before/after fix and compare counts |
| Spatial join fix changes "Fatores de Risco" results | Certain | Document expected output and validate against known cases |
| `st.fragment` requires Streamlit 1.37+ | Low | Already on 1.55+ per pyproject.toml |
| Map batch GeoJSON changes popup/tooltip behavior | Medium | Test with specific polygon interactions |

---

## References

### Internal
- [data_loader.py](app/components/data_loader.py) — DuckDB connection layer (C1)
- [normalize.py](src/licenciaminer/processors/normalize.py) — CNPJ validation (C2)
- [queries.py](src/licenciaminer/database/queries.py) — SQL queries including broken spatial join (C3, C7)
- [schema.py](src/licenciaminer/database/schema.py) — Parquet source mapping (H1)
- [loader.py](src/licenciaminer/database/loader.py) — View creation (H1)
- [cli.py](src/licenciaminer/cli.py) — CLI entry point (H3)
- [app.py](app/app.py) — Landing page (M3, M4, M6)
- [theme.py](app/styles/theme.py) — Design system
- [6_mapa_concessoes.py](app/pages/6_mapa_concessoes.py) — Map page (M1)

### External
- [Streamlit `st.fragment` docs](https://docs.streamlit.io/develop/concepts/architecture/fragments)
- [Streamlit `st.navigation` docs](https://docs.streamlit.io/develop/api-reference/navigation/st.navigation)
- [DuckDB thread safety](https://duckdb.org/docs/stable/guides/python/multiple_threads.html)
- [DuckDB parameterized queries](https://duckdb.org/docs/api/python/dbapi.html)
- [Folium batch GeoJSON](https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson.html)
- [PyDeck GeoJsonLayer](https://deckgl.readthedocs.io/en/latest/layer.html)
