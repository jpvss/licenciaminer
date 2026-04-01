"""Sistema Integrado Summo Quartile — Router principal.

Utiliza st.navigation() para organizar todas as páginas em seções
correspondentes às 6 unidades de negócio da Summo Quartile.
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import inject_theme  # noqa: E402

st.set_page_config(
    page_title="Summo Quartile",
    page_icon="SQ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Definição de páginas ──
# Cada seção corresponde a uma unidade de negócio da Summo Quartile.
# Páginas com dados reais usam os arquivos existentes.
# Páginas em desenvolvimento usam stubs com "Em Construção".

_pages_dir = Path(__file__).resolve().parent / "pages"


def _page(filename: str, **kwargs) -> st.Page:
    return st.Page(str(_pages_dir / filename), **kwargs)


pages = {
    "Início": [
        _page("home.py", title="Painel Principal", icon="🏠", default=True),
    ],
    "Summo Ambiental": [
        _page("1_visao_geral.py", title="Base de Dados", icon="🗃️"),
        _page("2_explorar_dados.py", title="Explorar Licenças", icon="🔍"),
        _page("3_consulta.py", title="Consulta por Empresa", icon="🏢"),
        _page("4_analise_decisoes.py", title="Análise de Risco", icon="⚖️"),
        _page("due_diligence.py", title="Due Diligence Ambiental", icon="📑"),
    ],
    "Direitos e Concessões": [
        _page("5_concessoes.py", title="Base de Concessões", icon="🗃️"),
        _page("6_mapa_concessoes.py", title="Mapa de Concessões", icon="🗺️"),
        _page("viabilidade.py", title="Análise de Viabilidade", icon="📐"),
        _page("7_prospeccao.py", title="Prospecção de Oportunidades", icon="🎯"),
    ],
    "Mineral Intelligence": [
        _page("inteligencia_comercial.py", title="Inteligência Comercial", icon="📈"),
        _page("monitoramento.py", title="Monitoramento de Indicadores", icon="📡"),
    ],
    "SQ Solutions": [
        _page("mineradora_modelo.py", title="Mineradora Modelo (IA)", icon="⚙️"),
    ],
    "Gestão Interna": [
        _page("gestao_interna.py", title="Gestão Interna SQ", icon="🏢"),
    ],
}

pg = st.navigation(pages)

# ── Tema global (frame compartilhado entre todas as páginas) ──
inject_theme(st)

# ── Sidebar branding ──
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Summo Quartile</h2>
        <div class="brand-accent"></div>
        <p>Sistema Integrado</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Fontes públicas oficiais · "
        "Cada registro rastreável à origem"
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

# ── Executar a página selecionada ──
pg.run()
