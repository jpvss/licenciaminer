"""Tab 1: Visão Geral — Executive intelligence briefing."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from app.components.data_loader import (  # noqa: E402
    get_source_info,
    load_metadata,
    run_query,
    run_query_df,
)
from app.styles.theme import (  # noqa: E402
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_MG_SUMMARY,
    QUERY_MINING_TREND,
)

inject_theme(st)

# ── Hero ──
st.markdown(
    hero_html("Visão Geral", "Resumo executivo — dados, tendências e insights"),
    unsafe_allow_html=True,
)

# ── Metric Cards ──
st.markdown(section_header("Painel de Indicadores"), unsafe_allow_html=True)

try:
    semad_count = run_query("SELECT COUNT(*) AS n FROM v_mg_semad")[0]["n"]
    mining_count = run_query(
        "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'"
    )[0]["n"]
except Exception:
    semad_count = 0
    mining_count = 0

try:
    anm_count = run_query("SELECT COUNT(*) AS n FROM v_anm")[0]["n"]
except Exception:
    anm_count = 0

try:
    inf_count = run_query(
        "SELECT COUNT(*) AS n FROM v_ibama_infracoes WHERE UF = 'MG'"
    )[0]["n"]
except Exception:
    inf_count = 0

try:
    mg_summary = run_query(QUERY_MG_SUMMARY)
    approval_rate = mg_summary[0].get("taxa_aprovacao_geral", 0) if mg_summary else 0
except Exception:
    approval_rate = 0

metadata = load_metadata()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Decisões SEMAD", f"{semad_count:,}")
    semad_date = metadata.get("mg_semad", {}).get("last_collected", "")[:10]
    st.markdown(source_attribution(f"SEMAD MG · {semad_date}"), unsafe_allow_html=True)

with col2:
    st.metric("Processos ANM (MG)", f"{anm_count:,}")
    st.markdown(source_attribution("ANM SIGMINE"), unsafe_allow_html=True)

with col3:
    st.metric("Infrações IBAMA (MG)", f"{inf_count:,}")
    st.markdown(source_attribution("IBAMA Dados Abertos"), unsafe_allow_html=True)

with col4:
    st.metric("Aprovação Mineração", f"{approval_rate}%")
    st.markdown(
        source_attribution(f"N = {mining_count:,} decisões"),
        unsafe_allow_html=True,
    )

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
            # Get overall average for reference line
            overall_avg = approval_rate

            fig = go.Figure()

            # Area fill
            fig.add_trace(go.Scatter(
                x=trend_df["ano"],
                y=trend_df["taxa_aprovacao"],
                mode="none",
                fill="tozeroy",
                fillcolor="rgba(212, 168, 71, 0.06)",
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
                textfont={"size": 11, "color": "#8B9BB4", "family": "Instrument Sans"},
                line={"color": "#D4A847", "width": 2.5},
                marker={"size": 7, "color": "#D4A847",
                        "line": {"width": 2, "color": "#0C0E12"}},
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
                line_color="#5E6B80",
                line_width=1,
                annotation_text=f"Média: {overall_avg:.0f}%",
                annotation_position="right",
                annotation_font={"size": 10, "color": "#5E6B80",
                                  "family": "JetBrains Mono"},
            )

            # Count bars on secondary axis
            fig.add_trace(go.Bar(
                x=trend_df["ano"],
                y=trend_df["total"],
                yaxis="y2",
                marker_color="rgba(139, 155, 180, 0.15)",
                showlegend=False,
                hoverinfo="skip",
            ))

            fig.update_layout(
                yaxis={
                    "range": [0, 100],
                    "title": {"text": "Taxa (%)", "font": {"size": 11}},
                    "gridcolor": "rgba(36, 41, 53, 0.8)",
                    "zerolinecolor": "rgba(36, 41, 53, 0.8)",
                },
                yaxis2={
                    "overlaying": "y",
                    "side": "right",
                    "showgrid": False,
                    "showticklabels": False,
                    "range": [0, max(trend_df["total"]) * 5],
                },
                xaxis={
                    "gridcolor": "rgba(36, 41, 53, 0.5)",
                    "dtick": 1,
                },
                height=340,
                margin={"t": 10, "b": 35, "l": 45, "r": 20},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#8B9BB4", "family": "Instrument Sans"},
                hovermode="x unified",
                hoverlabel={
                    "bgcolor": "#1A1E28",
                    "bordercolor": "#2E3442",
                    "font": {"family": "Instrument Sans", "size": 12},
                },
            )
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown(
                source_attribution(
                    f"SEMAD MG · {mining_count:,} decisões · Apenas anos com N ≥ 10"
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
                    / COUNT(*), 1) AS taxa
            FROM v_mg_semad WHERE atividade LIKE 'A-0%' AND classe IS NOT NULL
            GROUP BY classe ORDER BY classe
        """)

        regional_stats = run_query("""
            SELECT
                REPLACE(regional, 'Unidade Regional de Regularização Ambiental ', '') AS reg,
                COUNT(*) AS n,
                ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                    / COUNT(*), 1) AS taxa
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
                    / COUNT(*), 1) AS taxa
            FROM v_mg_semad s
            INNER JOIN ei ON s.cnpj_cpf = ei.cnpj
            WHERE s.atividade LIKE 'A-0%'
        """)

        # Insight 1: Mining vs general
        diff = approval_rate - 78
        tone = "negative" if diff < 0 else "positive"
        st.markdown(
            insight_card(
                "Mineração vs Geral",
                f"{approval_rate}% vs ~78%",
                f"Mineração tem taxa {'menor' if diff < 0 else 'maior'} "
                f"({abs(diff):.0f}pp) · N={mining_count:,}",
                tone,
            ),
            unsafe_allow_html=True,
        )

        # Insight 2: Worst class
        if class_stats:
            worst = min(class_stats, key=lambda x: x["taxa"])
            st.markdown(
                insight_card(
                    "Classe Mais Difícil",
                    f"Classe {int(worst['classe'])}: {worst['taxa']}%",
                    f"Menor taxa de aprovação · N={worst['n']:,}",
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
                    f"Regional com menor taxa · N={r['n']:,}",
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
                    f"Empresas maiores navegam melhor o sistema · N={i['n']:,}",
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

# Source table as HTML table (Streamlit sanitizer-friendly)
table_html = """
<table style="width:100%; border-collapse:collapse; font-family:var(--font-body); font-size:0.82rem;">
<thead>
<tr style="border-bottom:1px solid var(--stratum-4);">
    <th style="padding:0.5rem 0.6rem; text-align:left; font-size:0.68rem; text-transform:uppercase;
               letter-spacing:0.1em; color:var(--slate-dim); font-weight:400;">Fonte</th>
    <th style="padding:0.5rem 0.6rem; text-align:right; font-size:0.68rem; text-transform:uppercase;
               letter-spacing:0.1em; color:var(--slate-dim); font-weight:400;">Registros</th>
    <th style="padding:0.5rem 0.6rem; text-align:right; font-size:0.68rem; text-transform:uppercase;
               letter-spacing:0.1em; color:var(--slate-dim); font-weight:400;">Atualização</th>
    <th style="padding:0.5rem 0.6rem; text-align:right; font-size:0.68rem; text-transform:uppercase;
               letter-spacing:0.1em; color:var(--slate-dim); font-weight:400;">Link</th>
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
    dot_color = "var(--malachite)" if is_fresh else "var(--oxide)"
    date_display = date if is_fresh else "—"

    # Records
    if isinstance(records, int):
        rec_display = (
            f'<span style="color:var(--amber); font-family:var(--font-mono);'
            f' font-weight:500; font-size:0.8rem;">{records:,}</span>'
        )
    elif records and records != "—":
        rec_display = (
            f'<span style="color:var(--amber); font-family:var(--font-mono);'
            f' font-weight:500; font-size:0.8rem;">{records}</span>'
        )
    else:
        rec_display = '<span style="color:var(--slate-dim);">—</span>'

    # Link
    link_html = ""
    if url and url.startswith("http"):
        link_html = (
            f'<a href="{url}" target="_blank" style="color:var(--link);'
            f' text-decoration:none; font-size:0.75rem;">verificar ↗</a>'
        )

    table_html += f"""
<tr style="border-bottom:1px solid var(--stratum-2);">
    <td style="padding:0.55rem 0.6rem; color:var(--quartz); font-weight:500;">
        <span style="display:inline-block; width:7px; height:7px; border-radius:50%;
                     background:{dot_color}; margin-right:8px; vertical-align:middle;"></span>
        {name}
    </td>
    <td style="padding:0.55rem 0.6rem; text-align:right;">{rec_display}</td>
    <td style="padding:0.55rem 0.6rem; text-align:right; font-family:var(--font-mono);
               font-size:0.75rem; color:var(--slate-dim);">{date_display}</td>
    <td style="padding:0.55rem 0.6rem; text-align:right;">{link_html}</td>
</tr>
"""

table_html += "</tbody></table>"
st.markdown(table_html, unsafe_allow_html=True)

# ── Methodology ──
st.markdown("")
with st.expander("Sobre / Metodologia"):
    st.markdown("""
**LicenciaMiner** consolida dados públicos de licenciamento ambiental minerário
em Minas Gerais, cruzando informações de 12 fontes oficiais.

**Incluído:** Decisões SEMAD/MG (desde 2016) · Pareceres técnicos (PDFs) ·
Processos ANM · Infrações IBAMA · CFEM · CNPJ empresas · COPAM CMI ·
Sobreposições espaciais (UCs, TIs, biomas)

**Não incluído:** Licenças federais indeferidas · Outros estados ·
Processos em análise · Cavernas CECAV · Outorgas ANA

**Metodologia:** APIs públicas + scraping + shapefiles · Pareceres via PyMuPDF
(86.6% cobertura) · Cruzamento por CNPJ e sobreposição espacial

**Atualização:** Pipeline incremental — decisões novas detectadas automaticamente
""")
