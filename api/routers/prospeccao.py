"""Endpoints de prospecção — identificação de oportunidades em concessões minerárias."""

import logging

from fastapi import APIRouter, HTTPException, Query

from api.services.database import run_query

logger = logging.getLogger(__name__)

router = APIRouter()


def _resolve_view() -> str:
    """Retorna view disponível: v_concessoes (preferido) ou v_scm (fallback)."""
    try:
        r = run_query("SELECT COUNT(*) AS n FROM v_concessoes LIMIT 1")
        if r and r[0]["n"] > 0:
            return "v_concessoes"
    except Exception:
        pass
    try:
        r = run_query("SELECT COUNT(*) AS n FROM v_scm LIMIT 1")
        if r and r[0]["n"] > 0:
            return "v_scm"
    except Exception:
        pass
    raise HTTPException(status_code=503, detail="Dataset de concessões não disponível")


def _score_sql(view: str) -> str:
    """SQL de score de oportunidade (0-100)."""
    return f"""
    SELECT
        processo_norm,
        regime,
        titular,
        substancia_principal,
        municipio_principal,
        categoria,
        AREA_HA,
        ativo_cfem,
        cfem_total,
        cfem_ultimo_ano,
        estrategico,
        (
            CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 30 ELSE 0 END
            + CASE WHEN estrategico = 'sim' THEN 25 ELSE 0 END
            + CASE WHEN AREA_HA > 500 THEN 15
                   WHEN AREA_HA > 100 THEN 8
                   ELSE 0 END
            + CASE WHEN cfem_total IS NULL OR cfem_total = 0 THEN 15 ELSE 0 END
            + CASE WHEN categoria IN ('Metálicos Preciosos', 'Metálicos Estratégicos') THEN 15
                   WHEN categoria IN ('Metálicos Ferrosos', 'Metálicos Não-Ferrosos') THEN 8
                   ELSE 0 END
        ) AS score,
        CONCAT_WS(', ',
            CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 'Inativo' END,
            CASE WHEN estrategico = 'sim' THEN 'Estratégico' END,
            CASE WHEN AREA_HA > 500 THEN 'Área grande' END,
            CASE WHEN cfem_total IS NULL OR cfem_total = 0 THEN 'Sem CFEM' END,
            CASE WHEN categoria IN (
                'Metálicos Preciosos', 'Metálicos Estratégicos'
            ) THEN 'Alto valor' END
        ) AS motivo
    FROM {view}
    WHERE regime IS NOT NULL
    """


