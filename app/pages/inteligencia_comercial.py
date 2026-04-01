"""Inteligência Comercial — Mineral Intelligence.

Objetivo: Dashboard de indicadores do mercado de mineração brasileira
          com 4 pilares: Mercado/Cotações, Comércio Exterior,
          Produção/Arrecadação e Gestão Territorial.
Fontes de dados:
    - BCB PTAX API (câmbio USD/BRL)
    - Comex Stat / MDIC (comércio exterior por NCM)
    - ANM CFEM (arrecadação de royalties — v_cfem, 91K registros)
    - ANM RAL (produção mineral — v_ral, 1K registros)
    - ANM SIGMINE (processos minerários — v_anm, 50K registros)
    - Cotações de commodities (CSV manual — Investing.com, IndexMundi)
Status: Em desenvolvimento — coleta de dados e dashboard em construção.
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
    hero_html("Inteligência Comercial", "Mineral Intelligence — Summo Quartile"),
    unsafe_allow_html=True,
)

st.info(
    "🚧 **Em Construção** — O dashboard de inteligência comercial está em desenvolvimento ativo."
)

st.markdown(section_header("Pilares do Dashboard"), unsafe_allow_html=True)

st.markdown("""
**4 pilares de inteligência de mercado:**

1. **Mercado & Cotações** — Câmbio USD/BRL (BCB PTAX), cotações de minério
   de ferro, ouro, cobre, níquel
2. **Comércio Exterior** — Exportação e importação de minerais por substância,
   UF e país (Comex Stat/MDIC)
3. **Produção & Arrecadação** — CFEM por município, substância e empresa
   (ANM dados abertos) + produção mineral (RAL)
4. **Gestão e Território** — Processos minerários por fase e substância
   (ANM SIGMINE) + dados de barragens (SIGBM)

**Fontes de dados:**
- Banco Central do Brasil — API PTAX (câmbio, gratuito e oficial)
- MDIC/SECEX — Comex Stat API (comércio exterior, gratuito e oficial)
- ANM — CFEM, RAL, SIGMINE (já integrados ao sistema)
- Cotações de commodities — atualização manual via CSV
""")

st.markdown("")
st.caption("Em desenvolvimento ativo — disponível em breve")
