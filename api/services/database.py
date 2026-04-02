"""Serviço de banco de dados para a API.

Substitui app/components/data_loader.py removendo dependências do Streamlit.
Gerencia conexão DuckDB e execução de queries com thread-safety.
"""

import json
import logging
import tempfile
from functools import lru_cache
from pathlib import Path
from threading import Lock

import duckdb

from licenciaminer.config import DATA_DIR
from licenciaminer.database.loader import create_views

logger = logging.getLogger(__name__)

_connection: duckdb.DuckDBPyConnection | None = None
_lock = Lock()


def get_connection() -> duckdb.DuckDBPyConnection:
    """Retorna conexão DuckDB singleton com views sobre parquets.

    Thread-safe via lock. Cria banco em arquivo temporário
    para permitir spill-to-disk em ambientes com RAM limitada.
    """
    global _connection
    if _connection is not None:
        return _connection

    with _lock:
        if _connection is not None:
            return _connection

        db_dir = tempfile.mkdtemp(prefix="licenciaminer_api_")
        db_path = str(Path(db_dir) / "api.duckdb")
        con = duckdb.connect(db_path)
        con.execute("SET memory_limit = '600MB'")
        con.execute("SET threads = 4")
        create_views(con, DATA_DIR)
        _connection = con
        logger.info("DuckDB conectado: %s", db_path)

    return _connection


def close_connection() -> None:
    """Fecha conexão DuckDB (chamado no shutdown do FastAPI)."""
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
        logger.info("DuckDB desconectado")


def run_query(query: str, params: list | None = None) -> list[dict]:
    """Executa query no DuckDB e retorna lista de dicts.

    Usa cursor separado para thread-safety.
    """
    con = get_connection()
    cursor = con.cursor()
    try:
        result = cursor.execute(query, params) if params else cursor.execute(query)
        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()
        return [dict(zip(columns, row, strict=False)) for row in rows]
    finally:
        cursor.close()


def safe_query(query: str, params: list | None = None) -> list[dict]:
    """Like run_query but returns [] on any error (missing view, bad SQL, etc.).

    Use for non-critical queries where an empty result is acceptable.
    """
    try:
        return run_query(query, params) or []
    except Exception as exc:
        logger.warning("safe_query failed: %s — %s", exc, query[:120])
        return []


def run_query_df(query: str, params: list | None = None):
    """Executa query e retorna DataFrame pandas."""
    con = get_connection()
    cursor = con.cursor()
    try:
        result = cursor.execute(query, params) if params else cursor.execute(query)
        return result.df()
    finally:
        cursor.close()


# ── Formatação brasileira ──


def fmt_br(n: float | int, decimals: int = 0) -> str:
    """Formata número no padrão brasileiro: 1.234.567,89."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    if decimals > 0:
        formatted = f"{n:,.{decimals}f}"
    else:
        formatted = f"{n:,.0f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_reais(n: float | None) -> str:
    """Formata como R$ 1.234,56."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    return f"R$ {fmt_br(n, 2)}"


def fmt_pct(n: float | None) -> str:
    """Formata como 85,3%."""
    if n is None or (isinstance(n, float) and n != n):
        return "—"
    return f"{fmt_br(n, 1)}%"


def load_metadata() -> dict:
    """Carrega metadados de coleta."""
    meta_path = DATA_DIR / "processed" / "collection_metadata.json"
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


@lru_cache(maxsize=1)
def get_dataset_options() -> dict[str, str]:
    """Retorna datasets disponíveis para exploração."""
    from licenciaminer.database.schema import PARQUET_SOURCES

    get_connection()
    processed = DATA_DIR / "processed"
    options = {}
    for view_name, parquet_spec in PARQUET_SOURCES.items():
        if isinstance(parquet_spec, list):
            exists = all((processed / f).exists() for f in parquet_spec)
            if not exists:
                base_name = parquet_spec[0].replace("_part1", "")
                exists = (processed / base_name).exists()
            if not exists:
                api_name = parquet_spec[0].replace("_part1", "").replace(".parquet", "_api.parquet")
                exists = (processed / api_name).exists()
        else:
            exists = (processed / parquet_spec).exists()

        if exists:
            display = view_name.replace("v_", "").replace("_", " ").title()
            options[display] = view_name
    return options
