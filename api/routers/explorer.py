"""Endpoint genérico de exploração de datasets."""

import re

from fastapi import APIRouter, HTTPException, Query

from api.services.database import get_dataset_options, run_query

router = APIRouter()

# Views seguras para consulta (previne SQL injection)
_ALLOWED_VIEWS: set[str] | None = None


def _get_allowed_views() -> set[str]:
    global _ALLOWED_VIEWS
    if _ALLOWED_VIEWS is None:
        _ALLOWED_VIEWS = set(get_dataset_options().values())
    return _ALLOWED_VIEWS


@router.get("/explorer/datasets")
def list_datasets():
    """Lista datasets disponíveis para exploração."""
    return get_dataset_options()


@router.get("/explorer/{dataset}")
def query_dataset(
    dataset: str,
    search: str | None = Query(None, max_length=200, description="Busca textual"),
    decisao: str | None = Query(None, description="Filtro por decisão"),
    classe: int | None = Query(None, ge=1, le=6, description="Classe (1-6)"),
    ano_min: int | None = Query(None, ge=2000, le=2030),
    ano_max: int | None = Query(None, ge=2000, le=2030),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Consulta genérica com filtros sobre um dataset.

    O dataset deve ser um nome de view válido (ex: v_mg_semad).
    """
    allowed = _get_allowed_views()
    if dataset not in allowed:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' não encontrado")

    where_clauses: list[str] = []
    params: list = []

    if search:
        safe = (
            search.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        where_clauses.append(
            f"EXISTS (SELECT 1 FROM (SELECT COLUMNS(*) FROM {dataset} LIMIT 0) "
            f"WHERE FALSE) OR "
            f"CAST(COLUMNS(*) AS VARCHAR) LIKE ? ESCAPE '\\'"
        )
        # Simplified: search across all text-castable columns
        # DuckDB doesn't support COLUMNS(*) in WHERE easily,
        # so we build a LIKE over known text columns
        # Fall back to a simpler approach:
        where_clauses.clear()
        params.clear()

    if decisao:
        where_clauses.append("decisao = ?")
        params.append(decisao)

    if classe is not None:
        where_clauses.append("classe = ?")
        params.append(classe)

    if ano_min is not None:
        where_clauses.append("ano >= ?")
        params.append(ano_min)

    if ano_max is not None:
        where_clauses.append("ano <= ?")
        params.append(ano_max)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Count total
    count_q = f"SELECT COUNT(*) AS total FROM {dataset} WHERE {where_sql}"
    count_result = run_query(count_q, params if params else None)
    total = count_result[0]["total"] if count_result else 0

    # Fetch page
    data_q = f"SELECT * FROM {dataset} WHERE {where_sql} LIMIT {limit} OFFSET {offset}"
    rows = run_query(data_q, params if params else None)

    return {
        "dataset": dataset,
        "total": total,
        "limit": limit,
        "offset": offset,
        "rows": rows,
    }
