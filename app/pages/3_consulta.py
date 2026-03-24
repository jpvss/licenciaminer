"""Tab 3: Consulta — Intelligence dossier by project params or CNPJ."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.data_loader import run_query, run_query_df  # noqa: E402
from app.styles.theme import (  # noqa: E402
    case_card_html,
    decision_badge,
    donut_svg,
    hero_html,
    inject_theme,
    insight_card,
    section_header,
    source_attribution,
)
from licenciaminer.database.queries import (  # noqa: E402
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    query_approval_stats,
    query_similar_cases,
)

inject_theme(st)


def _render_company_profile(cnpj: str) -> None:
    """Renderiza perfil completo de uma empresa por CNPJ como dossier."""
    try:
        profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
    except Exception:
        profile = []

    if not profile:
        st.info(f"CNPJ {cnpj} não encontrado nas decisões de mineração em MG.")
        return

    p = profile[0]
    razao = p.get("razao_social", cnpj)
    cnae = p.get("cnae_fiscal", "—")
    cnae_desc = p.get("cnae_descricao", "")
    porte = p.get("porte", "—")
    abertura = p.get("data_abertura", "—")
    situacao = p.get("situacao", "—")
    taxa = p.get("taxa_aprovacao", 0)
    total_dec = p.get("total_decisoes", 0)

    # Dossier header
    st.markdown(f"""
    <div class="geo-dossier">
        <div class="dossier-header">
            <p class="dossier-name">{razao}</p>
            <span class="dossier-cnae">{cnae} {cnae_desc}</span>
        </div>
        <div class="geo-kpi-row">
            <div class="geo-kpi">
                <p class="kpi-value">{porte}</p>
                <p class="kpi-label">Porte</p>
            </div>
            <div class="geo-kpi">
                <p class="kpi-value">{abertura}</p>
                <p class="kpi-label">Abertura</p>
            </div>
            <div class="geo-kpi">
                <p class="kpi-value">{taxa}%</p>
                <p class="kpi-label">Aprovação (N={total_dec})</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        source_attribution("Receita Federal via BrasilAPI + SEMAD MG"),
        unsafe_allow_html=True,
    )

    # Infrações IBAMA
    st.markdown(section_header("Infrações IBAMA"), unsafe_allow_html=True)
    try:
        inf = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
        if inf and inf[0]["total_infracoes"] > 0:
            total_inf = inf[0]["total_infracoes"]
            anos_inf = inf[0]["anos_com_infracao"]
            tone = "negative" if total_inf >= 3 else "neutral"
            st.markdown(
                insight_card(
                    "Total de Infrações",
                    f"{total_inf} infrações",
                    f"Distribuídas em {anos_inf} anos",
                    tone,
                ),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                insight_card(
                    "Infrações IBAMA",
                    "Nenhuma",
                    "Sem registros de infrações ambientais",
                    "positive",
                ),
                unsafe_allow_html=True,
            )
    except Exception:
        st.caption("Dados de infrações não disponíveis")
    st.markdown(
        source_attribution("IBAMA Dados Abertos"),
        unsafe_allow_html=True,
    )

    # CFEM
    st.markdown(section_header("Pagamentos CFEM"), unsafe_allow_html=True)
    try:
        cfem = run_query(QUERY_CNPJ_CFEM, [cnpj])
        if cfem and cfem[0]["meses_pagamento"] > 0:
            total_pago = cfem[0]["total_pago"]
            meses = cfem[0]["meses_pagamento"]
            if total_pago:
                st.markdown(
                    insight_card(
                        "Royalties Minerários",
                        f"R$ {total_pago:,.2f}",
                        f"{meses} meses de pagamento (2022-2026)",
                        "neutral",
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    insight_card(
                        "CFEM",
                        f"{meses} meses",
                        "Pagamentos registrados",
                        "neutral",
                    ),
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Não encontrado nos registros CFEM (2022-2026)")
    except Exception:
        st.caption("Dados CFEM não disponíveis")
    st.markdown(
        source_attribution("ANM Arrecadação"),
        unsafe_allow_html=True,
    )

    # Decision history
    st.markdown(section_header("Histórico de Decisões"), unsafe_allow_html=True)
    try:
        decisions = run_query_df(
            "SELECT ano, decisao, atividade, classe, modalidade, detail_id "
            "FROM v_mg_semad "
            "WHERE cnpj_cpf = ? AND atividade LIKE 'A-0%' "
            "ORDER BY data_de_publicacao DESC",
            [cnpj],
        )
        if not decisions.empty:
            st.dataframe(decisions, width="stretch", hide_index=True)
    except Exception as e:
        st.warning(f"Erro ao carregar decisões: {e}")
    st.markdown(
        source_attribution("SEMAD MG"),
        unsafe_allow_html=True,
    )


# ── Page Layout ──

st.markdown(
    hero_html(
        "Consulta de Inteligência",
        "Briefing com estatísticas, casos similares e perfil da empresa",
    ),
    unsafe_allow_html=True,
)

# ── Search Mode via Tabs ──
tab_projeto, tab_empresa = st.tabs(["Por Projeto", "Por Empresa (CNPJ)"])

with tab_projeto:
    col1, col2, col3 = st.columns(3)

    with col1:
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
        classe = st.selectbox(
            "Classe", [None, 1, 2, 3, 4, 5, 6], index=0,
            format_func=lambda x: "Todas" if x is None else str(x),
        )

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

    cnpj_input = st.text_input(
        "CNPJ (opcional)", placeholder="00.000.000/0000-00",
        key="proj_cnpj",
    )
    cnpj_clean = (
        "".join(c for c in cnpj_input if c.isdigit()) if cnpj_input else None
    )

    search_clicked = st.button("Consultar", type="primary", key="proj_search")

    if search_clicked and atividade:
        st.divider()

        # ── 1. Contexto Estatístico ──
        st.markdown(
            section_header("Contexto Estatístico"),
            unsafe_allow_html=True,
        )

        stats_query = query_approval_stats(atividade, classe, regional)
        stats = run_query(stats_query)

        if stats and stats[0]["total"] > 0:
            s = stats[0]
            taxa = s["taxa_aprovacao"]
            total = s["total"]
            deferidos = s["deferidos"]
            indeferidos = s["indeferidos"]

            # Dashboard layout: donut + metrics
            donut_col, metrics_col = st.columns([1, 2])

            with donut_col:
                # Donut color based on rate
                donut_color = (
                    "var(--malachite)" if taxa >= 70
                    else "var(--amber)" if taxa >= 50
                    else "var(--oxide)"
                )
                st.markdown(
                    donut_svg(taxa, size=110, stroke=10, color=donut_color),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<p style="text-align:center; font-family:var(--font-body); '
                    'font-size:0.75rem; color:var(--slate-dim); '
                    'text-transform:uppercase; letter-spacing:0.08em;">'
                    "Taxa de Aprovação</p>",
                    unsafe_allow_html=True,
                )

            with metrics_col:
                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Decisões Analisadas", f"{total:,}")
                with m2:
                    st.metric("Deferidos / Indeferidos", f"{deferidos} / {indeferidos}")

                # Comparison bar
                overall = run_query(query_approval_stats())
                if overall:
                    avg = overall[0]["taxa_aprovacao"]
                    diff = taxa - avg
                    direction = "acima" if diff > 0 else "abaixo"

                    # Visual comparison bar
                    bar_color = (
                        "var(--malachite)" if diff > 0
                        else "var(--oxide)"
                    )
                    marker_pos = min(avg, 100)

                    st.markdown(f"""
                    <div style="margin-top: 0.5rem;">
                        <div style="display:flex; justify-content:space-between;
                                    font-size:0.7rem; color:var(--slate-dim);
                                    font-family:var(--font-mono); margin-bottom:4px;">
                            <span>0%</span>
                            <span>{abs(diff):.1f}pp {direction} da média ({avg:.0f}%)</span>
                            <span>100%</span>
                        </div>
                        <div class="geo-compare-bar">
                            <div class="geo-compare-fill"
                                 style="width:{min(taxa, 100)}%; background:{bar_color};">
                            </div>
                            <div class="geo-compare-marker"
                                 style="left:{marker_pos}%;">
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            if total < 10:
                st.warning(
                    "Poucos casos similares (N < 10) — interpretar com cautela"
                )

            with st.expander("Como calculamos"):
                st.code(stats_query, language="sql")

            st.markdown(
                source_attribution("SEMAD MG"),
                unsafe_allow_html=True,
            )
        else:
            st.info("Nenhum registro encontrado para esses parâmetros.")

        # ── 2. Casos Similares ──
        st.markdown(
            section_header("Casos Similares"),
            unsafe_allow_html=True,
        )

        cases_query = query_similar_cases(atividade, classe, regional, limit=5)
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
            # Summary row
            n_def = len(cases_df[cases_df["decisao"] == "deferido"])
            n_ind = len(cases_df[cases_df["decisao"] == "indeferido"])
            n_arq = len(cases_df[cases_df["decisao"] == "arquivamento"])
            parts = []
            if n_def:
                parts.append(f"{n_def} deferido(s)")
            if n_ind:
                parts.append(f"{n_ind} indeferido(s)")
            if n_arq:
                parts.append(f"{n_arq} arquivamento(s)")
            st.markdown(
                source_attribution(
                    f"{len(cases_df)} casos mais recentes: {' · '.join(parts)}"
                ),
                unsafe_allow_html=True,
            )

            for idx, (_, case) in enumerate(cases_df.iterrows()):
                decisao = case["decisao"]
                icon_map = {
                    "deferido": "✅",
                    "indeferido": "❌",
                    "arquivamento": "📁",
                }
                badge_map = {
                    "deferido": "badge-deferido",
                    "indeferido": "badge-indeferido",
                    "arquivamento": "badge-arquivamento",
                }
                icon = icon_map.get(decisao, "❓")
                badge_cls = badge_map.get(decisao, "badge-arquivamento")

                empr = str(case["empreendimento"])[:60]
                meta = (
                    f"{case['municipio']} · {case['atividade']} · "
                    f"Classe {case['classe']} · {case['ano']}"
                )

                st.markdown(
                    case_card_html(icon, empr, meta, decisao, badge_cls),
                    unsafe_allow_html=True,
                )

                # Expandable detail
                with st.expander(f"Detalhes — {empr[:40]}"):
                    portal_url = (
                        "https://sistemas.meioambiente.mg.gov.br/"
                        f"licenciamento/site/view-externo?id={case['detail_id']}"
                    )
                    st.markdown(f"[Ver no portal SEMAD]({portal_url})")

                    if case.get("texto_chars", 0) > 10:
                        texto_row = run_query(
                            f"SELECT texto_documentos FROM v_mg_semad "
                            f"WHERE detail_id = '{case['detail_id']}'"
                        )
                        if texto_row:
                            texto = str(
                                texto_row[0].get("texto_documentos", "")
                            )
                            if len(texto) > 10:
                                st.text_area(
                                    "Texto do Parecer",
                                    texto[:5000],
                                    height=250,
                                    disabled=True,
                                )
                                if len(texto) > 5000:
                                    st.caption(
                                        f"Mostrando 5.000 de {len(texto):,} chars"
                                    )

            st.markdown(
                source_attribution(
                    "SEMAD MG — decisões mais recentes para esses parâmetros"
                ),
                unsafe_allow_html=True,
            )
        else:
            st.info("Nenhum caso similar encontrado. Tente relaxar os filtros.")

        # ── 3. Perfil da Empresa ──
        if cnpj_clean and len(cnpj_clean) == 14:
            st.markdown(
                section_header("Perfil da Empresa"),
                unsafe_allow_html=True,
            )
            _render_company_profile(cnpj_clean)

with tab_empresa:
    cnpj_input_emp = st.text_input(
        "CNPJ", placeholder="00.000.000/0000-00", key="emp_cnpj"
    )
    cnpj_clean_emp = (
        "".join(c for c in cnpj_input_emp if c.isdigit())
        if cnpj_input_emp
        else None
    )

    search_emp = st.button("Consultar", type="primary", key="emp_search")

    if search_emp and cnpj_clean_emp and len(cnpj_clean_emp) == 14:
        st.divider()
        st.markdown(
            section_header("Perfil da Empresa"),
            unsafe_allow_html=True,
        )
        _render_company_profile(cnpj_clean_emp)
    elif search_emp:
        st.warning("CNPJ deve ter 14 dígitos.")
