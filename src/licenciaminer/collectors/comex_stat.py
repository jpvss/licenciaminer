"""Coletor de dados de comércio exterior mineral via Comex Stat (MDIC)."""

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
from licenciaminer.processors.normalize import add_metadata, atomic_parquet_write

logger = logging.getLogger(__name__)

COMEX_API_URL = "https://api-comexstat.mdic.gov.br/general"

# NCMs minerais: capítulo 26 (minérios, escórias, cinzas)
MINERAL_NCM_CHAPTER = "26"


@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout)
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _query_comex(payload: dict) -> list[dict]:
    """Envia consulta à API Comex Stat."""
    logger.info("Comex Stat: consultando %s", payload.get("flow", "?"))
    with httpx.Client(timeout=HTTP_TIMEOUT) as client:
        resp = client.post(COMEX_API_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", data) if isinstance(data, dict) else data


def collect_comex(
    data_dir: Path,
    years: int = 5,
) -> Path:
    """Coleta dados de exportação/importação mineral e salva como parquet.

    Args:
        data_dir: Diretório base de dados.
        years: Anos de histórico (padrão: 5).

    Returns:
        Caminho do arquivo parquet gerado.
    """
    from datetime import datetime

    current_year = datetime.now().year
    year_start = current_year - years

    all_records = []

    for flow in ["EXP", "IMP"]:
        payload = {
            "flow": flow,
            "monthDetail": True,
            "period": {
                "from": f"{year_start}-01",
                "to": f"{current_year}-12",
            },
            "filters": [
                {"filter": "chapter", "values": [MINERAL_NCM_CHAPTER]},
            ],
            "details": [
                "chapter",
                "heading",
                "state",
                "country",
            ],
            "metrics": [
                "metricFOB",
                "metricKG",
            ],
        }

        try:
            records = _query_comex(payload)
            if isinstance(records, list):
                for r in records:
                    r["fluxo"] = "Exportação" if flow == "EXP" else "Importação"
                all_records.extend(records)
                logger.info("Comex %s: %d registros", flow, len(records))
        except Exception:
            logger.exception("Comex Stat %s: erro na consulta", flow)

    output = data_dir / "processed" / "comex_mineracao.parquet"

    if not all_records:
        logger.warning("Comex Stat: nenhum registro retornado")
        # Criar parquet vazio com schema esperado
        df = pd.DataFrame(columns=[
            "year", "month", "chapter", "heading",
            "state", "country", "metricFOB", "metricKG", "fluxo",
        ])
    else:
        df = pd.DataFrame(all_records)

    # Normalizar nomes
    col_map = {
        "metricFOB": "valor_fob_usd",
        "metricKG": "peso_kg",
        "year": "ano",
        "month": "mes",
        "chapter": "capitulo_ncm",
        "heading": "posicao_ncm",
        "state": "uf",
        "country": "pais",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    atomic_parquet_write(df, output)
    add_metadata(output, "comex_stat", len(df))

    logger.info("Comex Stat: %d registros salvos em %s", len(df), output)
    return output
