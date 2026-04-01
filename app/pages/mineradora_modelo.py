"""Mineradora Modelo (IA) — SQ Solutions.

Objetivo: Dashboard operacional modelo de uma mineradora de ferro
          (5.0 MTPA, disposição de rejeitos em pilhas filtrados).
          Ferramenta de demonstração comercial (POC) para venda
          de consultoria e soluções de IA.
Dados: 100% simulados com base em benchmarks da indústria de mineração.
       NÃO são dados reais de nenhuma empresa.
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from app.components.mining_simulator import (  # noqa: E402
    SETORES,
    gerar_todos_os_dados,
    get_kpi_info,
)
from app.styles.theme import (  # noqa: E402
    hero_html,
    inject_theme,
    section_header,
    source_attribution,
)

inject_theme(st)

st.markdown(
    hero_html("Mineradora Modelo (IA)", "SQ Solutions — Summo Quartile"),
    unsafe_allow_html=True,
)

st.warning(
    "**DADOS SIMULADOS** — Este dashboard utiliza dados fictícios gerados "
    "com base em benchmarks da indústria para uma mineradora modelo de "
    "5.0 MTPA de minério de ferro com disposição de rejeitos em pilhas."
)

st.markdown(source_attribution(
    "Mineradora Modelo: 5.0 MTPA · Minério de Ferro · "
    "Rejeitos em Pilhas · 24 meses simulados · Seed fixa"
), unsafe_allow_html=True)

# Gerar todos os dados uma vez (seed fixa = determinístico)
all_data = gerar_todos_os_dados()

# ── Tabs por setor ──
setor_names = list(SETORES.keys())
tabs = st.tabs(setor_names)

for tab, setor in zip(tabs, setor_names, strict=False):
    with tab:
        st.markdown(
            section_header(f"⚠️ DADOS SIMULADOS — {setor}"),
            unsafe_allow_html=True,
        )

        kpi_infos = get_kpi_info(setor)
        kpi_data = all_data[setor]

        # Métricas resumo
        n_cols = min(len(kpi_infos), 4)
        cols = st.columns(n_cols)

        for i, kpi in enumerate(kpi_infos):
            df = kpi_data[kpi.nome]
            current = df["valor"].iloc[-1]
            previous = df["valor"].iloc[-2]
            delta = current - previous

            with cols[i % n_cols]:
                # Formatar valor
                if kpi.unidade == "%":
                    display = f"{current:.1f}%"
                    delta_str = f"{delta:+.1f}%"
                elif kpi.unidade in (":1", ""):
                    display = f"{current:.2f}"
                    delta_str = f"{delta:+.2f}"
                elif kpi.unidade.startswith("R$"):
                    display = f"R$ {current:,.0f}"
                    delta_str = f"R$ {delta:+,.0f}"
                else:
                    display = f"{current:,.1f}"
                    delta_str = f"{delta:+.1f}"

                # Delta: verde se bom, vermelho se ruim
                # Para custos e tempos, menor é melhor
                inverted = kpi.nome in (
                    "Ciclo de Transporte",
                    "Consumo de Diesel",
                    "MTTR",
                    "Custo por Tonelada",
                    "Lead Time Médio",
                    "Demurrage",
                    "TRIFR",
                    "Volume Disposto",
                    "REM (Relação Estéril/Minério)",
                )
                delta_dir = "inverse" if inverted else "normal"

                st.metric(
                    f"{kpi.nome} ({kpi.unidade})" if kpi.unidade else kpi.nome,
                    display,
                    delta=delta_str,
                    delta_color=delta_dir,
                )
                st.caption(f"Target: {kpi.target} | Min: {kpi.min_val} | Max: {kpi.max_val}")

        # Gráficos
        for kpi in kpi_infos:
            df = kpi_data[kpi.nome]

            fig = go.Figure()

            # Faixa target
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["target"],
                mode="lines",
                name="Target",
                line={"color": "#D4A847", "width": 1, "dash": "dash"},
            ))

            # Valor real
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["valor"],
                mode="lines+markers",
                name="Realizado",
                line={"color": "#5BA77D", "width": 2},
                marker={"size": 4},
            ))

            # Faixas min/max
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["max"],
                mode="lines",
                name="Máximo",
                line={"color": "rgba(196,91,82,0.3)", "width": 1},
                showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=df["data"], y=df["min"],
                mode="lines",
                name="Mínimo",
                line={"color": "rgba(196,91,82,0.3)", "width": 1},
                fill="tonexty",
                fillcolor="rgba(196,91,82,0.05)",
                showlegend=False,
            ))

            unit_label = f" ({kpi.unidade})" if kpi.unidade else ""
            fig.update_layout(
                title=(
                    f"⚠️ SIMULADO — {kpi.nome}{unit_label}"
                ),
                xaxis_title="Mês",
                yaxis_title=kpi.unidade or "Valor",
                template="plotly_dark",
                height=350,
                legend={"orientation": "h", "y": -0.15},
            )

            st.plotly_chart(fig, use_container_width=True)

# ── Resumo ──
st.markdown("---")
st.markdown(section_header("Parâmetros da Mineradora Modelo"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Produção:** 5,0 MTPA de minério de ferro\n
    **Teor ROM:** ~45% Fe\n
    **Teor concentrado:** ~65% Fe
    """)
with col2:
    st.markdown("""
    **Disposição de rejeitos:** Pilhas (dry stacking)\n
    **Recuperação metalúrgica:** ~85%\n
    **Disponibilidade física:** ~88%
    """)
with col3:
    st.markdown("""
    **Período simulado:** 24 meses\n
    **7 setores organizacionais**\n
    **Seed fixa:** Resultados reproduzíveis
    """)

st.caption(
    "Todos os dados são fictícios, gerados com base em benchmarks da "
    "indústria de mineração de ferro. Ferramenta de demonstração comercial."
)
