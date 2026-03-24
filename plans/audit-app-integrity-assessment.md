# Audit: App Integrity & Data Accuracy Assessment

**Type:** Assessment (no production changes)
**Date:** 2026-03-24
**Scope:** All 3 implemented pages, queries.py, loader.py, data_loader.py, all 9 parquet datasets

---

## Executive Summary

The app is **functionally sound** — all 28 SQL queries execute correctly, all column names match their parquets, and the core data (42,758 SEMAD decisions) has zero duplicates and near-zero NULLs. However, the audit found **1 critical data bug**, **2 high-severity issues**, and **several methodological gaps** that affect the accuracy of what we present to users.

---

## CRITICAL — Fix Before Any Demo

### BUG-1: Page 1 "Aprovação Mineração" metric is WRONG

**File:** `app/pages/1_visao_geral.py` ~line 67
**What happens:** The "Aprovação Mineração" card displays `78.3%` (the rate for ALL 42,758 activities), but labels it as mining and shows `N = 8,072` (the correct mining count). The rate should be `63.0%`.
**Root cause:** Uses `QUERY_MG_SUMMARY` which aggregates ALL decisions, not just `atividade LIKE 'A-0%'`.
**Impact:** Overstates mining approval by **15.3 percentage points**. Anyone reading the dashboard gets a fundamentally wrong number.
**Fix:** Use a mining-filtered query for this card, or add a second query that filters `WHERE atividade LIKE 'A-0%'`.

### BUG-2: Hardcoded 78% baseline comparison

**File:** `app/pages/1_visao_geral.py` ~line 248
**What happens:** The insight card compares mining approval rate against a hardcoded `78` (representing the general approval rate). But this should be dynamically queried, not hardcoded.
**Impact:** If general rate changes (e.g., new data collection), the insight becomes stale without anyone noticing. Combined with BUG-1, this comparison is doubly wrong.
**Fix:** Query the general rate dynamically and use it for comparison.

---

## HIGH — Fix Before Release

### BUG-3: ibama_infracoes loader may crash on multi-part parquets

**File:** `src/licenciaminer/database/loader.py` ~line 35
**What happens:** When loading multi-part parquets (ibama_infracoes has part1 + part2), the `read_parquet([...])` call does NOT pass `union_by_name=true`. The two parts have schema mismatches (`DS_ENQUADRAMENTO_COMPLEMENTAR` is VARCHAR in part2, NULL type in part1).
**Impact:** App crashes when trying to load infracoes from split files. Currently works because a single merged file exists as fallback.
**Fix:** Add `union_by_name=true` to all multi-part `read_parquet()` calls.

### DATA-1: 478 duplicate rows in CFEM

**Dataset:** `data/processed/anm_cfem.parquet`
**What happens:** 478 rows are exact duplicates, concentrated in a few companies (e.g., CNPJ 33931486001455 has 73 dupes for 2025/Aug/FOSFATO).
**Impact:** Inflates CFEM totals in cross-source analyses. Small in absolute terms but violates our auditability principle.
**Fix:** Deduplicate on `(Ano, Mes, Processo, CPF_CNPJ, Substancia)` in the processor pipeline.

### DATA-2: Arquivamento methodology undisclosed

**What happens:** The approval rate calculation includes `arquivamento` (3,711 records = 14.1% of mining decisions) in the denominator. These are shelved/abandoned processes — NOT rejections. Including them deflates the reported approval rate by **10.3 percentage points** (63.0% → 73.3% if excluded).
**Impact:** The user sees a lower approval rate than reality, with no explanation of methodology. A consultant using this data could give wrong advice.
**Fix:** Either:
- (a) Exclude arquivamentos from rate calculation, OR
- (b) Keep them but add a clear methodology disclosure on every page that shows approval rates, explaining what "taxa de aprovação" means, OR
- (c) Show both rates: "63.0% (incluindo arquivamentos) / 73.3% (apenas deferido vs indeferido)"

---

## MEDIUM — Improve Robustness

### SEC-1: SQL injection patterns in explorar_dados.py

**File:** `app/pages/2_explorar_dados.py` ~lines 94, 100, 111
**What happens:** Decision, class, and UF filters use f-strings instead of parameterized queries: `f"decisao = '{decisao}'"`.
**Mitigation:** Values come from Streamlit selectboxes with fixed options, so exploitation requires modifying the client. DuckDB also rejects malformed SQL.
**Risk:** Low in practice, but bad pattern. If someone copies this pattern for user-input fields, it becomes exploitable.
**Fix:** Use parameterized `?` placeholders consistently everywhere.

### SEC-2: Document URLs not validated (XSS risk)

**File:** `app/pages/2_explorar_dados.py` ~line 238
**What happens:** URLs from parquet data are put directly into `<a href="{url}">` without validation.
**Impact:** If a URL in the data contains JavaScript (`javascript:alert()`), it executes in the user's browser.
**Fix:** Validate URLs start with `http://` or `https://` before rendering.

### ROBUST-1: Division by zero in 6+ queries

**Files:** `queries.py` lines 18-20, 416-418, 458-460, and inline queries in `1_visao_geral.py`
**What happens:** `100.0 * SUM(...) / COUNT(*)` without `NULLIF(COUNT(*), 0)`. If a filter combination returns zero rows, this produces NULL/error.
**Mitigation:** Most queries have `HAVING COUNT(*) >= N` which prevents zero-row groups. But edge cases exist.
**Fix:** Add `NULLIF(COUNT(*), 0)` to ALL approval rate calculations for defensive consistency.

