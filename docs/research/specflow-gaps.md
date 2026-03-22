# SpecFlow Analysis — Gaps and Edge Cases

Compiled: 2026-03-21

## Critical Gaps (must resolve before implementation)

### 1. ANM 5000-record subdivision strategy
MG alone has ~55,000 mining processes. A single UF+FASE combination could exceed 5000.
**Decision**: Try `resultOffset` pagination first. If not supported, iterate UF → FASE → ANO. Log warning if any combo still hits 5000.

### 2. Re-run / incremental update behavior
What happens on second `collect --ibama`?
**Decision**: Full overwrite. Each parquet = latest snapshot. Previous version NOT backed up (can re-download). Add `_collected_at` metadata column.

### 3. ANM mid-iteration failure
If collection fails on UF 15 of 27, do we keep the first 14?
**Decision**: Write to temp file, rename atomically on success. Partial data is NOT saved.

### 4. Analysis output format
**Decision**: Formatted tables to stdout. `--output` flag for JSON export. `--format csv|json` option.

### 5. Partial data analysis
Running analyze with only some sources collected.
**Decision**: Each analysis block runs independently if its source exists. Warn about missing sources, don't crash.

## Important Gaps

### 6. Status command
Kickoff mentions `status` but no spec.
**Decision**: Defer to Phase 1.5. For now, show collection status in `analyze` output header.

### 7. Process command
Kickoff mentions `process` as separate from `collect`.
**Decision**: Fold into `collect`. No separate `process` command.

### 8. Excel format validation
MG may change column names/format.
**Decision**: Validate expected columns on load. Warn on missing columns, fail on critical missing columns (Decisão, Código de Atividade).

### 9. MG Excel file path
Hardcoded path is fragile.
**Decision**: `--file` argument for `collect --mg`, default to `data/raw/mg_decisoes.xlsx`.

### 10. Source URLs as config
**Decision**: Configurable via `.env` with defaults in `config.py`.

## Nice-to-Have (Phase 2+)

- `--dry-run` option
- `--uf` filter for ANM
- Data lineage columns (`_source`, `_collected_at`)
- Data freshness warnings (>30 days old)
- Exit codes (0=success, 1=failure, 2=partial)
- Progress bars (rich library)
