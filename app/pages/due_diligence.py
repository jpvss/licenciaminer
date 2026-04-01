"""Due Diligence Ambiental — Summo Ambiental.

Objetivo: Verificação da aderência de processos de licenciamento ambiental
          à legislação aplicável, com checklist documental, testes de
          conformidade e enriquecimento com dados históricos.
Fontes de dados:
    - Referência: Inventário de 119 documentos (DN COPAM 217/2017 + legislação MG)
    - Referência: 1.934 testes de aderência mapeados
    - Enriquecimento: v_mg_semad (42.758 decisões), v_ibama_infracoes, v_cfem, v_copam
    - Input do usuário: Marcações de documentos e testes de conformidade
"""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
for p in [_project_root, _project_root + "/src"]:
    if p not in sys.path:
        sys.path.insert(0, p)

import streamlit as st  # noqa: E402

from app.components.dd_inventory import (  # noqa: E402
    LICENCA_DESC,
    LICENCA_TIPOS,
    filtrar_documentos,
    filtrar_requisitos,
    load_requisitos,
)
from app.components.dd_scoring import (  # noqa: E402
    AVALIACOES,
    CONFORMIDADE_ESCALA,
    DOC_STATUS,
    calcular_checklist_completude,
    calcular_conformidade,
    classificar_conformidade,
    gerar_recomendacoes,
)
from app.styles.theme import (  # noqa: E402
    conformity_gauge_html,
    hero_html,
    inject_theme,
    section_header,
    source_attribution,
    stepper_html,
)

inject_theme(st)

st.markdown(
    hero_html("Due Diligence Ambiental", "Summo Ambiental — Summo Quartile"),
    unsafe_allow_html=True,
)

st.markdown(source_attribution(
    "Metodologia: DN COPAM 217/2017 + legislação ambiental MG · "
    "119 documentos mapeados · 1.934 testes de aderência"
), unsafe_allow_html=True)

# ── Inicializar session_state ──
if "dd_step" not in st.session_state:
    st.session_state.dd_step = 1
if "dd_config" not in st.session_state:
    st.session_state.dd_config = {}
if "dd_doc_status" not in st.session_state:
    st.session_state.dd_doc_status = {}
if "dd_avaliacoes" not in st.session_state:
    st.session_state.dd_avaliacoes = {}

