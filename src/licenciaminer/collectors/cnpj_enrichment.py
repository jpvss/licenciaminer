"""Coletor de dados cadastrais de CNPJ via BrasilAPI."""

import logging
import time
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

from licenciaminer.config import RETRY_ATTEMPTS, RETRY_MAX_WAIT, RETRY_MIN_WAIT
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

CNPJ_API_URL = "https://brasilapi.com.br/api/cnpj/v1"


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_cnpj(client: httpx.Client, cnpj: str) -> dict[str, object] | None:
    """Consulta dados de um CNPJ na BrasilAPI."""
    response = client.get(f"{CNPJ_API_URL}/{cnpj}")
    if response.status_code in (400, 404):
        return None
    if response.status_code == 429:
        # Rate limited — esperar e deixar tenacity retry
        raise httpx.ReadTimeout("Rate limited")
    response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if "json" not in content_type:
        logger.debug("CNPJ %s retornou content-type=%s (não JSON)", cnpj, content_type)
        return None
    data: dict[str, object] = response.json()
    return data


def collect_cnpj_data(
    data_dir: Path,
    max_records: int | None = None,
) -> Path:
    """Enriquece CNPJs únicos de mineração com dados da Receita Federal.

    Extrai CNPJs válidos (14 dígitos) de SEMAD, consulta BrasilAPI
    e salva perfil das empresas.
    """
    # Coletar CNPJs únicos das fontes existentes
    cnpjs: set[str] = set()

    semad_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    if semad_path.exists():
        df_semad = pd.read_parquet(semad_path, columns=["cnpj_cpf"])
        valid = df_semad["cnpj_cpf"].dropna()
        # Apenas CNPJs (14 dígitos), não CPFs (11 dígitos)
        cnpjs.update(str(v) for v in valid if len(str(v)) == 14)

    # Carregar existentes para não re-consultar
    output_path = data_dir / "processed" / "cnpj_empresas.parquet"
    already_done: set[str] = set()
    if output_path.exists():
        df_existing = pd.read_parquet(output_path, columns=["cnpj"])
        already_done = set(df_existing["cnpj"].dropna().astype(str))
        logger.info("CNPJ: %d já consultados anteriormente", len(already_done))

    to_fetch = sorted(cnpjs - already_done)
    logger.info("CNPJ: %d novos para consultar (de %d únicos total)", len(to_fetch), len(cnpjs))

    if max_records is not None:
        to_fetch = to_fetch[:max_records]

    records: list[dict[str, object]] = []
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        for i, cnpj in enumerate(to_fetch):
            try:
                data = _query_cnpj(client, cnpj)
                if data:
                    record: dict[str, object] = {
                        "cnpj": cnpj,
                        "razao_social": data.get("razao_social", ""),
                        "nome_fantasia": data.get("nome_fantasia", ""),
                        "cnae_fiscal": data.get("cnae_fiscal", ""),
                        "cnae_descricao": data.get(
                            "cnae_fiscal_descricao", ""
                        ),
                        "porte": data.get("porte", ""),
                        "data_abertura": data.get(
                            "data_inicio_atividade", ""
                        ),
                        "situacao": data.get(
                            "descricao_situacao_cadastral", ""
                        ),
                        "natureza_juridica": data.get(
                            "natureza_juridica", ""
                        ),
                        "uf": data.get("uf", ""),
                        "municipio": data.get("municipio", ""),
                        "_source_url": f"{CNPJ_API_URL}/{cnpj}",
                    }
                    records.append(record)
            except Exception:
                logger.warning("Erro ao consultar CNPJ %s", cnpj, exc_info=True)

            if (i + 1) % 100 == 0:
                logger.info("CNPJ: %d/%d consultados", i + 1, len(to_fetch))

            time.sleep(0.5)

    logger.info(
        "CNPJ: %d registros obtidos de %d consultados", len(records), len(to_fetch)
    )

    df_new = pd.DataFrame(records)

    # Metadata apenas nos novos registros (preserva timestamps dos existentes)
    if not df_new.empty:
        df_new = add_metadata(df_new, source="receita_federal_cnpj")

    # Juntar com existentes
    if already_done and not df_new.empty:
        df_existing = pd.read_parquet(output_path)
        df = pd.concat([df_existing, df_new], ignore_index=True)
        df = df.drop_duplicates(subset="cnpj", keep="first")
    elif already_done:
        df = pd.read_parquet(output_path)
    else:
        df = df_new

    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("CNPJ: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
