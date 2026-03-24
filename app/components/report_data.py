"""Camada de dados para geração de relatórios PDF.

Coleta todos os dados necessários para um relatório de inteligência ambiental
a partir de um CNPJ, reutilizando queries existentes.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from app.components.data_loader import run_query
from licenciaminer.database.queries import (
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    QUERY_HISTORICO_CNPJ,
    QUERY_INFRACOES_FAIXA_DECISAO,
    QUERY_MG_SUMMARY,
    QUERY_SPATIAL_VS_APROVACAO,
    query_approval_stats,
    query_similar_cases,
)

logger = logging.getLogger(__name__)


@dataclass
class ReportData:
    """Dados consolidados para um relatório de inteligência ambiental."""

    cnpj: str
    generated_at: datetime = field(default_factory=datetime.now)

    # Perfil da empresa (QUERY_CNPJ_PROFILE)
    razao_social: str = ""
    cnae_fiscal: str = ""
    cnae_descricao: str = ""
    porte: str = ""
    data_abertura: str = ""
    situacao: str = ""
    total_decisoes: int = 0
    deferidos: int = 0
    indeferidos: int = 0
    arquivamentos: int = 0
    taxa_aprovacao: float = 0.0

    # Infrações IBAMA
    total_infracoes: int = 0
    anos_com_infracao: int = 0

    # CFEM
    cfem_meses_pagamento: int = 0
    cfem_total_pago: float = 0.0

    # Histórico de decisões (lista de dicts)
    decisoes: list[dict] = field(default_factory=list)

    # Contexto estatístico
    taxa_aprovacao_geral: float = 0.0
    total_decisoes_geral: int = 0

    # Casos similares
    casos_similares: list[dict] = field(default_factory=list)

    # Aprovação filtrada (mesmo perfil de atividade)
    taxa_aprovacao_filtrada: float = 0.0
    total_filtrado: int = 0
    atividade_principal: str = ""

    # Faixas de infração (contexto estatístico)
    faixas_infracoes: list[dict] = field(default_factory=list)

    # Espacial
    analise_espacial: list[dict] = field(default_factory=list)

    # Títulos ANM
    titulos_anm: list[dict] = field(default_factory=list)

    # Nível de risco calculado
    risk_level: str = "MODERADO"  # BAIXO, MODERADO, ALTO

    # Achados principais (auto-gerados)
    findings: list[str] = field(default_factory=list)

    def compute_risk_level(self) -> str:
        """Calcula nível de risco baseado nos dados disponíveis."""
        score = 0

        # Infrações IBAMA
        if self.total_infracoes >= 6:
            score += 3
        elif self.total_infracoes >= 3:
            score += 2
        elif self.total_infracoes >= 1:
            score += 1

        # Taxa de aprovação
        if self.taxa_aprovacao < 50:
            score += 3
        elif self.taxa_aprovacao < 70:
            score += 1

        # CFEM inativo
        if self.cfem_meses_pagamento == 0 and self.total_decisoes > 0:
            score += 1

        # Indeferimentos
        if self.indeferidos > self.deferidos:
            score += 2

        if score >= 5:
            self.risk_level = "ALTO"
        elif score >= 2:
            self.risk_level = "MODERADO"
        else:
            self.risk_level = "BAIXO"

        return self.risk_level

    def generate_findings(self) -> list[str]:
        """Gera lista de achados principais para o sumário executivo."""
        findings = []

        # Infrações
        if self.total_infracoes >= 6:
            findings.append(
                f"Empresa possui {self.total_infracoes} infrações IBAMA em "
                f"{self.anos_com_infracao} anos — perfil de alto risco regulatório."
            )
        elif self.total_infracoes >= 1:
            findings.append(
                f"Registradas {self.total_infracoes} infração(ões) IBAMA."
            )
        else:
            findings.append("Sem infrações IBAMA registradas — histórico limpo.")

        # Taxa de aprovação comparativa
        diff = self.taxa_aprovacao - self.taxa_aprovacao_geral
        if abs(diff) > 5:
            direction = "acima" if diff > 0 else "abaixo"
            findings.append(
                f"Taxa de aprovação ({self.taxa_aprovacao:.0f}%) está "
                f"{abs(diff):.0f}pp {direction} da média estadual "
                f"({self.taxa_aprovacao_geral:.0f}%)."
            )

        # CFEM
        if self.cfem_total_pago > 0:
            findings.append(
                f"Pagamentos CFEM regulares: R$ {self.cfem_total_pago:,.2f} "
                f"em {self.cfem_meses_pagamento} meses."
            )
        elif self.total_decisoes > 0:
            findings.append("Sem pagamentos CFEM registrados no período analisado.")

        self.findings = findings[:5]  # Máximo 5 achados
        return self.findings


def collect_report_data(cnpj: str) -> ReportData:
    """Coleta todos os dados para o relatório de um CNPJ.

    Reutiliza as queries existentes em queries.py.
    """
    data = ReportData(cnpj=cnpj)

    # 1. Perfil da empresa
    try:
        profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
        if profile:
            p = profile[0]
            data.razao_social = p.get("razao_social", "") or cnpj
            data.cnae_fiscal = p.get("cnae_fiscal", "") or ""
            data.cnae_descricao = p.get("cnae_descricao", "") or ""
            data.porte = p.get("porte", "") or ""
            data.data_abertura = str(p.get("data_abertura", "")) or ""
            data.situacao = p.get("situacao", "") or ""
            data.total_decisoes = p.get("total_decisoes", 0) or 0
            data.deferidos = p.get("deferidos", 0) or 0
            data.indeferidos = p.get("indeferidos", 0) or 0
            data.arquivamentos = p.get("arquivamentos", 0) or 0
            data.taxa_aprovacao = p.get("taxa_aprovacao", 0) or 0
    except Exception:
        logger.exception("Erro ao buscar perfil CNPJ %s", cnpj)

    # 2. Infrações IBAMA
    try:
        inf = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
        if inf and inf[0].get("total_infracoes"):
            data.total_infracoes = inf[0]["total_infracoes"]
            data.anos_com_infracao = inf[0].get("anos_com_infracao", 0) or 0
    except Exception:
        logger.exception("Erro ao buscar infrações CNPJ %s", cnpj)

    # 3. CFEM
    try:
        cfem = run_query(QUERY_CNPJ_CFEM, [cnpj])
        if cfem and cfem[0].get("meses_pagamento"):
            data.cfem_meses_pagamento = cfem[0]["meses_pagamento"]
            data.cfem_total_pago = cfem[0].get("total_pago", 0) or 0
    except Exception:
        logger.exception("Erro ao buscar CFEM CNPJ %s", cnpj)

    # 4. Histórico de decisões
    try:
        hist = run_query(QUERY_HISTORICO_CNPJ, [cnpj])
        data.decisoes = hist or []
    except Exception:
        logger.exception("Erro ao buscar histórico CNPJ %s", cnpj)

    # 5. Contexto estatístico geral
    try:
        summary = run_query(QUERY_MG_SUMMARY)
        if summary:
            data.taxa_aprovacao_geral = summary[0].get("taxa_aprovacao_geral", 0) or 0
            data.total_decisoes_geral = summary[0].get("total_decisoes", 0) or 0
    except Exception:
        logger.exception("Erro ao buscar resumo geral")

    # 6. Aprovação filtrada por atividade principal
    if data.decisoes:
        # Pegar atividade mais frequente
        atividades = [d.get("atividade", "") for d in data.decisoes if d.get("atividade")]
        if atividades:
            data.atividade_principal = max(set(atividades), key=atividades.count)
            prefix = data.atividade_principal[:7] if len(data.atividade_principal) >= 7 else None
            if prefix:
                try:
                    q, p = query_approval_stats(prefix)
                    stats = run_query(q, p)
                    if stats and stats[0].get("total", 0) > 0:
                        data.taxa_aprovacao_filtrada = stats[0]["taxa_aprovacao"]
                        data.total_filtrado = stats[0]["total"]
                except Exception:
                    logger.exception("Erro ao buscar stats filtradas")

    # 7. Casos similares
    if data.atividade_principal:
        prefix = data.atividade_principal[:7] if len(data.atividade_principal) >= 7 else None
        if prefix:
            try:
                q, p = query_similar_cases(prefix, limit=5)
                cases = run_query(q, p)
                data.casos_similares = cases or []
            except Exception:
                logger.exception("Erro ao buscar casos similares")

    # 8. Faixas de infração (contexto)
    try:
        faixas = run_query(QUERY_INFRACOES_FAIXA_DECISAO)
        data.faixas_infracoes = faixas or []
    except Exception:
        logger.exception("Erro ao buscar faixas de infração")

    # 9. Análise espacial
    try:
        spatial = run_query(QUERY_SPATIAL_VS_APROVACAO)
        data.analise_espacial = spatial or []
    except Exception:
        logger.exception("Erro ao buscar análise espacial")

    # 10. Títulos ANM (busca por nome da empresa)
    if data.razao_social and data.razao_social != cnpj:
        try:
            from licenciaminer.database.queries import QUERY_CNPJ_ANM_TITULOS
            titulos = run_query(QUERY_CNPJ_ANM_TITULOS, [data.razao_social])
            data.titulos_anm = titulos or []
        except Exception:
            logger.exception("Erro ao buscar títulos ANM")

    # Computar risco e achados
    data.compute_risk_level()
    data.generate_findings()

    return data
