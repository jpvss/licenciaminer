"""Tab 1: Base de Dados — Executive intelligence briefing."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from app.components.data_loader import (  # noqa: E402
    fmt_br,
    fmt_pct,
    get_source_info,
    load_metadata,
    run_query,
    run_query_df,
    safe_query,
)
from app.styles.theme import (  # noqa: E402
    CHART_COLORS,
    get_plotly_layout,
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_MG_SUMMARY,
    QUERY_MINING_SUMMARY,
    QUERY_MINING_TREND,
)

inject_theme(st)

# ── Hero ──
st.markdown(
    hero_html("Base de Dados", "Resumo executivo — dados, tendências e insights"),
    unsafe_allow_html=True,
)

# ── Metric Cards ──
st.markdown(section_header("Painel de Indicadores"), unsafe_allow_html=True)

_semad_r = safe_query(
    "SELECT COUNT(*) AS n FROM v_mg_semad", context="SEMAD", fallback=[{"n": 0}]
)
semad_count = _semad_r[0]["n"] if _semad_r else 0

_mining_r = safe_query(
    "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'",
    context="SEMAD mineração", fallback=[{"n": 0}],
)
mining_count = _mining_r[0]["n"] if _mining_r else 0

_anm_r = safe_query(
    "SELECT COUNT(*) AS n FROM v_anm", context="ANM", fallback=[{"n": 0}]
)
anm_count = _anm_r[0]["n"] if _anm_r else 0

_inf_r = safe_query(
    "SELECT COUNT(*) AS n FROM v_ibama_infracoes WHERE UF = 'MG'",
    context="IBAMA Infrações", fallback=[{"n": 0}],
)
inf_count = _inf_r[0]["n"] if _inf_r else 0

_mg_summary = safe_query(QUERY_MG_SUMMARY, context="Resumo MG", fallback=[])
general_approval_rate = _mg_summary[0].get("taxa_aprovacao_geral", 0) if _mg_summary else 0

_mining_summary = safe_query(QUERY_MINING_SUMMARY, context="Resumo Mineração", fallback=[])
mining_approval_rate = _mining_summary[0].get("taxa_aprovacao_mineracao", 0) if _mining_summary else 0

metadata = load_metadata()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Decisões SEMAD", fmt_br(semad_count),
        help="Total de decisões de licenciamento ambiental em MG (deferimentos + indeferimentos + arquivamentos)",
    )
    semad_date = metadata.get("mg_semad", {}).get("last_collected", "")[:10]
    st.markdown(source_attribution(f"SEMAD MG · {semad_date}"), unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-blue">', unsafe_allow_html=True)
    st.metric(
        "Processos ANM (MG)", fmt_br(anm_count),
        help="Processos minerários ativos na ANM: pesquisa, lavra, licenciamento, etc.",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(source_attribution("ANM SIGMINE"), unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-danger">', unsafe_allow_html=True)
    st.metric(
        "Infrações IBAMA (MG)", fmt_br(inf_count),
        help="Autos de infração ambiental registrados pelo IBAMA em Minas Gerais",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(source_attribution("IBAMA Dados Abertos"), unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-orange">', unsafe_allow_html=True)
    st.metric("Aprovação Mineração", fmt_pct(mining_approval_rate),
              help="Deferidos / total (inclui arquivamentos no denominador)")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        source_attribution(f"N = {fmt_br(mining_count)} decisões"),
        unsafe_allow_html=True,
    )

# Decision distribution summary
_dist = safe_query(
    "SELECT decisao, COUNT(*) AS n FROM v_mg_semad "
    "WHERE atividade LIKE 'A-0%' GROUP BY decisao ORDER BY n DESC",
    context="distribuição", fallback=[],
)
if _dist:
    _parts = []
    for d in _dist:
        dec = d.get("decisao", "?")
        n = d.get("n", 0)
        _parts.append(f"{fmt_br(n)} {dec}s")
    st.caption(f"Mineração: {' · '.join(_parts)}")

st.markdown("")

# ── Two-column: chart + insights ──
chart_col, insights_col = st.columns([3, 2])

with chart_col:
    st.markdown(
        section_header("Taxa de Aprovação — Mineração MG"),
        unsafe_allow_html=True,
    )
    try:
        trend_df = run_query_df(QUERY_MINING_TREND)
        if not trend_df.empty:
            overall_avg = mining_approval_rate

            fig = go.Figure()

            # Area fill
            fig.add_trace(go.Scatter(
                x=trend_df["ano"],
                y=trend_df["taxa_aprovacao"],
                mode="none",
                fill="tozeroy",
                fillcolor="rgba(21, 96, 130, 0.06)",
                showlegend=False,
                hoverinfo="skip",
            ))

            # Main line
            fig.add_trace(go.Scatter(
                x=trend_df["ano"],
                y=trend_df["taxa_aprovacao"],
                mode="lines+markers+text",
                text=[f"{v:.0f}%" for v in trend_df["taxa_aprovacao"]],
                textposition="top center",
                textfont={"size": 11, "color": "#4A5568", "family": "Inter"},
                line={"color": CHART_COLORS["primary"], "width": 2.5},
                marker={"size": 7, "color": CHART_COLORS["primary"],
                        "line": {"width": 2, "color": "#FFFFFF"}},
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Taxa: %{y:.1f}%<br>"
                    "Decisões: %{customdata:,}"
                    "<extra></extra>"
                ),
                customdata=trend_df["total"],
                showlegend=False,
            ))

            # Average reference line
            fig.add_hline(
                y=overall_avg,
                line_dash="dot",
                line_color="#8896A6",
                line_width=1,
                annotation_text=f"Média: {overall_avg:.0f}%",
                annotation_position="right",
                annotation_font={"size": 10, "color": "#8896A6",
                                  "family": "JetBrains Mono"},
            )

            # Count bars on secondary axis
            fig.add_trace(go.Bar(
                x=trend_df["ano"],
                y=trend_df["total"],
                yaxis="y2",
                marker_color="rgba(41, 128, 185, 0.08)",
                showlegend=False,
                hoverinfo="skip",
            ))

            layout = get_plotly_layout(
                height=340,
                yaxis={
                    "range": [0, 100],
                    "title": {"text": "Taxa (%)", "font": {"size": 11}},
                    "gridcolor": "rgba(226, 230, 237, 0.6)",
                    "zerolinecolor": "#E2E6ED",
                },
                yaxis2={
                    "overlaying": "y",
                    "side": "right",
                    "showgrid": False,
                    "showticklabels": False,
                    "range": [0, max(trend_df["total"]) * 5],
                },
                xaxis={
                    "gridcolor": "rgba(226, 230, 237, 0.4)",
                    "dtick": 1,
                },
            )
            fig.update_layout(**layout)
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution(
                    f"SEMAD MG · {fmt_br(mining_count)} decisões · Apenas anos com N >= 10"
                ),
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro ao carregar tendência: {e}")

with insights_col:
    st.markdown(
        section_header("Insights Chave"),
        unsafe_allow_html=True,
    )
    try:
        class_stats = run_query("""
            SELECT classe, COUNT(*) AS n,
                ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0), 1) AS taxa
            FROM v_mg_semad WHERE atividade LIKE 'A-0%' AND classe IS NOT NULL
            GROUP BY classe ORDER BY classe
        """)

        regional_stats = run_query("""
            SELECT
                REPLACE(regional, 'Unidade Regional de Regularização Ambiental ', '') AS reg,
                COUNT(*) AS n,
                ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0), 1) AS taxa
            FROM v_mg_semad WHERE atividade LIKE 'A-0%'
            GROUP BY regional HAVING COUNT(*) >= 50
            ORDER BY taxa ASC LIMIT 1
        """)

        inf_insight = run_query("""
            WITH ei AS (
                SELECT REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') AS cnpj,
                    COUNT(*) AS n_inf
                FROM v_ibama_infracoes WHERE UF = 'MG'
                GROUP BY REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g')
                HAVING COUNT(*) >= 6
            )
            SELECT COUNT(*) AS n,
                ROUND(100.0 * SUM(CASE WHEN s.decisao = 'deferido' THEN 1 ELSE 0 END)
                    / NULLIF(COUNT(*), 0), 1) AS taxa
            FROM v_mg_semad s
            INNER JOIN ei ON s.cnpj_cpf = ei.cnpj
            WHERE s.atividade LIKE 'A-0%'
        """)

        # Insight 1: Mining vs general
        diff = mining_approval_rate - general_approval_rate
        tone = "negative" if diff < 0 else "positive"
        st.markdown(
            insight_card(
                "Mineração vs Geral",
                f"{mining_approval_rate}% vs {general_approval_rate}%",
                f"Mineração tem taxa {'menor' if diff < 0 else 'maior'} "
                f"({abs(diff):.0f}pp) · N={fmt_br(mining_count)}",
                tone,
            ),
            unsafe_allow_html=True,
        )

        # Insight 2: Worst class
        valid_class_stats = [c for c in class_stats if c.get("taxa") is not None]
        if valid_class_stats:
            worst = min(valid_class_stats, key=lambda x: x["taxa"])
            st.markdown(
                insight_card(
                    "Classe Mais Difícil",
                    f"Classe {int(worst['classe'])}: {worst['taxa']}%",
                    f"Menor taxa de aprovação · N={fmt_br(worst['n'])}",
                    "negative",
                ),
                unsafe_allow_html=True,
            )

        # Insight 3: Worst regional
        if regional_stats:
            r = regional_stats[0]
            st.markdown(
                insight_card(
                    "Regional Mais Rigorosa",
                    f"{r['reg']}: {r['taxa']}%",
                    f"Regional com menor taxa · N={fmt_br(r['n'])}",
                    "negative",
                ),
                unsafe_allow_html=True,
            )

        # Insight 4: Infractions
        if inf_insight and inf_insight[0]["n"] > 0:
            i = inf_insight[0]
            st.markdown(
                insight_card(
                    "Empresas com 6+ Infrações",
                    f"{i['taxa']}% aprovação",
                    f"Empresas maiores navegam melhor o sistema · N={fmt_br(i['n'])}",
                    "neutral",
                ),
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.error(f"Erro nos insights: {e}")

st.markdown("")

# ── Data Sources ──
st.markdown(section_header("Fontes de Dados"), unsafe_allow_html=True)

sources = get_source_info()

# Source table using the new table class
table_html = """
<table class="source-table">
<thead>
<tr>
    <th>Fonte</th>
    <th>Registros</th>
    <th>Atualização</th>
    <th>Link</th>
