"""Tab 2: Explorar Dados — Data laboratory with filters, detail view, export."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import (  # noqa: E402
    fmt_br,
    get_dataset_options,
    run_query,
    run_query_df,
)
from app.styles.theme import (  # noqa: E402
    decision_badge,
    empty_state,
    hero_html,
    inject_theme,
    section_header,
    source_attribution,
)

inject_theme(st)

st.markdown(
    hero_html("Explorar Dados", "Navegue pelos datasets, filtre e verifique na fonte original"),
    unsafe_allow_html=True,
)

# ── Dataset Selector ──
st.caption(
    "Selecione um dataset abaixo, use os filtros na barra lateral e clique em uma linha "
    "para ver os detalhes completos. Dados exportáveis em CSV."
)

datasets = get_dataset_options()
if not datasets:
    st.markdown(
        empty_state("📭", "Nenhum dataset disponível. Execute os coletores primeiro."),
        unsafe_allow_html=True,
    )
    st.stop()

selected_label = st.selectbox(
    "Dataset", list(datasets.keys()), label_visibility="collapsed",
    help="Mg Semad = decisões de licenciamento MG · Anm = processos minerários · "
         "Ibama Infracoes = infrações ambientais · Cfem = royalties pagos",
)
view_name = datasets[selected_label]

# ── Get columns ──
try:
    sample = run_query_df(f"SELECT * FROM {view_name} LIMIT 1")
    all_columns = list(sample.columns)
except Exception as e:
    st.error(f"Erro ao carregar dataset: {e}")
    st.stop()

# Heavy columns to exclude from display
exclude_cols = {"texto_documentos", "documentos_pdf", "documents_str"}

# ── Filters in sidebar ──
with st.sidebar:
    st.markdown(section_header("Filtros"), unsafe_allow_html=True)

    where_clauses: list[str] = []
    query_params: list = []

    search_text = st.text_input(
        "Busca", placeholder="CNPJ, empresa...", key="search"
    )
    if search_text:
        # Escape LIKE wildcards and SQL special chars for safe interpolation
        safe = (
            search_text
            .replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
            .replace("'", "''")
        ).strip()
        if safe:
            conds = [
                f"LOWER(CAST({c} AS VARCHAR)) LIKE '%{safe.lower()}%' ESCAPE '\\'"
                for c in all_columns
                if c not in exclude_cols and sample[c].dtype == "object"
            ]
            if conds:
                where_clauses.append(f"({' OR '.join(conds)})")

    if view_name == "v_mg_semad":
        mining_only = st.toggle("Apenas mineração", value=True)
        if mining_only:
            where_clauses.append("atividade LIKE 'A-0%'")

        decisao = st.selectbox(
            "Decisão",
            ["Todos", "deferido", "indeferido", "arquivamento"],
        )
        if decisao != "Todos":
            where_clauses.append("decisao = ?")
            query_params.append(decisao)

        classe = st.selectbox(
            "Classe", ["Todas", "1", "2", "3", "4", "5", "6"]
        )
        if classe != "Todas":
            where_clauses.append("classe = ?")
            query_params.append(int(classe))

        from datetime import datetime
        _current_year = datetime.now().year
        ano_range = st.slider("Ano", 2016, _current_year, (2018, _current_year))
        where_clauses.append("CAST(ano AS INTEGER) >= ?")
        query_params.append(ano_range[0])
        where_clauses.append("CAST(ano AS INTEGER) <= ?")
        query_params.append(ano_range[1])

    elif view_name == "v_ibama_infracoes":
        uf = st.selectbox("UF", ["MG", "Todos"])
        if uf != "Todos":
            where_clauses.append("UF = ?")
            query_params.append(uf)

    # Active filter chips
    active_filters = [c for c in where_clauses if "CAST(ano" not in c]
    if active_filters:
        st.markdown(
            source_attribution(f"{len(active_filters)} filtro(s) ativo(s)"),
            unsafe_allow_html=True,
        )

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# ── Count ──
try:
    count_r = run_query(
        f"SELECT COUNT(*) AS n FROM {view_name} WHERE {where_sql}",
        query_params or None,
    )
    total_count = count_r[0]["n"] if count_r else 0
except Exception:
    total_count = 0

# ── Results header ──
st.markdown(
    section_header(f"{fmt_br(total_count)} registros encontrados"),
    unsafe_allow_html=True,
)

# Pagination
page_size = 50
total_pages = max(1, (total_count + page_size - 1) // page_size)

if total_pages > 1:
    col_page, col_info = st.columns([1, 3])
    with col_page:
        page = st.number_input(
            "Página", min_value=1, max_value=total_pages, value=1,
            label_visibility="collapsed",
        )
    with col_info:
        st.markdown(
            source_attribution(f"Página {page} de {total_pages} · {page_size} por página"),
            unsafe_allow_html=True,
        )
else:
    page = 1

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
    df = run_query_df(query, query_params or None)
except Exception as e:
    st.error(f"Erro: {e}")
    st.stop()

if df.empty:
    st.markdown(
        empty_state("🔍", "Nenhum registro encontrado. Tente ajustar os filtros."),
        unsafe_allow_html=True,
    )
    st.stop()

# ── Column config for better formatting ──
_col_config: dict = {}
if view_name == "v_mg_semad":
    _col_config = {
        "detail_id": None,
        "texto_documentos": None,
        "documentos_pdf": None,
        "ano": st.column_config.NumberColumn("Ano", format="%d"),
        "classe": st.column_config.NumberColumn("Classe", format="%d"),
        "_source": None,
        "_collected_at": None,
    }
elif view_name == "v_ibama_infracoes":
    # Hide the 60+ internal/empty columns, show only the useful ones
    _useful_cols = {
        "NUM_AUTO_INFRACAO", "TIPO_AUTO", "VAL_AUTO_INFRACAO",
        "DES_AUTO_INFRACAO", "DAT_HORA_AUTO_INFRACAO", "MUNICIPIO", "UF",
        "CPF_CNPJ_INFRATOR", "NOME_INFRATOR", "TIPO_INFRACAO",
        "DES_STATUS_FORMULARIO", "SIT_CANCELADO",
    }
    _col_config = {
        c: None for c in df.columns if c not in _useful_cols
    }
    _col_config["NUM_AUTO_INFRACAO"] = st.column_config.TextColumn("N° Auto")
    _col_config["DAT_HORA_AUTO_INFRACAO"] = st.column_config.TextColumn("Data")
    _col_config["NOME_INFRATOR"] = st.column_config.TextColumn("Infrator")
    _col_config["VAL_AUTO_INFRACAO"] = st.column_config.TextColumn("Valor (R$)")
    _col_config["TIPO_INFRACAO"] = st.column_config.TextColumn("Tipo")
    _col_config["DES_AUTO_INFRACAO"] = st.column_config.TextColumn("Descrição")
elif view_name == "v_cfem":
    _col_config = {
        "_source": None, "_collected_at": None, "_source_url": None,
        "Ano": st.column_config.NumberColumn("Ano", format="%d"),
        "CPF_CNPJ": st.column_config.TextColumn("CNPJ"),
        "Substância": st.column_config.TextColumn("Substância"),
        "ValorRecolhido": st.column_config.TextColumn("Valor (R$)"),
    }
elif view_name in ("v_anm", "v_spatial"):
    _col_config = {
        "_source": None, "_collected_at": None,
        "AREA_HA": st.column_config.NumberColumn("Área (ha)", format="%.1f"),
        "ANO": st.column_config.NumberColumn("Ano", format="%d"),
    }
elif view_name == "v_cnpj":
    _col_config = {
        "_source": None, "_collected_at": None, "_source_url": None,
    }
else:
    # Generic: hide internal columns
    _col_config = {
        c: None for c in df.columns
        if c.startswith("_") and c not in {"_tipo_producao"}
    }

# ── Table with row selection ──
if view_name == "v_mg_semad" and "detail_id" in df.columns:
    event = st.dataframe(
        df,
        column_config=_col_config,
        use_container_width=True,
        hide_index=True,
        height=420,
        on_select="rerun",
        selection_mode="single-row",
    )

    selected_rows = event.selection.rows if event.selection else []

    if selected_rows:
        row_idx = selected_rows[0]
        row = df.iloc[row_idx]
        selected_id = str(row.get("detail_id", ""))

        st.markdown(
            section_header("Detalhes do Registro"),
            unsafe_allow_html=True,
        )

        # Full record (exclude heavy columns, fetch text separately)
        detail_cols = [c for c in all_columns if c not in {"texto_documentos"}]
        detail_select = ", ".join(detail_cols)
        detail = run_query_df(
            f"SELECT {detail_select} FROM {view_name} WHERE detail_id = ?",
            [selected_id],
        )

        if not detail.empty:
            full_row = detail.iloc[0]

            decisao_val = str(full_row.get("decisao", "—"))
            badge = decision_badge(decisao_val)
            empreendimento = full_row.get("empreendimento", "—")
            cnpj = full_row.get("cnpj_cpf", "—")
            atividade = full_row.get("atividade", "—")
            classe_val = full_row.get("classe", "—")
            modalidade = full_row.get("modalidade", "—")
            regional_val = str(full_row.get("regional", "—")).replace(
                "Unidade Regional de Regularização Ambiental ", ""
            )
            municipio = full_row.get("municipio", "—")
            ano_val = full_row.get("ano", "—")

            portal_url = (
                "https://sistemas.meioambiente.mg.gov.br/"
                f"licenciamento/site/view-externo?id={selected_id}"
            )

            # Build detail card HTML
            docs_html = ""
            docs = str(full_row.get("documentos_pdf", ""))
            if docs and len(docs) > 5:
                doc_links = []
                for entry in docs.split(";"):
                    if "|" in entry:
                        name, url = entry.split("|", 1)
                        url = url.strip()
                        if url.startswith(("http://", "https://")):
                            doc_links.append(
                                f'<a href="{url}" target="_blank">'
                                f'📄 {name.strip()}</a>'
                            )
                if doc_links:
                    docs_html = (
                        '<div class="detail-actions">'
                        + " ".join(doc_links)
                        + "</div>"
                    )

            st.markdown(f"""
            <div class="geo-detail">
                <div class="detail-header">
                    <p class="detail-title">{empreendimento}</p>
                    {badge}
                </div>
                <div class="detail-grid">
                    <div class="detail-field">
                        <span class="detail-label">CNPJ</span>
                        <span class="detail-value mono">{cnpj}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">Atividade</span>
                        <span class="detail-value">{atividade}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">Classe · Modalidade</span>
                        <span class="detail-value">{classe_val} · {modalidade}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">Regional</span>
                        <span class="detail-value">{regional_val}</span>
                    </div>
                    <div class="detail-field">
                        <span class="detail-label">Município · Ano</span>
                        <span class="detail-value">{municipio} · {ano_val}</span>
                    </div>
                </div>
                <div class="detail-actions">
                    <a href="{portal_url}" target="_blank">🔗 Portal SEMAD</a>
                </div>
                {docs_html}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(
                source_attribution(f"SEMAD MG · ID {selected_id}"),
                unsafe_allow_html=True,
            )

            # Parecer text — fetch lazily only when requested
            if "texto_documentos" in all_columns:
                with st.expander("Ver Texto do Parecer"):
                    texto_rows = run_query(
                        f"SELECT texto_documentos FROM {view_name} WHERE detail_id = ?",
                        [selected_id],
                    )
                    texto = str(texto_rows[0].get("texto_documentos", "")) if texto_rows else ""
                    if texto and len(texto) > 10:
                        st.text(texto[:8000])
                        if len(texto) > 8000:
                            st.caption(
                                f"Mostrando 8.000 de {len(texto):,} caracteres"
                            )
                    else:
                        st.caption("Texto não disponível para este registro.")
    else:
        st.markdown(
            empty_state(
                "👆",
                "Selecione um registro na tabela acima para ver os detalhes completos",
            ),
            unsafe_allow_html=True,
        )

else:
    st.dataframe(
        df, column_config=_col_config,
        use_container_width=True, hide_index=True, height=420,
    )

# ── Export ──
st.markdown("")
if total_count <= 20000:
    # Exclude heavy text columns from export to avoid OOM
    export_cols = [c for c in all_columns if c not in exclude_cols]
    export_select = ", ".join(export_cols)
    export_query = f"SELECT {export_select} FROM {view_name} WHERE {where_sql}"

    @st.cache_data(ttl=60)
    def get_csv(q: str, params: list | None = None) -> bytes:
        return run_query_df(q, params).to_csv(index=False).encode("utf-8")

    st.download_button(
        f"Exportar CSV ({fmt_br(total_count)} registros)",
        get_csv(export_query, query_params or None),
        file_name=f"{view_name}.csv",
        mime="text/csv",
    )
else:
    st.caption(
        f"Dataset muito grande para exportar ({fmt_br(total_count)} registros). "
        "Aplique filtros para reduzir a menos de 20.000."
    )
