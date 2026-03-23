"""Tab 2: Explorar Dados — Browse datasets with filters, detail view, export."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import (  # noqa: E402
    get_dataset_options,
    run_query,
    run_query_df,
)

st.markdown("# 🔍 Explorar Dados")
st.markdown(
    "*Navegue pelos datasets, filtre e verifique qualquer registro "
    "na fonte original.*"
)

# ── Dataset Selector ──
datasets = get_dataset_options()
if not datasets:
    st.error("Nenhum dataset disponível. Execute os coletores primeiro.")
    st.stop()

selected_label = st.selectbox("Dataset", list(datasets.keys()))
view_name = datasets[selected_label]

# ── Get columns ──
try:
    sample = run_query_df(f"SELECT * FROM {view_name} LIMIT 1")
    all_columns = list(sample.columns)
except Exception as e:
    st.error(f"Erro ao carregar dataset: {e}")
    st.stop()

# Heavy columns to exclude
exclude_cols = {"texto_documentos", "documentos_pdf", "documents_str"}

# ── Filters in sidebar for better UX ──
with st.sidebar:
    st.markdown("### Filtros")

    where_clauses: list[str] = []

    search_text = st.text_input(
        "Busca", placeholder="CNPJ, empresa...", key="search"
    )
    if search_text:
        safe = search_text.replace("'", "").replace(";", "").replace("--", "")
        if safe:
            conds = [
                f"LOWER(CAST({c} AS VARCHAR)) LIKE '%{safe.lower()}%'"
                for c in all_columns
                if c not in exclude_cols and sample[c].dtype == "object"
            ]
            if conds:
                where_clauses.append(f"({' OR '.join(conds)})")

    if view_name == "v_mg_semad":
        mining_only = st.checkbox("Apenas mineração", value=True)
        if mining_only:
            where_clauses.append("atividade LIKE 'A-0%'")

        decisao = st.selectbox(
            "Decisão",
            ["Todos", "deferido", "indeferido", "arquivamento"],
        )
        if decisao != "Todos":
            where_clauses.append(f"decisao = '{decisao}'")

        classe = st.selectbox(
            "Classe", ["Todas", "1", "2", "3", "4", "5", "6"]
        )
        if classe != "Todas":
            where_clauses.append(f"classe = {classe}")

        ano_range = st.slider("Ano", 2016, 2026, (2018, 2026))
        where_clauses.append(f"CAST(ano AS INTEGER) >= {ano_range[0]}")
        where_clauses.append(f"CAST(ano AS INTEGER) <= {ano_range[1]}")

    elif view_name == "v_ibama_infracoes":
        uf = st.selectbox("UF", ["MG", "Todos"])
        if uf != "Todos":
            where_clauses.append(f"UF = '{uf}'")

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# ── Count ──
try:
    count_r = run_query(f"SELECT COUNT(*) AS n FROM {view_name} WHERE {where_sql}")
    total_count = count_r[0]["n"] if count_r else 0
except Exception:
    total_count = 0

# ── Results header ──
st.markdown(
    f'<p class="section-header">'
    f'{total_count:,} registros encontrados</p>',
    unsafe_allow_html=True,
)

# Pagination
page_size = 50
total_pages = max(1, (total_count + page_size - 1) // page_size)

col_page, col_info = st.columns([1, 3])
with col_page:
    page = st.number_input(
        "Página", min_value=1, max_value=total_pages, value=1, label_visibility="collapsed"
    )
with col_info:
    st.caption(f"Página {page} de {total_pages} · {page_size} por página")

offset = (page - 1) * page_size

# ── Query data ──
select_cols = [c for c in all_columns if c not in exclude_cols]
select_sql = ", ".join(select_cols)

query = (
    f"SELECT {select_sql} FROM {view_name} "
    f"WHERE {where_sql} ORDER BY 1 DESC "
    f"LIMIT {page_size} OFFSET {offset}"
)

try:
    df = run_query_df(query)
except Exception as e:
    st.error(f"Erro: {e}")
    st.stop()

if df.empty:
    st.info("Nenhum registro encontrado.")
    st.stop()

# ── Table with row selection ──
if view_name == "v_mg_semad" and "detail_id" in df.columns:
    # Use st.dataframe with selection
    event = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=450,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Auto-show detail for selected row
    selected_rows = event.selection.rows if event.selection else []

    if selected_rows:
        row_idx = selected_rows[0]
        row = df.iloc[row_idx]
        selected_id = str(row.get("detail_id", ""))

        st.markdown(
            '<p class="section-header">Detalhes do Registro</p>',
            unsafe_allow_html=True,
        )

        # Full record with enrichment columns
        detail = run_query_df(
            f"SELECT * FROM {view_name} WHERE detail_id = ?",
            [selected_id],
        )

        if not detail.empty:
            full_row = detail.iloc[0]

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Empreendimento**")
                st.markdown(f"{full_row.get('empreendimento', '—')}")
                st.markdown(f"**CNPJ**: `{full_row.get('cnpj_cpf', '—')}`")
            with c2:
                st.markdown("**Atividade**")
                st.markdown(f"{full_row.get('atividade', '—')}")
                st.markdown(
                    f"**Classe**: {full_row.get('classe', '—')} · "
                    f"**Modalidade**: {full_row.get('modalidade', '—')}"
                )
            with c3:
                decisao_val = full_row.get("decisao", "—")
                icon = {
                    "deferido": "✅", "indeferido": "❌", "arquivamento": "📁"
                }.get(decisao_val, "❓")
                st.markdown(f"**Decisão**: {icon} {decisao_val}")
                st.markdown("**Regional**")
                reg = str(full_row.get("regional", "—")).replace(
                    "Unidade Regional de Regularização Ambiental ", ""
                )
                st.markdown(reg)

            # Source link
            portal_url = (
                "https://sistemas.meioambiente.mg.gov.br/"
                f"licenciamento/site/view-externo?id={selected_id}"
            )
            st.markdown(f"🔗 [Ver no portal SEMAD]({portal_url})")

            # PDF documents
            docs = str(full_row.get("documentos_pdf", ""))
            if docs and len(docs) > 5:
                st.markdown("**Documentos:**")
                for entry in docs.split(";"):
                    if "|" in entry:
                        name, url = entry.split("|", 1)
                        st.markdown(
                            f"- 📄 [{name.strip()}]({url.strip()})"
                        )

            # Parecer text
            texto = str(full_row.get("texto_documentos", ""))
            if texto and len(texto) > 10:
                with st.expander(
                    f"📝 Texto do Parecer ({len(texto):,} caracteres)"
                ):
                    st.text(texto[:8000])
                    if len(texto) > 8000:
                        st.caption(
                            f"Mostrando 8.000 de {len(texto):,} caracteres"
                        )
    else:
        st.caption("👆 Clique em uma linha acima para ver os detalhes")

else:
    # Non-SEMAD datasets: simple table
    st.dataframe(df, use_container_width=True, hide_index=True, height=450)

# ── Export ──
st.markdown("")
if total_count <= 50000:
    export_query = (
        f"SELECT * FROM {view_name} WHERE {where_sql}"
    )

    @st.cache_data(ttl=60)
    def get_csv(q: str) -> bytes:
        return run_query_df(q).to_csv(index=False).encode("utf-8")

    st.download_button(
        f"📥 Exportar CSV ({total_count:,} registros)",
        get_csv(export_query),
        file_name=f"{view_name}.csv",
        mime="text/csv",
    )
else:
    st.caption(
        f"Dataset muito grande ({total_count:,}). "
        "Aplique filtros para exportar."
    )
