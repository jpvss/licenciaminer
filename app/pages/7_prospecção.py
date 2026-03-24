"""Tab 6: Prospecção — Identificação de oportunidades em mineração."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import REGIME_LABELS, run_query, run_query_df  # noqa: E402
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
        "Prospecção de Oportunidades",
        "Identificar concessões com potencial de aquisição ou investimento",
    ),
    unsafe_allow_html=True,
)
st.caption(
    "Concessões ranqueadas por score de oportunidade: inativas (sem CFEM), "
    "minerais estratégicos, áreas grandes e categorias de alto valor. "
    "Use 'Análise por Empresa' para ver portfolios e 'Substâncias por Município' "
    "para concentração regional."
)

# ── Verificar dataset ──
try:
    test = run_query("SELECT COUNT(*) AS n FROM v_concessoes LIMIT 1")
    if not test or test[0]["n"] == 0:
        raise ValueError("vazio")
    VIEW = "v_concessoes"
except Exception:
    # Fallback para v_scm (dados básicos sem enriquecimento)
    try:
        test = run_query("SELECT COUNT(*) AS n FROM v_scm LIMIT 1")
        if not test or test[0]["n"] == 0:
            raise ValueError("vazio")
        VIEW = "v_scm"
    except Exception:
        st.markdown(
            empty_state(
                "📊",
                "Dataset de concessões não disponível. Execute:\n\n"
                "1. `licenciaminer collect scm`\n"
                "2. `licenciaminer join-concessoes`",
            ),
            unsafe_allow_html=True,
        )
        st.stop()


# ── Score de oportunidade ──
SCORE_SQL = f"""
SELECT
    processo_norm,
    regime,
    titular,
    substancia_principal,
    municipio_principal,
    categoria,
    AREA_HA,
    ativo_cfem,
    cfem_total,
    cfem_ultimo_ano,
    estrategico,
    -- Score de oportunidade (0-100)
    (
        CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 30 ELSE 0 END
        + CASE WHEN estrategico = 'sim' THEN 25 ELSE 0 END
        + CASE WHEN AREA_HA > 500 THEN 15
               WHEN AREA_HA > 100 THEN 8
               ELSE 0 END
        + CASE WHEN cfem_total IS NULL OR cfem_total = 0 THEN 15 ELSE 0 END
        + CASE WHEN categoria IN ('Metálicos Preciosos', 'Metálicos Estratégicos') THEN 15
               WHEN categoria IN ('Metálicos Ferrosos', 'Metálicos Não-Ferrosos') THEN 8
               ELSE 0 END
    ) AS score,
    -- Motivo
    CONCAT_WS(', ',
        CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 'Inativo' END,
        CASE WHEN estrategico = 'sim' THEN 'Estratégico' END,
        CASE WHEN AREA_HA > 500 THEN 'Área grande' END,
        CASE WHEN cfem_total IS NULL OR cfem_total = 0 THEN 'Sem CFEM' END,
        CASE WHEN categoria IN ('Metálicos Preciosos', 'Metálicos Estratégicos') THEN 'Alto valor' END
    ) AS motivo
