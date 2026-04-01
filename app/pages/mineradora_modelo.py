"""IA na Mineração — SQ Solutions.

Objetivo: Dashboard operacional modelo de uma mineradora de ferro
          (5.0 MTPA, disposição de rejeitos em pilhas filtrados).
          Ferramenta de demonstração comercial (POC) para venda
          de consultoria e soluções de IA.
Dados: 100% simulados com base em benchmarks da indústria de mineração.
       NÃO são dados reais de nenhuma empresa.
Status: Em desenvolvimento — simulador e dashboard em construção.
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
    hero_html("IA na Mineração", "SQ Solutions — Summo Quartile"),
    unsafe_allow_html=True,
)

st.warning(
    "**DADOS SIMULADOS** — Este dashboard utiliza dados fictícios gerados "
    "com base em benchmarks da indústria para uma mineradora modelo de "
    "5.0 MTPA de minério de ferro com disposição de rejeitos em pilhas."
)

st.info(
    "🚧 **Em Construção** — O dashboard da Mineradora Modelo está em desenvolvimento ativo."
)

st.markdown(section_header("Estrutura do Dashboard"), unsafe_allow_html=True)

st.markdown("""
**7 setores organizacionais** de uma mineradora integrada:

| Setor | KPIs Principais |
|-------|----------------|
| 1. Planejamento de Mina | Aderência ao plano, REM, Conformidade de cava |
| 2. Operação de Mina | Produtividade da frota, Ciclo de transporte, Consumo de diesel |
| 3. Processamento Mineral | Recuperação metalúrgica, Utilização de planta, Teor do concentrado |
| 4. Rejeitos e Meio Ambiente | Volume disposto, Recirculação de água, Fator de segurança |
| 5. Manutenção | MTBF, MTTR, Disponibilidade física, Custo/tonelada |
| 6. Logística e Supply Chain | Giro de estoque, Lead time, Demurrage |
| 7. SSMA/ESG | TRIFR, Investimento social |

**Parâmetros da mineradora modelo:**
- Produção: 5,0 MTPA de minério de ferro
- Disposição de rejeitos: Pilhas (dry stacking)
- Teor ROM: ~45% Fe
- Teor concentrado: ~65% Fe
- 24 meses de dados simulados
""")

st.markdown("")
st.caption("Em desenvolvimento ativo — disponível em breve")
