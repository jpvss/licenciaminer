"""Monitoramento de Indicadores — Mineral Intelligence.

Objetivo: Dashboard de monitoramento de indicadores operacionais
          e de mercado do setor minerário brasileiro.
Fontes planejadas: ANM (CFEM, RAL, SIGMINE), IBRAM, BCB, Comex Stat.
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
    hero_html("Monitoramento de Indicadores", "Mineral Intelligence — Summo Quartile"),
    unsafe_allow_html=True,
)

st.info(
    "🚧 **Em Construção** — Esta funcionalidade está em desenvolvimento."
)

st.markdown(section_header("O que será construído"), unsafe_allow_html=True)

st.markdown("""
**Dashboard de monitoramento contínuo** dos principais indicadores do setor mineral:

- **Produção mineral** — Volume por substância, município e empresa (ANM/RAL)
- **Arrecadação CFEM** — Royalties por período, tendências de arrecadação
- **Indicadores de segurança** — SIGBM (barragens), compliance ambiental
- **Alertas automáticos** — Notificações de mudanças significativas nos indicadores

O monitoramento será atualizado com base nas coletas periódicas de dados
das fontes oficiais já integradas ao sistema.
""")

st.markdown("")
st.caption("Previsão de disponibilidade: Q3 2026")