@router.get("/prospeccao/opportunities")
def list_opportunities(
    min_score: int = Query(30, ge=0, le=100),
    regime: list[str] | None = Query(None),
    categoria: list[str] | None = Query(None),
    estrategico: bool | None = Query(None),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Retorna concessões ranqueadas por score de oportunidade."""
    view = _resolve_view()
    where_extra: list[str] = []
    params: list = []

    if regime:
        placeholders = ", ".join("?" for _ in regime)
        where_extra.append(f"regime IN ({placeholders})")
        params.extend(regime)

    if categoria:
        placeholders = ", ".join("?" for _ in categoria)
        where_extra.append(f"categoria IN ({placeholders})")
        params.extend(categoria)

    if estrategico is True:
        where_extra.append("estrategico = 'sim'")

    extra_sql = (" AND " + " AND ".join(where_extra)) if where_extra else ""

    # Count total matching
    count_q = f"""
    WITH scored AS ({_score_sql(view)})
    SELECT COUNT(*) AS total FROM scored
    WHERE score >= ?{extra_sql}
    """
    count_r = run_query(count_q, [min_score, *params])
    total = count_r[0]["total"] if count_r else 0

    # Fetch page
    data_q = f"""
    WITH scored AS ({_score_sql(view)})
    SELECT * FROM scored
    WHERE score >= ?{extra_sql}
    ORDER BY score DESC, cfem_total DESC NULLS LAST
    LIMIT ? OFFSET ?
    """
    rows = run_query(data_q, [min_score, *params, limit, offset])

    # Compute KPIs from this result set
    stats = {
        "total": total,
        "avg_score": 0,
        "strategic_count": 0,
        "total_area": 0,
    }
    if rows:
        scores = [r.get("score", 0) or 0 for r in rows]
        stats["avg_score"] = round(sum(scores) / len(scores), 1)
        stats["strategic_count"] = sum(
            1 for r in rows if r.get("estrategico") == "sim"
        )
        stats["total_area"] = sum(r.get("AREA_HA", 0) or 0 for r in rows)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "stats": stats,
        "rows": rows,
    }


@router.get("/prospeccao/empresas")
def list_empresa_portfolios(
    limit: int = Query(100, ge=1, le=500),
):
    """Retorna portfolio de empresas (titulares com 2+ concessões)."""
    view = _resolve_view()

    query = f"""
    SELECT
        titular,
        COUNT(*) AS total_concessoes,
        COUNT(DISTINCT substancia_principal) AS substancias_distintas,
        SUM(CASE WHEN ativo_cfem = true THEN 1 ELSE 0 END) AS ativas_cfem,
        SUM(CASE WHEN ativo_cfem = false OR ativo_cfem IS NULL THEN 1 ELSE 0 END) AS inativas,
        COALESCE(SUM(cfem_total), 0) AS cfem_total,
        COALESCE(SUM(AREA_HA), 0) AS area_total
    FROM {view}
    WHERE titular IS NOT NULL
    GROUP BY titular
    HAVING COUNT(*) > 1
    ORDER BY total_concessoes DESC
    LIMIT ?
    """

    rows = run_query(query, [limit])

    stats = {}
    if rows:
        stats["total_empresas"] = len(rows)
        stats["top_empresa"] = rows[0].get("titular", "—")
        stats["top_count"] = rows[0].get("total_concessoes", 0)
        stats["total_inativas"] = sum(r.get("inativas", 0) or 0 for r in rows)

    return {"stats": stats, "rows": rows}


@router.get("/prospeccao/empresas/{titular}/concessoes")
def get_empresa_concessoes(titular: str):
    """Retorna concessões de uma empresa específica."""
    view = _resolve_view()

    rows = run_query(
        f"""
        SELECT processo_norm, regime, substancia_principal, municipio_principal,
               categoria, AREA_HA, ativo_cfem, cfem_total
        FROM {view}
        WHERE titular = ?
        ORDER BY cfem_total DESC NULLS LAST
        """,
        [titular],
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    return {"titular": titular, "total": len(rows), "rows": rows}


@router.get("/prospeccao/municipios")
def list_municipio_concentration(
    limit: int = Query(500, ge=1, le=1000),
):
    """Retorna concentração de concessões por município × substância."""
    view = _resolve_view()

    rows = run_query(
        f"""
        SELECT
            municipio_principal AS municipio,
            substancia_principal AS substancia,
            COUNT(*) AS concessoes,
            SUM(CASE WHEN ativo_cfem = true THEN 1 ELSE 0 END) AS ativas,
            COALESCE(SUM(AREA_HA), 0) AS area_total,
            COALESCE(SUM(cfem_total), 0) AS cfem_total
        FROM {view}
        WHERE municipio_principal IS NOT NULL AND substancia_principal IS NOT NULL
        GROUP BY municipio_principal, substancia_principal
        ORDER BY concessoes DESC
        LIMIT ?
        """,
        [limit],
    )

    return {"total": len(rows), "rows": rows}


@router.get("/prospeccao/ral")
def get_ral_production():
    """Retorna dados de produção mineral RAL para MG."""
    try:
        rows = run_query("""
            SELECT
                "Substância Mineral" AS substancia,
                MAX("Ano base") AS ultimo_ano,
                COUNT(DISTINCT "Ano base") AS anos_dados
            FROM v_ral
            WHERE UF = 'MG'
            GROUP BY "Substância Mineral"
            ORDER BY anos_dados DESC, substancia
        """)
        return {"total": len(rows), "rows": rows}
    except Exception:
        return {"total": 0, "rows": []}


@router.get("/prospeccao/score-breakdown")
def get_score_breakdown():
    """Retorna explicação do cálculo de score."""
    return {
        "max_score": 100,
        "criteria": [
            {"criterion": "Concessão inativa (sem CFEM recente)", "points": 30},
            {"criterion": "Mineral estratégico", "points": 25},
            {"criterion": "Categoria de alto valor (preciosos/estratégicos)", "points": 15},
            {"criterion": "Área > 500 ha", "points": 15},
            {"criterion": "Sem arrecadação CFEM registrada", "points": 15},
            {"criterion": "Área > 100 ha", "points": 8},
            {"criterion": "Categoria metálicos ferrosos/não-ferrosos", "points": 8},
        ],
    }
