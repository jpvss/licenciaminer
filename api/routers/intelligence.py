"""Endpoints de Inteligência Comercial — Mineral Intelligence.

Pilares: Mercado/Cotações, Comércio Exterior, Produção/Arrecadação, Gestão Territorial.
"""

import csv
import logging

from fastapi import APIRouter, Query

from api.services.database import run_query
from licenciaminer.config import REFERENCE_DIR

logger = logging.getLogger(__name__)

router = APIRouter()


def _safe_query(sql: str, params: list | None = None) -> list[dict]:
    """Query com fallback para lista vazia."""
    try:
        return run_query(sql, params) or []
    except Exception:
        logger.exception("Erro query intelligence")
        return []


# ── Mercado & Cotações ──


@router.get("/intelligence/ptax")
def get_ptax():
    """Retorna série histórica de câmbio USD/BRL (BCB PTAX)."""
    rows = _safe_query(
        "SELECT data, cotacao_venda FROM v_bcb_cotacoes ORDER BY data"
    )
    latest = rows[-1] if rows else None
    return {"rows": rows, "latest": latest, "total": len(rows)}


@router.get("/intelligence/commodities")
def get_commodity_prices():
    """Retorna cotações de commodities (CSV manual)."""
    commodity_csv = REFERENCE_DIR / "commodity_prices.csv"
    if not commodity_csv.exists():
        return {"rows": [], "minerals": []}

    with open(commodity_csv, encoding="utf-8") as f:
        commodities = list(csv.DictReader(f))

    minerals = sorted({r["mineral"] for r in commodities})

    # Última cotação por mineral
    latest_by_mineral = {}
    for row in commodities:
        mineral = row["mineral"]
        latest_by_mineral[mineral] = row  # CSV é cronológico, último ganha

    return {
        "rows": commodities,
        "minerals": minerals,
        "latest": latest_by_mineral,
    }


# ── Comércio Exterior ──


@router.get("/intelligence/comex")
def get_comex_data():
    """Retorna dados de comércio exterior mineral (Comex Stat/MDIC)."""
    rows = _safe_query("SELECT * FROM v_comex_mineracao")
    if not rows:
        return {"rows": [], "summary": None}

    # Resumo por fluxo
    summary = {"Exportação": 0, "Importação": 0}
    for r in rows:
        fluxo = r.get("fluxo", "")
        valor = r.get("valor_fob_usd", 0) or 0
        if fluxo in summary:
            summary[fluxo] += valor

    return {"rows": rows, "summary": summary, "total": len(rows)}


@router.get("/intelligence/comex/yearly")
def get_comex_yearly():
    """Retorna comércio exterior agrupado por ano e fluxo."""
    rows = _safe_query("""
        SELECT ano, fluxo,
               SUM(valor_fob_usd) AS valor_fob_usd
        FROM v_comex_mineracao
        WHERE ano IS NOT NULL AND fluxo IS NOT NULL
        GROUP BY ano, fluxo
        ORDER BY ano
    """)
    return {"rows": rows}


@router.get("/intelligence/comex/by-uf")
def get_comex_by_uf(
    fluxo: str = Query("Exportação", pattern="^(Exportação|Importação)$"),
    limit: int = Query(10, ge=1, le=30),
):
    """Retorna comércio exterior por UF."""
    rows = _safe_query(
        """
        SELECT uf, SUM(valor_fob_usd) AS valor_fob_usd
        FROM v_comex_mineracao
        WHERE fluxo = ?
        GROUP BY uf
        ORDER BY valor_fob_usd DESC
        LIMIT ?
        """,
        [fluxo, limit],
    )
    return {"fluxo": fluxo, "rows": rows}


# ── Produção & Arrecadação ──


@router.get("/intelligence/cfem/stats")
def get_cfem_stats():
    """Retorna estatísticas de arrecadação CFEM."""
    total = _safe_query("SELECT COUNT(*) AS n FROM v_cfem")
    n = total[0]["n"] if total else 0
    return {"total_records": n}


@router.get("/intelligence/cfem/top-municipios")
def get_cfem_top_municipios(limit: int = Query(15, ge=1, le=50)):
    """Top municípios por arrecadação CFEM."""
    rows = _safe_query(
        """
        SELECT "Município" AS municipio,
               SUM(TRY_CAST(
                   REPLACE(REPLACE("ValorRecolhido", '.', ''), ',', '.')
                   AS DOUBLE
               )) AS total
        FROM v_cfem
        WHERE "Município" IS NOT NULL
        GROUP BY "Município"
        ORDER BY total DESC
        LIMIT ?
        """,
        [limit],
    )
    return {"rows": rows}


@router.get("/intelligence/cfem/top-substancias")
def get_cfem_top_substancias(limit: int = Query(10, ge=1, le=50)):
    """Top substâncias por arrecadação CFEM."""
    rows = _safe_query(
        """
        SELECT "Substância" AS substancia,
               SUM(TRY_CAST(
                   REPLACE(REPLACE("ValorRecolhido", '.', ''), ',', '.')
                   AS DOUBLE
               )) AS total
        FROM v_cfem
        WHERE "Substância" IS NOT NULL
        GROUP BY "Substância"
        ORDER BY total DESC
        LIMIT ?
        """,
        [limit],
    )
    return {"rows": rows}


@router.get("/intelligence/ral/stats")
def get_ral_stats():
    """Retorna estatísticas do RAL (Relatório Anual de Lavra)."""
    total = _safe_query("SELECT COUNT(*) AS n FROM v_ral")
    n = total[0]["n"] if total else 0
    return {"total_records": n}


@router.get("/intelligence/ral/top-substancias")
def get_ral_top_substancias(limit: int = Query(10, ge=1, le=50)):
    """Top substâncias por registros RAL."""
    rows = _safe_query(
        """
        SELECT "Substância Mineral" AS substancia, COUNT(*) AS n
        FROM v_ral
        WHERE "Substância Mineral" IS NOT NULL
        GROUP BY "Substância Mineral"
        ORDER BY n DESC
        LIMIT ?
        """,
        [limit],
    )
    return {"rows": rows}


# ── Gestão Territorial ──


@router.get("/intelligence/anm/stats")
def get_anm_stats():
    """Retorna estatísticas de processos ANM."""
    total = _safe_query("SELECT COUNT(*) AS n FROM v_anm")
    n = total[0]["n"] if total else 0
    return {"total_records": n}


@router.get("/intelligence/anm/by-fase")
def get_anm_by_fase():
    """Processos ANM agrupados por fase."""
    rows = _safe_query("""
        SELECT FASE AS fase, COUNT(*) AS n
        FROM v_anm
        WHERE FASE IS NOT NULL
        GROUP BY FASE
        ORDER BY n DESC
    """)
    return {"rows": rows}


@router.get("/intelligence/anm/by-substancia")
def get_anm_by_substancia(limit: int = Query(15, ge=1, le=50)):
    """Top substâncias por processos ANM."""
    rows = _safe_query(
        """
        SELECT SUBS AS substancia, COUNT(*) AS n
        FROM v_anm
        WHERE SUBS IS NOT NULL
        GROUP BY SUBS
        ORDER BY n DESC
        LIMIT ?
        """,
        [limit],
    )
    return {"rows": rows}
