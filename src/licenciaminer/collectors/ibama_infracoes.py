"""Coletor de autos de infração ambiental do IBAMA."""

import io
import logging
import zipfile
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

IBAMA_INFRACOES_URL = (
    "https://dadosabertos.ibama.gov.br/dados/SIFISC/"
    "auto_infracao/auto_infracao/auto_infracao_csv.zip"
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
def _download_zip(url: str) -> bytes:
    """Baixa arquivo ZIP."""
    logger.info("Baixando %s", url)
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def collect_ibama_infracoes(data_dir: Path, uf_filter: str | None = "MG") -> Path:
    """Coleta autos de infração ambiental do IBAMA.

    Baixa o CSV de autos de infração, opcionalmente filtra por UF,
    e salva como parquet.
    """
    zip_bytes = _download_zip(IBAMA_INFRACOES_URL)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_names = sorted(n for n in zf.namelist() if n.endswith(".csv"))
        if not csv_names:
            raise ValueError("Nenhum CSV encontrado no ZIP de infrações IBAMA")
        logger.info("IBAMA Infrações: %d arquivos CSV no ZIP", len(csv_names))

        dfs: list[pd.DataFrame] = []
        for csv_name in csv_names:
            with zf.open(csv_name) as f:
                chunk = pd.read_csv(
                    f,
                    sep=";",
                    encoding="latin-1",
                    dtype=str,
                    low_memory=False,
                )
                dfs.append(chunk)
        df = pd.concat(dfs, ignore_index=True)

    logger.info("IBAMA Infrações: %d registros brutos", len(df))

    # Filtrar por UF se solicitado
    if uf_filter and "uf_infracao" in df.columns:
        df = df[df["uf_infracao"] == uf_filter].copy()
        logger.info("IBAMA Infrações: %d registros para UF=%s", len(df), uf_filter)

    # Normalizar CNPJ
    if "cpf_cnpj_infrator" in df.columns:
        df["cpf_cnpj_infrator"] = df["cpf_cnpj_infrator"].apply(
            lambda x: normalize_cnpj(str(x)) if pd.notna(x) else None
        )

    # Adicionar URL de origem para auditoria
    df["_source_url"] = (
        "https://dadosabertos.ibama.gov.br/dataset/fiscalizacao-auto-de-infracao"
    )

    df = add_metadata(df, source="ibama_infracoes")

    output_path = data_dir / "processed" / "ibama_infracoes.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info(
        "IBAMA Infrações: dados salvos em %s (%d registros)", output_path, len(df)
    )
    return output_path
