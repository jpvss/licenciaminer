"""Endpoints de consulta por empresa (CNPJ)."""

from fastapi import APIRouter, Path

from api.services.database import run_query
from licenciaminer.database.queries import (
    QUERY_CNPJ_ANM_TITULOS,
    QUERY_CNPJ_CFEM,
    QUERY_CNPJ_INFRACOES,
    QUERY_CNPJ_PROFILE,
    QUERY_EMPRESA_PROFILE,
    QUERY_HISTORICO_CNPJ,
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
