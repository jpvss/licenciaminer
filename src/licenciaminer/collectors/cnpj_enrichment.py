"""Coletor de dados cadastrais de CNPJ via API pública."""

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

CNPJ_API_URL = "https://opencnpj.org/api/cnpj"


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_cnpj(client: httpx.Client, cnpj: str) -> dict[str, object] | None:
    """Consulta dados de um CNPJ na API pública."""
    response = client.get(f"{CNPJ_API_URL}/{cnpj}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    data: dict[str, object] = response.json()
    return data


def collect_cnpj_data(
    data_dir: Path,
    max_records: int | None = None,
) -> Path:
    """Enriquece CNPJs únicos de mineração com dados da Receita Federal.

    Extrai CNPJs de SEMAD e ANM, consulta API pública e salva perfil
    das empresas.
    """
    # Coletar CNPJs únicos das fontes existentes
    cnpjs: set[str] = set()

    semad_path = data_dir / "processed" / "mg_semad_licencas.parquet"
    if semad_path.exists():
        df_semad = pd.read_parquet(semad_path, columns=["cnpj_cpf"])
        valid = df_semad["cnpj_cpf"].dropna()
        # Apenas CNPJs (14 dígitos), não CPFs (11 dígitos)
        cnpjs.update(v for v in valid if len(str(v)) == 14)

    anm_path = data_dir / "processed" / "anm_processos.parquet"
    if anm_path.exists():
        # ANM não tem CNPJ diretamente — pular
        pass

    logger.info("CNPJ: %d CNPJs únicos para consultar", len(cnpjs))

    cnpj_list = sorted(cnpjs)
    if max_records is not None:
        cnpj_list = cnpj_list[:max_records]

    records: list[dict[str, object]] = []
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        for i, cnpj in enumerate(cnpj_list):
            try:
                data = _query_cnpj(client, cnpj)
                if data:
                    record: dict[str, object] = {
                        "cnpj": cnpj,
                        "razao_social": data.get("razao_social", ""),
                        "nome_fantasia": data.get("nome_fantasia", ""),
                        "cnae_principal": str(
                            data.get("cnae_fiscal_principal", {})
                        ),
                        "porte": data.get("porte", ""),
                        "data_abertura": data.get("data_inicio_atividade", ""),
                        "situacao": data.get("descricao_situacao_cadastral", ""),
                        "natureza_juridica": data.get(
                            "descricao_natureza_juridica", ""
                        ),
                        "uf": data.get("uf", ""),
                        "municipio": data.get("municipio", ""),
                        "_source_url": f"https://opencnpj.org/api/cnpj/{cnpj}",
                    }
                    records.append(record)
                else:
                    logger.debug("CNPJ %s não encontrado", cnpj)
            except Exception:
                logger.warning("Erro ao consultar CNPJ %s", cnpj, exc_info=True)

            if (i + 1) % 100 == 0:
                logger.info("CNPJ: %d/%d consultados", i + 1, len(cnpj_list))

            time.sleep(0.5)

    logger.info("CNPJ: %d registros obtidos de %d consultados", len(records), len(cnpj_list))

    df = pd.DataFrame(records)
    df = add_metadata(df, source="receita_federal_cnpj")

    output_path = data_dir / "processed" / "cnpj_empresas.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_parquet_write(df, output_path)
    logger.info("CNPJ: dados salvos em %s (%d registros)", output_path, len(df))
    return output_path