### ROBUST-2: NULL handling in Python min()

**File:** `app/pages/1_visao_geral.py` ~line 263
**What happens:** `worst = min(class_stats, key=lambda x: x["taxa"])` — if any class has `taxa = NULL` (from a zero-count edge case), Python raises `TypeError`.
**Fix:** Filter out NULL taxa before calling `min()`.

### ROBUST-3: Silent failure on missing metadata

**File:** `app/app.py` ~lines 44-56
**What happens:** If `collection_metadata.json` is missing, the entire freshness section is swallowed by `except Exception: pass`. User sees no data staleness warning.
**Fix:** Show a warning banner when metadata is unavailable.

### ROBUST-4: Temp directory never cleaned

**File:** `app/components/data_loader.py` ~line 28
**What happens:** `tempfile.mkdtemp()` creates a new temp directory per session, never cleaned up.
**Impact:** On long-running Streamlit Cloud, `/tmp` fills up.
**Fix:** Use `tempfile.TemporaryDirectory()` context manager or register cleanup.

---

## LOW — Code Quality

### QUALITY-1: 69 malformed cnpj_cpf values

Lengths 6-13 instead of 14. Likely CNPJs missing leading zeros. Could recover ~60 records by zero-padding to 14 digits. Low impact since they represent 0.16% of data.

### QUALITY-2: 1 row with ano="201"

Truncated year value. Should investigate source and fix in processor pipeline.

### QUALITY-3: Hardcoded thresholds scattered across files

- `HAVING COUNT(*) >= 10` (trend), `>= 5` (class breakdown), `>= 50` (regional)
- Infraction bands: `<= 2`, `<= 5`, `6+`
- Page size: `50`, Export limit: `20,000`, Text truncation: `8,000` chars

Should be constants in `config.py`.

### QUALITY-4: Missing CNPJ checksum validation

**File:** `app/pages/3_consulta.py` ~lines 233-235
Only checks length=14, no modulo-11 checksum. Accepts `00000000000000`.

### QUALITY-5: Home page stat cards 3 & 4 show duplicate/zero metrics

**File:** `app/app.py` ~lines 83-117
`mining_n` defaults to 0 and may not be populated correctly, resulting in duplicate or zero cards.

---

## Data Integrity Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| **Schema consistency** | 10/10 | All columns match across all views |
| **Data completeness** | 9.5/10 | Only modalidade has 2.8% NULLs |
| **Deduplication** | 9/10 | Perfect in SEMAD; 478 dupes in CFEM |
| **Query correctness** | 9/10 | All 28 queries execute; 1 metric mismatch (BUG-1) |
| **Cross-source joins** | 7/10 | CNPJ lookup 98.4%; CFEM 37.7%; Infracoes only 7.3% |
| **Parameterized queries** | 7/10 | Mostly good; 3 f-string patterns remain |
| **Error handling** | 6/10 | Silent failures, missing NULLIF, no input validation |
| **Methodology transparency** | 4/10 | Arquivamento treatment, hardcoded baselines undisclosed |

---

## Cross-Source Join Coverage (for reference)

Starting pool: 4,206 distinct mining CNPJs in SEMAD.

| Target | CNPJs matched | Match % | Decisions covered |
|--------|--------------|---------|-------------------|
| cnpj_empresas | 4,139 | 98.4% | 99.1% |
| CFEM | 1,584 | 37.7% | 43.4% |
| IBAMA infracoes | 309 | 7.3% | 10.6% |
| SCM concessões | 1,981 | 47.1% | — |

The "infractions vs approval rate" analysis (60.8% COM vs 50.9% SEM) operates on only 309 companies / 811 decisions. This should be disclosed as a limited sample.

---

## What My Previous Response Got Wrong

Auditing my own intelligence showcase from the previous conversation turn:

| Claim | Verdict | Detail |
|-------|---------|--------|
| "Top CFEM payer is Vale" | **UNVERIFIED** | CNPJ 33592510000154 is not in our cnpj_empresas table. Publicly known to be Vale, but not provable from our data. |
| "Samarco has 0% approval" | **WRONG** | Grouped by empreendimento name, which fragmented the CNPJ. Actual: 16 mining decisions = 7 deferido + 9 arquivamento = 43.75% |
| "Companies with infractions have higher approval (counter-intuitive)" | **Numbers correct, interpretation speculative** | 60.8% vs 50.9% is real, but based on only 309 vs 623 companies. Causation not established. |
| "63.0% mining approval rate" | **Correct but methodologically incomplete** | Doesn't disclose that arquivamentos are in denominator. Rate is 73.3% if excluded. |
| All other numbers | **Verified correct** | Year trend, class breakdown, regional spread, spatial overlaps all confirmed. |

---

## Recommended Fix Priority

```
Week 1 (before any demo):
  → BUG-1: Fix page 1 metric (critical — shows wrong number)
  → BUG-2: Query baseline dynamically
  → DATA-2: Add methodology disclosure for arquivamento

Week 2 (before release):
  → BUG-3: Fix loader union_by_name
  → DATA-1: Deduplicate CFEM
  → SEC-1: Parameterize remaining f-string queries
  → SEC-2: Validate document URLs
  → ROBUST-1: Add NULLIF to all rate calculations

Backlog:
  → ROBUST-2 through ROBUST-4
  → QUALITY-1 through QUALITY-5
  → Extract hardcoded thresholds to config.py
```
