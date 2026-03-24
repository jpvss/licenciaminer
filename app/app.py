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

    if st.button("Atualizar dados", help="Limpar cache e recarregar dados dos parquets"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

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
        else:
            st.warning("Metadados de coleta não encontrados. Execute `licenciaminer collect`.")
    except Exception:
        st.warning("Não foi possível verificar a data dos dados.")

# ── Hero ──
st.markdown(
    hero_html("LicenciaMiner", "Inteligência de Licenciamento Ambiental Minerário — Minas Gerais"),
    unsafe_allow_html=True,
)

# ── Stats for nav cards (from metadata, no heavy queries at startup) ──
try:
    from app.components.data_loader import load_metadata, safe_query
    _meta = load_metadata()
    semad_n = int(_meta.get("mg_semad", {}).get("records", 0))
    anm_n = int(_meta.get("anm_processos", {}).get("records", 0))
    # Mining count from a lightweight query (cached)
    _mining_r = safe_query(
        "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'",
        context="mineração", fallback=[{"n": 0}],
    )
    mining_n = _mining_r[0]["n"] if _mining_r else 0
except Exception:
    semad_n, anm_n, mining_n = 0, 0, 0

# ── Navigation cards ──
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="geo-nav-card animate-in-d1">
        <span class="nav-icon">📊</span>
        <p class="nav-title">Visão Geral</p>
        <p class="nav-desc">Resumo executivo do banco de dados, tendências de aprovação e insights chave</p>
        <span class="nav-stat">{semad_n:,} decisões</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_visão_geral.py", label="Abrir Visão Geral →", icon=None)

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

with col4:
    st.markdown(f"""
    <div class="geo-nav-card animate-in-d4">
        <span class="nav-icon">📋</span>
        <p class="nav-title">Análise de Decisões</p>
        <p class="nav-desc">Padrões de deferimento/indeferimento, fatores de risco e dossiê por empresa</p>
        <span class="nav-stat">{anm_n:,} títulos ANM</span>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/4_análise_decisões.py", label="Abrir Análise →", icon=None)

# ── Additional nav cards (pages 5-7) ──
col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("""
    <div class="geo-nav-card animate-in-d1">
        <span class="nav-icon">🏗️</span>
        <p class="nav-title">Concessões</p>
        <p class="nav-desc">Decretos de lavra e instrumentos similares com filtros avançados</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/5_concessões.py", label="Abrir Concessões →", icon=None)

with col6:
    st.markdown("""
    <div class="geo-nav-card animate-in-d2">
        <span class="nav-icon">🗺️</span>
        <p class="nav-title">Mapa</p>
        <p class="nav-desc">Visualização geoespacial de polígonos de concessões minerárias</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/6_mapa_concessões.py", label="Abrir Mapa →", icon=None)

with col7:
    st.markdown("""
    <div class="geo-nav-card animate-in-d3">
        <span class="nav-icon">🎯</span>
        <p class="nav-title">Prospecção</p>
        <p class="nav-desc">Identificar oportunidades de aquisição e investimento em concessões</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/7_prospecção.py", label="Abrir Prospecção →", icon=None)

# ── Trust strip ──
# Count sources dynamically
try:
    from app.components.data_loader import get_source_info as _gsi
    _n_sources = len(_gsi())
except Exception:
    _n_sources = 14

st.markdown("")
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0; border-top: 1px solid var(--stratum-3);">
    <span style="font-family: var(--font-mono); font-size: 0.72rem; color: var(--slate-dim);
                 letter-spacing: 0.06em;">
        {_n_sources} FONTES OFICIAIS · 100% RASTREÁVEL · DADOS PÚBLICOS
    </span>
</div>
""", unsafe_allow_html=True)
