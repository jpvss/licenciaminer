"""Tab 3: Consulta — Intelligence query by project params or CNPJ."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from app.components.data_loader import run_query, run_query_df  # noqa: E402
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    query_approval_stats,
    query_similar_cases,
)


def _render_company_profile(cnpj: str) -> None:
    """Renderiza perfil completo de uma empresa por CNPJ."""
    try:
        profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
    except Exception:
        profile = []

    if profile:
        p = profile[0]
        st.markdown(f"### {p.get('razao_social', cnpj)}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**CNAE**: {p.get('cnae_fiscal', '—')} {p.get('cnae_descricao', '')}")
            st.markdown(f"**Porte**: {p.get('porte', '—')}")
        with col2:
            st.markdown(f"**Desde**: {p.get('data_abertura', '—')}")
            st.markdown(f"**Situação**: {p.get('situacao', '—')}")
        with col3:
            st.metric("Taxa Aprovação", f"{p.get('taxa_aprovacao', 0)}%")
            st.caption(f"N={p.get('total_decisoes', 0)} decisões")

        st.caption("Fonte: Receita Federal via BrasilAPI + SEMAD MG")
    else:
        st.info(f"CNPJ {cnpj} não encontrado nas decisões de mineração em MG.")
        return

    st.markdown("---")
    st.markdown("**Infrações IBAMA**")
    try:
        inf = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
        if inf and inf[0]["total_infracoes"] > 0:
            st.markdown(
                f"{inf[0]['total_infracoes']} infrações em "
                f"{inf[0]['anos_com_infracao']} anos"
            )
        else:
            st.markdown("Nenhuma infração registrada")
    except Exception:
        st.markdown("Dados de infrações não disponíveis")
    st.caption("Fonte: IBAMA Dados Abertos")

    st.markdown("**Pagamentos CFEM**")
    try:
        cfem = run_query(QUERY_CNPJ_CFEM, [cnpj])
        if cfem and cfem[0]["meses_pagamento"] > 0:
            total = cfem[0]["total_pago"]
            meses = cfem[0]["meses_pagamento"]
            if total:
                st.markdown(f"{meses} meses | Total: R$ {total:,.2f}")
            else:
                st.markdown(f"{meses} meses de pagamento")
        else:
            st.markdown("Não encontrado nos registros CFEM (2022-2026)")
    except Exception:
        st.markdown("Dados CFEM não disponíveis")
    st.caption("Fonte: ANM Arrecadação")

    st.markdown("**Histórico de Decisões**")
    try:
        decisions = run_query_df(
            "SELECT ano, decisao, atividade, classe, modalidade, detail_id "
            "FROM v_mg_semad "
            f"WHERE cnpj_cpf = '{cnpj}' AND atividade LIKE 'A-0%' "
            "ORDER BY data_de_publicacao DESC"
        )
        if not decisions.empty:
            st.dataframe(decisions, use_container_width=True, hide_index=True)
    except Exception:
        pass
    st.caption("Fonte: SEMAD MG")


# ── Page Layout ──

st.title("Consulta de Inteligência")
st.markdown(
    "Busque por parâmetros de projeto ou por CNPJ para obter um briefing "
    "com estatísticas, casos similares e perfil da empresa."
)
st.divider()

# ── Search Mode ──
mode = st.radio(
    "Tipo de consulta",
    ["Por Projeto", "Por Empresa (CNPJ)"],
    horizontal=True,
)

if mode == "Por Projeto":
    col1, col2, col3 = st.columns(3)

    with col1:
        # Get distinct activity prefixes
        try:
            atividades = run_query("""
                SELECT DISTINCT SUBSTRING(atividade, 1, 7) AS prefix
                FROM v_mg_semad
                WHERE atividade LIKE 'A-0%'
                ORDER BY prefix
            """)
            ativ_options = [a["prefix"] for a in atividades]
        except Exception:
            ativ_options = []

        atividade = st.selectbox("Código de Atividade", ativ_options, index=0)

    with col2:
        classe = st.selectbox("Classe", [None, 1, 2, 3, 4, 5, 6], index=0,
                              format_func=lambda x: "Todas" if x is None else str(x))

    with col3:
        try:
            regionais = run_query("""
                SELECT DISTINCT regional FROM v_mg_semad
                WHERE atividade LIKE 'A-0%' ORDER BY regional
            """)
            reg_options = [None] + [r["regional"] for r in regionais]
        except Exception:
            reg_options = [None]

        regional = st.selectbox(
            "Regional",
            reg_options,
            index=0,
            format_func=lambda x: "Todas" if x is None else x.replace(
                "Unidade Regional de Regularização Ambiental ", ""
            ),
        )

    cnpj_input = st.text_input("CNPJ (opcional)", placeholder="00.000.000/0000-00")
    cnpj_clean = "".join(c for c in cnpj_input if c.isdigit()) if cnpj_input else None

    search_clicked = st.button("Consultar", type="primary")

    if search_clicked and atividade:
        st.divider()

        # ── 1. Contexto Estatístico ──
        st.subheader("📊 Contexto Estatístico")

        stats_query = query_approval_stats(atividade, classe, regional)
        stats = run_query(stats_query)

        if stats and stats[0]["total"] > 0:
            s = stats[0]
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Taxa de Aprovação", f"{s['taxa_aprovacao']}%")
            with col_b:
                st.metric("Decisões Analisadas", f"{s['total']:,}")
            with col_c:
                st.metric("Deferidos / Indeferidos", f"{s['deferidos']} / {s['indeferidos']}")

            if s["total"] < 10:
                st.warning("⚠ Poucos casos similares (N < 10) — use com cautela")

            # Compare to overall mining average
            overall = run_query(query_approval_stats())
            if overall:
                avg = overall[0]["taxa_aprovacao"]
                diff = s["taxa_aprovacao"] - avg
                direction = "acima" if diff > 0 else "abaixo"
                st.caption(
                    f"Média geral mineração: {avg}% — "
                    f"esta combinação está {abs(diff):.1f}pp {direction}"
                )

            with st.expander("Como calculamos"):
                st.code(stats_query, language="sql")
            st.caption("Fonte: SEMAD MG")
        else:
            st.info("Nenhum registro encontrado para esses parâmetros.")

        # ── 2. Casos Similares ──
        st.subheader("📋 Casos Similares")

        cases_query = query_similar_cases(atividade, classe, regional, limit=5)
        # Need to execute with params for LIKE
        try:
            cases_df = run_query_df(
                f"""
                SELECT
                    detail_id, empreendimento, municipio, cnpj_cpf,
                    atividade, classe, regional, modalidade,
                    decisao, ano, data_de_publicacao,
                    LENGTH(CAST(texto_documentos AS VARCHAR)) AS texto_chars
                FROM v_mg_semad
                WHERE atividade LIKE '{atividade}%'
                  {"AND classe = " + str(classe) if classe else ""}
                  {"AND regional = '" + regional + "'" if regional else ""}
                  AND atividade LIKE 'A-0%'
                ORDER BY data_de_publicacao DESC
                LIMIT 5
                """
            )
        except Exception:
            cases_df = None

        if cases_df is not None and not cases_df.empty:
            for _, case in cases_df.iterrows():
                icon = {"deferido": "✅", "indeferido": "❌", "arquivamento": "📁"}.get(
                    case["decisao"], "❓"
                )
                with st.expander(
                    f"{icon} {case['empreendimento'][:50]} — "
                    f"{case['decisao']} ({case['ano']})"
                ):
                    st.markdown(f"**Município**: {case['municipio']}")
                    st.markdown(f"**Atividade**: {case['atividade']}")
                    st.markdown(
                        f"**Classe**: {case['classe']} | "
                        f"**Modalidade**: {case.get('modalidade', '')}"
                    )

                    portal_url = (
                        "https://sistemas.meioambiente.mg.gov.br/"
                        f"licenciamento/site/view-externo?id={case['detail_id']}"
                    )
                    st.markdown(f"🔗 [Ver no portal SEMAD]({portal_url})")

                    if case.get("texto_chars", 0) > 10:
                        # Load full text for this case
                        texto_row = run_query(
                            f"SELECT texto_documentos FROM v_mg_semad "
                            f"WHERE detail_id = '{case['detail_id']}'"
                        )
                        if texto_row:
                            texto = str(texto_row[0].get("texto_documentos", ""))
                            if len(texto) > 10:
                                st.text_area(
                                    "Texto do Parecer",
                                    texto[:5000],
                                    height=300,
                                    disabled=True,
                                )
                                if len(texto) > 5000:
                                    st.caption(f"Mostrando 5.000 de {len(texto):,} chars")

            st.caption("Fonte: SEMAD MG — decisões mais recentes para esses parâmetros")
        else:
            st.info("Nenhum caso similar encontrado. Tente relaxar os filtros.")

        # ── 3. Perfil da Empresa (if CNPJ provided) ──
        if cnpj_clean and len(cnpj_clean) == 14:
            st.subheader("🏢 Perfil da Empresa")
            _render_company_profile(cnpj_clean)

elif mode == "Por Empresa (CNPJ)":
    cnpj_input = st.text_input("CNPJ", placeholder="00.000.000/0000-00")
    cnpj_clean = "".join(c for c in cnpj_input if c.isdigit()) if cnpj_input else None

    search_clicked = st.button("Consultar", type="primary")

    if search_clicked and cnpj_clean and len(cnpj_clean) == 14:
        st.divider()
        st.subheader("🏢 Perfil da Empresa")
        _render_company_profile(cnpj_clean)
    elif search_clicked:
        st.warning("CNPJ deve ter 14 dígitos.")
