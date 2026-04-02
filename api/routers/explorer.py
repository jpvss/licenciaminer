"""Endpoint genérico de exploração de datasets."""

import csv
import io

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from api.services.database import get_dataset_options, run_query

router = APIRouter()

# Views seguras para consulta (previne SQL injection)
_ALLOWED_VIEWS: set[str] | None = None

# Colunas pesadas excluídas do SELECT em listagens
_HEAVY_COLUMNS = {"texto_documentos", "documentos_pdf", "documents_str"}

# Colunas de texto pesquisáveis por view (pré-definidas para segurança e performance)
_SEARCHABLE_COLUMNS: dict[str, list[str]] = {
    "v_mg_semad": ["empreendimento", "cnpj_cpf", "municipio", "regional", "atividade", "modalidade"],
    "v_ibama_infracoes": ["NOME_INFRATOR", "CPF_CNPJ_INFRATOR", "MUNICIPIO", "DES_AUTO_INFRACAO"],
    "v_cfem": ["CPF_CNPJ", "Substância", "Município"],
    "v_anm": ["NOME", "UF", "SUBS", "FASE"],
    "v_cnpj": ["razao_social", "cnpj", "cnae_fiscal_descricao", "municipio"],
    "v_scm": ["titular", "processo_norm", "substancia_principal", "municipio"],
    "v_concessoes": ["titular", "processo_norm", "substancia_principal", "municipio"],
}


def _get_allowed_views() -> set[str]:
    global _ALLOWED_VIEWS
    if _ALLOWED_VIEWS is None:
        _ALLOWED_VIEWS = set(get_dataset_options().values())
    return _ALLOWED_VIEWS