FROM {VIEW}
WHERE regime IS NOT NULL
"""


# ── Filtros ──
with st.sidebar:
    st.markdown(section_header("Filtros de Prospecção"), unsafe_allow_html=True)

    min_score = st.slider("Score mínimo", 0, 100, 30, step=5)

    # Filtro por regime
    regimes_r = run_query(
        f"SELECT DISTINCT regime FROM {VIEW} WHERE regime IS NOT NULL ORDER BY regime"
    )
    regimes = [r["regime"] for r in regimes_r]
    selected_regimes = st.multiselect(
        "Regime",
        regimes,
        format_func=lambda x: REGIME_LABELS.get(x, x),
    )

    # Filtro por categoria
    cats_r = run_query(
        f"SELECT DISTINCT categoria FROM {VIEW} WHERE categoria IS NOT NULL ORDER BY categoria"
    )
    selected_cats = st.multiselect(
        "Categoria", [r["categoria"] for r in cats_r]
    )

    only_strategic = st.toggle("Apenas estratégicos", value=False)

    st.divider()

    view_mode = st.radio(
        "Visualização",
        ["Top Oportunidades", "Análise por Empresa", "Substâncias por Município"],
    )


# ── TOP OPORTUNIDADES ──
if view_mode == "Top Oportunidades":
    st.markdown(section_header("Ranking de Oportunidades"), unsafe_allow_html=True)

    where_extra = []
    if selected_regimes:
        vals = ", ".join(f"'{r}'" for r in selected_regimes)
        where_extra.append(f"regime IN ({vals})")
    if selected_cats:
        vals = ", ".join(f"'{c}'" for c in selected_cats)
        where_extra.append(f"categoria IN ({vals})")
    if only_strategic:
        where_extra.append("estrategico = 'sim'")

    extra_sql = (" AND " + " AND ".join(where_extra)) if where_extra else ""

    query = f"""
    WITH scored AS ({SCORE_SQL})
    SELECT * FROM scored
    WHERE score >= {min_score}{extra_sql}
    ORDER BY score DESC, cfem_total DESC NULLS LAST
    LIMIT 200
    """

    try:
        df = run_query_df(query)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if df.empty:
        st.markdown(
            empty_state("📊", "Nenhuma oportunidade encontrada com esses filtros."),
            unsafe_allow_html=True,
        )
        st.stop()

    # KPIs
    cols_kpi = st.columns(4)
    with cols_kpi[0]:
        st.markdown(
            insight_card("Oportunidades", f"{len(df):,}", f"score >= {min_score}"),
            unsafe_allow_html=True,
        )
    with cols_kpi[1]:
        avg_score = df["score"].mean()
        st.markdown(
            insight_card("Score Médio", f"{avg_score:.0f}", "pontos"),
            unsafe_allow_html=True,
        )
    with cols_kpi[2]:
        strategic_count = (df["estrategico"] == "sim").sum() if "estrategico" in df.columns else 0
        st.markdown(
            insight_card("Estratégicos", f"{strategic_count:,}", "minerais"),
            unsafe_allow_html=True,
        )
    with cols_kpi[3]:
        area_total = df["AREA_HA"].sum() if "AREA_HA" in df.columns else 0
        st.markdown(
            insight_card("Área Total", f"{area_total:,.0f}", "hectares"),
            unsafe_allow_html=True,
        )

    # Score explanation
    with st.expander("Como o score é calculado"):
        st.markdown("""
        | Critério | Pontos |
        |----------|--------|
        | Concessão inativa (sem CFEM recente) | +30 |
        | Mineral estratégico | +25 |
        | Categoria de alto valor (preciosos/estratégicos) | +15 |
        | Área > 500 ha | +15 |
        | Sem arrecadação CFEM registrada | +15 |
        | Área > 100 ha | +8 |
        | Categoria metálicos ferrosos/não-ferrosos | +8 |
        """)

    # Tabela de resultados
    display_cols = {
        "score": "Score",
        "processo_norm": "Processo",
        "regime": "Regime",
        "titular": "Titular",
        "substancia_principal": "Substância",
        "categoria": "Categoria",
        "municipio_principal": "Município",
        "AREA_HA": "Área (ha)",
        "ativo_cfem": "CFEM Ativo",
        "cfem_total": "CFEM Total",
        "motivo": "Motivo",
    }

    display_df = df[[c for c in display_cols if c in df.columns]].rename(
        columns={k: v for k, v in display_cols.items() if k in df.columns}
    )

    # Formatar
    if "Área (ha)" in display_df.columns:
        display_df["Área (ha)"] = display_df["Área (ha)"].apply(
            lambda x: f"{x:,.1f}" if isinstance(x, (int, float)) and x == x else "—"
        )
    if "CFEM Total" in display_df.columns:
        display_df["CFEM Total"] = display_df["CFEM Total"].apply(
            lambda x: f"R$ {x:,.0f}" if isinstance(x, (int, float)) and x == x else "—"
        )
    if "Regime" in display_df.columns:
        display_df["Regime"] = display_df["Regime"].map(REGIME_LABELS).fillna(display_df.get("Regime", ""))

    st.dataframe(display_df, width="stretch", hide_index=True, height=500)

    # Export
    st.download_button(
        f"Exportar Shortlist ({len(df)} oportunidades)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="prospecção_oportunidades.csv",
        mime="text/csv",
    )

    st.markdown(
        source_attribution("Fontes: SCM/ANM + CFEM + SIGMINE · Classificação própria"),
        unsafe_allow_html=True,
    )


# ── ANÁLISE POR EMPRESA ──
elif view_mode == "Análise por Empresa":
    st.markdown(section_header("Portfolio por Empresa"), unsafe_allow_html=True)

    # Top empresas por número de concessões
    empresas_query = f"""
    SELECT
        titular,
        COUNT(*) AS total_concessoes,
        COUNT(DISTINCT substancia_principal) AS substancias_distintas,
        SUM(CASE WHEN ativo_cfem = true THEN 1 ELSE 0 END) AS ativas_cfem,
        SUM(CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 1 ELSE 0 END) AS inativas,
        COALESCE(SUM(cfem_total), 0) AS cfem_total,
        COALESCE(SUM(AREA_HA), 0) AS area_total
    FROM {VIEW}
    WHERE titular IS NOT NULL
    GROUP BY titular
    HAVING total_concessoes > 1
    ORDER BY total_concessoes DESC
    LIMIT 100
    """

    try:
        empresas = run_query_df(empresas_query)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if empresas.empty:
        st.markdown(
            empty_state("🏢", "Sem dados de empresas."),
            unsafe_allow_html=True,
        )
        st.stop()

    # KPIs
    cols_kpi = st.columns(3)
    with cols_kpi[0]:
        st.markdown(
            insight_card("Empresas", f"{len(empresas):,}", "com 2+ concessões"),
            unsafe_allow_html=True,
        )
    with cols_kpi[1]:
        top_empresa = empresas.iloc[0]["titular"] if len(empresas) > 0 else "—"
        top_count = empresas.iloc[0]["total_concessoes"] if len(empresas) > 0 else 0
        st.markdown(
            insight_card("Maior Portfolio", str(int(top_count)), str(top_empresa)[:30]),
            unsafe_allow_html=True,
        )
    with cols_kpi[2]:
        total_inativas = int(empresas["inativas"].sum())
        st.markdown(
            insight_card("Inativas", f"{total_inativas:,}", "concessões sem CFEM"),
            unsafe_allow_html=True,
        )

    # Tabela de empresas
    display_empresas = empresas.rename(columns={
        "titular": "Titular",
        "total_concessoes": "Total",
        "substancias_distintas": "Substâncias",
        "ativas_cfem": "Ativas",
        "inativas": "Inativas",
        "cfem_total": "CFEM Total (R$)",
        "area_total": "Área Total (ha)",
    })

    if "CFEM Total (R$)" in display_empresas.columns:
        display_empresas["CFEM Total (R$)"] = display_empresas["CFEM Total (R$)"].apply(
            lambda x: f"R$ {x:,.0f}" if isinstance(x, (int, float)) and x == x else "—"
        )
    if "Área Total (ha)" in display_empresas.columns:
        display_empresas["Área Total (ha)"] = display_empresas["Área Total (ha)"].apply(
            lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) and x == x else "—"
        )

    event = st.dataframe(
        display_empresas,
        width="stretch",
        hide_index=True,
        height=400,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Detalhe da empresa selecionada
    selected_rows = event.selection.rows if event.selection else []
    if selected_rows:
        row_idx = selected_rows[0]
        empresa_nome = empresas.iloc[row_idx]["titular"]

        st.markdown(
            section_header(f"Concessões de {str(empresa_nome)[:50]}"),
            unsafe_allow_html=True,
        )

        detalhe_query = f"""
        SELECT processo_norm, regime, substancia_principal, municipio_principal,
               categoria, AREA_HA, ativo_cfem, cfem_total
        FROM {VIEW}
        WHERE titular = ?
        ORDER BY cfem_total DESC NULLS LAST
        """

        try:
            empresa_df = run_query_df(detalhe_query, [empresa_nome])
            st.dataframe(empresa_df, width="stretch", hide_index=True, height=300)
        except Exception as e:
            st.error(f"Erro: {e}")


# ── SUBSTÂNCIAS POR MUNICÍPIO ──
elif view_mode == "Substâncias por Município":
    st.markdown(section_header("Concentração por Município"), unsafe_allow_html=True)

    mun_query = f"""
    SELECT
        municipio_principal AS municipio,
        substancia_principal AS substancia,
        COUNT(*) AS concessoes,
        SUM(CASE WHEN ativo_cfem = true THEN 1 ELSE 0 END) AS ativas,
        COALESCE(SUM(AREA_HA), 0) AS area_total,
        COALESCE(SUM(cfem_total), 0) AS cfem_total
    FROM {VIEW}
    WHERE municipio_principal IS NOT NULL AND substancia_principal IS NOT NULL
    GROUP BY municipio_principal, substancia_principal
    ORDER BY concessoes DESC
    LIMIT 500
    """

    try:
        mun_df = run_query_df(mun_query)
    except Exception as e:
        st.error(f"Erro: {e}")
        st.stop()

    if mun_df.empty:
        st.markdown(
            empty_state("🗺️", "Sem dados por município."),
            unsafe_allow_html=True,
        )
        st.stop()

    # Top municípios
    top_mun = mun_df.groupby("municipio").agg(
        total=("concessoes", "sum"),
        substancias=("substancia", "nunique"),
        cfem=("cfem_total", "sum"),
    ).sort_values("total", ascending=False).head(30).reset_index()

    cols_kpi = st.columns(3)
    with cols_kpi[0]:
        st.markdown(
            insight_card(
                "Top Município",
                str(top_mun.iloc[0]["municipio"])[:20] if len(top_mun) > 0 else "—",
                f"{int(top_mun.iloc[0]['total'])} concessões" if len(top_mun) > 0 else "",
            ),
            unsafe_allow_html=True,
        )
    with cols_kpi[1]:
        st.markdown(
            insight_card("Municípios", f"{mun_df['municipio'].nunique():,}", "com concessões"),
            unsafe_allow_html=True,
        )
    with cols_kpi[2]:
        st.markdown(
            insight_card("Pares", f"{len(mun_df):,}", "município × substância"),
            unsafe_allow_html=True,
        )

    # Tabela de municípios
    display_mun = top_mun.rename(columns={
        "municipio": "Município",
        "total": "Concessões",
        "substancias": "Substâncias",
        "cfem": "CFEM Total (R$)",
    })
    if "CFEM Total (R$)" in display_mun.columns:
        display_mun["CFEM Total (R$)"] = display_mun["CFEM Total (R$)"].apply(
            lambda x: f"R$ {x:,.0f}" if isinstance(x, (int, float)) and x == x else "—"
        )

    st.dataframe(display_mun, width="stretch", hide_index=True, height=400)

    # Detalhe por município selecionado
    mun_select = st.selectbox(
        "Selecionar município para detalhes",
        top_mun["municipio"].tolist(),
    )

    if mun_select:
        mun_detail = mun_df[mun_df["municipio"] == mun_select].sort_values(
            "concessoes", ascending=False
        )
        st.markdown(
            section_header(f"Substâncias em {mun_select}"),
            unsafe_allow_html=True,
        )
        st.dataframe(
            mun_detail.rename(columns={
                "substancia": "Substância",
                "concessoes": "Concessões",
                "ativas": "Ativas CFEM",
                "area_total": "Área Total (ha)",
                "cfem_total": "CFEM Total (R$)",
            }),
            width="stretch",
            hide_index=True,
        )

    st.markdown(
        source_attribution("Fontes: SCM/ANM + CFEM · Agrupamento por município e substância"),
        unsafe_allow_html=True,
    )
