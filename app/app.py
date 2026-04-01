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

# ── Definição de páginas ──
# Cada seção corresponde a uma unidade de negócio da Summo Quartile.
# Páginas com dados reais usam os arquivos existentes.
# Páginas em desenvolvimento usam stubs com "Em Construção".

pages = {
    "Início": [
        st.Page("app/pages/home.py", title="Painel Principal", icon="🏠", default=True),
    ],
    "Summo Ambiental": [
        st.Page("app/pages/1_visao_geral.py", title="Base de Dados", icon="🗃️"),
        st.Page("app/pages/2_explorar_dados.py", title="Explorar Licenças", icon="🔍"),
        st.Page("app/pages/3_consulta.py", title="Consulta por Empresa", icon="🏢"),
        st.Page("app/pages/4_analise_decisoes.py", title="Análise de Risco", icon="⚖️"),
        st.Page("app/pages/due_diligence.py", title="Due Diligence Ambiental", icon="📑"),
    ],
    "Direitos e Concessões": [
        st.Page("app/pages/5_concessoes.py", title="Base de Concessões", icon="🗃️"),
        st.Page("app/pages/6_mapa_concessoes.py", title="Mapa de Concessões", icon="🗺️"),
        st.Page("app/pages/viabilidade.py", title="Análise de Viabilidade", icon="📐"),
        st.Page("app/pages/7_prospeccao.py", title="Prospecção de Oportunidades", icon="🎯"),
    ],
    "Mineral Intelligence": [
        st.Page("app/pages/inteligencia_comercial.py", title="Inteligência Comercial", icon="📈"),
        st.Page("app/pages/monitoramento.py", title="Monitoramento de Indicadores", icon="📡"),
    ],
    "SQ Solutions": [
        st.Page("app/pages/mineradora_modelo.py", title="Mineradora Modelo (IA)", icon="⚙️"),
    ],
    "Gestão Interna": [
        st.Page("app/pages/gestao_interna.py", title="Gestão Interna SQ", icon="🏢"),
    ],
}

pg = st.navigation(pages)

st.set_page_config(
    page_title="Summo Quartile",
    page_icon="SQ",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# ── Executar a página selecionada ──
pg.run()
