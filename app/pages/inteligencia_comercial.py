"""Inteligência Comercial — Mineral Intelligence.

Objetivo: Dashboard de indicadores do mercado de mineração brasileira
          com 4 pilares: Mercado/Cotações, Comércio Exterior,
          Produção/Arrecadação e Gestão Territorial.
Fontes de dados:
    - BCB PTAX API (câmbio USD/BRL) → v_bcb_cotacoes
    - Comex Stat / MDIC (comércio exterior por NCM) → v_comex_mineracao
    - ANM CFEM (arrecadação de royalties) → v_cfem
    - ANM RAL (produção mineral) → v_ral
    - ANM SIGMINE (processos minerários) → v_anm
    - Cotações de commodities (CSV manual)
"""

import csv
import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import (  # noqa: E402
    fmt_br,
    safe_query,
)
from app.styles.theme import (  # noqa: E402
    hero_html,
    inject_theme,
    section_header,
    source_attribution,
)

inject_theme(st)

st.markdown(
    hero_html("Inteligência Comercial", "Mineral Intelligence — Summo Quartile"),
    unsafe_allow_html=True,
)
st.markdown(source_attribution(
    "Fontes: BCB PTAX (câmbio) · Comex Stat/MDIC (comércio exterior) · "
    "ANM (CFEM/RAL/SIGMINE) · Cotações manuais (CSV)"
), unsafe_allow_html=True)

# ── Tabs ──
tab_mercado, tab_comex, tab_producao, tab_territorio = st.tabs([
    "Mercado & Cotações",
    "Comércio Exterior",
    "Produção & Arrecadação",
    "Gestão e Território",
])


