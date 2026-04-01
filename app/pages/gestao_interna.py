"""Gestão Interna SQ — Ferramentas internas da Summo Quartile.

Objetivo: Automatização de gestão financeira, processos internos
          e ferramentas de suporte à operação da Summo Quartile.
Status: Em desenvolvimento.
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.styles.theme import hero_html, inject_theme, section_header  # noqa: E402

inject_theme(st)

st.markdown(
    hero_html("Gestão Interna SQ", "Summo Quartile"),
    unsafe_allow_html=True,
)

st.info(
    "🚧 **Em Construção** — Esta funcionalidade está em desenvolvimento."
)

st.markdown(section_header("O que será construído"), unsafe_allow_html=True)

st.markdown("""
**Ferramentas de gestão interna** para a Summo Quartile:

- **Gestão financeira** — Controle de receitas, custos e fluxo de caixa
- **Gestão de projetos** — Acompanhamento de entregas e prazos
- **CRM de clientes** — Base de clientes e histórico de interações
- **Relatórios gerenciais** — Indicadores de performance do grupo

Esta seção é destinada ao uso interno da equipe Summo Quartile.
""")

st.markdown("")
st.caption("Previsão de disponibilidade: Q4 2026")
