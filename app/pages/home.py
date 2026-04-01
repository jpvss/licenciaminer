"""Painel Principal — Landing page do Sistema Integrado Summo Quartile.

Objetivo: Visão geral das 6 unidades de negócio com navegação rápida
          e estatísticas resumidas dos dados disponíveis.
Fontes de dados: Todas as fontes integradas do sistema (14+ fontes oficiais).
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import hero_html, section_header  # noqa: E402

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

with st.expander("Como usar o sistema", expanded=False):
    st.markdown("""
**Navegue pelas seções no menu lateral:**

1. **Summo Ambiental** — Inteligência de licenciamento ambiental minerário (MG)
2. **Direitos e Concessões** — Base de concessões, mapa geoespacial e prospecção
3. **Mineral Intelligence** — Indicadores comerciais e de mercado do setor mineral
4. **SQ Solutions** — Soluções em IA para mineração
5. **Gestão Interna** — Ferramentas internas da Summo Quartile

**CNPJs para testar (Summo Ambiental > Consulta):**
- `17.170.150/0001-46` — Vallourec (siderurgia/mineração)
- `16.628.281/0003-23` — Samarco Mineração
- `08.902.291/0001-15` — CSN Mineração
""")

# ── Stats (lightweight cached queries) ──
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

# ── Unidades de Negócio ──

# --- Summo Ambiental ---
st.markdown(section_header("Summo Ambiental"), unsafe_allow_html=True)
st.caption("Soluções em licenciamento ambiental")

cols = st.columns(5)
_ambiental = [
    (_page_path("1_visao_geral.py"), "**Base de Dados**",
     "Resumo executivo e tendências", f"{fmt_br(semad_n)} decisões"),
    (_page_path("2_explorar_dados.py"), "**Explorar Licenças**",
     "Navegue pelos datasets", f"{fmt_br(anm_n)} processos ANM"),
    (_page_path("3_consulta.py"), "**Consulta por Empresa**",
     "Dossiê por CNPJ ou projeto", f"{fmt_br(mining_n)} decisões mineração"),
    (_page_path("4_analise_decisoes.py"), "**Análise de Risco**",
     "Padrões e fatores de risco", f"{fmt_br(infracoes_n)} infrações"),
    (_page_path("due_diligence.py"), "**Due Diligence**",
     "Verificação de conformidade", "Novo"),
]
for col, (page, title, desc, stat) in zip(cols, _ambiental, strict=False):
    with col:
        st.page_link(
            page, label=f"{title}\n\n{desc}\n\n`{stat}`",
            use_container_width=True,
        )

# --- Direitos e Concessões ---
st.markdown(section_header("Direitos e Concessões"), unsafe_allow_html=True)
st.caption("Novos negócios e análise de oportunidades")

cols2 = st.columns(4)
_concessoes = [
    (_page_path("5_concessoes.py"), "**Base de Concessões**",
     "Decretos de lavra e instrumentos"),
    (_page_path("6_mapa_concessoes.py"), "**Mapa de Concessões**",
     "Polígonos de concessões minerárias"),
    (_page_path("viabilidade.py"), "**Análise de Viabilidade**",
     "Em construção"),
    (_page_path("7_prospeccao.py"), "**Prospecção de Oportunidades**",
     "Oportunidades de aquisição"),
]
for col, (page, title, desc) in zip(cols2, _concessoes, strict=False):
    with col:
        st.page_link(
            page, label=f"{title}\n\n{desc}",
            use_container_width=True,
        )

# --- Mineral Intelligence ---
st.markdown(section_header("Mineral Intelligence"), unsafe_allow_html=True)
st.caption("Consultoria e geração de dados relevantes para o setor")

cols3 = st.columns(2)
_mi = [
    (_page_path("inteligencia_comercial.py"), "**Inteligência Comercial**",
     "Indicadores de mercado da mineração"),
    (_page_path("monitoramento.py"), "**Monitoramento**",
     "Em construção"),
]
for col, (page, title, desc) in zip(cols3, _mi, strict=False):
    with col:
        st.page_link(
            page, label=f"{title}\n\n{desc}",
            use_container_width=True,
        )

# --- SQ Solutions ---
st.markdown(section_header("SQ Solutions"), unsafe_allow_html=True)
st.caption("Soluções em Tecnologia e IA")

cols4 = st.columns(2)
with cols4[0]:
    st.page_link(
        _page_path("mineradora_modelo.py"),
        label="**Mineradora Modelo (IA)**\n\nDashboard operacional modelo (POC)",
        use_container_width=True,
    )
with cols4[1]:
    st.page_link(
        _page_path("gestao_interna.py"),
        label="**Gestão Interna SQ**\n\nEm construção",
        use_container_width=True,
    )

# ── Trust strip ──
try:
    from app.components.data_loader import get_source_info as _gsi

    _n_sources = len(_gsi())
except Exception:
    _n_sources = 14

st.markdown("")
st.markdown(f"""
<div class="trust-strip">
    <span>
        {_n_sources} FONTES OFICIAIS &middot; 100% RASTREÁVEL &middot; DADOS PÚBLICOS &middot; SUMMO QUARTILE
    </span>
</div>
""", unsafe_allow_html=True)
