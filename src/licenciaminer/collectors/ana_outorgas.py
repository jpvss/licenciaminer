"""Coletor de outorgas de direito de uso de recursos hídricos da ANA.

Outorgas (water rights) são necessárias para atividades de mineração
que utilizam recursos hídricos. Dados da Agência Nacional de Águas.
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
from licenciaminer.config import RETRY_ATTEMPTS, RETRY_MIN_WAIT
from licenciaminer.processors.normalize import (
    add_metadata,
    atomic_parquet_write,
    normalize_cnpj,
)

logger = logging.getLogger(__name__)

# URL pode mudar — checar dados.ana.gov.br se falhar
ANA_OUTORGAS_URL = (
    "https://dados.ana.gov.br/dataset/"
    "9ec2afdb-19cc-4dbe-a6ed-efc1142976d5/resource/"
    "9ec2afdb-19cc-4dbe-a6ed-efc1142976d5/download/outorgas.csv"
)


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=60),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _download_csv(url: str) -> bytes:
    """Baixa CSV da ANA com timeout longo."""
    logger.info("Baixando %s", url[:80])
    with httpx.Client(timeout=300.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def collect_ana_outorgas(data_dir: Path, uf_filter: str | None = "MG") -> Path:
    """Coleta outorgas de direito de uso de recursos hídricos da ANA.

    Nota: ANA cobre apenas rios federais (interestaduais).
    Outorgas estaduais são emitidas pelo IGAM em MG.
    """
    csv_bytes = _download_csv(ANA_OUTORGAS_URL)

    df = pd.read_csv(
        io.BytesIO(csv_bytes),
        sep=";",
        encoding="latin-1",
        dtype=str,
        low_memory=False,
    )
    logger.info("ANA Outorgas: %d registros brutos", len(df))

    # Filtrar por UF se possível
    if uf_filter:
        uf_col = next((c for c in df.columns if "uf" in c.lower()), None)
        if uf_col:
            df = df[df[uf_col] == uf_filter].copy()
            logger.info("ANA Outorgas: %d registros para UF=%s", len(df), uf_filter)

    # Normalizar CNPJ se coluna existir
    cnpj_col = next(
        (c for c in df.columns if "cpf" in c.lower() or "cnpj" in c.lower()),
        None,
    )
    if cnpj_col:
        df[cnpj_col] = df[cnpj_col].apply(
            lambda x: normalize_cnpj(str(x)) if pd.notna(x) else None
        )

    df["_source_url"] = "https://dados.ana.gov.br/dataset/outorgas"
    df = add_metadata(df, source="ana_outorgas")

    output_path = data_dir / "processed" / "ana_outorgas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    save_collection_metadata(data_dir, "ana_outorgas", len(df))
    logger.info("ANA Outorgas: salvos em %s (%d registros)", output_path, len(df))
    return output_path
