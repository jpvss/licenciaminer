"""Tab 2: Explorar Dados — Browse datasets with filters, detail view, export."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from app.components.data_loader import (  # noqa: E402
    get_dataset_options,
    run_query_df,
)

st.title("Explorar Dados")
st.markdown("Navegue pelos datasets, filtre, e verifique qualquer registro na fonte original.")
st.divider()

# ── Dataset Selector ──
datasets = get_dataset_options()
if not datasets:
    st.error("Nenhum dataset disponível. Execute os coletores primeiro.")
    st.stop()

selected_label = st.selectbox("Dataset", list(datasets.keys()))
view_name = datasets[selected_label]

# ── Get columns for this view ──
try:
    sample = run_query_df(f"SELECT * FROM {view_name} LIMIT 1")
    all_columns = list(sample.columns)
except Exception as e:
    st.error(f"Erro ao carregar dataset: {e}")
    st.stop()

# ── Filters ──
st.subheader("Filtros")

# Build dynamic filters based on dataset
where_clauses: list[str] = []
filter_cols = st.columns(3)

# Common: text search
with filter_cols[0]:
    search_text = st.text_input("Busca por texto", placeholder="CNPJ, empresa, etc.")
    if search_text:
        # Search across all string columns
        search_conditions = []
        for col in all_columns:
            if sample[col].dtype == "object":
                search_conditions.append(
                    f"LOWER(CAST({col} AS VARCHAR)) LIKE '%{search_text.lower()}%'"
                )
        if search_conditions:
            where_clauses.append(f"({' OR '.join(search_conditions)})")

# Dataset-specific filters
if view_name == "v_mg_semad":
    with filter_cols[1]:
        decisao_filter = st.selectbox(
            "Decisão", ["Todos", "deferido", "indeferido", "arquivamento", "outro"]
        )
        if decisao_filter != "Todos":
            where_clauses.append(f"decisao = '{decisao_filter}'")

    with filter_cols[2]:
        mining_only = st.checkbox("Apenas mineração (A-0x)", value=True)
        if mining_only:
            where_clauses.append("atividade LIKE 'A-0%'")

    filter_cols2 = st.columns(3)
    with filter_cols2[0]:
        classe_options = ["Todos", "1", "2", "3", "4", "5", "6"]
        classe_filter = st.selectbox("Classe", classe_options)
        if classe_filter != "Todos":
            where_clauses.append(f"classe = {classe_filter}")

    with filter_cols2[1]:
        ano_min = st.number_input("Ano mínimo", min_value=2000, max_value=2026, value=2018)
        where_clauses.append(f"CAST(ano AS INTEGER) >= {ano_min}")

    with filter_cols2[2]:
        ano_max = st.number_input("Ano máximo", min_value=2000, max_value=2026, value=2026)
        where_clauses.append(f"CAST(ano AS INTEGER) <= {ano_max}")

elif view_name == "v_ibama_infracoes":
    with filter_cols[1]:
        uf_filter = st.selectbox("UF", ["MG", "Todos"])
        if uf_filter != "Todos":
            where_clauses.append(f"UF = '{uf_filter}'")

# ── Build and Execute Query ──
where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# Count total
try:
    count_result = run_query_df(f"SELECT COUNT(*) AS n FROM {view_name} WHERE {where_sql}")
    total_count = int(count_result.iloc[0]["n"])
except Exception:
    total_count = 0

st.markdown(f"**{total_count:,} registros** encontrados")

# Pagination
page_size = 50
total_pages = max(1, (total_count + page_size - 1) // page_size)
page = st.number_input("Página", min_value=1, max_value=total_pages, value=1)
offset = (page - 1) * page_size

st.caption(f"Página {page} de {total_pages}")

# Exclude heavy columns from table view
exclude_cols = {"texto_documentos", "documentos_pdf", "documents_str"}
select_cols = [c for c in all_columns if c not in exclude_cols]
select_sql = ", ".join(select_cols)

query = f"""
SELECT {select_sql}
FROM {view_name}
WHERE {where_sql}
ORDER BY 1 DESC
LIMIT {page_size} OFFSET {offset}
"""

try:
    df = run_query_df(query)

    if df.empty:
        st.info("Nenhum registro encontrado com esses filtros.")
    else:
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)

        # ── Row Detail ──
        if view_name == "v_mg_semad" and "detail_id" in df.columns:
            st.subheader("Detalhes do Registro")
            detail_ids = df["detail_id"].tolist()
            selected_id = st.selectbox(
                "Selecione um registro pelo detail_id",
                detail_ids,
                index=0,
            )

            if selected_id:
                detail = run_query_df(
                    f"SELECT * FROM {view_name} WHERE detail_id = '{selected_id}'"
                )
                if not detail.empty:
                    row = detail.iloc[0]

                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"**Empreendimento**: {row.get('empreendimento', '')}")
                        st.markdown(f"**CNPJ/CPF**: {row.get('cnpj_cpf', '')}")
                        st.markdown(f"**Atividade**: {row.get('atividade', '')}")
                        st.markdown(f"**Classe**: {row.get('classe', '')}")

                    with col_b:
                        st.markdown(f"**Regional**: {row.get('regional', '')}")
                        st.markdown(f"**Modalidade**: {row.get('modalidade', '')}")
                        st.markdown(f"**Decisão**: {row.get('decisao', '')}")
                        st.markdown(f"**Data**: {row.get('data_de_publicacao', '')}")

                    # Source link
                    portal_url = (
                        "https://sistemas.meioambiente.mg.gov.br/"
                        f"licenciamento/site/view-externo?id={selected_id}"
                    )
                    st.markdown(f"🔗 [Ver no portal SEMAD]({portal_url})")

                    # PDF documents
                    docs = str(row.get("documentos_pdf", ""))
                    if docs and len(docs) > 5:
                        st.markdown("**Documentos PDF:**")
                        for doc_entry in docs.split(";"):
                            if "|" in doc_entry:
                                name, url = doc_entry.split("|", 1)
                                st.markdown(f"- [{name.strip()}]({url.strip()})")

                    # Parecer text
                    texto = str(row.get("texto_documentos", ""))
                    if texto and len(texto) > 10:
                        with st.expander(
                            f"Texto do Parecer ({len(texto):,} caracteres)"
                        ):
                            st.text(texto[:5000])
                            if len(texto) > 5000:
                                st.caption(
                                    f"... mostrando 5.000 de {len(texto):,} caracteres"
                                )

        # ── Export ──
        st.divider()
        export_query = f"SELECT * FROM {view_name} WHERE {where_sql}"
        if total_count <= 50000:
            csv_df = run_query_df(export_query)
            csv_data = csv_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                f"Exportar CSV ({total_count:,} registros)",
                csv_data,
                file_name=f"{view_name}.csv",
                mime="text/csv",
            )
        else:
            st.caption(
                f"Dataset muito grande ({total_count:,} registros). "
                "Aplique filtros para exportar."
            )

except Exception as e:
    st.error(f"Erro na consulta: {e}")