# ── Stepper ──
step_labels = ["Configuração", "Checklist", "Conformidade", "Relatório"]
st.markdown(
    stepper_html(step_labels, st.session_state.dd_step),
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
# STEP 1: Configuração do Projeto
# ═══════════════════════════════════════════════════════════
if st.session_state.dd_step == 1:
    st.markdown(section_header("Etapa 1 — Configuração do Projeto"), unsafe_allow_html=True)
    st.markdown("Selecione os parâmetros do processo de licenciamento para filtrar "
                "os documentos e requisitos aplicáveis.")

    col1, col2 = st.columns(2)

    with col1:
        licenca_tipo = st.selectbox(
            "Tipo de Licença",
            options=LICENCA_TIPOS,
            format_func=lambda x: f"{x} — {LICENCA_DESC.get(x, '')}",
            help="Modalidade de licenciamento conforme DN COPAM 217/2017",
        )

        atividade = st.selectbox(
            "Atividade",
            options=[
                "A-01 — Pesquisa Mineral",
                "A-02 — Lavra a Céu Aberto",
                "A-03 — Lavra Subterrânea",
                "A-04 — Dragagem / Água Mineral",
                "A-05 — Beneficiamento",
                "A-06 — Pilha de Estéril / Barragem",
                "A-07 — Infraestrutura de Mineração",
            ],
            help="Código de atividade minerária (DN COPAM 217/2017)",
        )

    with col2:
        classe = st.selectbox(
            "Classe Ambiental",
            options=[1, 2, 3, 4, 5, 6],
            index=3,  # Default to class 4
            help="Classe de impacto ambiental (1=mínimo, 6=máximo)",
        )

        cnpj = st.text_input(
            "CNPJ do Empreendedor (opcional)",
            placeholder="00.000.000/0000-00",
            help="Se informado, o relatório incluirá dados históricos da empresa",
        )

    # Preview de documentos aplicáveis
    docs = filtrar_documentos(licenca_tipo)
    st.markdown(f"**{len(docs)} documentos aplicáveis** para {licenca_tipo} (Classe {classe})")

    if docs:
        with st.expander(f"Ver lista de {len(docs)} documentos"):
            for i, doc in enumerate(docs, 1):
                nome = doc.get("documento", "")
                modalidade = doc.get("modalidade", "")
                st.markdown(f"{i}. **{nome}** ({modalidade})")

    if st.button("Próxima etapa", type="primary", use_container_width=True):
        st.session_state.dd_config = {
            "licenca_tipo": licenca_tipo,
            "atividade": atividade.split(" — ")[0],
            "atividade_desc": atividade,
            "classe": classe,
            "cnpj": cnpj.strip() if cnpj else "",
        }
        st.session_state.dd_step = 2
        # Pre-populate doc status
        st.session_state.dd_doc_status = {
            doc["documento"]: "Não Apresentado" for doc in docs
        }
        st.rerun()


# ═══════════════════════════════════════════════════════════
# STEP 2: Checklist de Documentos
# ═══════════════════════════════════════════════════════════
elif st.session_state.dd_step == 2:
    st.markdown(section_header("Etapa 2 — Checklist de Documentos"), unsafe_allow_html=True)
    config = st.session_state.dd_config
    st.markdown(
        f"**Licença:** {config['licenca_tipo']} · "
        f"**Atividade:** {config['atividade_desc']} · "
        f"**Classe:** {config['classe']}"
    )

    docs = filtrar_documentos(config["licenca_tipo"])
    doc_status = st.session_state.dd_doc_status

    # Completude
    completude = calcular_checklist_completude(doc_status)
    st.progress(
        completude["percentual_com_parciais"],
        text=f"Completude: {completude['apresentados']}/{completude['total']} documentos "
             f"({completude['percentual']:.0%})",
    )

    # Agrupar documentos por modalidade
    modalidades: dict[str, list[dict[str, str]]] = {}
    for doc in docs:
        mod = doc.get("modalidade", "Outros") or "Outros"
        modalidades.setdefault(mod, []).append(doc)

    for modalidade, docs_grupo in modalidades.items():
        with st.expander(f"{modalidade} ({len(docs_grupo)} documentos)", expanded=True):
            for doc in docs_grupo:
                nome = doc["documento"]
                col_nome, col_status = st.columns([3, 1])
                with col_nome:
                    desc = doc.get("descricao", "")
                    if desc:
                        st.markdown(f"**{nome}**")
                        st.caption(desc[:200])
                    else:
                        st.markdown(f"**{nome}**")
                with col_status:
                    current = doc_status.get(nome, "Não Apresentado")
                    new_status = st.selectbox(
                        "Status",
                        options=DOC_STATUS,
                        index=DOC_STATUS.index(current),
                        key=f"doc_{nome}",
                        label_visibility="collapsed",
                    )
                    doc_status[nome] = new_status

    st.session_state.dd_doc_status = doc_status

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Voltar", use_container_width=True):
            st.session_state.dd_step = 1
            st.rerun()
    with col_next:
        if st.button("Próxima etapa", type="primary", use_container_width=True):
            st.session_state.dd_step = 3
            # Pre-populate avaliacoes for presented docs
            all_requisitos = load_requisitos()
            avaliacoes: dict[str, str] = {}
            for nome, status in doc_status.items():
                if status in ("Apresentado", "Parcial"):
                    reqs = filtrar_requisitos(nome, all_requisitos)
                    for req in reqs:
                        avaliacoes[req["requisito_id"]] = "Não Aplica"
            st.session_state.dd_avaliacoes = avaliacoes
            st.rerun()


# ═══════════════════════════════════════════════════════════
# STEP 3: Avaliação de Conformidade
# ═══════════════════════════════════════════════════════════
elif st.session_state.dd_step == 3:
    st.markdown(section_header("Etapa 3 — Avaliação de Conformidade"), unsafe_allow_html=True)
    config = st.session_state.dd_config
    doc_status = st.session_state.dd_doc_status
    avaliacoes = st.session_state.dd_avaliacoes

    # Documentos apresentados
    docs_apresentados = [
        nome for nome, status in doc_status.items()
        if status in ("Apresentado", "Parcial")
    ]

    if not docs_apresentados:
        st.warning("Nenhum documento foi marcado como apresentado na etapa anterior.")
    else:
        st.markdown(f"**{len(docs_apresentados)} documentos** para avaliação · "
                    f"**{len(avaliacoes)} requisitos** mapeados")

        # Live score
        if avaliacoes:
            result = calcular_conformidade(avaliacoes)
            score = result.conformidade_nao_ponderada

            col_score, col_detail = st.columns([1, 2])
            with col_score:
                cls = classificar_conformidade(score)
                st.markdown(
                    conformity_gauge_html(score, cls["label"], cls["cor"]),
                    unsafe_allow_html=True,
                )
            with col_detail:
                st.markdown(
                    f"**Atende:** {result.atende} · "
                    f"**Parcial:** {result.atende_parcial} · "
                    f"**Não atende:** {result.nao_atende} · "
                    f"**N/A:** {result.nao_aplica}"
                )
                st.markdown(
                    f'<div style="background:{cls["cor"]}10; border-left:4px solid {cls["cor"]}; '
                    f'padding:0.6rem 0.8rem; border-radius:0 var(--radius-sm) var(--radius-sm) 0; '
                    f'font-size:0.85rem; color:var(--text-secondary);">'
                    f'{cls["descricao"]}</div>',
                    unsafe_allow_html=True,
                )
                if result.requisitos_aplicaveis > 0:
                    st.progress(score)

        # Requisitos por documento
        all_requisitos = load_requisitos()
        avaliacao_opcoes = list(AVALIACOES.keys())

        for doc_nome in docs_apresentados:
            reqs = filtrar_requisitos(doc_nome, all_requisitos)
            if not reqs:
                continue

            with st.expander(f"{doc_nome} ({len(reqs)} requisitos)", expanded=False):
                # Agrupar por módulo/tópico
                topicos: dict[str, list[dict[str, str]]] = {}
                for req in reqs:
                    topico = req.get("topico", "Geral") or "Geral"
                    topicos.setdefault(topico, []).append(req)

                for topico, reqs_topico in topicos.items():
                    st.markdown(f"**{topico}**")
                    for req in reqs_topico:
                        req_id = req["requisito_id"]
                        teste = req.get("teste_aderencia", "")
                        evidencia = req.get("evidencia_esperada", "")

                        col_teste, col_aval = st.columns([3, 1])
                        with col_teste:
                            label = f"`{req_id}` {teste}" if teste else f"`{req_id}`"
                            if evidencia:
                                label += f"\n\n*Evidência: {evidencia[:100]}*"
                            st.markdown(label)
                        with col_aval:
                            current = avaliacoes.get(req_id, "Não Aplica")
                            idx = (
                                avaliacao_opcoes.index(current)
                                if current in avaliacao_opcoes else 3
                            )
                            new_val = st.selectbox(
                                "Avaliação",
                                options=avaliacao_opcoes,
                                index=idx,
                                key=f"req_{req_id}",
                                label_visibility="collapsed",
                            )
                            avaliacoes[req_id] = new_val

        st.session_state.dd_avaliacoes = avaliacoes

    col_back, col_next = st.columns(2)
    with col_back:
        if st.button("Voltar", use_container_width=True):
            st.session_state.dd_step = 2
            st.rerun()
    with col_next:
        if st.button("Gerar Relatório", type="primary", use_container_width=True):
            st.session_state.dd_step = 4
            st.rerun()


# ═══════════════════════════════════════════════════════════
# STEP 4: Relatório e Contexto
# ═══════════════════════════════════════════════════════════
elif st.session_state.dd_step == 4:
    st.markdown(section_header("Etapa 4 — Relatório de Conformidade"), unsafe_allow_html=True)
    config = st.session_state.dd_config
    doc_status = st.session_state.dd_doc_status
    avaliacoes = st.session_state.dd_avaliacoes

    # ── Dashboard de conformidade ──
    result = calcular_conformidade(avaliacoes)
    all_requisitos = load_requisitos()
    recomendacoes = gerar_recomendacoes(avaliacoes, all_requisitos)

    # Visão Geral
    tab_geral, tab_docs, tab_recom, tab_contexto = st.tabs([
        "Visão Geral", "Por Documento", "Recomendações", "Contexto Histórico"
    ])

    with tab_geral:
        st.markdown(
            f"**Licença:** {config['licenca_tipo']} · "
            f"**Atividade:** {config['atividade_desc']} · "
            f"**Classe:** {config['classe']}"
        )

        # KPI Cards
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            score = result.conformidade_nao_ponderada
            cls = classificar_conformidade(score)
            st.markdown(
                conformity_gauge_html(score, cls["label"], cls["cor"]),
                unsafe_allow_html=True,
            )
        with kpi_cols[1]:
            completude = calcular_checklist_completude(doc_status)
            st.metric("Documentos", f"{completude['apresentados']}/{completude['total']}")
        with kpi_cols[2]:
            st.metric("Requisitos Avaliados", f"{result.requisitos_aplicaveis}")
        with kpi_cols[3]:
            st.markdown('<div class="metric-orange">', unsafe_allow_html=True)
            st.metric("Recomendações", f"{len(recomendacoes)}")
            st.markdown('</div>', unsafe_allow_html=True)

        # Breakdown
        st.markdown("")
        col_break1, col_break2 = st.columns(2)
        with col_break1:
            st.markdown("**Resultado por Avaliação:**")
            total_aval = result.atende + result.atende_parcial + result.nao_atende
            if total_aval > 0:
                pct_a = result.atende / total_aval
                pct_p = result.atende_parcial / total_aval
                pct_n = result.nao_atende / total_aval
                st.markdown(
                    f"- Atende: **{result.atende}** ({pct_a:.0%})\n"
                    f"- Parcial: **{result.atende_parcial}** ({pct_p:.0%})\n"
                    f"- Não atende: **{result.nao_atende}** ({pct_n:.0%})\n"
                    f"- Não aplica: **{result.nao_aplica}**"
                )
        with col_break2:
            st.markdown("**Escala de Conformidade:**")
            for faixa in CONFORMIDADE_ESCALA:
                marker = "**>**" if faixa["min"] <= score <= faixa["max"] else " "
                cor = faixa["cor"]
                label = faixa["label"]
                rng = f'{faixa["min"]:.0%}–{faixa["max"]:.0%}'
                st.markdown(
                    f'{marker} <span style="color:{cor};'
                    f' font-weight:bold;">&#9679;</span>'
                    f" {label} ({rng})",
                    unsafe_allow_html=True,
                )

    with tab_docs:
        st.markdown("**Conformidade por documento apresentado:**")

        docs_apresentados = [
            nome for nome, status in doc_status.items()
            if status in ("Apresentado", "Parcial")
        ]

        for doc_nome in docs_apresentados:
            reqs = filtrar_requisitos(doc_nome, all_requisitos)
            doc_avals = {
                r["requisito_id"]: avaliacoes.get(r["requisito_id"], "Não Aplica")
                for r in reqs
            }
            if not doc_avals:
                continue

            doc_result = calcular_conformidade(doc_avals)
            doc_cls = classificar_conformidade(doc_result.conformidade_nao_ponderada)

            col_name, col_score, col_detail = st.columns([2, 1, 2])
            with col_name:
                st.markdown(f"**{doc_nome}**")
            with col_score:
                st.markdown(
                    f'<span style="color:{doc_cls["cor"]}; font-weight:bold;">'
                    f'{doc_result.conformidade_nao_ponderada:.0%}</span> '
                    f'({doc_cls["label"]})',
                    unsafe_allow_html=True,
                )
            with col_detail:
                st.caption(
                    f"Atende: {doc_result.atende} · Parcial: {doc_result.atende_parcial} · "
                    f"Não atende: {doc_result.nao_atende} · N/A: {doc_result.nao_aplica}"
                )
            st.markdown("---")

    with tab_recom:
        if not recomendacoes:
            st.success(
                "Nenhuma recomendação — todos os requisitos avaliados "
                "estão em conformidade."
            )
        else:
            st.markdown(f"**{len(recomendacoes)} recomendações** identificadas:")

            # Agrupar por tipo
            alta = [r for r in recomendacoes if r["prioridade"] == "Alta"]
            media = [r for r in recomendacoes if r["prioridade"] == "Média"]

            if alta:
                st.error(f"**{len(alta)} itens de alta prioridade** (Não Atende)")
                for r in alta[:20]:
                    st.markdown(
                        f"- `{r['requisito_id']}` **{r['documento']}** — {r['teste'][:150]}"
                    )
                if len(alta) > 20:
                    st.caption(f"... e mais {len(alta) - 20} itens")

            if media:
                st.warning(f"**{len(media)} pontos de atenção** (Atende Parcialmente)")
                for r in media[:20]:
                    st.markdown(
                        f"- `{r['requisito_id']}` **{r['documento']}** — {r['teste'][:150]}"
                    )
                if len(media) > 20:
                    st.caption(f"... e mais {len(media) - 20} itens")

    with tab_contexto:
        cnpj = config.get("cnpj", "")
        atividade = config.get("atividade", "")
        classe = config.get("classe", 4)

        st.markdown("**Contexto histórico** — Dados de licenciamento ambiental em MG:")

        try:
            from app.components.data_loader import safe_query

            # Taxa de aprovação para atividade/classe similar
            stats = safe_query(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN decisao = 'deferido' THEN 1 ELSE 0 END) AS deferidos,
                    ROUND(
                        SUM(CASE WHEN decisao = 'deferido' THEN 1.0 ELSE 0 END)
                        / NULLIF(COUNT(*), 0) * 100, 1
                    ) AS taxa_aprovacao
                FROM v_mg_semad
                WHERE atividade LIKE ? || '%'
                  AND classe = ?
                """,
                params=[atividade, str(classe)],
                context="contexto DD",
                fallback=[],
            )

            if stats:
                s = stats[0]
                st.metric(
                    f"Taxa de Aprovação ({atividade}, Classe {classe})",
                    f"{s['taxa_aprovacao']}%",
                    delta=f"{s['total']} decisões analisadas",
                )

            # Se tem CNPJ, buscar dados da empresa
            if cnpj:
                cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
                st.markdown(f"**Dados da empresa:** CNPJ {cnpj}")

                infracoes = safe_query(
                    "SELECT COUNT(*) AS n FROM v_ibama_infracoes"
                    " WHERE cpf_cnpj_infrator = ?",
                    params=[cnpj_clean],
                    context="infrações DD",
                    fallback=[{"n": 0}],
                )
                n_infracoes = infracoes[0]["n"] if infracoes else 0
                if n_infracoes > 0:
                    st.warning(f"{n_infracoes} infrações IBAMA registradas para este CNPJ")
                else:
                    st.success("Nenhuma infração IBAMA registrada")

        except Exception as e:
            st.info(f"Dados de contexto não disponíveis: {e}")

        st.markdown("")
        st.caption(
            "Fonte: SEMAD/MG (decisões), IBAMA (infrações), ANM (CFEM). "
            "Dados públicos oficiais."
        )

    # ── Ações ──
    st.markdown("")
    col_back, col_reset = st.columns(2)
    with col_back:
        if st.button("Voltar para Conformidade", use_container_width=True):
            st.session_state.dd_step = 3
            st.rerun()
    with col_reset:
        if st.button("Nova Avaliação", type="primary", use_container_width=True):
            st.session_state.dd_step = 1
            st.session_state.dd_config = {}
            st.session_state.dd_doc_status = {}
            st.session_state.dd_avaliacoes = {}
            st.rerun()
