"""Painel Principal — Landing page do Sistema Integrado Summo Quartile.

Objetivo: Visão geral das unidades de negócio com navegação rápida,
          KPIs resumidos e identidade visual premium.
Fontes de dados: Todas as fontes integradas do sistema (16+ fontes oficiais).
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import hero_html  # noqa: E402

_pages_dir = Path(__file__).resolve().parent


def _page_path(filename: str) -> str:
    return str(_pages_dir / filename)


# ── Hero ──
st.markdown(
    hero_html(
        "Sistema Integrado Summo Quartile",
        "Inteligência Ambiental, Mineral e Operacional",
    ),
    unsafe_allow_html=True,
)

# ── Stats ──
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
    infracoes_n = _count("SELECT COUNT(*) AS n FROM v_ibama_infracoes", "infrações")
except Exception:
    from app.components.data_loader import fmt_br

    semad_n, anm_n, mining_n, infracoes_n = 0, 0, 0, 0

try:
    from app.components.data_loader import get_source_info as _gsi

    _n_sources = len(_gsi())
except Exception:
    _n_sources = 16

# ── KPI Row ──
st.markdown(f"""
<div class="dash-kpi-row">
    <div class="dash-kpi">
        <span class="dash-kpi-value">{fmt_br(semad_n)}</span>
        <span class="dash-kpi-label">Decisões SEMAD</span>
    </div>
    <div class="dash-kpi">
        <span class="dash-kpi-value">{fmt_br(anm_n)}</span>
        <span class="dash-kpi-label">Processos ANM</span>
    </div>
    <div class="dash-kpi">
        <span class="dash-kpi-value">{fmt_br(infracoes_n)}</span>
        <span class="dash-kpi-label">Infrações IBAMA</span>
    </div>
    <div class="dash-kpi">
        <span class="dash-kpi-value">{_n_sources}</span>
        <span class="dash-kpi-label">Fontes Oficiais</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Section helper ──
def _section_header(title: str, subtitle: str, accent: str) -> str:
    return f"""
    <div class="dash-section-header" style="--section-accent: var(--{accent});">
        <div class="dash-section-accent"></div>
        <div>
            <h3 class="dash-section-title">{title}</h3>
            <p class="dash-section-sub">{subtitle}</p>
        </div>
    </div>
    """


def _card_label(icon: str, title: str, desc: str, stat: str = "") -> str:
    """Build a rich label for st.page_link with icon, title, desc, and stat."""
    stat_part = f"\n\n`{stat}`" if stat else ""
    return f"{icon} **{title}**\n\n{desc}{stat_part}"


# ── Summo Ambiental ──
st.markdown(
    _section_header("Summo Ambiental", "Soluções em licenciamento ambiental", "orange"),
    unsafe_allow_html=True,
)

cols = st.columns(3)
_ambiental = [
    ("1_visao_geral.py", "🗃️", "Base de Dados",
     "Resumo executivo e tendências", f"{fmt_br(semad_n)} decisões"),
    ("2_explorar_dados.py", "🔍", "Explorar Licenças",
     "Navegue pelos datasets", f"{fmt_br(anm_n)} processos"),
    ("3_consulta.py", "🏢", "Consulta por Empresa",
     "Dossiê por CNPJ ou projeto", f"{fmt_br(mining_n)} mineração"),
]
for col, (page, icon, title, desc, stat) in zip(cols, _ambiental, strict=False):
    with col:
        st.page_link(
            _page_path(page),
            label=_card_label(icon, title, desc, stat),
            use_container_width=True,
        )

cols2 = st.columns(3)
_ambiental2 = [
    ("4_analise_decisoes.py", "⚖️", "Análise de Risco",
     "Padrões e fatores de risco", f"{fmt_br(infracoes_n)} infrações"),
    ("due_diligence.py", "📑", "Due Diligence",
     "Verificação de conformidade", ""),
]
for col, (page, icon, title, desc, stat) in zip(cols2, _ambiental2, strict=False):
    with col:
        st.page_link(
            _page_path(page),
            label=_card_label(icon, title, desc, stat),
            use_container_width=True,
        )


# ── Direitos e Concessões ──
st.markdown(
    _section_header("Direitos e Concessões",
                    "Novos negócios e análise de oportunidades", "teal"),
    unsafe_allow_html=True,
)

cols3 = st.columns(4)
_concessoes = [
    ("5_concessoes.py", "🗃️", "Base de Concessões",
     "Decretos de lavra e instrumentos"),
    ("6_mapa_concessoes.py", "🗺️", "Mapa de Concessões",
     "Polígonos de concessões minerárias"),
    ("viabilidade.py", "📐", "Análise de Viabilidade",
     "Em construção"),
    ("7_prospeccao.py", "🎯", "Prospecção",
     "Oportunidades de aquisição"),
]
for col, (page, icon, title, desc) in zip(cols3, _concessoes, strict=False):
    with col:
        st.page_link(
            _page_path(page),
            label=_card_label(icon, title, desc),
            use_container_width=True,
        )


# ── Mineral Intelligence ──
st.markdown(
    _section_header("Mineral Intelligence",
                    "Consultoria e dados relevantes para o setor", "blue"),
    unsafe_allow_html=True,
)

cols4 = st.columns(2)
_intel = [
    ("inteligencia_comercial.py", "📈", "Inteligência Comercial",
     "Indicadores de mercado mineral"),
    ("monitoramento.py", "📡", "Monitoramento",
     "Em construção"),
]
for col, (page, icon, title, desc) in zip(cols4, _intel, strict=False):
    with col:
        st.page_link(
            _page_path(page),
            label=_card_label(icon, title, desc),
            use_container_width=True,
        )


# ── SQ Solutions ──
st.markdown(
    _section_header("SQ Solutions", "Soluções em Tecnologia e IA", "navy"),
    unsafe_allow_html=True,
)

cols5 = st.columns(2)
_solutions = [
    ("mineradora_modelo.py", "⚙️", "Mineradora Modelo (IA)",
     "Dashboard operacional modelo"),
    ("gestao_interna.py", "🏢", "Gestão Interna SQ",
     "Em construção"),
]
for col, (page, icon, title, desc) in zip(cols5, _solutions, strict=False):
    with col:
        st.page_link(
            _page_path(page),
            label=_card_label(icon, title, desc),
            use_container_width=True,
        )


# ── Trust strip ──
st.markdown(f"""
<div class="trust-strip">
    <span>
        {_n_sources} FONTES OFICIAIS &middot; 100% RASTREÁVEL &middot; DADOS PÚBLICOS &middot; SUMMO QUARTILE
    </span>
</div>
""", unsafe_allow_html=True)
