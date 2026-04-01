"""Endpoints de consulta por empresa (CNPJ)."""

from fastapi import APIRouter, Path, Query
from typing import Optional

from api.services.database import run_query
from licenciaminer.database.queries import (
    QUERY_CNPJ_ANM_TITULOS,
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    QUERY_EMPRESA_PROFILE,
    QUERY_HISTORICO_CNPJ,
    query_approval_stats,
    query_similar_cases,
)

router = APIRouter()


@router.get("/empresa/{cnpj}")
def get_empresa_profile(
    cnpj: str = Path(..., min_length=11, max_length=14, description="CNPJ (somente dígitos)"),
):
    """Perfil completo de empresa: decisões, infrações, CFEM."""
    profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
    infracoes = run_query(QUERY_CNPJ_INFRACOES, [cnpj])
    cfem = run_query(QUERY_CNPJ_CFEM, [cnpj])

    result = {
        "cnpj": cnpj,
        "profile": profile[0] if profile else None,
        "infracoes": infracoes[0] if infracoes else {"total_infracoes": 0, "anos_com_infracao": 0},
        "cfem": cfem[0] if cfem else {"meses_pagamento": 0, "total_pago": 0},
    }

    return result


@router.get("/empresa/{cnpj}/decisions")
def get_empresa_decisions(
    cnpj: str = Path(..., min_length=11, max_length=14),
):
    """Histórico completo de decisões para um CNPJ."""
    return run_query(QUERY_HISTORICO_CNPJ, [cnpj])


@router.get("/empresa/{cnpj}/anm")
def get_empresa_anm_titles(
    cnpj: str = Path(..., min_length=11, max_length=14),
):
    """Títulos ANM vinculados à empresa (busca por razão social).

    Nota: busca pelo CNPJ primeiro para obter razão social,
    depois busca títulos ANM por nome.
    """
    profile = run_query(QUERY_CNPJ_PROFILE, [cnpj])
    if not profile or not profile[0].get("razao_social"):
        return []
    razao_social = profile[0]["razao_social"]
    return run_query(QUERY_CNPJ_ANM_TITULOS, [razao_social])


@router.get("/empresas/ranking")
def get_empresas_ranking():
    """Top 50 empresas por número de decisões (cross-source)."""
    return run_query(QUERY_EMPRESA_PROFILE)


@router.get("/consulta/atividades")
def get_atividades():
    """Distinct mining activity codes from SEMAD decisions."""
    rows = run_query(
        "SELECT DISTINCT atividade FROM v_mg_semad "
        "WHERE atividade LIKE 'A-0%' ORDER BY atividade"
    )
    return [r["atividade"] for r in rows]


@router.get("/consulta/regionais")
def get_regionais():
    """Distinct SEMAD regional offices."""
    rows = run_query(
        "SELECT DISTINCT regional FROM v_mg_semad "
        "WHERE regional IS NOT NULL ORDER BY regional"
    )
    return [r["regional"] for r in rows]


@router.get("/consulta/viabilidade")
def get_viabilidade(
    atividade: Optional[str] = Query(None),
    classe: Optional[int] = Query(None),
    regional: Optional[str] = Query(None),
    cnpj: Optional[str] = Query(None),
):
    """Approval stats + similar cases for viability analysis."""
    # Filtered stats
    sql, params = query_approval_stats(
        atividade_prefix=atividade,
        classe=classe,
        regional=regional,
    )
    stats_rows = run_query(sql, params)
    stats = stats_rows[0] if stats_rows else {
        "total": 0, "deferidos": 0, "indeferidos": 0,
        "arquivamentos": 0, "taxa_aprovacao": 0,
    }

    # Overall average (no filters)
    overall_sql, overall_params = query_approval_stats()
    overall_rows = run_query(overall_sql, overall_params)
    media_geral = overall_rows[0]["taxa_aprovacao"] if overall_rows else 0

    # Similar cases
    if atividade:
        cases_sql, cases_params = query_similar_cases(
            atividade=atividade, classe=classe, regional=regional, limit=10
        )
        casos = run_query(cases_sql, cases_params)
    else:
        casos = []

    return {
        "stats": stats,
        "media_geral": media_geral,
        "casos_similares": casos,
    }
