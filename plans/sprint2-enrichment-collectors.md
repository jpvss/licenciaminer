# Sprint 2: Quick-Win Enrichment Collectors

## Principle: Full Auditability

Every enriched field MUST have:
- `_source_url`: direct URL to verify the data point
- `_source_date`: when the data was fetched
- `_source_name`: which dataset it came from

No derived/inferred fields without explicit `_derived = True` label and explanation.
No LLM-generated content in the dataset — only raw extracted text from official documents.

---

## Implementation Plan

### 2.1 IBAMA Environmental Infractions
**Source**: https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao
**Format**: CSV/JSON with CNPJ
**Join**: CNPJ → match with SEMAD and ANM records

**Collector tasks**:
- [ ] Download CSV from IBAMA open data portal
- [ ] Parse fields: CNPJ, data_auto, tipo_infracao, descricao, valor_multa, municipio, uf
- [ ] Filter UF='MG' (optional — national data is also useful)
- [ ] Save as `data/processed/ibama_infracoes.parquet`
- [ ] NO interpretation — store raw infraction records

**DuckDB enrichment query**:
```sql
-- Count infractions per CNPJ, join to SEMAD decisions
CREATE VIEW v_empresa_infracoes AS
SELECT
    cnpj,
    COUNT(*) AS total_infracoes,
    SUM(valor_multa) AS total_multas,
    MAX(data_auto) AS infracao_mais_recente
FROM v_ibama_infracoes
GROUP BY cnpj;
```

**Audit trail**: Each infraction row has its own auto_infracao_id from IBAMA. Verifiable at the source portal.

---

### 2.2 ANM CFEM Royalty Payments
**Source**: https://dados.gov.br/dataset/sistema-arrecadacao
**Format**: CSV
**Join**: CNPJ + processo ANM

**Collector tasks**:
- [ ] Download CFEM CSV from dados.gov.br
- [ ] Parse fields: cnpj, processo, ano, mes, valor_recolhido, substancia, municipio, uf
- [ ] Filter UF='MG'
- [ ] Save as `data/processed/anm_cfem.parquet`
- [ ] NO aggregation at collection time — store raw monthly payments

**Audit trail**: Each payment row has ano+mes+processo as compound key.

---

### 2.3 ANM RAL Production Reports
**Source**: https://dados.gov.br/dados/conjuntos-dados/relatorio-anual-de-lavra-ral
**Format**: 3 CSV files (raw production, benefited production, mineral water)
**Join**: Processo ANM, CNPJ, município

**Collector tasks**:
- [ ] Download 3 CSVs from dados.gov.br
- [ ] Parse fields: processo, cnpj, substancia, quantidade_produzida, unidade, ano, municipio
- [ ] Filter UF='MG'
- [ ] Save as `data/processed/anm_ral.parquet`

**Audit trail**: Each row = one annual declaration per processo+substancia+ano.

---

### 2.4 Receita Federal CNPJ Enrichment
**Source**: https://opencnpj.org (free API, no auth) or Receita Federal bulk files
**Format**: JSON API (per-CNPJ lookup)
**Join**: CNPJ

**Collector tasks**:
- [ ] Extract unique CNPJs from SEMAD + ANM data
- [ ] Query opencnpj.org API for each (rate limit: ~2/sec)
- [ ] Parse fields: razao_social, nome_fantasia, cnae_principal, porte, data_abertura, situacao, uf, municipio, natureza_juridica
- [ ] Save as `data/processed/cnpj_empresas.parquet`
- [ ] Store raw API response in a `_raw_json` column for full auditability

**Audit trail**: Each record traceable to `https://opencnpj.org/api/cnpj/{CNPJ}`.

**Estimate**: ~5,000 unique CNPJs from mining records × 0.5s = ~42 min.

---

## Implementation Order

1. **IBAMA infractions** (simplest — single CSV download)
2. **CFEM** (single CSV download)
3. **RAL** (3 CSV downloads)
4. **CNPJ enrichment** (API calls, longer but straightforward)

Each collector follows the same pattern as existing ones:
- Download/fetch data
- Filter to MG where applicable
- Add `_source`, `_collected_at` metadata
- Atomic parquet write
- CLI command: `licenciaminer collect infracoes|cfem|ral|cnpj`

## What We Do NOT Do

- No LLM summarization of any data
- No "risk scores" computed from rules we invent — only raw data
- No fuzzy matching labeled as exact matching
- If CNPJ doesn't match, it doesn't match — we don't guess
- All derived columns (e.g., "has_infracoes") are computed via SQL at query time, not stored as source data
- Every analysis output shows the source query and data lineage

## Testing

- [ ] Each collector has tests with fixture data
- [ ] Verify CNPJ join rates (how many SEMAD records actually match)
- [ ] Validate data against portal (spot-check 10 random records per source)
- [ ] DuckDB queries return correct results on test fixtures
