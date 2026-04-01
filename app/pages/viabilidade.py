"""Análise de Viabilidade — Direitos e Concessões.

Objetivo: Sistema automático de análise de viabilidade de projetos
          minerários a partir de parâmetros coletados.
Fontes planejadas: v_concessoes, v_cfem, v_spatial, v_anm, dados de mercado.
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
    hero_html("Análise de Viabilidade", "Direitos e Concessões — Summo Quartile"),
    unsafe_allow_html=True,
)

st.info(
    "🚧 **Em Construção** — Esta funcionalidade está em desenvolvimento."
)

st.markdown(section_header("O que será construído"), unsafe_allow_html=True)

st.markdown("""
**Análise automática de viabilidade** para projetos de mineração, integrando:

- **Dados de concessões** — Área, substância, regime, titular
- **Histórico CFEM** — Arrecadação passada como proxy de viabilidade econômica
- **Restrições espaciais** — Sobreposição com UCs, TIs, biomas (fatores de bloqueio)
- **Cotações de mercado** — Preço da substância vs custo estimado de operação
- **Análise de risco regulatório** — Taxa de aprovação histórica para atividade/classe/regional

O sistema cruzará esses dados para gerar um **score de viabilidade** com
recomendações objetivas para cada concessão avaliada.
""")

st.markdown("")
st.caption("Previsão de disponibilidade: Q3 2026")