</tr>
</thead>
<tbody>
"""

for s in sources:
    name = s["Fonte"]
    records = s["Registros"]
    date = s["Atualização"]
    url = s.get("URL", "")

    # Status dot
    is_fresh = date and date != "—"
    dot_color = "var(--success)" if is_fresh else "var(--danger)"
    date_display = date if is_fresh else "—"

    # Records
    if isinstance(records, int):
        rec_display = f'<span class="td-count">{fmt_br(records)}</span>'
    elif records and records != "—":
        rec_display = f'<span class="td-count">{records}</span>'
    else:
        rec_display = '<span style="color:var(--text-muted);">—</span>'

    # Link
    link_html = ""
    if url and url.startswith("http"):
        link_html = f'<a href="{url}" target="_blank">verificar &#8599;</a>'

    table_html += f"""
<tr>
    <td class="td-name">
        <span style="display:inline-block; width:7px; height:7px; border-radius:50%;
                     background:{dot_color}; margin-right:8px; vertical-align:middle;"></span>
        {name}
    </td>
    <td>{rec_display}</td>
    <td class="td-date">{date_display}</td>
    <td class="td-link">{link_html}</td>
</tr>
"""

table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)

# ── Methodology ──
st.markdown("")
with st.expander("Sobre / Metodologia"):
    st.markdown("""
**LicenciaMiner** consolida dados públicos de licenciamento ambiental minerário
em Minas Gerais, cruzando informações de 14 fontes oficiais.

**Incluído:** Decisões SEMAD/MG (desde 2016) · Pareceres técnicos (PDFs) ·
Processos ANM · Infrações IBAMA · CFEM · CNPJ empresas · COPAM CMI ·
Sobreposições espaciais (UCs, TIs, biomas)

**Não incluído:** Licenças federais indeferidas · Outros estados ·
Processos em análise · Cavernas CECAV · Outorgas ANA

**Metodologia:** APIs públicas + scraping + shapefiles · Pareceres via PyMuPDF
(86.6% cobertura) · Cruzamento por CNPJ e sobreposição espacial

**Taxa de aprovação:** Calculada como `deferidos / total de decisões`. O denominador
inclui arquivamentos (processos encerrados sem decisão de mérito), o que reduz a taxa
em ~10pp vs considerar apenas deferido/indeferido. Esta é uma escolha conservadora
que reflete a realidade do processo: projetos arquivados **não obtiveram** licença.

**Atualização:** Pipeline incremental — decisões novas detectadas automaticamente
""")
