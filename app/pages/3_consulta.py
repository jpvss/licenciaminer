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


def _render_report_button(cnpj: str) -> None:
    """Botão para gerar relatório PDF de inteligência ambiental."""
    st.markdown("")
    st.divider()
    st.markdown(
        section_header("Relatório de Inteligência Ambiental"),
        unsafe_allow_html=True,
    )
    st.caption(
        "Gere um relatório profissional em PDF com análise comparativa, "
        "infrações, títulos minerários e aviso legal completo."
    )

    # Use session_state to persist PDF across reruns
    state_key = f"report_pdf_{cnpj}"

    if st.button("Gerar Relatório PDF", type="primary", key=f"report_{cnpj}"):
        try:
            from app.components.report_data import collect_report_data
            from app.components.report_generator import generate_report

            with st.status("Gerando relatório...", expanded=True) as status:
                st.write("Coletando dados de 10 fontes oficiais...")
                report_data = collect_report_data(cnpj)

                st.write("Renderizando PDF com 8 seções...")
                pdf_bytes = generate_report(report_data)

                empresa = report_data.razao_social or cnpj
                filename = f"relatorio_{cnpj}_{report_data.generated_at:%Y%m%d}.pdf"

                status.update(
                    label=f"Relatório pronto — Risco: {report_data.risk_level}",
                    state="complete",
                    expanded=False,
                )

            # Persist in session state so download survives reruns
            st.session_state[state_key] = {
                "pdf": pdf_bytes,
                "filename": filename,
                "empresa": empresa,
                "risk": report_data.risk_level,
                "n_decisoes": len(report_data.decisoes),
            }
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")

    # Show download button if PDF was generated (persists across reruns)
    if state_key in st.session_state:
        r = st.session_state[state_key]
        st.download_button(
            f"Baixar Relatório — {r['empresa'][:40]}",
            r["pdf"],
            file_name=r["filename"],
            mime="application/pdf",
            type="primary",
        )
        st.success(
            f"Risco: **{r['risk']}** · "
            f"{r['n_decisoes']} decisões analisadas"
        )


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

    # Traduzir código de porte da Receita Federal
    _porte_labels = {
        "MEI": "Microempreendedor Individual (MEI)",
        "ME": "Microempresa (ME)",
        "EPP": "Pequeno Porte (EPP)",
        "DEMAIS": "Médio/Grande Porte",
    }
    porte_raw = p.get("porte", "—") or "—"
    porte = _porte_labels.get(porte_raw.strip().upper(), porte_raw)

    # Formatar data de abertura para DD/MM/YYYY
    abertura_raw = str(p.get("data_abertura", "—") or "—")
    if len(abertura_raw) >= 10 and "-" in abertura_raw:
        try:
            parts = abertura_raw[:10].split("-")
            abertura = f"{parts[2]}/{parts[1]}/{parts[0]}"
        except (IndexError, ValueError):
            abertura = abertura_raw
    else:
        abertura = abertura_raw
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

            # Detail table with actual infractions
            try:
                inf_detail = run_query_df(f"""
                    SELECT
                        DAT_HORA_AUTO_INFRACAO AS data,
                        TIPO_INFRACAO AS tipo,
                        MUNICIPIO AS municipio,
                        VAL_AUTO_INFRACAO AS valor,
                        DES_AUTO_INFRACAO AS descricao,
                        DES_STATUS_FORMULARIO AS status,
                        SIT_CANCELADO AS cancelado
                    FROM v_ibama_infracoes
                    WHERE REGEXP_REPLACE(CPF_CNPJ_INFRATOR, '[^0-9]', '', 'g') = ?
                      AND UF = 'MG'
                    ORDER BY DAT_HORA_AUTO_INFRACAO DESC
                """, [cnpj])

                if not inf_detail.empty:
                    # Format for display
                    inf_display = inf_detail.copy()
                    if "descricao" in inf_display.columns:
                        inf_display["descricao"] = inf_display["descricao"].apply(
                            lambda x: str(x)[:80] + "..." if x and len(str(x)) > 80 else x
                        )
                    if "cancelado" in inf_display.columns:
                        inf_display["status_display"] = inf_display.apply(
                            lambda r: "Cancelado" if r.get("cancelado") == "S"
                            else str(r.get("status", "—")),
                            axis=1,
                        )
                    with st.expander(f"Ver {len(inf_detail)} infrações detalhadas"):
                        st.dataframe(
                            inf_display[["data", "tipo", "municipio", "valor",
                                         "descricao", "status_display"]].rename(
                                columns={
                                    "data": "Data",
                                    "tipo": "Tipo",
                                    "municipio": "Município",
                                    "valor": "Valor (R$)",
                                    "descricao": "Descrição",
                                    "status_display": "Status",
                                }
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )
            except Exception:
                pass  # Detail is optional enhancement
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
                from app.components.data_loader import fmt_reais
                st.markdown(
                    insight_card(
                        "Royalties Minerários",
                        fmt_reais(total_pago),
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

            # CFEM yearly breakdown
            try:
                cfem_detail = run_query_df(f"""
                    SELECT
                        Ano AS ano,
                        "Substância" AS substancia,
                        COUNT(*) AS meses,
                        SUM(TRY_CAST(
                            REPLACE(REPLACE(ValorRecolhido, '.', ''), ',', '.') AS DOUBLE
                        )) AS total
                    FROM v_cfem
                    WHERE CPF_CNPJ = ?
                    GROUP BY Ano, "Substância"
                    ORDER BY Ano DESC, total DESC
                """, [cnpj])

                if not cfem_detail.empty:
                    from app.components.data_loader import fmt_reais as _fr
                    cfem_display = cfem_detail.copy()
                    cfem_display["total"] = cfem_display["total"].apply(_fr)
                    with st.expander(f"Detalhamento por ano e substância"):
                        st.dataframe(
                            cfem_display.rename(columns={
                                "ano": "Ano",
                                "substancia": "Substância",
                                "meses": "Meses",
                                "total": "Total (R$)",
                            }),
                            use_container_width=True,
                            hide_index=True,
                        )
            except Exception:
                pass
        else:
            st.caption("Não encontrado nos registros CFEM (2022-2026)")
    except Exception:
        st.caption("Dados CFEM não disponíveis")
    st.markdown(
        source_attribution("ANM Arrecadação"),
        unsafe_allow_html=True,
    )

    # Títulos Minerários ANM
    st.markdown(section_header("Títulos Minerários ANM"), unsafe_allow_html=True)
    try:
        from licenciaminer.database.queries import QUERY_CNPJ_ANM_TITULOS
        # Search by company name (ANM doesn't have CNPJ, only NOME)
        search_name = razao if razao and razao != cnpj else None
        if search_name:
            titulos = run_query_df(QUERY_CNPJ_ANM_TITULOS, [search_name])
            if not titulos.empty:
                st.markdown(
                    insight_card(
                        "Processos ANM",
                        str(len(titulos)),
                        f"títulos encontrados para {razao[:30]}",
                        "neutral",
                    ),
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    titulos.rename(columns={
                        "PROCESSO": "Processo",
                        "FASE": "Fase",
                        "SUBS": "Substância",
                        "AREA_HA": "Área (ha)",
                        "ANO": "Ano",
                    }),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.caption("Nenhum título ANM encontrado vinculado a esta empresa.")
        else:
            st.caption("Nome da empresa não disponível para busca de títulos ANM.")
    except Exception:
        st.caption("Dados ANM não disponíveis")
    st.markdown(
        source_attribution("ANM SIGMINE"),
        unsafe_allow_html=True,
    )

    # Decision history
    st.markdown(section_header("Histórico de Decisões"), unsafe_allow_html=True)
    try:
        decisions = run_query_df(
            "SELECT ano, decisao, atividade, classe, modalidade, municipio, detail_id "
            "FROM v_mg_semad "
            "WHERE cnpj_cpf = ? "
            "ORDER BY data_de_publicacao DESC",
            [cnpj],
        )
        if not decisions.empty:
            # Add portal link column
            decisions["portal"] = decisions["detail_id"].apply(
                lambda x: (
                    f"https://sistemas.meioambiente.mg.gov.br/"
                    f"licenciamento/site/view-externo?id={x}"
                )
            )
            st.dataframe(
                decisions,
                column_config={
                    "detail_id": None,  # hide internal ID
                    "ano": st.column_config.NumberColumn("Ano", format="%d"),
                    "classe": st.column_config.NumberColumn("Classe", format="%d"),
                    "portal": st.column_config.LinkColumn(
                        "Verificar", display_text="Abrir"
                    ),
                },
                use_container_width=True,
                hide_index=True,
            )
    except Exception as e:
        st.warning(f"Erro ao carregar decisões: {e}")
    st.markdown(
        source_attribution("SEMAD MG"),
        unsafe_allow_html=True,
    )

    # Other branches (filiais) of the same company
    cnpj_root = cnpj[:8]
    try:
        filiais = run_query(f"""
            SELECT cnpj_cpf, COUNT(*) AS n, MIN(empreendimento) AS emp
            FROM v_mg_semad
            WHERE cnpj_cpf LIKE '{cnpj_root}%'
              AND cnpj_cpf != ?
              AND LENGTH(cnpj_cpf) = 14
            GROUP BY cnpj_cpf
            ORDER BY n DESC
        """, [cnpj])

        if filiais:
            total_other = sum(f["n"] for f in filiais)
            st.markdown(
                section_header("Outras Filiais"),
                unsafe_allow_html=True,
            )
            st.caption(
                f"Encontradas {len(filiais)} outra(s) filial(is) do mesmo grupo "
                f"com {total_other} decisão(ões) adicional(is)."
            )
            for f in filiais:
                f_cnpj = f["cnpj_cpf"]
                f_formatted = (
                    f"{f_cnpj[:2]}.{f_cnpj[2:5]}.{f_cnpj[5:8]}/"
                    f"{f_cnpj[8:12]}-{f_cnpj[12:]}"
                )
                emp = str(f["emp"])[:60] if f.get("emp") else "—"
                st.markdown(
                    f'<div style="padding:0.5rem 0.8rem; margin-bottom:0.4rem; '
                    f'background:var(--stratum-2); border-radius:var(--radius-sm); '
                    f'border-left:3px solid var(--amber);">'
                    f'<span style="font-family:var(--font-mono); font-size:0.85rem; '
                    f'color:var(--quartz);">{f_formatted}</span>'
                    f'<span style="color:var(--slate-dim); font-size:0.8rem;"> · '
                    f'{f["n"]} decisão(ões) · {emp}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.caption(
                "Para ver o dossiê completo de uma filial, "
                "pesquise o CNPJ dela na aba 'Por Empresa'."
            )
    except Exception:
        pass  # Filiais lookup is optional


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
    st.caption(
        "Selecione atividade, classe e regional para ver estatísticas de aprovação "
        "e casos similares. Ideal para avaliar viabilidade de um novo projeto."
    )
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

        atividade = st.selectbox(
            "Código de Atividade", ativ_options, index=0,
            help="A-01: Pesquisa mineral · A-02: Lavra · A-03: Beneficiamento · "
                 "A-04: Pilha de estéril · A-05: Barragem · A-06: Transporte · A-07: Infraestrutura",
        )

    with col2:
        classe = st.selectbox(
            "Classe", [None, 1, 2, 3, 4, 5, 6], index=0,
            format_func=lambda x: "Todas" if x is None else str(x),
            help="Classificação de impacto ambiental conforme DN COPAM 217/2017. "
                 "Classe 1 = menor impacto, Classe 6 = maior impacto.",
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
            help="Regional da SEMAD responsável pela análise. "
                 "Cada regional tem taxas de aprovação diferentes.",
        )

    cnpj_input = st.text_input(
        "CNPJ (opcional)", placeholder="00.000.000/0000-00",
        key="proj_cnpj",
    )
    cnpj_clean = (
        "".join(c for c in cnpj_input if c.isdigit()) if cnpj_input else None
    )

    search_clicked = st.button("Consultar", type="primary", key="proj_search")

    # Persist search params so results survive reruns (e.g. report button click)
    if search_clicked and atividade:
        st.session_state["proj_search_active"] = True
        st.session_state["proj_atividade"] = atividade
        st.session_state["proj_classe"] = classe
        st.session_state["proj_regional"] = regional
        st.session_state["proj_cnpj_clean"] = cnpj_clean

    if st.session_state.get("proj_search_active") and atividade:
        st.divider()

        # ── 1. Contexto Estatístico ──
        st.markdown(
            section_header("Contexto Estatístico"),
            unsafe_allow_html=True,
        )

        stats_query, stats_params = query_approval_stats(atividade, classe, regional)
        stats = run_query(stats_query, stats_params)

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
                overall_q, overall_p = query_approval_stats()
                overall = run_query(overall_q, overall_p)
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

        cases_query, cases_params = query_similar_cases(atividade, classe, regional, limit=5)
        try:
            cases_df = run_query_df(cases_query, cases_params)
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
                            "SELECT texto_documentos FROM v_mg_semad "
                            "WHERE detail_id = ?",
                            [case["detail_id"]],
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
            _render_report_button(cnpj_clean)

with tab_empresa:
    st.caption(
        "Digite o CNPJ de uma empresa para ver o dossiê completo: "
        "infrações IBAMA, pagamentos CFEM, decisões de licenciamento e relatório PDF."
    )
    st.markdown(
        '<span style="font-size:0.78rem; color:var(--slate-dim);">'
        'Exemplos: <code>08.902.291/0001-15</code> (CSN Mineração) · '
        '<code>16.628.281/0003-23</code> (Samarco) · '
        '<code>19.095.249/0001-56</code> (Caldense)'
        '</span>',
        unsafe_allow_html=True,
    )
    cnpj_input_emp = st.text_input(
        "CNPJ", placeholder="00.000.000/0000-00", key="emp_cnpj"
    )
    cnpj_clean_emp = (
        "".join(c for c in cnpj_input_emp if c.isdigit())
        if cnpj_input_emp
        else None
    )

    search_emp = st.button("Consultar", type="primary", key="emp_search")

    # Persist searched CNPJ so profile survives reruns (e.g. report button click)
    if search_emp and cnpj_clean_emp and len(cnpj_clean_emp) == 14:
        st.session_state["active_cnpj_emp"] = cnpj_clean_emp
    elif search_emp:
        st.warning("CNPJ deve ter 14 dígitos.")

    active_cnpj = st.session_state.get("active_cnpj_emp")
    if active_cnpj:
        st.divider()
        st.markdown(
            section_header("Perfil da Empresa"),
            unsafe_allow_html=True,
        )
        _render_company_profile(active_cnpj)
        _render_report_button(active_cnpj)
