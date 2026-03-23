"""LicenciaMiner — Inteligência de Licenciamento Ambiental Minerário."""

import sys
from pathlib import Path

# Add project root + src to path
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

st.sidebar.title("⛏️ LicenciaMiner")
st.sidebar.caption(
    "Inteligência de Licenciamento Ambiental Minerário em Minas Gerais"
)
st.sidebar.divider()
st.sidebar.markdown(
    "Todos os dados são de fontes públicas oficiais. "
    "Cada informação mostra sua fonte e data de atualização."
)

# Landing page
st.title("⛏️ LicenciaMiner")
st.markdown(
    "### Inteligência de Licenciamento Ambiental Minerário — Minas Gerais"
)
st.markdown(
    "Use o menu lateral para navegar entre as páginas:"
)
st.markdown(
    """
    - **Visão Geral** — resumo do banco de dados, fontes, insights
    - **Explorar Dados** — navegue pelos datasets, filtre e exporte
    - **Consulta** — busque por projeto ou empresa para análise detalhada
    """
)
