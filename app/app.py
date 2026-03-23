"""LicenciaMiner — Inteligência de Licenciamento Ambiental Minerário."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="LicenciaMiner",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──
st.markdown("""
<style>
    /* Tighter spacing */
    .block-container { padding-top: 2rem; padding-bottom: 1rem; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #e8b931;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #a0a0b0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* Source badge styling */
    .fonte-badge {
        display: inline-block;
        background: #1e2740;
        border: 1px solid #3a4565;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.75rem;
        color: #8899bb;
        margin-top: 4px;
    }

    /* Insight cards */
    .insight-card {
        background: #111827;
        border-left: 3px solid #e8b931;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .insight-card h4 { margin: 0 0 4px 0; color: #f0f0f0; font-size: 1rem; }
    .insight-card p { margin: 0; color: #a0a0b0; font-size: 0.85rem; }
    .insight-card .stat { color: #e8b931; font-size: 1.3rem; font-weight: 700; }

    /* Data source table */
    .source-row {
        display: flex;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid #1e2740;
    }
    .source-name { flex: 2; color: #e0e0e0; font-weight: 500; }
    .source-count { flex: 1; color: #e8b931; font-weight: 600; text-align: right; }
    .source-date { flex: 1; color: #6b7280; font-size: 0.85rem; text-align: right; }
    .source-link { flex: 0.5; text-align: right; }
    .source-link a { color: #6b8afd; text-decoration: none; font-size: 0.8rem; }
    .source-link a:hover { text-decoration: underline; }

    /* Fresh/stale indicators */
    .fresh { color: #22c55e; }
    .stale { color: #f59e0b; }
    .old { color: #ef4444; }

    /* Section headers */
    .section-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #6b7280;
        margin-bottom: 0.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #1e2740;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### ⛏️ LicenciaMiner")
st.sidebar.caption(
    "Inteligência de Licenciamento Ambiental\n"
    "Minerário em Minas Gerais"
)
st.sidebar.divider()
st.sidebar.markdown(
    "📊 **Dados de fontes públicas oficiais**\n\n"
    "Cada informação mostra sua fonte\n"
    "e data de atualização."
)

# Landing page
st.markdown("# ⛏️ LicenciaMiner")
st.markdown(
    "*Inteligência de Licenciamento Ambiental Minerário — Minas Gerais*"
)
st.markdown("")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("pages/1_visao_geral.py", label="📊 Visão Geral", icon="📊")
    st.caption("Resumo do banco de dados, fontes e insights")
with col2:
    st.page_link("pages/2_explorar_dados.py", label="🔍 Explorar Dados", icon="🔍")
    st.caption("Navegue pelos datasets, filtre e exporte")
with col3:
    st.page_link("pages/3_consulta.py", label="💡 Consulta", icon="💡")
    st.caption("Busque por projeto ou empresa")
