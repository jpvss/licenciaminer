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
        st.toast("Cache limpo. Recarregando...")
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

# ── Stats for nav cards (lightweight cached queries) ──
try:
    from app.components.data_loader import fmt_br, safe_query

    def _count(query: str, ctx: str) -> int:
        r = safe_query(query, context=ctx, fallback=[{"n": 0}])
        return r[0]["n"] if r else 0

    semad_n = _count("SELECT COUNT(*) AS n FROM v_mg_semad", "SEMAD")
    anm_n = _count("SELECT COUNT(*) AS n FROM v_anm", "ANM")
    mining_n = _count(
        "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'",
        "mineração",
    )
except Exception:
    from app.components.data_loader import fmt_br
    semad_n, anm_n, mining_n = 0, 0, 0

# ── Navigation cards ──
_nav_cards = [
    ("pages/1_visão_geral.py", "📊", "Visão Geral",
     "Resumo executivo, tendências de aprovação e insights chave",
     f"{fmt_br(semad_n)} decisões", "d1"),
    ("pages/2_explorar_dados.py", "🔍", "Explorar Dados",
     "Navegue pelos datasets, filtre e verifique na fonte original",
     f"{fmt_br(anm_n)} processos ANM", "d2"),
    ("pages/3_consulta.py", "💡", "Consulta",
     "Briefing com estatísticas e casos similares por projeto ou empresa",
     f"{fmt_br(mining_n)} decisões mineração", "d3"),
    ("pages/4_análise_decisões.py", "📋", "Análise de Decisões",
     "Padrões de deferimento, fatores de risco e dossiê por empresa",
     f"{fmt_br(mining_n)} decisões analisadas", "d4"),
]

cols = st.columns(4)
for col, (page, icon, title, desc, stat, anim) in zip(cols, _nav_cards):
    with col:
        st.markdown(f"""
        <div class="geo-nav-card animate-in-{anim}">
            <span class="nav-icon">{icon}</span>
            <p class="nav-title">{title}</p>
            <p class="nav-desc">{desc}</p>
            <span class="nav-stat">{stat}</span>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(page, label="→")

st.markdown("")

_nav_cards_2 = [
    ("pages/5_concessões.py", "🏗️", "Concessões",
     "Decretos de lavra e instrumentos similares com filtros avançados", "d1"),
    ("pages/6_mapa_concessões.py", "🗺️", "Mapa",
     "Visualização geoespacial de polígonos de concessões minerárias", "d2"),
    ("pages/7_prospecção.py", "🎯", "Prospecção",
     "Identificar oportunidades de aquisição e investimento em concessões", "d3"),
]

cols2 = st.columns(3)
for col, (page, icon, title, desc, anim) in zip(cols2, _nav_cards_2):
    with col:
        st.markdown(f"""
        <div class="geo-nav-card animate-in-{anim}">
            <span class="nav-icon">{icon}</span>
            <p class="nav-title">{title}</p>
            <p class="nav-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)
        st.page_link(page, label="→")

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
