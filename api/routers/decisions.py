"""Endpoints de análise de decisões de licenciamento."""

from fastapi import APIRouter, Query

from api.services.database import run_query
from licenciaminer.database.queries import (
    QUERY_APROVACAO_ATIVIDADE_CLASSE,
    QUERY_ARQUIVAMENTO_ANALYSIS,
    QUERY_CFEM_VS_APROVACAO,
    QUERY_CLASSE_MODALIDADE,
    QUERY_DECISAO_POR_MODALIDADE,
    QUERY_INFRACOES_FAIXA_DECISAO,
    QUERY_INFRACOES_VS_APROVACAO,
    QUERY_MG_APPROVAL_RATES,
    QUERY_REINCIDENCIA,
    QUERY_RIGOR_REGIONAL,
    QUERY_SPATIAL_VS_APROVACAO,
    QUERY_TENDENCIA_INDEFERIMENTO,
    query_approval_stats,
    query_similar_cases,
)

router = APIRouter()


@router.get("/decisions/approval-rates")
def get_approval_rates():
    """Taxa de aprovação por classe/atividade/regional/ano."""
    return run_query(QUERY_MG_APPROVAL_RATES)


@router.get("/decisions/by-modalidade")
def get_decisions_by_modalidade():
    """Distribuição de decisões por modalidade."""
    return run_query(QUERY_DECISAO_POR_MODALIDADE)


@router.get("/decisions/activity-class-heatmap")
def get_activity_class_heatmap():
    """Heatmap: taxa de aprovação por atividade x classe."""
    return run_query(QUERY_APROVACAO_ATIVIDADE_CLASSE)


@router.get("/decisions/rejection-trend")
def get_rejection_trend():
    """Tendência temporal de indeferimentos."""
    return run_query(QUERY_TENDENCIA_INDEFERIMENTO)


@router.get("/decisions/regional-rigor")
def get_regional_rigor():
    """Ranking de regionais por rigor (taxa de indeferimento)."""
    return run_query(QUERY_RIGOR_REGIONAL)


@router.get("/decisions/infraction-bands")
def get_infraction_bands():
    """Correlação infrações IBAMA x decisão por faixa."""
    return run_query(QUERY_INFRACOES_FAIXA_DECISAO)


@router.get("/decisions/recidivism")
def get_recidivism():
    """Reincidência: empresas com múltiplas decisões."""
    return run_query(QUERY_REINCIDENCIA)


@router.get("/decisions/shelving-analysis")
def get_shelving_analysis():
    """Análise de arquivamentos por classe e grupo de atividade."""
    return run_query(QUERY_ARQUIVAMENTO_ANALYSIS)


@router.get("/decisions/class-modalidade")
def get_class_modalidade():
    """Interação classe x modalidade."""
    return run_query(QUERY_CLASSE_MODALIDADE)


@router.get("/decisions/infractions-vs-approval")
def get_infractions_vs_approval():
    """Empresas com infrações IBAMA vs taxa de aprovação."""
    return run_query(QUERY_INFRACOES_VS_APROVACAO)


@router.get("/decisions/cfem-vs-approval")
def get_cfem_vs_approval():
    """CFEM vs taxa de aprovação."""
    return run_query(QUERY_CFEM_VS_APROVACAO)


@router.get("/decisions/spatial-vs-approval")
def get_spatial_vs_approval():
    """Sobreposição espacial vs taxa de aprovação."""
    return run_query(QUERY_SPATIAL_VS_APROVACAO)


@router.get("/decisions/similar-cases")
def get_similar_cases(
    atividade: str = Query(..., description="Código de atividade (ex: A-01-01)"),
    classe: int | None = Query(None, description="Classe (1-6)"),
    regional: str | None = Query(None, description="Regional SEMAD"),
    limit: int = Query(10, ge=1, le=50),
):
    """Casos similares para uma atividade/classe/regional."""
    q, p = query_similar_cases(atividade, classe, regional, limit)
    return run_query(q, p)


@router.get("/decisions/approval-stats")
def get_approval_stats(
    atividade: str | None = Query(None, description="Prefixo de atividade"),
    classe: int | None = Query(None, description="Classe (1-6)"),
    regional: str | None = Query(None, description="Regional SEMAD"),
):
    """Estatísticas de aprovação filtradas."""
    q, p = query_approval_stats(atividade, classe, regional)
    return run_query(q, p)
