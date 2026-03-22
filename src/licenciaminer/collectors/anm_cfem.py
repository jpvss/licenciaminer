"""Coletor de dados de arrecadação CFEM (royalties minerários) da ANM."""

import io
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
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_cnpj,
)

logger = logging.getLogger(__name__)

# Usar o arquivo mais recente (2022-2026) para agilizar; arquivo completo tem 300MB
CFEM_URL = (
    "https://app.anm.gov.br/dadosabertos/ARRECADACAO/CFEM_Arrecadacao_2022_2026.csv"
)
CFEM_URL_FULL = (
    "https://app.anm.gov.br/dadosabertos/ARRECADACAO/CFEM_Arrecadacao.csv"
)


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _download_csv(url: str) -> bytes:
    """Baixa arquivo CSV."""
    logger.info("Baixando %s", url)
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def collect_cfem(
    data_dir: Path,
    uf_filter: str | None = "MG",
    full_history: bool = False,
) -> Path:
    """Coleta dados de arrecadação CFEM da ANM.

    Por padrão baixa apenas 2022-2026 (~75MB). Use full_history=True
    para todo o histórico (~300MB).
    """
    url = CFEM_URL_FULL if full_history else CFEM_URL
    csv_bytes = _download_csv(url)

    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        sep=",",
        encoding="latin-1",
        dtype={"CPF_CNPJ": str, "Processo": str},
        low_memory=False,
    )
    logger.info("CFEM: %d registros brutos", len(df))

    # Filtrar por UF
    if uf_filter:
        uf_col = next((c for c in df.columns if "uf" in c.lower()), None)
        if uf_col:
            df = df[df[uf_col] == uf_filter].copy()
            logger.info("CFEM: %d registros para UF=%s", len(df), uf_filter)

    # Normalizar CNPJ
    cnpj_col = next((c for c in df.columns if "cpf" in c.lower() or "cnpj" in c.lower()), None)
    if cnpj_col:
        df[cnpj_col] = df[cnpj_col].apply(
            lambda x: normalize_cnpj(str(x)) if pd.notna(x) else None
        )

    df["_source_url"] = "https://app.anm.gov.br/dadosabertos/ARRECADACAO/"

    df = add_metadata(df, source="anm_cfem")

    output_path = data_dir / "processed" / "anm_cfem.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    from licenciaminer.collectors.metadata import save_collection_metadata
    save_collection_metadata(data_dir, "anm_cfem", len(df))
    logger.info("CFEM: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
