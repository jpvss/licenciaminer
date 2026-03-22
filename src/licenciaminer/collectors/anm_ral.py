"""Coletor de dados de produção mineral RAL (Relatório Anual de Lavra) da ANM.

Dados agregados por UF e substância (sem CNPJ individual).
Útil para contexto de mercado, não para perfil de empresa.
"""

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

from licenciaminer.collectors.metadata import save_collection_metadata
from licenciaminer.config import (
    HTTP_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
)
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

RAL_URLS = {
    "producao_bruta": (
        "https://app.anm.gov.br/dadosabertos/AMB/Producao_Bruta.csv"
    ),
    "producao_beneficiada": (
        "https://app.anm.gov.br/dadosabertos/AMB/Producao_Beneficiada.csv"
    ),
}


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


def collect_ral(data_dir: Path, uf_filter: str | None = "MG") -> Path:
    """Coleta dados de produção mineral (RAL) da ANM.

    Baixa produção bruta e beneficiada, filtra por UF.
    Dados agregados por UF/substância/ano — sem CNPJ individual.
    """
    dfs: list[pd.DataFrame] = []

    for name, url in RAL_URLS.items():
        csv_bytes = _download_csv(url)
        df = pd.read_csv(
            io.BytesIO(csv_bytes),
            sep=",",
            encoding="latin-1",
            dtype=str,
            low_memory=False,
        )
        df["_tipo_producao"] = name
        dfs.append(df)
        logger.info("RAL %s: %d registros", name, len(df))

    df_all = pd.concat(dfs, ignore_index=True)
    logger.info("RAL: %d registros brutos totais", len(df_all))

    if uf_filter and "UF" in df_all.columns:
        df_all = df_all[df_all["UF"] == uf_filter].copy()
        logger.info("RAL: %d registros para UF=%s", len(df_all), uf_filter)

    df_all["_source_url"] = "https://app.anm.gov.br/dadosabertos/AMB/"
    df_all = add_metadata(df_all, source="anm_ral")

    output_path = data_dir / "processed" / "anm_ral.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df_all, output_path)
    save_collection_metadata(data_dir, "anm_ral", len(df_all))
    logger.info("RAL: dados salvos em %s (%d registros)", output_path, len(df_all))
    return output_path