# ═══════════════════════════════════════════════════════════════
# Tab 1: Mercado & Cotações
# ═══════════════════════════════════════════════════════════════
with tab_mercado:
    st.markdown(section_header("Câmbio USD/BRL"), unsafe_allow_html=True)

    ptax_data = safe_query(
        "SELECT data, cotacao_venda FROM v_bcb_cotacoes ORDER BY data",
        context="BCB PTAX",
    )

    if ptax_data:
        import plotly.graph_objects as go  # noqa: E402

        dates = [r["data"] for r in ptax_data]
        rates = [r["cotacao_venda"] for r in ptax_data]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=rates,
            mode="lines",
            name="USD/BRL (venda)",
            line={"color": "#D4A847", "width": 2},
        ))
        fig.update_layout(
            title="Cotação USD/BRL — BCB PTAX",
            xaxis_title="Data",
            yaxis_title="R$/USD",
            template="plotly_dark",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = ptax_data[-1]
        st.metric(
            "Última cotação (venda)",
            f"R$ {latest['cotacao_venda']:.4f}",
        )
        st.caption(f"Data: {latest['data']}")
    else:
        st.info(
            "Dados de câmbio não disponíveis. "
            "Execute `licenciaminer collect bcb` para coletar."
        )

    # Cotações de commodities (CSV manual)
    st.markdown(section_header("Cotações de Commodities"), unsafe_allow_html=True)

    ref_dir = Path(_project_root) / "data" / "reference"
    commodity_csv = ref_dir / "commodity_prices.csv"

    if commodity_csv.exists():
        with open(commodity_csv, encoding="utf-8") as f:
            commodities = list(csv.DictReader(f))

        if commodities:
            # Agrupar por mineral
            minerals = sorted({r["mineral"] for r in commodities})
            for mineral in minerals:
                rows = [r for r in commodities if r["mineral"] == mineral]
                last = rows[-1]
                unit = last.get("unidade", "USD")
                st.metric(
                    mineral,
                    f"{float(last['preco_usd']):,.2f} {unit}",
                    help=f"Fonte: {last.get('fonte', '?')} — {last['data']}",
                )

            st.caption(
                "Cotações atualizadas manualmente via CSV. "
                "Fontes: Investing.com, IndexMundi, TradingEconomics."
            )
    else:
        st.info("Arquivo `data/reference/commodity_prices.csv` não encontrado.")

    # Upload de atualização
    with st.expander("Atualizar cotações (upload CSV)"):
        st.markdown(
            "Formato: `data,mineral,preco_usd,unidade,fonte`\n\n"
            "Faça upload de um CSV com cotações atualizadas. "
            "O arquivo substitui o existente."
        )
        uploaded = st.file_uploader(
            "CSV de cotações",
            type=["csv"],
            key="commodity_upload",
        )
        if uploaded is not None:
            content = uploaded.read().decode("utf-8")
            lines = content.strip().split("\n")
            if len(lines) > 1 and "mineral" in lines[0]:
                commodity_csv.write_text(content, encoding="utf-8")
                st.success(f"Atualizado com {len(lines) - 1} registros.")
                st.rerun()
            else:
                st.error("CSV inválido — verifique o cabeçalho.")


# ═══════════════════════════════════════════════════════════════
# Tab 2: Comércio Exterior
# ═══════════════════════════════════════════════════════════════
with tab_comex:
    st.markdown(section_header("Comércio Exterior Mineral"), unsafe_allow_html=True)
    st.markdown(source_attribution(
        "Fonte: Comex Stat / MDIC — Capítulo 26 NCM (minérios e concentrados)"
    ), unsafe_allow_html=True)

    comex_data = safe_query(
        "SELECT * FROM v_comex_mineracao",
        context="Comex Stat",
    )

    if comex_data:
        import pandas as pd  # noqa: E402
        import plotly.express as px  # noqa: E402

        df = pd.DataFrame(comex_data)

        # Resumo por fluxo
        col1, col2 = st.columns(2)
        if "fluxo" in df.columns and "valor_fob_usd" in df.columns:
            for col, fluxo in zip([col1, col2], ["Exportação", "Importação"], strict=False):
                subset = df[df["fluxo"] == fluxo]
                total = subset["valor_fob_usd"].sum()
                with col:
                    st.metric(
                        f"Total {fluxo} (FOB)",
                        f"US$ {fmt_br(total / 1e9, 2)} bi",
                    )

            # Série temporal por ano
            if "ano" in df.columns:
                yearly = (
                    df.groupby(["ano", "fluxo"])["valor_fob_usd"]
                    .sum()
                    .reset_index()
                )
                yearly["valor_bi"] = yearly["valor_fob_usd"] / 1e9
                fig = px.bar(
                    yearly, x="ano", y="valor_bi", color="fluxo",
                    barmode="group",
                    title="Comércio Exterior Mineral — Valor FOB (US$ bi)",
                    labels={
                        "ano": "Ano",
                        "valor_bi": "US$ bilhões",
                        "fluxo": "Fluxo",
                    },
                    template="plotly_dark",
                    color_discrete_map={
                        "Exportação": "#5BA77D",
                        "Importação": "#C45B52",
                    },
                )
                st.plotly_chart(fig, use_container_width=True)

            # Por UF
            if "uf" in df.columns:
                st.markdown("**Por UF (exportação):**")
                exp_uf = (
                    df[df["fluxo"] == "Exportação"]
                    .groupby("uf")["valor_fob_usd"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index()
                )
                exp_uf["valor_mi"] = exp_uf["valor_fob_usd"] / 1e6
                fig_uf = px.bar(
                    exp_uf, x="uf", y="valor_mi",
                    title="Top 10 UFs — Exportação Mineral (US$ mi)",
                    labels={"uf": "UF", "valor_mi": "US$ milhões"},
                    template="plotly_dark",
                    color_discrete_sequence=["#D4A847"],
                )
                st.plotly_chart(fig_uf, use_container_width=True)
        else:
            st.dataframe(df.head(100))
    else:
        st.info(
            "Dados de comércio exterior não disponíveis. "
            "Execute `licenciaminer collect comex` para coletar."
        )


# ═══════════════════════════════════════════════════════════════
# Tab 3: Produção & Arrecadação (dados existentes)
# ═══════════════════════════════════════════════════════════════
with tab_producao:
    st.markdown(section_header("CFEM — Arrecadação"), unsafe_allow_html=True)
    st.markdown(source_attribution(
        "Fonte: ANM Dados Abertos — CFEM (royalties minerários)"
    ), unsafe_allow_html=True)

    cfem_total = safe_query(
        "SELECT COUNT(*) AS n FROM v_cfem",
        context="CFEM total",
        fallback=[{"n": 0}],
    )
    n_cfem = cfem_total[0]["n"] if cfem_total else 0

    if n_cfem > 0:
        import plotly.express as px  # noqa: E402

        st.metric("Registros CFEM", fmt_br(n_cfem))

        # Top municípios por arrecadação
        top_muni = safe_query(
            """
            SELECT "Município" AS municipio,
                   SUM(TRY_CAST(
                       REPLACE(REPLACE("ValorRecolhido", '.', ''), ',', '.')
                       AS DOUBLE
                   )) AS total
            FROM v_cfem
            WHERE "Município" IS NOT NULL
            GROUP BY "Município"
            ORDER BY total DESC
            LIMIT 15
            """,
            context="CFEM top municípios",
        )
        if top_muni:
            import pandas as pd  # noqa: E402

            df_muni = pd.DataFrame(top_muni)
            df_muni["total_mi"] = df_muni["total"] / 1e6
            fig = px.bar(
                df_muni, x="municipio", y="total_mi",
                title="Top 15 Municípios — Arrecadação CFEM (R$ mi)",
                labels={"municipio": "Município", "total_mi": "R$ milhões"},
                template="plotly_dark",
                color_discrete_sequence=["#D4A847"],
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Top substâncias
        top_sub = safe_query(
            """
            SELECT "Substância" AS substancia,
                   SUM(TRY_CAST(
                       REPLACE(REPLACE("ValorRecolhido", '.', ''), ',', '.')
                       AS DOUBLE
                   )) AS total
            FROM v_cfem
            WHERE "Substância" IS NOT NULL
            GROUP BY "Substância"
            ORDER BY total DESC
            LIMIT 10
            """,
            context="CFEM top substâncias",
        )
        if top_sub:
            import pandas as pd  # noqa: E402

            df_sub = pd.DataFrame(top_sub)
            df_sub["total_mi"] = df_sub["total"] / 1e6
            fig_sub = px.bar(
                df_sub, x="substancia", y="total_mi",
                title="Top 10 Substâncias — Arrecadação CFEM (R$ mi)",
                labels={"substancia": "Substância", "total_mi": "R$ milhões"},
                template="plotly_dark",
                color_discrete_sequence=["#8BB85C"],
            )
            st.plotly_chart(fig_sub, use_container_width=True)
    else:
        st.info(
            "Dados CFEM não disponíveis. "
            "Execute `licenciaminer collect cfem` para coletar."
        )

    # RAL
    st.markdown(section_header("RAL — Produção Mineral"), unsafe_allow_html=True)
    st.markdown(source_attribution(
        "Fonte: ANM Dados Abertos — Relatório Anual de Lavra"
    ), unsafe_allow_html=True)

    ral_total = safe_query(
        "SELECT COUNT(*) AS n FROM v_ral",
        context="RAL total",
        fallback=[{"n": 0}],
    )
    n_ral = ral_total[0]["n"] if ral_total else 0

    if n_ral > 0:
        st.metric("Registros RAL", fmt_br(n_ral))

        top_ral = safe_query(
            """
            SELECT "Substância Mineral" AS substancia, COUNT(*) AS n
            FROM v_ral
            WHERE "Substância Mineral" IS NOT NULL
            GROUP BY "Substância Mineral"
            ORDER BY n DESC
            LIMIT 10
            """,
            context="RAL top substâncias",
        )
        if top_ral:
            import pandas as pd  # noqa: E402

            df_ral = pd.DataFrame(top_ral)
            fig_ral = px.bar(
                df_ral, x="substancia", y="n",
                title="Top 10 Substâncias — Registros RAL",
                labels={"substancia": "Substância", "n": "Registros"},
                template="plotly_dark",
                color_discrete_sequence=["#D4A847"],
            )
            st.plotly_chart(fig_ral, use_container_width=True)
    else:
        st.info(
            "Dados RAL não disponíveis. "
            "Execute `licenciaminer collect ral` para coletar."
        )


# ═══════════════════════════════════════════════════════════════
# Tab 4: Gestão e Território (dados existentes)
# ═══════════════════════════════════════════════════════════════
with tab_territorio:
    st.markdown(
        section_header("Processos Minerários"),
        unsafe_allow_html=True,
    )
    st.markdown(source_attribution(
        "Fonte: ANM SIGMINE — Processos minerários por fase"
    ), unsafe_allow_html=True)

    anm_total = safe_query(
        "SELECT COUNT(*) AS n FROM v_anm",
        context="ANM total",
        fallback=[{"n": 0}],
    )
    n_anm = anm_total[0]["n"] if anm_total else 0

    if n_anm > 0:
        import plotly.express as px  # noqa: E402

        st.metric("Processos ANM", fmt_br(n_anm))

        # Por fase
        by_fase = safe_query(
            """
            SELECT FASE AS fase, COUNT(*) AS n
            FROM v_anm
            WHERE FASE IS NOT NULL
            GROUP BY FASE
            ORDER BY n DESC
            """,
            context="ANM por fase",
        )
        if by_fase:
            import pandas as pd  # noqa: E402

            df_fase = pd.DataFrame(by_fase)
            fig_fase = px.bar(
                df_fase, x="fase", y="n",
                title="Processos Minerários por Fase",
                labels={"fase": "Fase", "n": "Processos"},
                template="plotly_dark",
                color_discrete_sequence=["#D4A847"],
            )
            fig_fase.update_xaxes(tickangle=45)
            st.plotly_chart(fig_fase, use_container_width=True)

        # Por substância
        by_sub = safe_query(
            """
            SELECT SUBS AS subs, COUNT(*) AS n
            FROM v_anm
            WHERE SUBS IS NOT NULL
            GROUP BY SUBS
            ORDER BY n DESC
            LIMIT 15
            """,
            context="ANM por substância",
        )
        if by_sub:
            import pandas as pd  # noqa: E402

            df_sub = pd.DataFrame(by_sub)
            fig_sub = px.bar(
                df_sub, x="subs", y="n",
                title="Top 15 Substâncias — Processos Minerários",
                labels={"subs": "Substância", "n": "Processos"},
                template="plotly_dark",
                color_discrete_sequence=["#8BB85C"],
            )
            fig_sub.update_xaxes(tickangle=45)
            st.plotly_chart(fig_sub, use_container_width=True)
    else:
        st.info(
            "Dados ANM não disponíveis. "
            "Execute `licenciaminer collect anm` para coletar."
        )
