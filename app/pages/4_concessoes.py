"""Tab 4: Concessões Minerárias — Lista filtrável de decretos de lavra e instrumentos similares."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import run_query, run_query_df  # noqa: E402
from app.styles.theme import (  # noqa: E402
    empty_state,
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)

inject_theme(st)

st.markdown(
    hero_html(
        "Concessões Minerárias",
        "Decretos de lavra e instrumentos similares vigentes em Minas Gerais",
    ),
    unsafe_allow_html=True,
)

# ── Verificar se dataset existe ──
try:
    test = run_query("SELECT COUNT(*) AS n FROM v_concessoes LIMIT 1")
    if not test or test[0]["n"] == 0:
        raise ValueError("vazio")
except Exception:
    # Tentar v_scm como fallback
    try:
        test = run_query("SELECT COUNT(*) AS n FROM v_scm LIMIT 1")
        if not test or test[0]["n"] == 0:
            raise ValueError("vazio")
        VIEW = "v_scm"
    except Exception:
        st.markdown(
            empty_state(
                "📭",
                "Dataset de concessões não disponível. Execute:\n\n"
                "`licenciaminer collect scm` e depois `licenciaminer join-concessoes`",
            ),
            unsafe_allow_html=True,
        )
        st.stop()
else:
    VIEW = "v_concessoes"

# ── Carregar metadados para filtros ──
@st.cache_data(ttl=300)
def _load_filter_options():
    """Carrega opções únicas para filtros."""
    options = {}

    # Regimes
    try:
        r = run_query(f"SELECT DISTINCT regime FROM {VIEW} WHERE regime IS NOT NULL ORDER BY regime")
        options["regimes"] = [row["regime"] for row in r]
    except Exception:
        options["regimes"] = []

    # Categorias de substância
    try:
        r = run_query(
            f"SELECT DISTINCT categoria FROM {VIEW} "
            "WHERE categoria IS NOT NULL ORDER BY categoria"
        )
        options["categorias"] = [row["categoria"] for row in r]
    except Exception:
        options["categorias"] = []

    # Substâncias principais
    try:
        r = run_query(
            f"SELECT DISTINCT substancia_principal FROM {VIEW} "
            "WHERE substancia_principal IS NOT NULL "
            "ORDER BY substancia_principal LIMIT 200"
        )
        options["substancias"] = [row["substancia_principal"] for row in r]
    except Exception:
        options["substancias"] = []

    # Municípios principais
    try:
        r = run_query(
            f"SELECT DISTINCT municipio_principal FROM {VIEW} "
            "WHERE municipio_principal IS NOT NULL "
            "ORDER BY municipio_principal LIMIT 300"
        )
        options["municipios"] = [row["municipio_principal"] for row in r]
    except Exception:
        options["municipios"] = []

    return options

filter_opts = _load_filter_options()

REGIME_LABELS = {
    "portaria_lavra": "Portaria de Lavra",
    "licenciamento": "Licenciamento",
    "plg": "Lavra Garimpeira (PLG)",
    "registro_extracao": "Registro de Extração",
}

# ── Filtros na sidebar ──
with st.sidebar:
    st.markdown(section_header("Filtros"), unsafe_allow_html=True)

    where_clauses: list[str] = []

    # Busca textual
    search_text = st.text_input(
        "Busca", placeholder="Titular, CNPJ, processo...", key="conc_search"
    )
    if search_text:
        safe = search_text.replace("'", "").replace(";", "").replace("--", "")
        if safe:
            conds = []
            for col in ["titular", "processo", "processo_norm", "substancia_principal",
                        "municipio_principal"]:
                conds.append(
                    f"LOWER(CAST({col} AS VARCHAR)) LIKE '%{safe.lower()}%'"
                )
            # CNPJ column (varies)
            conds.append(
                f"CAST(cpf_cnpj_do_titular AS VARCHAR) LIKE '%{safe}%'"
            )
            where_clauses.append(f"({' OR '.join(conds)})")

    # Regime
    if filter_opts["regimes"]:
        selected_regimes = st.multiselect(
            "Regime",
            filter_opts["regimes"],
            format_func=lambda x: REGIME_LABELS.get(x, x),
        )
        if selected_regimes:
            vals = ", ".join(f"'{r}'" for r in selected_regimes)
            where_clauses.append(f"regime IN ({vals})")

    # Categoria
    if filter_opts["categorias"]:
        selected_cats = st.multiselect("Categoria", filter_opts["categorias"])
        if selected_cats:
            vals = ", ".join(f"'{c}'" for c in selected_cats)
            where_clauses.append(f"categoria IN ({vals})")

    # Substância
    if filter_opts["substancias"]:
        selected_subs = st.multiselect(
            "Substância", filter_opts["substancias"]
        )
        if selected_subs:
            vals = ", ".join(f"'{s}'" for s in selected_subs)
            where_clauses.append(f"substancia_principal IN ({vals})")

    # Município
    if filter_opts["municipios"]:
        selected_muns = st.multiselect(
            "Município", filter_opts["municipios"]
        )
        if selected_muns:
            vals = ", ".join(f"'{m}'" for m in selected_muns)
            where_clauses.append(f"municipio_principal IN ({vals})")

    # Ativo CFEM
    if VIEW == "v_concessoes":
        cfem_filter = st.radio(
            "Status CFEM",
            ["Todos", "Ativo (CFEM recente)", "Inativo (sem CFEM)"],
            index=0,
        )
        if cfem_filter == "Ativo (CFEM recente)":
            where_clauses.append("ativo_cfem = true")
        elif cfem_filter == "Inativo (sem CFEM)":
            where_clauses.append("(ativo_cfem = false OR ativo_cfem IS NULL)")

    # Estratégico
    if VIEW == "v_concessoes":
        only_strategic = st.toggle("Apenas minerais estratégicos", value=False)
        if only_strategic:
            where_clauses.append("estrategico = 'sim'")

    # Filter chips
    active_filters = len(where_clauses)
    if active_filters:
        st.markdown(
            source_attribution(f"{active_filters} filtro(s) ativo(s)"),
            unsafe_allow_html=True,
        )

where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

# ── KPIs ──
@st.cache_data(ttl=120)
def _get_kpis(where: str):
    """Busca KPIs principais."""
    kpis = {}
    try:
        r = run_query(f"SELECT COUNT(*) AS n FROM {VIEW} WHERE {where}")
        kpis["total"] = r[0]["n"] if r else 0
    except Exception:
        kpis["total"] = 0

    if VIEW == "v_concessoes":
        try:
            r = run_query(
                f"SELECT COUNT(*) AS n FROM {VIEW} WHERE {where} AND ativo_cfem = true"
            )
            kpis["ativos"] = r[0]["n"] if r else 0
        except Exception:
            kpis["ativos"] = 0

    try:
        r = run_query(
            f"SELECT COUNT(DISTINCT substancia_principal) AS n FROM {VIEW} WHERE {where}"
        )
        kpis["substancias"] = r[0]["n"] if r else 0
    except Exception:
        kpis["substancias"] = 0

    try:
        r = run_query(
            f"SELECT COUNT(DISTINCT municipio_principal) AS n FROM {VIEW} WHERE {where}"
        )
        kpis["municipios"] = r[0]["n"] if r else 0
    except Exception:
        kpis["municipios"] = 0

    return kpis

kpis = _get_kpis(where_sql)

cols_kpi = st.columns(4)
with cols_kpi[0]:
    st.markdown(
        insight_card("Total", f"{kpis['total']:,}", "concessões"),
        unsafe_allow_html=True,
    )
with cols_kpi[1]:
    if VIEW == "v_concessoes":
        st.markdown(
            insight_card(
                "Ativas CFEM",
                f"{kpis.get('ativos', 0):,}",
                "pagando royalties",
            ),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            insight_card("Regimes", str(len(filter_opts["regimes"])), "tipos"),
            unsafe_allow_html=True,
        )
with cols_kpi[2]:
    st.markdown(
        insight_card("Substâncias", str(kpis["substancias"]), "minerais distintos"),
        unsafe_allow_html=True,
    )
with cols_kpi[3]:
    st.markdown(
        insight_card("Municípios", str(kpis["municipios"]), "em MG"),
        unsafe_allow_html=True,
    )

# ── Tabela ──
st.markdown(
    section_header(f"{kpis['total']:,} registros"),
    unsafe_allow_html=True,
)

# Colunas para exibição
DISPLAY_COLS = [
    "processo_norm",
    "regime",
    "titular",
    "substancia_principal",
    "municipio_principal",
]
if VIEW == "v_concessoes":
    DISPLAY_COLS.extend([
        "categoria",
        "AREA_HA",
        "ativo_cfem",
        "cfem_total",
        "estrategico",
    ])

# Verificar quais colunas existem
try:
    sample = run_query_df(f"SELECT * FROM {VIEW} LIMIT 1")
    available_cols = [c for c in DISPLAY_COLS if c in sample.columns]
except Exception:
    available_cols = DISPLAY_COLS

select_sql = ", ".join(available_cols) if available_cols else "*"

# Pagination
page_size = 100
total_pages = max(1, (kpis["total"] + page_size - 1) // page_size)

col_page, col_info = st.columns([1, 3])
with col_page:
    page = st.number_input(
        "Página",
        min_value=1,
        max_value=total_pages,
        value=1,
        label_visibility="collapsed",
    )
with col_info:
    st.markdown(
        source_attribution(f"Página {page} de {total_pages} · {page_size} por página"),
        unsafe_allow_html=True,
    )

offset = (page - 1) * page_size

query = (
    f"SELECT {select_sql} FROM {VIEW} "
    f"WHERE {where_sql} ORDER BY processo_norm "
    f"LIMIT {page_size} OFFSET {offset}"
)

try:
    df = run_query_df(query)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

if df.empty:
    st.markdown(
        empty_state("🔍", "Nenhum registro encontrado. Ajuste os filtros."),
        unsafe_allow_html=True,
    )
    st.stop()

# Renomear colunas para exibição
COLUMN_LABELS = {
    "processo_norm": "Processo",
    "regime": "Regime",
    "titular": "Titular",
    "substancia_principal": "Substância",
    "municipio_principal": "Município",
    "categoria": "Categoria",
    "AREA_HA": "Área (ha)",
    "ativo_cfem": "CFEM Ativo",
    "cfem_total": "CFEM Total (R$)",
    "estrategico": "Estratégico",
}

display_df = df.rename(columns={k: v for k, v in COLUMN_LABELS.items() if k in df.columns})

# Formatar valores
if "CFEM Total (R$)" in display_df.columns:
    display_df["CFEM Total (R$)"] = display_df["CFEM Total (R$)"].apply(
        lambda x: f"R$ {x:,.2f}" if isinstance(x, (int, float)) and x == x else "—"
    )
if "Área (ha)" in display_df.columns:
    display_df["Área (ha)"] = display_df["Área (ha)"].apply(
        lambda x: f"{x:,.1f}" if isinstance(x, (int, float)) and x == x else "—"
    )
if "Regime" in display_df.columns:
    display_df["Regime"] = display_df["Regime"].map(REGIME_LABELS).fillna(display_df.get("Regime", ""))

event = st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
    height=500,
    on_select="rerun",
    selection_mode="single-row",
)

# ── Detalhe do registro selecionado ──
selected_rows = event.selection.rows if event.selection else []

if selected_rows:
    row_idx = selected_rows[0]
    row = df.iloc[row_idx]
    processo = str(row.get("processo_norm", ""))

    st.markdown(section_header("Detalhes da Concessão"), unsafe_allow_html=True)

    # Buscar registro completo
    try:
        detail = run_query_df(
            f"SELECT * FROM {VIEW} WHERE processo_norm = ?", [processo]
        )
    except Exception:
        detail = df.iloc[[row_idx]]

    if not detail.empty:
        full = detail.iloc[0]

        titular = str(full.get("titular", "—"))
        substancia = str(full.get("substancia_principal", "—"))
        municipio = str(full.get("municipio_principal", "—"))
        regime_val = REGIME_LABELS.get(str(full.get("regime", "")), str(full.get("regime", "—")))
        area = full.get("AREA_HA", None)
        area_str = f"{area:,.1f} ha" if isinstance(area, (int, float)) and area == area else "—"
        cnpj = str(full.get("cpf_cnpj_do_titular", "—"))
        cfem = full.get("cfem_total", None)
        cfem_str = f"R$ {cfem:,.2f}" if isinstance(cfem, (int, float)) and cfem == cfem else "—"
        ativo = full.get("ativo_cfem", None)
        status_str = "Ativo" if ativo else ("Inativo" if ativo is not None and not ativo else "—")
        categoria = str(full.get("categoria", "—"))
        estrategico_val = str(full.get("estrategico", "—"))

        scm_url = "https://sistemas.anm.gov.br/SCM/Extra/site/admin/pesquisarProcessos.aspx"

        st.markdown(f"""
        <div class="geo-detail">
            <div class="detail-header">
                <p class="detail-title">{titular}</p>
            </div>
            <div class="detail-grid">
                <div class="detail-field">
                    <span class="detail-label">Processo</span>
                    <span class="detail-value mono">{processo}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">CNPJ/CPF</span>
                    <span class="detail-value mono">{cnpj}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">Regime</span>
                    <span class="detail-value">{regime_val}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">Substância</span>
                    <span class="detail-value">{substancia}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">Categoria · Estratégico</span>
                    <span class="detail-value">{categoria} · {estrategico_val}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">Município</span>
                    <span class="detail-value">{municipio}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">Área</span>
                    <span class="detail-value">{area_str}</span>
                </div>
                <div class="detail-field">
                    <span class="detail-label">CFEM Total · Status</span>
                    <span class="detail-value">{cfem_str} · {status_str}</span>
                </div>
            </div>
            <div class="detail-actions">
                <a href="{scm_url}" target="_blank">🔗 Consultar no SCM/ANM</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            source_attribution(f"Fonte: SCM/ANM · Processo {processo}"),
            unsafe_allow_html=True,
        )

# ── Export ──
st.markdown("")
if kpis["total"] <= 20000:
    export_query = f"SELECT {select_sql} FROM {VIEW} WHERE {where_sql}"

    @st.cache_data(ttl=60)
    def _get_csv(q: str) -> bytes:
        return run_query_df(q).to_csv(index=False).encode("utf-8")

    st.download_button(
        f"Exportar CSV ({kpis['total']:,} registros)",
        _get_csv(export_query),
        file_name="concessoes_mg.csv",
        mime="text/csv",
    )
else:
    st.caption(
        f"Dataset grande ({kpis['total']:,} registros). "
        "Aplique filtros para exportar."
    )
