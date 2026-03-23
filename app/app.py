"""LicenciaMiner — Inteligência de Licenciamento Ambiental Minerário."""

import streamlit as st

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
    "**Navegação**: Use as páginas acima para explorar os dados."
)
st.sidebar.markdown(
    "Todos os dados são de fontes públicas oficiais. "
    "Cada informação mostra sua fonte e data de atualização."
)

# Main page redirects to Visão Geral
st.switch_page("pages/1_visao_geral.py")
