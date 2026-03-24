"""Tab 4: Análise de Decisões — Dashboard analítico de licenciamento."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from app.components.data_loader import run_query, run_query_df  # noqa: E402
from app.styles.theme import (  # noqa: E402
    decision_badge,
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_APROVACAO_ATIVIDADE_CLASSE,
    QUERY_ARQUIVAMENTO_ANALYSIS,
    QUERY_CLASSE_MODALIDADE,
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_DECISAO_POR_MODALIDADE,
    QUERY_HISTORICO_CNPJ,
    QUERY_INFRACOES_FAIXA_DECISAO,
    QUERY_REINCIDENCIA,
    QUERY_RIGOR_REGIONAL,
    QUERY_TENDENCIA_INDEFERIMENTO,
)

inject_theme(st)

# ── Plotly layout defaults ──
PLOTLY_LAYOUT = {
    "plot_bgcolor": "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#8B9BB4", "family": "Instrument Sans"},
    "margin": {"t": 10, "b": 35, "l": 45, "r": 20},
    "hoverlabel": {
        "bgcolor": "#1A1E28",
        "bordercolor": "#2E3442",
        "font": {"family": "Instrument Sans", "size": 12},
    },
}
COLORS = {
    "deferido": "#5BA77D",
    "indeferido": "#C45B52",
    "arquivamento": "#8B9BB4",
    "outro": "#5E6B80",
    "amber": "#D4A847",
    "copper": "#C17F59",
    "quartz": "#E8E4DC",
    "slate": "#8B9BB4",
}

# ── Hero ──
st.markdown(
    hero_html(
        "Análise de Decisões",
        "Padrões, fatores de risco e detalhamento de casos — licenciamento minerário MG",
    ),
    unsafe_allow_html=True,
)

# ── Tabs ──
tab_overview, tab_risk, tab_detail = st.tabs([
    "Visão Geral das Decisões",
    "Fatores de Risco",
    "Caso Detalhado",
])


# ════════════════════════════════════════════════════════════════
# TAB 1: VISÃO GERAL DAS DECISÕES
# ════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown(section_header("Painel de Indicadores"), unsafe_allow_html=True)

    try:
        summary = run_query("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
                SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END) AS indeferidos,
                SUM(CASE WHEN decisao = 'arquivamento' THEN 1 ELSE 0 END) AS arquivamentos,
                ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                    / COUNT(*), 1) AS taxa_aprovacao
            FROM v_mg_semad WHERE atividade LIKE 'A-0%'
        """)[0]

        last_year_rej = run_query("""
            SELECT COUNT(*) AS n FROM v_mg_semad
            WHERE atividade LIKE 'A-0%' AND decisao = 'indeferido'
              AND ano = (SELECT MAX(ano) FROM v_mg_semad WHERE atividade LIKE 'A-0%')
        """)[0]["n"]

        worst_mod = run_query("""
            SELECT modalidade,
                ROUND(100.0 * SUM(CASE WHEN decisao = 'indeferido' THEN 1 ELSE 0 END)
                    / COUNT(*), 1) AS taxa_ind
            FROM v_mg_semad
            WHERE atividade LIKE 'A-0%' AND modalidade != '' AND modalidade IS NOT NULL
            GROUP BY modalidade HAVING COUNT(*) >= 20
            ORDER BY taxa_ind DESC LIMIT 1
        """)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Taxa de Deferimento", f"{summary['taxa_aprovacao']}%")
            st.markdown(
                source_attribution(f"N = {summary['total']:,} decisões mineração"),
                unsafe_allow_html=True,
            )
        with c2:
            st.metric("Indeferimentos (último ano)", f"{last_year_rej:,}")
            st.markdown(
                source_attribution("SEMAD MG"),
                unsafe_allow_html=True,
            )
        with c3:
            arq_pct = round(
                100 * summary["arquivamentos"] / summary["total"], 1
            )
            st.metric("Arquivamentos", f"{arq_pct}%")
            st.markdown(
                source_attribution(f"{summary['arquivamentos']:,} processos"),
                unsafe_allow_html=True,
            )
        with c4:
            if worst_mod:
                wm = worst_mod[0]
                st.metric("Maior Rejeição", f"{wm['taxa_ind']}%")
                st.markdown(
                    source_attribution(f"Modalidade: {wm['modalidade']}"),
                    unsafe_allow_html=True,
                )
    except Exception as e:
        st.error(f"Erro ao carregar indicadores: {e}")

    st.markdown("")

    # ── Chart 1: Decisão por Modalidade ──
    st.markdown(
        section_header("Decisões por Modalidade de Licença"),
        unsafe_allow_html=True,
    )
    try:
        mod_df = run_query_df(QUERY_DECISAO_POR_MODALIDADE)
        if not mod_df.empty:
            # Group by modalidade, pivot decisions
            pivot = mod_df.pivot_table(
                index="modalidade", columns="decisao", values="n",
                aggfunc="sum", fill_value=0,
            )
            # Sort by total descending, take top 12
            pivot["_total"] = pivot.sum(axis=1)
            pivot = pivot.sort_values("_total", ascending=False).head(12)
            pivot = pivot.drop(columns=["_total"])

            fig = go.Figure()
            for decisao, color in [
                ("deferido", COLORS["deferido"]),
                ("indeferido", COLORS["indeferido"]),
                ("arquivamento", COLORS["arquivamento"]),
                ("outro", COLORS["outro"]),
            ]:
                if decisao in pivot.columns:
                    fig.add_trace(go.Bar(
                        name=decisao.capitalize(),
                        x=pivot.index,
                        y=pivot[decisao],
                        marker_color=color,
                        hovertemplate="%{x}<br>%{fullData.name}: %{y:,}<extra></extra>",
                    ))

            fig.update_layout(
                **PLOTLY_LAYOUT,
                barmode="stack",
                height=380,
                legend={
                    "orientation": "h", "y": -0.15,
                    "font": {"size": 11},
                },
                xaxis={"tickangle": -35, "tickfont": {"size": 10}},
                yaxis={"title": {"text": "Decisões", "font": {"size": 11}},
                       "gridcolor": "rgba(36, 41, 53, 0.8)"},
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution("SEMAD MG · Top 12 modalidades por volume"),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro no gráfico de modalidades: {e}")

    st.markdown("")

    # ── Chart 2 + Chart 3: two columns ──
    col_heat, col_trend = st.columns([3, 2])

    with col_heat:
        st.markdown(
            section_header("Taxa de Aprovação: Atividade × Classe"),
            unsafe_allow_html=True,
        )
        try:
            heat_df = run_query_df(QUERY_APROVACAO_ATIVIDADE_CLASSE)
            if not heat_df.empty:
                # Build heatmap pivot
                heat_pivot = heat_df.pivot_table(
                    index="atividade_code", columns="classe",
                    values="taxa_aprovacao", aggfunc="first",
                )
                # Counts for hover
                count_pivot = heat_df.pivot_table(
                    index="atividade_code", columns="classe",
                    values="total", aggfunc="first", fill_value=0,
                )

                fig = go.Figure(data=go.Heatmap(
                    z=heat_pivot.values,
                    x=[f"Classe {int(c)}" for c in heat_pivot.columns],
                    y=heat_pivot.index,
                    colorscale=[
                        [0.0, "#C45B52"],   # oxide (low approval)
                        [0.5, "#D4A847"],   # amber (mid)
                        [1.0, "#5BA77D"],   # malachite (high approval)
                    ],
                    zmin=0, zmax=100,
                    text=heat_pivot.values,
                    texttemplate="%{text:.0f}%",
                    textfont={"size": 10},
                    customdata=count_pivot.values,
                    hovertemplate=(
                        "%{y} · %{x}<br>"
                        "Aprovação: %{z:.1f}%<br>"
                        "N = %{customdata:,}"
                        "<extra></extra>"
                    ),
                    colorbar={
                        "title": {"text": "Aprovação %", "font": {"size": 10}},
                        "ticksuffix": "%",
                        "len": 0.6,
                    },
                ))
                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    height=max(300, len(heat_pivot) * 35 + 60),
                    yaxis={"tickfont": {"size": 10}, "autorange": "reversed"},
                    xaxis={"side": "top", "tickfont": {"size": 10}},
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown(
                    source_attribution("Apenas combinações com N ≥ 5"),
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Erro no heatmap: {e}")

    with col_trend:
        st.markdown(
            section_header("Tendência de Indeferimentos"),
            unsafe_allow_html=True,
        )
        try:
            trend_df = run_query_df(QUERY_TENDENCIA_INDEFERIMENTO)
            if not trend_df.empty:
                fig = go.Figure()

                # Bar: total decisions (background)
                fig.add_trace(go.Bar(
                    x=trend_df["ano"],
                    y=trend_df["total"],
                    marker_color="rgba(139, 155, 180, 0.12)",
                    showlegend=False,
                    hoverinfo="skip",
                    yaxis="y2",
                ))

                # Line: indeferimento rate
                fig.add_trace(go.Scatter(
                    x=trend_df["ano"],
                    y=trend_df["taxa_indeferimento"],
                    mode="lines+markers+text",
                    text=[f"{v:.0f}%" for v in trend_df["taxa_indeferimento"]],
                    textposition="top center",
                    textfont={"size": 10, "color": "#8B9BB4"},
                    line={"color": COLORS["indeferido"], "width": 2.5},
                    marker={"size": 6, "color": COLORS["indeferido"],
                            "line": {"width": 2, "color": "#0C0E12"}},
                    name="Indeferimento",
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
                ))

                # Line: arquivamento rate
                fig.add_trace(go.Scatter(
                    x=trend_df["ano"],
                    y=trend_df["taxa_arquivamento"],
                    mode="lines+markers",
                    line={"color": COLORS["arquivamento"], "width": 1.5,
                          "dash": "dot"},
                    marker={"size": 5, "color": COLORS["arquivamento"]},
                    name="Arquivamento",
                    hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
                ))

                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    height=320,
                    yaxis={"range": [0, 50], "title": {"text": "%", "font": {"size": 11}},
                           "gridcolor": "rgba(36, 41, 53, 0.8)"},
                    yaxis2={"overlaying": "y", "side": "right", "showgrid": False,
                            "showticklabels": False,
                            "range": [0, max(trend_df["total"]) * 4]},
                    xaxis={"dtick": 1, "gridcolor": "rgba(36, 41, 53, 0.5)"},
                    legend={"orientation": "h", "y": -0.2, "font": {"size": 10}},
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown(
                    source_attribution("Anos com N ≥ 10 decisões"),
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.error(f"Erro na tendência: {e}")

    st.markdown("")

    # ── Chart 4: Rigor Regional ──
    st.markdown(
        section_header("Rigor por Regional — Taxa de Indeferimento"),
        unsafe_allow_html=True,
    )
    try:
        reg_df = run_query_df(QUERY_RIGOR_REGIONAL)
        if not reg_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=reg_df["taxa_indeferimento"],
                y=reg_df["regional"],
                orientation="h",
                marker_color=[
                    COLORS["indeferido"] if t > 20
                    else COLORS["amber"] if t > 10
                    else COLORS["slate"]
                    for t in reg_df["taxa_indeferimento"]
                ],
                text=[f"{t:.0f}% (N={n:,})" for t, n
                      in zip(reg_df["taxa_indeferimento"], reg_df["total"],
                             strict=False)],
                textposition="outside",
                textfont={"size": 10, "color": "#8B9BB4"},
                hovertemplate=(
                    "%{y}<br>Indeferimento: %{x:.1f}%<br>"
                    "Total: %{customdata:,}<extra></extra>"
                ),
                customdata=reg_df["total"],
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=max(250, len(reg_df) * 30 + 60),
                xaxis={"title": {"text": "Taxa de Indeferimento (%)",
                                 "font": {"size": 11}},
                       "gridcolor": "rgba(36, 41, 53, 0.8)"},
                yaxis={"autorange": "reversed", "tickfont": {"size": 10}},
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution("Regionais com N ≥ 20 decisões"),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro no ranking regional: {e}")


# ════════════════════════════════════════════════════════════════
# TAB 2: FATORES DE RISCO
# ════════════════════════════════════════════════════════════════
with tab_risk:
    st.markdown(
        section_header("Correlação: Infrações IBAMA × Decisão"),
        unsafe_allow_html=True,
    )

    try:
        inf_df = run_query_df(QUERY_INFRACOES_FAIXA_DECISAO)
        if not inf_df.empty:
            col_chart, col_insight = st.columns([3, 2])

            with col_chart:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=inf_df["faixa_infracoes"],
                    y=inf_df["taxa_aprovacao"],
                    marker_color=[
                        COLORS["deferido"] if t >= 70
                        else COLORS["amber"] if t >= 50
                        else COLORS["indeferido"]
                        for t in inf_df["taxa_aprovacao"]
                    ],
                    text=[f"{t:.0f}%" for t in inf_df["taxa_aprovacao"]],
                    textposition="outside",
                    textfont={"size": 11, "color": "#8B9BB4"},
                    hovertemplate=(
                        "%{x}<br>Aprovação: %{y:.1f}%<br>"
                        "N = %{customdata:,}<extra></extra>"
                    ),
                    customdata=inf_df["total"],
                ))
                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    height=320,
                    yaxis={"range": [0, 100],
                           "title": {"text": "Taxa Aprovação (%)", "font": {"size": 11}},
                           "gridcolor": "rgba(36, 41, 53, 0.8)"},
                    xaxis={"tickfont": {"size": 10}},
                )
                st.plotly_chart(fig, use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown(
                    source_attribution(
                        "SEMAD MG × IBAMA Infrações · Apenas registros com CNPJ válido"
                    ),
                    unsafe_allow_html=True,
                )

            with col_insight:
                no_inf = inf_df[inf_df["faixa_infracoes"] == "Sem infrações"]
                hi_inf = inf_df[inf_df["faixa_infracoes"] == "6+ infrações"]
                if not no_inf.empty and not hi_inf.empty:
                    diff = float(hi_inf["taxa_aprovacao"].iloc[0]) - float(
                        no_inf["taxa_aprovacao"].iloc[0]
                    )
                    tone = "positive" if diff > 0 else "negative"
                    st.markdown(
                        insight_card(
                            "Infrações × Aprovação",
                            f"{'+'if diff > 0 else ''}{diff:.0f}pp",
                            "Empresas com 6+ infrações vs sem infrações · "
                            "Indica que porte da empresa pode ser fator confundidor",
                            tone,
                        ),
                        unsafe_allow_html=True,
                    )

                st.markdown(
                    insight_card(
                        "Como interpretar",
                        "Correlação, não causalidade",
                        "Empresas maiores têm mais infrações E mais recursos "
                        "para processos de licenciamento complexos",
                        "neutral",
                    ),
                    unsafe_allow_html=True,
                )
    except Exception as e:
        st.error(f"Erro na análise de infrações: {e}")

    st.markdown("")

    # ── CFEM analysis ──
    st.markdown(
        section_header("Correlação: CFEM (Royalties) × Decisão"),
        unsafe_allow_html=True,
    )
    try:
        from licenciaminer.database.queries import QUERY_CFEM_VS_APROVACAO
        cfem_data = run_query(QUERY_CFEM_VS_APROVACAO)
        if cfem_data:
            cols = st.columns(len(cfem_data))
            for i, row in enumerate(cfem_data):
                with cols[i]:
                    pct = row["taxa_aprovacao"]
                    tone = "positive" if pct >= 65 else "negative"
                    st.markdown(
                        insight_card(
                            row["perfil_empresa"],
                            f"{pct}% aprovação",
                            f"{row['total_decisoes']:,} decisões · "
                            f"{row['deferidos']:,} deferidos",
                            tone,
                        ),
                        unsafe_allow_html=True,
                    )
            st.markdown(
                source_attribution("SEMAD MG × ANM CFEM · CNPJ = 14 dígitos"),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro na análise CFEM: {e}")

    st.markdown("")

    # ── Classe × Modalidade ──
    st.markdown(
        section_header("Interação: Classe × Modalidade de Licença"),
        unsafe_allow_html=True,
    )
    try:
        cm_df = run_query_df(QUERY_CLASSE_MODALIDADE)
        if not cm_df.empty:
            pivot = cm_df.pivot_table(
                index="modalidade_grupo", columns="classe",
                values="taxa_aprovacao", aggfunc="first",
            )
            count_pv = cm_df.pivot_table(
                index="modalidade_grupo", columns="classe",
                values="total", aggfunc="first", fill_value=0,
            )

            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=[f"Classe {int(c)}" for c in pivot.columns],
                y=pivot.index,
                colorscale=[
                    [0.0, "#C45B52"],
                    [0.5, "#D4A847"],
                    [1.0, "#5BA77D"],
                ],
                zmin=0, zmax=100,
                text=pivot.values,
                texttemplate="%{text:.0f}%",
                textfont={"size": 10},
                customdata=count_pv.values,
                hovertemplate=(
                    "%{y} · %{x}<br>"
                    "Aprovação: %{z:.1f}%<br>"
                    "N = %{customdata:,}<extra></extra>"
                ),
                colorbar={
                    "title": {"text": "Aprovação %", "font": {"size": 10}},
                    "ticksuffix": "%",
                    "len": 0.6,
                },
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=max(250, len(pivot) * 40 + 80),
                yaxis={"tickfont": {"size": 10}},
                xaxis={"side": "top", "tickfont": {"size": 10}},
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution("Combinações com N ≥ 5 · Modalidades agrupadas"),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro na análise classe/modalidade: {e}")

    st.markdown("")

    # ── Reincidência ──
    st.markdown(
        section_header("Reincidência: Empresas com Múltiplas Decisões"),
        unsafe_allow_html=True,
    )
    try:
        reinc = run_query(QUERY_REINCIDENCIA)
        if reinc:
            cols = st.columns(len(reinc))
            for i, row in enumerate(reinc):
                with cols[i]:
                    pct = row["taxa_media_aprovacao"]
                    tone = "positive" if pct >= 65 else "neutral"
                    st.markdown(
                        insight_card(
                            row["faixa"],
                            f"{pct}% aprovação média",
                            f"{row['empresas']:,} empresas · "
                            f"{row['total_decisoes_grupo']:,} decisões",
                            tone,
                        ),
                        unsafe_allow_html=True,
                    )
            st.markdown(
                source_attribution(
                    "Empresas com ≥ 2 decisões · Taxa média por empresa"
                ),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro na análise de reincidência: {e}")

    st.markdown("")

    # ── Arquivamento ──
    st.markdown(
        section_header("Análise de Arquivamentos"),
        unsafe_allow_html=True,
    )
    try:
        arq_df = run_query_df(QUERY_ARQUIVAMENTO_ANALYSIS)
        if not arq_df.empty:
            top = arq_df.head(10)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=top["taxa_arquivamento"],
                y=[f"Cl.{int(c)} | {a}" for c, a
                   in zip(top["classe"], top["atividade_grupo"],
                          strict=False)],
                orientation="h",
                marker_color=[
                    COLORS["indeferido"] if t > 30
                    else COLORS["amber"] if t > 15
                    else COLORS["slate"]
                    for t in top["taxa_arquivamento"]
                ],
                text=[f"{t:.0f}% (N={n:,})" for t, n
                      in zip(top["taxa_arquivamento"], top["total"],
                             strict=False)],
                textposition="outside",
                textfont={"size": 10, "color": "#8B9BB4"},
                hovertemplate=(
                    "%{y}<br>Arquivamento: %{x:.1f}%<br>"
                    "Total: %{customdata:,}<extra></extra>"
                ),
                customdata=top["total"],
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                height=max(280, len(top) * 32 + 60),
                xaxis={"title": {"text": "Taxa de Arquivamento (%)",
                                 "font": {"size": 11}},
                       "gridcolor": "rgba(36, 41, 53, 0.8)"},
                yaxis={"autorange": "reversed", "tickfont": {"size": 10}},
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution(
                    "Combinações classe × atividade com N ≥ 10 · "
                    "Top 10 por taxa de arquivamento"
                ),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro na análise de arquivamento: {e}")


# ════════════════════════════════════════════════════════════════
# TAB 3: CASO DETALHADO
# ════════════════════════════════════════════════════════════════
with tab_detail:
    st.markdown(
        section_header("Buscar Caso por CNPJ"),
        unsafe_allow_html=True,
    )

    # Get list of companies with most decisions for autocomplete
    try:
        top_empresas = run_query("""
            SELECT cnpj_cpf, empreendimento, COUNT(*) AS n
            FROM v_mg_semad
            WHERE atividade LIKE 'A-0%'
              AND cnpj_cpf IS NOT NULL AND cnpj_cpf != '' AND LENGTH(cnpj_cpf) = 14
            GROUP BY cnpj_cpf, empreendimento
            HAVING COUNT(*) >= 3
            ORDER BY n DESC
            LIMIT 50
        """)
    except Exception:
        top_empresas = []

    cnpj_options = {
        f"{e['empreendimento'][:40]} ({e['cnpj_cpf']}) — {e['n']} decisões": e["cnpj_cpf"]
        for e in top_empresas
    }

    selected_label = st.selectbox(
        "Selecione uma empresa (top 50 por volume de decisões)",
        options=[""] + list(cnpj_options.keys()),
        index=0,
    )

    cnpj_input = st.text_input(
        "Ou digite um CNPJ (14 dígitos)",
        placeholder="00000000000000",
    )

    # Resolve CNPJ
    cnpj = ""
    if selected_label and selected_label in cnpj_options:
        cnpj = cnpj_options[selected_label]
    elif cnpj_input:
        cnpj = cnpj_input.replace(".", "").replace("-", "").replace("/", "").strip()

    if cnpj and len(cnpj) == 14:
        st.markdown("")
        st.markdown(
            section_header(
                f"Dossiê — CNPJ {cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}"
                f"/{cnpj[8:12]}-{cnpj[12:]}"
            ),
            unsafe_allow_html=True,
        )

        try:
            # ── Company info from CNPJ database ──
            company_info = run_query(
                "SELECT * FROM v_cnpj WHERE cnpj = ?", [cnpj]
            )

            if company_info:
                ci = company_info[0]
                st.markdown(f"""
                <div class="geo-dossier">
                    <div class="dossier-header">
                        <p class="dossier-name">🏢 {ci.get('razao_social', 'N/A')}</p>
                        <span class="dossier-cnae">{ci.get('cnae_descricao', '')}</span>
                    </div>
                    <div class="geo-kpi-row">
                        <div class="geo-kpi">
                            <p class="kpi-value">{ci.get('porte', 'N/A')}</p>
                            <p class="kpi-label">Porte</p>
                        </div>
                        <div class="geo-kpi">
                            <p class="kpi-value">{str(ci.get('data_abertura', ''))[:10]}</p>
                            <p class="kpi-label">Abertura</p>
                        </div>
                        <div class="geo-kpi">
                            <p class="kpi-value">{ci.get('situacao', 'N/A')}</p>
                            <p class="kpi-label">Situação</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Cross-references ──
            col_inf, col_cfem = st.columns(2)

            with col_inf:
                inf_data = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
                if inf_data:
                    inf = inf_data[0]
                    n_inf = inf["total_infracoes"]
                    tone = "positive" if n_inf == 0 else (
                        "negative" if n_inf >= 3 else "neutral"
                    )
                    st.markdown(
                        insight_card(
                            "Infrações IBAMA",
                            f"{n_inf} infração(ões)" if n_inf else "Nenhuma",
                            f"Em {inf.get('anos_com_infracao', 0)} ano(s) distintos",
                            tone,
                        ),
                        unsafe_allow_html=True,
                    )

            with col_cfem:
                cfem_data_row = run_query(QUERY_CNPJ_CFEM, [cnpj])
                if cfem_data_row:
                    cf = cfem_data_row[0]
                    meses = cf["meses_pagamento"]
                    total = cf.get("total_pago") or 0
                    tone = "positive" if meses > 0 else "neutral"
                    st.markdown(
                        insight_card(
                            "CFEM (Royalties)",
                            f"R$ {total:,.2f}" if total else "Sem pagamentos",
                            f"{meses} mês(es) de pagamento registrados",
                            tone,
                        ),
                        unsafe_allow_html=True,
                    )

            # ── Decision history ──
            st.markdown(
                section_header("Histórico de Decisões"),
                unsafe_allow_html=True,
            )
            hist = run_query(QUERY_HISTORICO_CNPJ, [cnpj])
            if hist:
                for row in hist:
                    badge = decision_badge(row["decisao"])
                    meta_parts = [
                        f"Classe {row['classe']}" if row.get("classe") else None,
                        row.get("modalidade"),
                        str(row.get("ano", "")),
                        row.get("regional", ""),
                    ]
                    meta = " · ".join(p for p in meta_parts if p)

                    st.markdown(f"""
                    <div class="geo-case">
                        <span class="case-icon">📄</span>
                        <div class="case-body">
                            <p class="case-title">{row.get('empreendimento', 'N/A')}</p>
                            <p class="case-meta">{meta}</p>
                            <p class="case-meta" style="margin-top:2px;">
                                {row.get('atividade', '')[:80]}
                            </p>
                        </div>
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)

                    # PDF links
                    docs = row.get("documentos_pdf", "")
                    if docs:
                        doc_links = []
                        for doc_entry in str(docs).split(";"):
                            parts = doc_entry.strip().split("|")
                            if len(parts) == 2 and parts[1].startswith("http"):
                                doc_links.append(
                                    f'<a href="{parts[1]}" target="_blank" '
                                    f'style="color:var(--link); font-size:0.75rem; '
                                    f'text-decoration:none;">{parts[0][:50]} ↗</a>'
                                )
                        if doc_links:
                            st.markdown(
                                '<div style="margin: -4px 0 8px 3.5rem; '
                                'display:flex; flex-wrap:wrap; gap:8px;">'
                                + " ".join(doc_links[:5])
                                + "</div>",
                                unsafe_allow_html=True,
                            )

                st.markdown(
                    source_attribution(
                        f"SEMAD MG · {len(hist)} decisão(ões) para este CNPJ"
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.info("Nenhuma decisão de mineração encontrada para este CNPJ.")

        except Exception as e:
            st.error(f"Erro ao carregar dossiê: {e}")
    elif cnpj:
        st.warning("CNPJ deve ter exatamente 14 dígitos.")
