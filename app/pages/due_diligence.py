"""Due Diligence Ambiental — Summo Ambiental.

Objetivo: Verificação da aderência de processos de licenciamento ambiental
          à legislação aplicável, com checklist documental, testes de
          conformidade e enriquecimento com dados históricos.
Fontes de dados:
    - Referência: Inventário de documentos (DN COPAM 217/2017 + legislação MG)
    - Enriquecimento: v_mg_semad (42.758 decisões), v_ibama_infracoes, v_cfem, v_spatial, v_copam
    - Input do usuário: Marcações de documentos e testes de conformidade
Status: Em desenvolvimento — estrutura e workflow em construção.
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
    hero_html("Due Diligence Ambiental", "Summo Ambiental — Summo Quartile"),
    unsafe_allow_html=True,
)

st.info(
    "🚧 **Em Construção** — O produto de Due Diligence está em desenvolvimento ativo."
)

st.markdown(section_header("Sobre o Produto"), unsafe_allow_html=True)

st.markdown("""
**Due Diligence de Processos Ambientais** — Verificação prévia da aderência
de processos de licenciamento ambiental à legislação aplicável.

**Workflow planejado (4 etapas):**

1. **Configuração do Projeto** — Selecionar tipo de licença, classe ambiental
   e atividade para filtrar documentos aplicáveis
2. **Checklist de Documentos** — Verificar quais documentos foram apresentados
   pelo empreendedor (inventário de 119+ documentos mapeados)
3. **Testes de Conformidade** — Avaliar aderência de cada documento aos
   requisitos legais (490+ testes mapeados)
4. **Relatório e Contexto** — Dashboard de conformidade + enriquecimento
   com dados históricos (taxa de aprovação, infrações, restrições espaciais)

**Metodologia:** Baseada na DN COPAM 217/2017 e legislação ambiental
do estado de Minas Gerais, com ponderação de risco operacional e legal.

**Escala de conformidade:**
- Alta aderência (≥ 90%)
- Sob controle (80-90%)
- Melhorias pontuais (65-80%)
- Melhorias significativas (50-65%)
- Não conforme (< 50%)
""")

st.markdown("")
st.caption("Em desenvolvimento ativo — disponível em breve")
