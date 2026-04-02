"""Endpoints do simulador Mineradora Modelo — dados 100% simulados.

Wrapper HTTP sobre app/components/mining_simulator.py.
Todos os dados são fictícios (seed fixa = determinísticos).
"""

import logging

from fastapi import APIRouter, HTTPException

from app.components.mining_simulator import (
    SETORES,
    gerar_todos_os_dados,
    get_kpi_info,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Cache dos dados simulados (determinísticos, seed fixa)
_sim_cache: dict | None = None


def _get_all_data() -> dict:
    """Retorna dados simulados cacheados."""
    global _sim_cache
    if _sim_cache is None:
        _sim_cache = gerar_todos_os_dados()
    return _sim_cache


@router.get("/simulator/setores")
def list_setores():
    """Lista setores disponíveis e seus KPIs."""
    result = {}
    for setor, kpis in SETORES.items():
        result[setor] = [
            {
                "nome": kpi.nome,
                "unidade": kpi.unidade,
                "target": kpi.target,
                "min_val": kpi.min_val,
                "max_val": kpi.max_val,
            }
            for kpi in kpis
        ]
    return {
        "setores": result,
        "disclaimer": (
            "DADOS SIMULADOS — Este simulador utiliza dados fictícios gerados "
            "com base em benchmarks da indústria para uma mineradora modelo de "
            "5.0 MTPA de minério de ferro com disposição de rejeitos em pilhas."
        ),
    }


@router.get("/simulator/setores/{setor}")
def get_setor_data(setor: str):
    """Retorna dados simulados de todos os KPIs de um setor."""
    all_data = _get_all_data()
    if setor not in all_data:
        raise HTTPException(
            status_code=404,
            detail=f"Setor '{setor}' não encontrado. Disponíveis: {list(SETORES.keys())}",
        )

    kpi_infos = get_kpi_info(setor)
    kpi_data = all_data[setor]

    kpis = []
    for kpi in kpi_infos:
        series = kpi_data[kpi.nome]
        current = series["valor"][-1]
        previous = series["valor"][-2]
        delta = current - previous

        kpis.append({
            "nome": kpi.nome,
            "unidade": kpi.unidade,
            "target": kpi.target,
            "min_val": kpi.min_val,
            "max_val": kpi.max_val,
            "current": round(current, 2),
            "previous": round(previous, 2),
            "delta": round(delta, 2),
            "series": {"data": series["data"], "valor": series["valor"]},
        })

    return {
        "setor": setor,
        "kpis": kpis,
        "disclaimer": "DADOS SIMULADOS",
    }


@router.get("/simulator/setores/{setor}/kpi/{nome}")
def get_kpi_detail(setor: str, nome: str):
    """Retorna série temporal de um KPI específico."""
    all_data = _get_all_data()
    if setor not in all_data:
        raise HTTPException(status_code=404, detail=f"Setor '{setor}' não encontrado")

    if nome not in all_data[setor]:
        available = list(all_data[setor].keys())
        raise HTTPException(
            status_code=404,
            detail=f"KPI '{nome}' não encontrado em '{setor}'. Disponíveis: {available}",
        )

    kpi_info = next((k for k in SETORES[setor] if k.nome == nome), None)
    series = all_data[setor][nome]

    return {
        "setor": setor,
        "nome": nome,
        "unidade": kpi_info.unidade if kpi_info else "",
        "target": kpi_info.target if kpi_info else series["target"][0],
        "min_val": kpi_info.min_val if kpi_info else series["min"][0],
        "max_val": kpi_info.max_val if kpi_info else series["max"][0],
        "series": {"data": series["data"], "valor": series["valor"]},
        "disclaimer": "DADOS SIMULADOS",
    }
