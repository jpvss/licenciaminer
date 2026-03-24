# Backlog: Future Improvements

Issues found during tab reviews that are acceptable now but worth fixing later.
Append as we go. Don't delete — cross out when done.

---

## Visão Geral

- [ ] **5 sources missing `last_collected` date** — IBAMA Licenças, ANM Processos, IBAMA Infrações, ANM CFEM, Receita Federal CNPJ show red dot despite having data. Fix: save metadata during collection, or infer date from parquet file mtime.
- [ ] **2016 trend data point has only N=28** — passes the N≥10 filter but barely reliable. Consider adding a visual indicator for low-N years.
- [ ] **Source table `records:,` still uses US format in the HTML** — the `fmt_br` fix covers `int` values but edge cases with string-type records from metadata may slip through.

## Consulta

- [ ] **Filiais detection uses f-string SQL** — `cnpj_cpf LIKE '{cnpj_root}%'` should use parameterized query for consistency (low risk since cnpj_root is digits-only from validated input, but architecturally wrong).
- [ ] **CFEM values in company profile use US format** — `R$ {total_pago:,.2f}` should use `fmt_reais`. One instance at line ~213 was fixed, check for others.
- [ ] **ANM titles search by company name** — LIKE match on `NOME` may return false positives for common names. Consider adding CNPJ bridge via SCM.
- [ ] **Infraction detail table** — `DES_AUTO_INFRACAO` has encoding issues (e.g. "ÃREA" instead of "ÁREA"). Data quality issue from source — could clean with `.encode('latin-1').decode('utf-8')` fallback.

## Explorar Dados

- [ ] **No custom filters for 9 of 11 datasets** — Only SEMAD and IBAMA Infrações have sidebar filters. CFEM could benefit from UF/Ano/Substância filters. ANM from UF/FASE. Low priority since text search works.
- [ ] **No detail view for non-SEMAD datasets** — Only SEMAD has row-click detail panel. CFEM and ANM have simpler schemas where a detail panel adds less value.
- [ ] **IBAMA Infrações column `DES_AUTO_INFRACAO` has encoding issues** — Shows "ÃREA" instead of "ÁREA". Source data quality issue from IBAMA's CSV export.

## Análise de Decisões

- [ ] **Caso Detalhado dropdown shows duplicate companies** — JENEVE appears twice because query groups by `cnpj_cpf, empreendimento` and the name varies slightly. Fix: use `MIN(empreendimento)` and group only by `cnpj_cpf`.
- [ ] **Caso Detalhado overlaps with Consulta tab** — Both have company dossier by CNPJ. Caso Detalhado is simpler (no infraction detail, no CFEM breakdown, no ANM titles, no PDF report). Consider merging or adding "Ver dossiê completo" link to Consulta.
- [ ] **Chart text labels use hardcoded `{n:,}` in some hover templates** — Plotly hovertemplate uses `%{customdata:,}` which always renders US format. Can't easily use fmt_br in Plotly hover. Low priority since hover is secondary.

## Concessões

_(pending review)_

## Mapa

_(pending review)_

## Prospecção

_(pending review)_

---

## Cross-cutting

- [ ] **Brazilian number formatting** — audit all pages for remaining `:,` format strings that should use `fmt_br`.
- [ ] **`st.fragment`** — could add to Explorar Dados filters and Mapa to avoid full-page reruns. Skipped for now (restructuring risk > UX gain).
- [ ] **`st.navigation` migration** — would give grouped sidebar sections. Skipped (high restructuring risk).
- [ ] **PDF report not tested on Streamlit Cloud** — session_state fix should work but needs live validation.
