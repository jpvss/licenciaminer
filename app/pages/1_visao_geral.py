"""Tab 1: Visão Geral — Executive overview + data sources + methodology."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

# Add project root to path so we can import licenciaminer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from app.components.data_loader import (  # noqa: E402
    get_source_info,
    load_metadata,
    run_query,
    run_query_df,
)
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_MG_SUMMARY,
    QUERY_MINING_TREND,
)

st.title("⛏️ LicenciaMiner")
st.markdown("### Inteligência de Licenciamento Ambiental Minerário — Minas Gerais")
st.divider()

# ── Metric Cards ──
st.subheader("Resumo do Banco de Dados")

col1, col2, col3, col4 = st.columns(4)

# SEMAD decisions
try:
    semad_count = run_query("SELECT COUNT(*) AS n FROM v_mg_semad")[0]["n"]
    mining_count = run_query(
        "SELECT COUNT(*) AS n FROM v_mg_semad WHERE atividade LIKE 'A-0%'"
    )[0]["n"]
except Exception:
    semad_count = 0
    mining_count = 0

# ANM processes
try:
    anm_count = run_query("SELECT COUNT(*) AS n FROM v_anm")[0]["n"]
except Exception:
    anm_count = 0

# IBAMA infractions
try:
    inf_count = run_query(
        "SELECT COUNT(*) AS n FROM v_ibama_infracoes WHERE UF = 'MG'"
    )[0]["n"]
except Exception:
    inf_count = 0

# Approval rate
try:
    mg_summary = run_query(QUERY_MG_SUMMARY)
    approval_rate = mg_summary[0].get("taxa_aprovacao_geral", 0) if mg_summary else 0
except Exception:
    approval_rate = 0

metadata = load_metadata()

with col1:
    st.metric("Decisões SEMAD", f"{semad_count:,}")
    semad_date = metadata.get("mg_semad", {}).get("last_collected", "")[:10]
    st.caption(f"Fonte: SEMAD MG | {semad_date}")

with col2:
    st.metric("Processos ANM", f"{anm_count:,}")
    st.caption("Fonte: ANM SIGMINE")

with col3:
    st.metric("Infrações IBAMA (MG)", f"{inf_count:,}")
    st.caption("Fonte: IBAMA Dados Abertos")

with col4:
    st.metric("Taxa Aprovação Mineração", f"{approval_rate}%")
    st.caption(f"De {mining_count:,} decisões de mineração")

st.divider()

# ── Approval Trend Chart ──
st.subheader("Taxa de Aprovação — Mineração MG (por ano)")

try:
    trend_df = run_query_df(QUERY_MINING_TREND)
    if not trend_df.empty:
        fig = px.line(
            trend_df,
            x="ano",
            y="taxa_aprovacao",
            markers=True,
            labels={"ano": "Ano", "taxa_aprovacao": "Taxa de Aprovação (%)"},
            text="taxa_aprovacao",
        )
        fig.update_traces(textposition="top center", texttemplate="%{text:.1f}%")
        fig.update_layout(yaxis_range=[0, 100], height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            f"Fonte: SEMAD MG — {mining_count:,} decisões de mineração. "
            "Apenas anos com N ≥ 10."
        )
except Exception as e:
    st.error(f"Erro ao carregar tendência: {e}")

st.divider()

# ── Data Sources Table ──
st.subheader("Fontes de Dados")

sources = get_source_info()
for s in sources:
    url = s.pop("URL", "")
    if url and url.startswith("http"):
        s["Fonte"] = f"[{s['Fonte']}]({url})"

st.dataframe(
    sources,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Fonte": st.column_config.LinkColumn("Fonte", display_text=".*"),
    },
)

st.divider()

# ── Key Insights ──
st.subheader("Insights Chave")

try:
    # Approval by class
    class_stats = run_query("""
        SELECT classe,
            COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS taxa
        FROM v_mg_semad WHERE atividade LIKE 'A-0%' AND classe IS NOT NULL
        GROUP BY classe ORDER BY classe
    """)

    # Worst regional
    regional_stats = run_query("""
        SELECT
            REPLACE(regional, 'Unidade Regional de Regularização Ambiental ', '') AS reg,
            COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS taxa
        FROM v_mg_semad WHERE atividade LIKE 'A-0%'
        GROUP BY regional HAVING COUNT(*) >= 50
        ORDER BY taxa ASC LIMIT 1
    """)

    # Infractions insight
    inf_insight = run_query("""
        WITH ei AS (
            SELECT REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') AS cnpj,
                COUNT(*) AS n_inf
            FROM v_ibama_infracoes WHERE UF = 'MG'
            GROUP BY REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g')
            HAVING COUNT(*) >= 6
        )
        SELECT COUNT(*) AS n,
            ROUND(100.0 * SUM(CASE WHEN s.decisao = 'deferido' THEN 1 ELSE 0 END)
                / COUNT(*), 1) AS taxa
        FROM v_mg_semad s
        INNER JOIN ei ON s.cnpj_cpf = ei.cnpj
        WHERE s.atividade LIKE 'A-0%'
    """)

    col_a, col_b = st.columns(2)

    with col_a:
        if class_stats:
            worst_class = min(class_stats, key=lambda x: x["taxa"])
            st.markdown(
                f"**Classe {int(worst_class['classe'])}**: "
                f"{worst_class['taxa']}% aprovação "
                f"(N={worst_class['n']:,})"
            )
            st.caption("Fonte: SEMAD MG — classe com menor taxa de aprovação")

        if regional_stats:
            r = regional_stats[0]
            st.markdown(
                f"**{r['reg']}**: regional mais rigorosa, "
                f"{r['taxa']}% aprovação (N={r['n']:,})"
            )
            st.caption("Fonte: SEMAD MG — regional com menor taxa (N ≥ 50)")

    with col_b:
        if inf_insight and inf_insight[0]["n"] > 0:
            i = inf_insight[0]
            st.markdown(
                f"**Empresas com 6+ infrações IBAMA**: "
                f"{i['taxa']}% aprovação (N={i['n']:,})"
            )
            st.caption(
                "Fonte: SEMAD + IBAMA — empresas maiores navegam melhor o sistema"
            )

        st.markdown(
            f"**Mineração vs Geral**: {approval_rate}% vs ~78% "
            f"(mineração tem taxa significativamente menor)"
        )
        st.caption(f"Fonte: SEMAD MG — {mining_count:,} decisões de mineração")

except Exception as e:
    st.error(f"Erro nos insights: {e}")

st.divider()

# ── About Section ──
st.subheader("Sobre / Metodologia")

st.markdown("""
**LicenciaMiner** consolida dados públicos de licenciamento ambiental minerário
em Minas Gerais, cruzando informações de 10+ fontes oficiais.

**O que está incluído:**
- Decisões da SEMAD/MG (deferido, indeferido, arquivamento) desde 2016
- Pareceres técnicos completos (texto extraído dos PDFs oficiais)
- Processos minerários da ANM com geometria e sobreposições espaciais
- Infrações ambientais do IBAMA
- Pagamentos CFEM (royalties minerários)
- Dados cadastrais de empresas (Receita Federal)
- Reuniões da CMI/COPAM (câmara de atividades minerárias)

**O que NÃO está incluído:**
- Licenças federais indeferidas (IBAMA publica apenas emitidas)
- Licenças de outros estados (apenas MG)
- Processos ainda em análise (apenas decisões publicadas)
- Dados de cavernas CECAV (URL indisponível) e outorgas ANA (portal fora do ar)

**Metodologia**: Dados coletados via APIs públicas, scraping de portais oficiais,
e download de shapefiles. Texto dos pareceres extraído dos PDFs com PyMuPDF
(86.6% de cobertura — 13.4% são PDFs escaneados sem texto extraível).
Cruzamento entre fontes via CNPJ e sobreposição espacial.

**Atualização**: Pipeline incremental — decisões novas detectadas automaticamente.
Fontes rápidas atualizadas semanalmente, fontes lentas mensalmente.
""")
