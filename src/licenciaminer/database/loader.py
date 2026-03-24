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

    for view_name, parquet_spec in PARQUET_SOURCES.items():
        # Support single file or list of parts (with single-file fallback)
        if isinstance(parquet_spec, list):
            paths = [processed_dir / f for f in parquet_spec]
            all_exist = all(p.exists() for p in paths)

            if all_exist:
                path_list = ", ".join(f"'{p}'" for p in paths)
                read_expr = f"read_parquet([{path_list}])"
                display_name = ", ".join(parquet_spec)
            else:
                # Fallback: try single file (e.g. ibama_infracoes.parquet)
                # Derive name from first part: "xxx_part1.parquet" → "xxx.parquet"
                base_name = parquet_spec[0].replace("_part1", "")
                single_path = processed_dir / base_name
                if single_path.exists():
                    read_expr = f"read_parquet('{single_path}')"
                    display_name = base_name
                    all_exist = True
                else:
                    display_name = ", ".join(parquet_spec)
        else:
            parquet_path = processed_dir / parquet_spec
            all_exist = parquet_path.exists()
            read_expr = f"read_parquet('{parquet_path}')"
            display_name = parquet_spec

        if all_exist:
            con.execute(
                f"CREATE OR REPLACE VIEW {view_name} AS "
                f"SELECT * FROM {read_expr}"
            )
            logger.info("View %s criada (lazy): %s", view_name, display_name)
            loaded[view_name] = True
        else:
            logger.warning(
                "Arquivo não encontrado: %s — view %s não criada",
                display_name,
                view_name,
            )
            loaded[view_name] = False

    return loaded
