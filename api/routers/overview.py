"""Endpoints de visão geral e estatísticas agregadas."""

from fastapi import APIRouter

from api.services.database import load_metadata, run_query
from licenciaminer.database.queries import (
    QUERY_ANM_SUMMARY,
    QUERY_IBAMA_SUMMARY,
    QUERY_MG_SUMMARY,
    QUERY_MINING_SUMMARY,
    QUERY_MINING_TREND,
)

router = APIRouter()


@router.get("/overview/stats")
def get_overview_stats():
    """Retorna KPIs agregados do dashboard principal."""
    mg = run_query(QUERY_MG_SUMMARY)
    mining = run_query(QUERY_MINING_SUMMARY)
    ibama = run_query(QUERY_IBAMA_SUMMARY)
    anm = run_query(QUERY_ANM_SUMMARY)

    return {
        "mg_summary": mg[0] if mg else None,
        "mining_summary": mining[0] if mining else None,
        "ibama_summary": ibama[0] if ibama else None,
        "anm_summary": anm[0] if anm else None,
    }


@router.get("/overview/trend")
def get_mining_trend():
    """Tendência temporal de aprovação de mineração."""
    return run_query(QUERY_MINING_TREND)


@router.get("/overview/metadata")
def get_metadata():
    """Retorna metadados de coleta de dados."""
    return load_metadata()