def _get_light_columns(dataset: str) -> list[str]:
    """Retorna colunas do dataset excluindo as pesadas."""
    rows = run_query(f"SELECT * FROM {dataset} LIMIT 0")
    if not rows:
        # Fallback: obter nomes de coluna via DESCRIBE
        desc = run_query(f"DESCRIBE {dataset}")
        all_cols = [r["column_name"] for r in desc]
    else:
        all_cols = list(rows[0].keys()) if rows else []

    # Quando LIMIT 0 retorna vazio, usar DESCRIBE
    if not all_cols:
        desc = run_query(f"DESCRIBE {dataset}")
        all_cols = [r["column_name"] for r in desc]

    return [c for c in all_cols if c not in _HEAVY_COLUMNS]


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
    mining_only: bool = Query(False, description="Apenas atividades de mineração (A-0x)"),
    uf: str | None = Query(None, max_length=2, description="Filtro por UF (ex: MG)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Consulta genérica com filtros sobre um dataset."""
    allowed = _get_allowed_views()
    if dataset not in allowed:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' não encontrado")

    where_clauses: list[str] = []
    params: list = []

    # Busca textual: LIKE em colunas conhecidas de texto
    if search:
        safe = (
            search.replace("\\", "\\\\")
            .replace("%", "\\%")
            .replace("_", "\\_")
        )
        searchable = _SEARCHABLE_COLUMNS.get(dataset, [])
        if searchable:
            conds = [
                f"LOWER(CAST({col} AS VARCHAR)) LIKE ? ESCAPE '\\'"
                for col in searchable
            ]
            where_clauses.append(f"({' OR '.join(conds)})")
            for _ in searchable:
                params.append(f"%{safe.lower()}%")

    if mining_only and dataset == "v_mg_semad":
        where_clauses.append("atividade LIKE 'A-0%'")

    if uf and dataset in ("v_ibama_infracoes", "v_anm"):
        where_clauses.append("UF = ?")
        params.append(uf.upper())

    if decisao:
        where_clauses.append("decisao = ?")
        params.append(decisao)

    if classe is not None:
        where_clauses.append("classe = ?")
        params.append(classe)

    if ano_min is not None:
        where_clauses.append("CAST(ano AS INTEGER) >= ?")
        params.append(ano_min)

    if ano_max is not None:
        where_clauses.append("CAST(ano AS INTEGER) <= ?")
        params.append(ano_max)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Colunas leves apenas
    light_cols = _get_light_columns(dataset)
    select_sql = ", ".join(light_cols)

    # Count total
    count_q = f"SELECT COUNT(*) AS total FROM {dataset} WHERE {where_sql}"
    count_result = run_query(count_q, params if params else None)
    total = count_result[0]["total"] if count_result else 0

    # Fetch page
    data_q = (
        f"SELECT {select_sql} FROM {dataset} WHERE {where_sql} "
        f"ORDER BY 1 DESC LIMIT {limit} OFFSET {offset}"
    )
    rows = run_query(data_q, params if params else None)

    return {
        "dataset": dataset,
        "total": total,
        "limit": limit,
        "offset": offset,
        "rows": rows,
    }


@router.get("/explorer/{dataset}/record/{record_id}")
def get_record_detail(dataset: str, record_id: str):
    """Retorna registro completo por detail_id (exceto texto do parecer)."""
    allowed = _get_allowed_views()
    if dataset not in allowed:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' não encontrado")

    # Apenas v_mg_semad tem detail_id
    if dataset != "v_mg_semad":
        raise HTTPException(status_code=400, detail="Detail view só disponível para v_mg_semad")

    cols = _get_light_columns(dataset)
    # Incluir documentos_pdf para links de documentos
    if "documentos_pdf" not in cols:
        cols.append("documentos_pdf")
    select_sql = ", ".join(cols)

    rows = run_query(
        f"SELECT {select_sql} FROM {dataset} WHERE detail_id = ?",
        [record_id],
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    return rows[0]


@router.get("/explorer/{dataset}/record/{record_id}/text")
def get_record_text(dataset: str, record_id: str):
    """Retorna texto do parecer (lazy load, até 8000 chars)."""
    allowed = _get_allowed_views()
    if dataset not in allowed:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' não encontrado")

    if dataset != "v_mg_semad":
        raise HTTPException(status_code=400, detail="Texto só disponível para v_mg_semad")

    rows = run_query(
        f"SELECT texto_documentos FROM {dataset} WHERE detail_id = ?",
        [record_id],
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Registro não encontrado")

    texto = str(rows[0].get("texto_documentos") or "")
    truncated = len(texto) > 8000
    return {
        "text": texto[:8000],
        "truncated": truncated,
        "total_length": len(texto),
    }


@router.get("/explorer/{dataset}/export.csv")
def export_csv(
    dataset: str,
    search: str | None = Query(None, max_length=200),
    decisao: str | None = Query(None),
    classe: int | None = Query(None, ge=1, le=6),
    ano_min: int | None = Query(None, ge=2000, le=2030),
    ano_max: int | None = Query(None, ge=2000, le=2030),
    mining_only: bool = Query(False),
):
    """Exporta dataset filtrado como CSV (max 20.000 linhas)."""
    allowed = _get_allowed_views()
    if dataset not in allowed:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset}' não encontrado")

    where_clauses: list[str] = []
    params: list = []

    if search:
        safe = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        searchable = _SEARCHABLE_COLUMNS.get(dataset, [])
        if searchable:
            conds = [f"LOWER(CAST({col} AS VARCHAR)) LIKE ? ESCAPE '\\'" for col in searchable]
            where_clauses.append(f"({' OR '.join(conds)})")
            for _ in searchable:
                params.append(f"%{safe.lower()}%")

    if mining_only and dataset == "v_mg_semad":
        where_clauses.append("atividade LIKE 'A-0%'")
    if decisao:
        where_clauses.append("decisao = ?")
        params.append(decisao)
    if classe is not None:
        where_clauses.append("classe = ?")
        params.append(classe)
    if ano_min is not None:
        where_clauses.append("CAST(ano AS INTEGER) >= ?")
        params.append(ano_min)
    if ano_max is not None:
        where_clauses.append("CAST(ano AS INTEGER) <= ?")
        params.append(ano_max)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Check count first
    count_result = run_query(f"SELECT COUNT(*) AS total FROM {dataset} WHERE {where_sql}", params or None)
    total = count_result[0]["total"] if count_result else 0
    if total > 20000:
        raise HTTPException(
            status_code=400,
            detail=f"Dataset muito grande ({total} registros). Aplique filtros para reduzir a menos de 20.000.",
        )

    light_cols = _get_light_columns(dataset)
    select_sql = ", ".join(light_cols)
    rows = run_query(
        f"SELECT {select_sql} FROM {dataset} WHERE {where_sql} ORDER BY 1 DESC",
        params or None,
    )

    # Gerar CSV em memória
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{dataset}.csv"'},
    )
