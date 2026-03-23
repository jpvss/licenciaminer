"""Tab 1: Visão Geral — Executive overview + data sources + methodology."""

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
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_MG_SUMMARY,
    QUERY_MINING_TREND,
)

st.markdown("# ⛏️ LicenciaMiner")
st.markdown("*Inteligência de Licenciamento Ambiental Minerário — Minas Gerais*")

# ── Metric Cards ──
st.markdown('<p class="section-header">Resumo do Banco de Dados</p>',
            unsafe_allow_html=True)

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
    st.caption(f"Fonte: SEMAD MG · {semad_date}")

with col2:
    st.metric("Processos ANM (MG)", f"{anm_count:,}")
    st.caption("Fonte: ANM SIGMINE")

with col3:
    st.metric("Infrações IBAMA (MG)", f"{inf_count:,}")
    st.caption("Fonte: IBAMA Dados Abertos")

with col4:
    st.metric("Aprovação Mineração", f"{approval_rate}%")
    st.caption(f"N = {mining_count:,} decisões")

st.markdown("")

# ── Two-column layout: chart + insights ──
chart_col, insights_col = st.columns([3, 2])

with chart_col:
    st.markdown('<p class="section-header">Taxa de Aprovação — Mineração MG</p>',
                unsafe_allow_html=True)
    try:
        trend_df = run_query_df(QUERY_MINING_TREND)
        if not trend_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_df["ano"],
                y=trend_df["taxa_aprovacao"],
                mode="lines+markers+text",
                text=[f"{v:.0f}%" for v in trend_df["taxa_aprovacao"]],
                textposition="top center",
                textfont={"size": 11, "color": "#a0a0b0"},
                line={"color": "#e8b931", "width": 3},
                marker={"size": 8, "color": "#e8b931"},
                hovertemplate="Ano: %{x}<br>Taxa: %{y:.1f}%<br>N: %{customdata}<extra></extra>",
                customdata=trend_df["total"],
            ))
            fig.update_layout(
                yaxis={"range": [0, 100], "title": "Taxa de Aprovação (%)",
                       "gridcolor": "#1e2740"},
                xaxis={"title": "Ano", "gridcolor": "#1e2740"},
                height=350,
                margin={"t": 10, "b": 40, "l": 50, "r": 20},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#a0a0b0"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"Fonte: SEMAD MG · {mining_count:,} decisões · "
                "Apenas anos com N ≥ 10"
            )
    except Exception as e:
        st.error(f"Erro ao carregar tendência: {e}")

with insights_col:
    st.markdown('<p class="section-header">Insights Chave</p>',
                unsafe_allow_html=True)
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
        st.markdown(f"""<div class="insight-card">
            <h4>Mineração vs Geral</h4>
            <span class="stat">{approval_rate}%</span> vs ~78%
            <p>Mineração tem taxa significativamente menor · N={mining_count:,}</p>
        </div>""", unsafe_allow_html=True)

        # Insight 2: Worst class
        if class_stats:
            worst = min(class_stats, key=lambda x: x["taxa"])
            st.markdown(f"""<div class="insight-card">
                <h4>Classe Mais Difícil</h4>
                <span class="stat">Classe {int(worst['classe'])}: {worst['taxa']}%</span>
                <p>Menor taxa de aprovação · N={worst['n']:,}</p>
            </div>""", unsafe_allow_html=True)

        # Insight 3: Worst regional
        if regional_stats:
            r = regional_stats[0]
            st.markdown(f"""<div class="insight-card">
                <h4>Regional Mais Rigorosa</h4>
                <span class="stat">{r['reg']}: {r['taxa']}%</span>
                <p>Regional com menor taxa · N={r['n']:,}</p>
            </div>""", unsafe_allow_html=True)

        # Insight 4: Infractions
        if inf_insight and inf_insight[0]["n"] > 0:
            i = inf_insight[0]
            st.markdown(f"""<div class="insight-card">
                <h4>Empresas com 6+ Infrações</h4>
                <span class="stat">{i['taxa']}% aprovação</span>
                <p>Empresas maiores navegam melhor o sistema · N={i['n']:,}</p>
            </div>""", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro nos insights: {e}")

st.markdown("")

# ── Data Sources ──
st.markdown('<p class="section-header">Fontes de Dados</p>',
            unsafe_allow_html=True)

sources = get_source_info()

# Build HTML table instead of st.dataframe to avoid LinkColumn issues
table_html = '<div style="margin-bottom: 1rem;">'
for s in sources:
    name = s["Fonte"]
    records = s["Registros"]
    date = s["Atualização"]
    url = s.get("URL", "")

    # Freshness color
    if date and date != "—":
        date_display = f'<span class="fresh">{date}</span>'
    else:
        date_display = '<span class="old">—</span>'

    # Records display
    if records and records != "—":
        rec_display = f'<span style="color:#e8b931;font-weight:600">{records:,}</span>' \
            if isinstance(records, int) else \
            f'<span style="color:#e8b931;font-weight:600">{records}</span>'
    else:
        rec_display = '<span style="color:#6b7280">—</span>'

    # Link
    if url and url.startswith("http"):
        link = (
            f'<a href="{url}" target="_blank" '
            'style="color:#6b8afd;text-decoration:none;'
            'font-size:0.8rem">↗ verificar</a>'
        )
    else:
        link = ""

    table_html += f"""<div class="source-row">
        <span class="source-name">{name}</span>
        <span class="source-count">{rec_display}</span>
        <span class="source-date">{date_display}</span>
        <span class="source-link">{link}</span>
    </div>"""

table_html += '</div>'
st.markdown(table_html, unsafe_allow_html=True)

# ── About Section (collapsed) ──
with st.expander("📋 Sobre / Metodologia"):
    st.markdown("""
**LicenciaMiner** consolida dados públicos de licenciamento ambiental minerário
em Minas Gerais, cruzando informações de 10+ fontes oficiais.

**Incluído:** Decisões SEMAD/MG (desde 2016) · Pareceres técnicos (PDFs) ·
Processos ANM · Infrações IBAMA · CFEM · CNPJ empresas · COPAM CMI ·
Sobreposições espaciais (UCs, TIs, biomas)

**Não incluído:** Licenças federais indeferidas · Outros estados ·
Processos em análise · Cavernas CECAV · Outorgas ANA

**Metodologia:** APIs públicas + scraping + shapefiles · Pareceres via PyMuPDF
(86.6% cobertura) · Cruzamento por CNPJ e sobreposição espacial

**Atualização:** Pipeline incremental — decisões novas detectadas automaticamente
""")
