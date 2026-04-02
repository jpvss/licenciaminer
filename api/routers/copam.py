"""Endpoints para deliberações COPAM CMI."""

from fastapi import APIRouter, Query
from typing import Optional

from api.services.database import run_query

router = APIRouter()


@router.get("/copam")
def get_copam_meetings(
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Reuniões da CMI/COPAM com documentos."""
    count_row = run_query("SELECT COUNT(*) AS n FROM v_copam")
    total = count_row[0]["n"] if count_row else 0

    rows = run_query(
        """
        SELECT
            data,
            titulo,
            total_documents,
            documents_str,
            municipio,
            sede
        FROM v_copam
        ORDER BY data DESC
        LIMIT ? OFFSET ?
        """,
        [limit, offset],
    )

    # Summary KPIs
    stats_row = run_query(
        """
        SELECT
            COUNT(*) AS total_reunioes,
            COALESCE(SUM(total_documents), 0) AS total_documentos,
            MAX(data) AS ultima_reuniao
        FROM v_copam
        """
    )
    stats = stats_row[0] if stats_row else {}

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "stats": stats,
        "rows": rows,
    }
