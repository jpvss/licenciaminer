"""Coletor de licenças ambientais do IBAMA SISLIC."""

import logging
from pathlib import Path

import httpx
import pandas as pd
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from licenciaminer.config import (
    HTTP_TIMEOUT,
    IBAMA_SISLIC_URL,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_columns,
    parse_date_br,
)

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _fetch_sislic() -> list[dict[str, object]]:
    """Baixa o JSON completo do SISLIC com retry."""
    logger.info("Baixando dados do IBAMA SISLIC: %s", IBAMA_SISLIC_URL)
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(IBAMA_SISLIC_URL)
        response.raise_for_status()
        data: list[dict[str, object]] = response.json()
        logger.info("IBAMA: %d registros brutos recebidos", len(data))
        return data


def collect_ibama(data_dir: Path) -> Path:
    """Coleta licenças ambientais de mineração do IBAMA SISLIC.

    Baixa o JSON completo, filtra registros de mineração,
    normaliza colunas e salva como parquet.
    """
    raw_data = _fetch_sislic()
    df = pd.DataFrame(raw_data)

    # Filtrar apenas mineração
    mask = df["tipologia"].str.contains("Mineração", case=False, na=False)
    df = df[mask].copy()
    logger.info("IBAMA: %d registros de mineração após filtro", len(df))

    # Normalizar
    df = normalize_columns(df)

    # Parsear datas brasileiras
    for col in ["data_emissao", "data_vencimento"]:
        if col in df.columns:
            df[col] = parse_date_br(df[col])

    # Renomear colunas para nomes padronizados
    rename_map = {
        "des_tipo_licenca": "tipo_licenca",
        "num_licenca": "numero_licenca",
        "numero_processo": "numero_processo",
        "nome_pessoa": "nome_empreendedor",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    df = add_metadata(df, source="ibama_sislic")

    output_path = data_dir / "processed" / "ibama_licencas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("IBAMA: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
