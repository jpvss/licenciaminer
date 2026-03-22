"""Carregador de dados parquet para DuckDB."""

import logging
from pathlib import Path

import duckdb

from licenciaminer.database.schema import PARQUET_SOURCES

logger = logging.getLogger(__name__)


def get_connection(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    """Retorna conexão DuckDB (em memória por padrão)."""
    return duckdb.connect(db_path or ":memory:")


def create_views(
    con: duckdb.DuckDBPyConnection, data_dir: Path
) -> dict[str, bool]:
    """Cria views DuckDB apontando para arquivos parquet processados.

    Retorna dicionário indicando quais views foram criadas com sucesso.
    """
    processed_dir = data_dir / "processed"
    loaded: dict[str, bool] = {}

    for view_name, parquet_file in PARQUET_SOURCES.items():
        parquet_path = processed_dir / parquet_file
        if parquet_path.exists():
            con.execute(
                f"CREATE OR REPLACE VIEW {view_name} AS "
                f"SELECT * FROM read_parquet('{parquet_path}')"
            )
            count = con.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()
            n = count[0] if count else 0
            logger.info("View %s criada: %d registros", view_name, n)
            loaded[view_name] = True
        else:
            logger.warning(
                "Arquivo não encontrado: %s — view %s não criada",
                parquet_path,
                view_name,
            )
            loaded[view_name] = False

    return loaded
