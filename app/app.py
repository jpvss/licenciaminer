"""LicenciaMiner — Inteligência de Licenciamento Ambiental Minerário."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import inject_theme, hero_html  # noqa: E402

st.set_page_config(
    page_title="LicenciaMiner",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme(st)

# ── Sidebar branding ──
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>⛏️ LicenciaMiner</h2>
        <p>Inteligência Ambiental Minerária</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Dados de fontes públicas oficiais. "
        "Cada registro é rastreável à fonte original."
    )

    # Data freshness
    try:
        from app.components.data_loader import load_metadata
        meta = load_metadata()
        last_date = meta.get("mg_semad", {}).get("last_collected", "")[:10]
        if last_date:
            st.markdown(f"""
            <div class="sidebar-freshness">
                <span class="dot"></span>
                Dados: {last_date}
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass

# ── Hero ──
st.markdown(
    hero_html("LicenciaMiner", "Inteligência de Licenciamento Ambiental Minerário — Minas Gerais"),
    unsafe_allow_html=True,
)

# ── Live stats for nav cards ──
try:
    from app.components.data_loader import run_query
    semad_n = run_query("SELECT COUNT(*) AS n FROM v_mg_semad")[0]["n"]
    anm_n = run_query("SELECT COUNT(*) AS n FROM v_anm")[0]["n"]
    mining_n = run_query(
        "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'"
    )[0]["n"]
except Exception:
    semad_n, anm_n, mining_n = 0, 0, 0

# ── Navigation cards ──
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="geo-nav-card animate-in-d1">
        <span class="nav-icon">📊</span>
        <p class="nav-title">Visão Geral</p>
        <p class="nav-desc">Resumo executivo do banco de dados, tendências de aprovação e insights chave</p>
        <span class="nav-stat">{semad_n:,} decisões</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_visao_geral.py", label="Abrir Visão Geral →", icon=None)

with col2:
    st.markdown(f"""
    <div class="geo-nav-card animate-in-d2">
        <span class="nav-icon">🔍</span>
        <p class="nav-title">Explorar Dados</p>
        <p class="nav-desc">Navegue pelos datasets, filtre registros e verifique na fonte original</p>
        <span class="nav-stat">{anm_n:,} processos ANM</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_explorar_dados.py", label="Abrir Explorador →", icon=None)

with col3:
    st.markdown(f"""
    <div class="geo-nav-card animate-in-d3">
        <span class="nav-icon">💡</span>
        <p class="nav-title">Consulta</p>
        <p class="nav-desc">Busque por projeto ou empresa para obter um briefing com estatísticas e casos similares</p>
        <span class="nav-stat">{mining_n:,} decisões mineração</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_consulta.py", label="Abrir Consulta →", icon=None)

# ── Trust strip ──
st.markdown("")
st.markdown("""
<div style="text-align: center; padding: 1rem 0; border-top: 1px solid var(--stratum-3);">
    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--slate-dim);
                 letter-spacing: 0.06em;">
        12 FONTES OFICIAIS · 100% RASTREÁVEL · DADOS PÚBLICOS
    </span>
</div>
""", unsafe_allow_html=True)
